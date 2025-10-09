"""Clean Docker-based Google Cloud Run Jobs executor."""

import asyncio
import logging
import subprocess
import time
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List
import shutil

from .base_executor import BaseExecutor
from ..models import CodeResult, CodeVersion


class GCloudExecutor(BaseExecutor):
    """Executor for running code on Google Cloud Run Jobs using Docker images."""
    
    @property
    def platform_name(self) -> str:
        return "gcloud"
    
    def __init__(self, python_path: str = "python", config: Dict[str, Any] = None):
        super().__init__(python_path, config)
        
        gcloud_config = config.get('gcloud', {}) if config else {}
        
        self.job_template = gcloud_config.get('job_template', 'default-job')
        self.region = gcloud_config.get('region', 'us-central1')
        self.bucket = gcloud_config.get('bucket', 'co-datascientist-runs')
        self.project_id = gcloud_config.get('project_id', self._get_project_id())
        self.artifact_registry = gcloud_config.get('artifact_registry', f'{self.region}-docker.pkg.dev/{self.project_id}/co-datascientist')
        self.timeout = gcloud_config.get('timeout', '30m')
        self.polling_interval = gcloud_config.get('polling_interval', 5)
        self.max_concurrent_jobs = gcloud_config.get('max_concurrent_jobs', 50)
        
        # Cached Docker image name for this workflow
        self._docker_image = None
        
        logging.info(f"GCloud Executor initialized: job={self.job_template}, region={self.region}")
    
    def _get_project_id(self) -> str:
        """Get GCloud project ID."""
        try:
            result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                                    capture_output=True, text=True, timeout=10)
            return result.stdout.strip()
        except Exception as e:
            logging.warning(f"Could not get project ID: {e}")
            return "co-datascientist"
    
    def supports_distributed_execution(self) -> bool:
        """Check if gcloud is available for distributed execution."""
        try:
            result = subprocess.run(['gcloud', 'version'], capture_output=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    # === Data Upload ===
    
    def upload_workflow_data(self, local_data_path: Optional[Path], workflow_id: str) -> str:
        """Upload data to GCS once per workflow.
        
        Args:
            local_data_path: Local path to data directory (or None if already in GCS)
            workflow_id: Unique workflow identifier
            
        Returns:
            GCS path to data (gs://bucket/workflows/{workflow_id}/data/)
        """
        gcs_data_path = f"gs://{self.bucket}/workflows/{workflow_id}/data/"
        
        if local_data_path and local_data_path.exists():
            logging.info(f"Uploading data from {local_data_path} to {gcs_data_path}")
            result = subprocess.run([
                'gsutil', '-m', 'rsync', '-r',
                str(local_data_path),
                gcs_data_path
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"Failed to upload data: {result.stderr}")
            
            logging.info("Data uploaded successfully")
        
        return gcs_data_path
    
    # === Docker Image Building ===
    
    def build_and_push_docker_image(self, base_path: Path, workflow_id: str) -> str:
        """Build Docker image with baseline code and push to Artifact Registry.
        
        Args:
            base_path: Local path to project root
            workflow_id: Unique workflow identifier
            
        Returns:
            Full Docker image URI
        """
        image_name = f"workflow-{workflow_id}"
        image_uri = f"{self.artifact_registry}/{image_name}:latest"
        
        # Create temporary build directory
        build_dir = Path(f"/tmp/docker_build_{workflow_id}")
        build_dir.mkdir(exist_ok=True, parents=True)
        
        try:
            # Copy project files (excluding checkpoints and venvs)
            logging.info(f"Preparing Docker build context from {base_path}")
            self._copy_project_for_docker(base_path, build_dir)
            
            # Copy Dockerfile and entrypoint
            templates_dir = Path(__file__).parent
            shutil.copy(templates_dir / "Dockerfile.template", build_dir / "Dockerfile")
            shutil.copy(templates_dir / "entrypoint.sh", build_dir / "entrypoint.sh")
            
            # Build using Cloud Build (faster, uses caching)
            logging.info(f"Building Docker image: {image_uri}")
            result = subprocess.run([
                'gcloud', 'builds', 'submit',
                '--tag', image_uri,
                '--timeout', '20m',
                str(build_dir)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"Docker build failed: {result.stderr}")
            
            logging.info(f"✓ Docker image built and pushed: {image_uri}")
            self._docker_image = image_uri
            return image_uri
            
        finally:
            # Cleanup build directory
            if build_dir.exists():
                shutil.rmtree(build_dir, ignore_errors=True)
    
    def _copy_project_for_docker(self, source: Path, dest: Path):
        """Copy project files excluding unwanted directories."""
        exclude_patterns = {
            '__pycache__', '.git', '.venv', 'venv', 'node_modules',
            'co_datascientist_checkpoints', 'current_runs', '.DS_Store'
        }
        
        for item in source.iterdir():
            if item.name in exclude_patterns or item.name.startswith('.'):
                continue
            
            dest_item = dest / item.name
            if item.is_dir():
                shutil.copytree(item, dest_item, ignore=shutil.ignore_patterns(*exclude_patterns))
            else:
                shutil.copy2(item, dest_item)
    
    # === Code Execution ===
    
    def execute(self, code: str | Dict[str, str], manifest: Optional[Dict] = None) -> CodeResult:
        """Execute code using Docker image on Cloud Run Job.
        
        Args:
            code: Dict[str, str] mapping filepath -> content (multi-file)
            manifest: Project manifest with workflow_id, run_command, etc.
            
        Returns:
            CodeResult containing stdout, stderr, return_code, and runtime_ms
        """
        t0 = time.time()
        
        if not isinstance(code, dict) or not manifest:
            return CodeResult(
                stdout=None,
                stderr="Docker executor requires dict code and manifest",
                return_code=1,
                runtime_ms=0
            )
        
        workflow_id = manifest['workflow_id']
        run_command = manifest['run_command']
        is_baseline = manifest.get('is_baseline', False)
        gcs_data_path = manifest.get('gcs_data_path', '')
        
        # Upload evolved files to GCS (if not baseline)
        gcs_evolved_path = ""
        if not is_baseline:
            execution_id = f"exec_{int(t0)}_{uuid.uuid4().hex[:8]}"
            gcs_evolved_path = f"gs://{self.bucket}/workflows/{workflow_id}/evolved/{execution_id}/"
            self._upload_evolved_files(code, gcs_evolved_path)
        
        # Get Docker image (should already be built)
        if not self._docker_image:
            self._docker_image = f"{self.artifact_registry}/workflow-{workflow_id}:latest"
        
        # Execute job
        return self._execute_docker_job(
            docker_image=self._docker_image,
            run_command=run_command,
            gcs_data_path=gcs_data_path,
            gcs_evolved_path=gcs_evolved_path,
            workflow_id=workflow_id,
            t0=t0
        )
    
    def _upload_evolved_files(self, evolved_files: Dict[str, str], gcs_path: str):
        """Upload evolved files to GCS."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Write files to temp directory
            for filepath, content in evolved_files.items():
                file_path = tmpdir_path / filepath
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
            
            # Upload to GCS
            result = subprocess.run([
                'gsutil', '-m', 'rsync', '-r',
                str(tmpdir_path) + '/',
                gcs_path
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"Failed to upload evolved files: {result.stderr}")
    
    def _execute_docker_job(self, docker_image: str, run_command: str,
                           gcs_data_path: str, gcs_evolved_path: str,
                           workflow_id: str, t0: float) -> CodeResult:
        """Execute Docker image on Cloud Run Job."""
        
        # Build environment variables
        env_vars = []
        if gcs_data_path:
            env_vars.append(f"DATA_PATH={gcs_data_path}")
        if gcs_evolved_path:
            env_vars.append(f"GCS_EVOLVED_PATH={gcs_evolved_path}")
        
        # Build gcloud command
        cmd = [
            'gcloud', 'run', 'jobs', 'execute', self.job_template,
            f'--region={self.region}',
            f'--image={docker_image}',
            f'--args={run_command}',
            '--wait',
            '--format=value(metadata.name)'
        ]
        
        # Add environment variables
        for env_var in env_vars:
            cmd.extend(['--set-env-vars', env_var])
        
        logging.info(f"Executing Docker job: {docker_image}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
            runtime_ms = int((time.time() - t0) * 1000)
            
            # Get execution name
            execution_name = result.stdout.strip()
            if not execution_name:
                return CodeResult(
                    stdout=None,
                    stderr=f"Failed to get execution name: {result.stderr}",
                    return_code=1,
                    runtime_ms=runtime_ms
                )
            
            logging.info(f"Job execution: {execution_name}")
            
            # Retrieve logs
            logs = self._get_job_logs_with_retry(execution_name)
            
            if logs:
                return CodeResult(
                    stdout=logs,
                    stderr=None,
                    return_code=0,
                    runtime_ms=runtime_ms
                )
            else:
                return CodeResult(
                    stdout="Job completed (no logs)",
                    stderr=None,
                    return_code=0,
                    runtime_ms=runtime_ms
                )
        
        except subprocess.TimeoutExpired:
            runtime_ms = int((time.time() - t0) * 1000)
            return CodeResult(
                stdout=None,
                stderr="Job execution timed out after 30 minutes",
                return_code=-9,
                runtime_ms=runtime_ms
            )
        
        except Exception as e:
            runtime_ms = int((time.time() - t0) * 1000)
            return CodeResult(
                stdout=None,
                stderr=f"Job execution error: {e}",
                return_code=1,
                runtime_ms=runtime_ms
            )
    
    # === Distributed Execution ===
    
    async def execute_batch_distributed(self, code_versions: List[CodeVersion],
                                       manifest: Optional[Dict] = None) -> List[CodeResult]:
        """Execute multiple code versions in parallel using Docker.
        
        Args:
            code_versions: List of CodeVersion objects
            manifest: Project manifest
            
        Returns:
            List of CodeResult objects in same order
        """
        if not manifest:
            raise ValueError("Manifest required for distributed execution")
        
        workflow_id = manifest['workflow_id']
        run_command = manifest['run_command']
        gcs_data_path = manifest.get('gcs_data_path', '')
        
        if not self._docker_image:
            self._docker_image = f"{self.artifact_registry}/workflow-{workflow_id}:latest"
        
        logging.info(f"Starting distributed execution: {len(code_versions)} jobs")
        
        # Upload all evolved files in parallel
        upload_tasks = []
        job_info = []  # (code_version_id, gcs_evolved_path)
        
        for cv in code_versions:
            execution_id = f"exec_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            gcs_evolved_path = f"gs://{self.bucket}/workflows/{workflow_id}/evolved/{execution_id}/"
            job_info.append((cv.code_version_id, gcs_evolved_path))
            
            task = asyncio.create_task(
                asyncio.to_thread(self._upload_evolved_files, cv.code, gcs_evolved_path)
            )
            upload_tasks.append(task)
        
        await asyncio.gather(*upload_tasks)
        logging.info("✓ All evolved files uploaded")
        
        # Submit all jobs
        submit_tasks = []
        for cv_id, gcs_evolved_path in job_info:
            task = asyncio.create_task(
                self._submit_docker_job(self._docker_image, run_command, 
                                       gcs_data_path, gcs_evolved_path)
            )
            submit_tasks.append(task)
        
        execution_names = await asyncio.gather(*submit_tasks)
        logging.info(f"✓ All {len(execution_names)} jobs submitted")
        
        # Poll for completion
        results_map = {}
        for (cv_id, _), exec_name in zip(job_info, execution_names):
            results_map[cv_id] = exec_name
        
        # Wait for all jobs to complete
        await self._wait_for_jobs(execution_names)
        
        # Retrieve all logs
        final_results = []
        for cv in code_versions:
            exec_name = results_map[cv.code_version_id]
            logs = await asyncio.to_thread(self._get_job_logs_with_retry, exec_name)
            
            final_results.append(CodeResult(
                stdout=logs if logs else "Job completed (no logs)",
                stderr=None,
                return_code=0,
                runtime_ms=0
            ))
        
        return final_results
    
    async def _submit_docker_job(self, docker_image: str, run_command: str,
                                 gcs_data_path: str, gcs_evolved_path: str) -> str:
        """Submit a Docker job asynchronously."""
        env_vars = []
        if gcs_data_path:
            env_vars.append(f"DATA_PATH={gcs_data_path}")
        if gcs_evolved_path:
            env_vars.append(f"GCS_EVOLVED_PATH={gcs_evolved_path}")
        
        cmd = [
            'gcloud', 'run', 'jobs', 'execute', self.job_template,
            f'--region={self.region}',
            f'--image={docker_image}',
            f'--args={run_command}',
            '--format=value(metadata.name)'
        ]
        
        for env_var in env_vars:
            cmd.extend(['--set-env-vars', env_var])
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        )
        
        return result.stdout.strip()
    
    async def _wait_for_jobs(self, execution_names: List[str]):
        """Wait for all jobs to complete."""
        completed = set()
        
        while len(completed) < len(execution_names):
            for exec_name in execution_names:
                if exec_name in completed:
                    continue
                
                status = await self._check_job_status(exec_name)
                if status in ['Completed', 'Failed']:
                    completed.add(exec_name)
                    logging.info(f"Job {exec_name}: {status}")
            
            if len(completed) < len(execution_names):
                await asyncio.sleep(self.polling_interval)
    
    async def _check_job_status(self, execution_name: str) -> str:
        """Check job status asynchronously."""
        cmd = [
            'gcloud', 'run', 'jobs', 'executions', 'describe', execution_name,
            f'--region={self.region}',
            '--format=value(status.conditions[0].type)'
        ]
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        return "Unknown"
    
    # === Log Retrieval ===
    
    def _get_job_logs_with_retry(self, execution_name: str) -> Optional[str]:
        """Retrieve logs with retry."""
        for attempt in range(3):
            logs = self._get_job_logs(execution_name)
            if logs:
                return logs
            if attempt < 2:
                time.sleep(2 ** attempt)
        return None
    
    def _get_job_logs(self, execution_name: str) -> Optional[str]:
        """Retrieve logs from Cloud Logging."""
        try:
            log_filter = f'resource.type="cloud_run_job" labels."run.googleapis.com/execution_name"="{execution_name}"'
            
            cmd = [
                'gcloud', 'logging', 'read', log_filter,
                '--limit=100',
                '--format=value(textPayload)',
                '--freshness=30m'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            
            return None
        except Exception as e:
            logging.error(f"Error retrieving logs: {e}")
            return None
    
    # === Cleanup ===
    
    def cleanup_workflow_storage(self, workflow_id: str):
        """Clean up GCS storage for a workflow."""
        gcs_workflow_path = f"gs://{self.bucket}/workflows/{workflow_id}/"
        
        logging.info(f"Cleaning up workflow storage: {gcs_workflow_path}")
        subprocess.run(['gsutil', '-m', 'rm', '-r', gcs_workflow_path],
                      capture_output=True)


