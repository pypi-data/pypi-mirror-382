"""Databricks Serverless Jobs executor."""

import json
import logging
import os
import pathlib
import subprocess
import tempfile
import time
from typing import Dict, Any, Optional

from .base_executor import BaseExecutor
from ..models import CodeResult


class DatabricksExecutor(BaseExecutor):
    """Executor for running Python code on Databricks Serverless Jobs."""
    
    @property
    def platform_name(self) -> str:
        return "databricks"
    
    def __init__(self, python_path: str = "python", config: Dict[str, Any] = None):
        super().__init__(python_path, config)
        
        # Extract databricks configuration with sensible defaults
        # Support both nested structure (databricks: {config}) and flat structure (databricks: true + top-level config)
        if config and config.get('databricks'):
            if isinstance(config.get('databricks'), dict):
                # New nested structure: databricks: {cli: ..., volume_uri: ..., etc}
                databricks_config = config['databricks']
                self.job_config = databricks_config.get('job', {})
            else:
                # Original flat structure: databricks: true + top-level fields
                databricks_config = config
                self.job_config = config.get('job', {})
        else:
            databricks_config = {}
            self.job_config = {}
        
        self.cli = databricks_config.get('cli', "databricks")
        self.volume_uri = databricks_config.get('volume_uri', "dbfs:/Volumes/workspace/default/volume")
        self.code_path = databricks_config.get('code_path', None)  # Specific code path if provided
        self.timeout = databricks_config.get('timeout', "30m")
    
    def execute(self, code: str) -> CodeResult:
        """Execute Python code on Databricks Serverless Jobs.
        
        Args:
            code: Python code to execute
            
        Returns:
            CodeResult containing stdout, stderr, return_code, and runtime_ms
        """
        logging.info(f"Databricks CLI: {self.cli}")
        logging.info(f"Volume URI: {self.volume_uri}")
        logging.info(f"Code Path: {self.code_path}")
        logging.info(f"Timeout: {self.timeout}")
        
        t0 = time.time()

        try:
            # 1. Write & upload code
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
                f.write(code.encode())
                local_tmp = pathlib.Path(f.name)

            # Always use temp filename to avoid overwriting original code_path
            remote_uri = f"{self.volume_uri}/{local_tmp.name}"
            subprocess.run([
                self.cli, "fs", "cp", str(local_tmp), remote_uri,
                "--overwrite", "--output", "json"
            ], check=True)
            os.unlink(local_tmp)

            # 2. Build job JSON
            job_name_template = self.job_config.get('name', 'run-<script-stem>-<timestamp>')
            job_name = job_name_template.replace('<script-stem>', local_tmp.stem).replace('<timestamp>', str(int(t0)))
            
            # Build tasks configuration
            default_task = {
                "task_key": "t",
                "spark_python_task": {"python_file": remote_uri},
                "environment_key": "default"
            }
            tasks = self.job_config.get('tasks', [default_task])
            # Update the python_file path in the first task
            if tasks and 'spark_python_task' in tasks[0]:
                tasks[0]['spark_python_task']['python_file'] = remote_uri
            
            # Build environments configuration
            default_environments = [{
                "environment_key": "default",
                "spec": {"client": "1"}
            }]
            environments = self.job_config.get('environments', default_environments)
            
            job_json = {
                "name": job_name,
                "tasks": tasks,
                "environments": environments
            }
            
            with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as spec:
                json.dump(job_json, spec)
                spec_path = spec.name

            # 3. Create job
            create = subprocess.run([
                self.cli, "jobs", "create",
                "--json", f"@{spec_path}", "--output", "json"
            ], text=True, capture_output=True, check=True)
            
            job_id = json.loads(create.stdout)["job_id"]
            os.unlink(spec_path)  # Clean up the job spec file

            # 4. Run job (blocks)
            try:
                output = subprocess.run([
                    self.cli, "jobs", "run-now",
                    str(job_id),
                    "--timeout", self.timeout,
                    "--output", "json"
                ], text=True, input="", capture_output=True)
                
                # Check if job submission failed
                if output.returncode != 0 or not output.stdout.strip():
                    runtime_ms = int((time.time() - t0) * 1000)
                    error_msg = "Databricks job submission failed"
                    if output.stderr:
                        error_msg += f": {output.stderr}"
                    elif not output.stdout.strip():
                        error_msg += ": Empty response from Databricks"
                    
                    logging.error(f"Job submission failed: stdout='{output.stdout}', stderr='{output.stderr}', returncode={output.returncode}")
                    return CodeResult(stdout=None, stderr=error_msg, return_code=1, runtime_ms=runtime_ms)
                
                # Parse the job run response
                try:
                    run_response = json.loads(output.stdout)
                    run_id = run_response["run_id"]
                except (json.JSONDecodeError, KeyError) as e:
                    runtime_ms = int((time.time() - t0) * 1000)
                    logging.error(f"Failed to parse job run response: {e}, stdout='{output.stdout}'")
                    return CodeResult(
                        stdout=None, 
                        stderr=f"Failed to parse Databricks response: {e}", 
                        return_code=1, 
                        runtime_ms=runtime_ms
                    )

            except subprocess.TimeoutExpired:
                runtime_ms = int((time.time() - t0) * 1000)
                error_msg = f"Databricks job submission timed out after {self.timeout}"
                logging.info(error_msg)
                return CodeResult(stdout=None, stderr=error_msg, return_code=-9, runtime_ms=runtime_ms)

            # 5. Find child task-run and fetch logs
            get_run = subprocess.run([
                self.cli, "jobs", "get-run", str(run_id), "--output", "json"
            ], text=True, capture_output=True, check=True)
            
            task_run_id = json.loads(get_run.stdout)["tasks"][0]["run_id"]

            # 6. Fetch logs
            out_json = subprocess.run([
                self.cli, "jobs", "get-run-output", str(task_run_id), "--output", "json"
            ], text=True, capture_output=True, check=True)
            
            out = json.loads(out_json.stdout)
            logs = out.get("logs")
            result_state = out.get("metadata", {}).get("state", {}).get("result_state", "FAILED")

            rc = 0 if result_state == "SUCCESS" else 1
            runtime_ms = int((time.time() - t0) * 1000)

            # Extract error details if available
            stderr_msg = None if rc == 0 else "Task failed"
            if rc != 0 and out.get("error"):
                stderr_msg = f"Task failed: {out['error']}"

            return CodeResult(stdout=logs, stderr=stderr_msg, return_code=rc, runtime_ms=runtime_ms)
            
        except Exception as e:
            # Handle any errors in the entire process
            runtime_ms = int((time.time() - t0) * 1000)
            logging.error(f"Failed to execute Databricks job: {e}")
            return CodeResult(
                stdout=None, 
                stderr=f"Failed to execute Databricks job: {e}", 
                return_code=1, 
                runtime_ms=runtime_ms
            )
    
    def is_available(self) -> bool:
        """Check if Databricks CLI is available and configured."""
        try:
            result = subprocess.run(
                [self.cli, "--version"], 
                capture_output=True, 
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False



# OLD CODE but maybe usefull later!
    # async def _save_checkpoint_to_databricks_volume(self, code_content: str, meta_content: str, base_filename: str, config: dict):
    #     """Save checkpoint files directly to Databricks volume using CLI (following existing upload pattern)."""
    #     try:
    #         # Extract databricks configuration (same pattern as _databricks_run_python_code)
    #         if isinstance(config.get('databricks'), dict):
    #             databricks_config = config['databricks']
    #         else:
    #             databricks_config = config
            
    #         CLI = databricks_config.get('cli', "databricks")
    #         VOLUME_URI = databricks_config.get('volume_uri', "dbfs:/Volumes/workspace/default/volume")
            
    #         # Ensure checkpoints directory exists
    #         checkpoints_dir = f"{VOLUME_URI}/{CHECKPOINTS_FOLDER}"
    #         mkdir_result = subprocess.run([CLI, "fs", "mkdir", checkpoints_dir], 
    #                                     capture_output=True, text=True)
    #         # mkdir is okay to fail if directory already exists
            
    #         # Create remote paths
    #         remote_code_path = f"{checkpoints_dir}/{base_filename}.py"
    #         remote_meta_path = f"{checkpoints_dir}/{base_filename}.json"
            
    #         # Save code file using temp file + CLI upload pattern (following existing code)
    #         with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
    #             f.write(code_content.encode())
    #             local_tmp_code = pathlib.Path(f.name)
            
    #         # Try uploading code file
    #         result = subprocess.run([CLI, "fs", "cp", str(local_tmp_code), remote_code_path,
    #                        "--overwrite", "--output", "json"], capture_output=True, text=True)
    #         if result.returncode != 0:
    #             print(f"Failed to upload checkpoint code: {result.stderr}")
    #             return
    #         os.unlink(local_tmp_code)
            
    #         # Save metadata file using temp file + CLI upload pattern
    #         with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
    #             f.write(meta_content.encode())
    #             local_tmp_meta = pathlib.Path(f.name)
            
    #         # Try uploading metadata file
    #         result = subprocess.run([CLI, "fs", "cp", str(local_tmp_meta), remote_meta_path,
    #                        "--overwrite", "--output", "json"], capture_output=True, text=True)
    #         if result.returncode != 0:
    #             print(f"Failed to upload checkpoint metadata: {result.stderr}")
    #             return
    #         os.unlink(local_tmp_meta)
            
    #         # print(f"Checkpoint uploaded to: {VOLUME_URI}/{CHECKPOINTS_FOLDER}/{base_filename}.*")
            
    #     except Exception as e:
    #         print(f"Checkpoint upload error: {e}")

    # async def _save_current_run_to_databricks_volume(self, code_content: str, meta_content: str, config: dict, unique_id: str, timestamp: str):
    #     """Save current run files directly to Databricks volume under `current_runs` directory."""
    #     try:
    #         if isinstance(config.get('databricks'), dict):
    #             databricks_config = config['databricks']
    #         else:
    #             databricks_config = config

    #         CLI = databricks_config.get('cli', "databricks")
    #         VOLUME_URI = databricks_config.get('volume_uri', "dbfs:/Volumes/workspace/default/volume")

    #         # Ensure current_runs directory exists
    #         current_dir = f"{VOLUME_URI}/{CURRENT_RUNS_FOLDER}"
    #         subprocess.run([CLI, "fs", "mkdir", current_dir], capture_output=True, text=True)

    #         remote_code_path = f"{current_dir}/latest.py"
    #         remote_meta_path = f"{current_dir}/latest.json"
    #         uid_safe = _make_filesystem_safe(unique_id)
    #         ts_safe = _make_filesystem_safe(timestamp)
    #         remote_code_uid_path = f"{current_dir}/run_{ts_safe}_{uid_safe}.py"
    #         remote_meta_uid_path = f"{current_dir}/run_{ts_safe}_{uid_safe}.json"

    #         # Upload code
    #         with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
    #             f.write(code_content.encode())
    #             local_tmp_code = pathlib.Path(f.name)
    #         result = subprocess.run([CLI, "fs", "cp", str(local_tmp_code), remote_code_path,
    #                                  "--overwrite", "--output", "json"], capture_output=True, text=True)
    #         os.unlink(local_tmp_code)
    #         if result.returncode != 0:
    #             print(f"Failed to upload current run code: {result.stderr}")
    #             return

    #         # Upload code (UUID version)
    #         with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
    #             f.write(code_content.encode())
    #             local_tmp_code_uid = pathlib.Path(f.name)
    #         result = subprocess.run([CLI, "fs", "cp", str(local_tmp_code_uid), remote_code_uid_path,
    #                                  "--overwrite", "--output", "json"], capture_output=True, text=True)
    #         os.unlink(local_tmp_code_uid)
    #         if result.returncode != 0:
    #             print(f"Failed to upload current run code (uuid): {result.stderr}")
    #             return

    #         # Upload metadata
    #         with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
    #             f.write(meta_content.encode())
    #             local_tmp_meta = pathlib.Path(f.name)
    #         result = subprocess.run([CLI, "fs", "cp", str(local_tmp_meta), remote_meta_path,
    #                                  "--overwrite", "--output", "json"], capture_output=True, text=True)
    #         os.unlink(local_tmp_meta)
    #         if result.returncode != 0:
    #             print(f"Failed to upload current run metadata: {result.stderr}")
    #             return

    #         # Upload metadata (UUID version)
    #         with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
    #             f.write(meta_content.encode())
    #             local_tmp_meta_uid = pathlib.Path(f.name)
    #         result = subprocess.run([CLI, "fs", "cp", str(local_tmp_meta_uid), remote_meta_uid_path,
    #                                  "--overwrite", "--output", "json"], capture_output=True, text=True)
    #         os.unlink(local_tmp_meta_uid)
    #         if result.returncode != 0:
    #             print(f"Failed to upload current run metadata (uuid): {result.stderr}")
    #             return

    #         # print(f"Current run uploaded to: {VOLUME_URI}/{CURRENT_RUNS_FOLDER}/latest.* and run_{uid_safe}.*")
    #     except Exception as e:
    #         print(f"Current run upload error: {e}")