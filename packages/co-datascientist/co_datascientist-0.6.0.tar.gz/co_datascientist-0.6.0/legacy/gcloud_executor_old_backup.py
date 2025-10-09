"""Google Cloud Run Jobs executor with GCS caching for multi-file support."""

import asyncio
import base64
import logging
import platform
import subprocess
import time
import uuid
import shlex
import tempfile
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

from .base_executor import BaseExecutor
from ..models import CodeResult, CodeVersion


class GCloudExecutor(BaseExecutor):
    """Executor for running Python code on Google Cloud Run Jobs with GCS caching."""
    
    @property
    def platform_name(self) -> str:
        return "gcloud"
    
    def __init__(self, python_path: str = "python", config: Dict[str, Any] = None):
        super().__init__(python_path, config)
        
        # Extract gcloud configuration with sensible defaults
        gcloud_config = config.get('gcloud', {}) if config else {}
        
        self.job_template = gcloud_config.get('job_template', 'default-job')
        self.region = gcloud_config.get('region', 'europe-west3')
        self.bucket = gcloud_config.get('bucket', 'co-datascientist-runs')
        self.base_args = gcloud_config.get('base_args', [])
        self.timeout = gcloud_config.get('timeout', '30m')
        self.code_injection_method = gcloud_config.get('code_injection_method', 'args')
        
        # Distributed execution configuration (auto-enabled for parallel execution)
        self.polling_interval = gcloud_config.get('polling_interval', 5)
        self.max_concurrent_jobs = gcloud_config.get('max_concurrent_jobs', 100)
        
        # Platform-specific configuration
        self.is_windows = platform.system().lower() == 'windows'
        self.gcloud_path = self._get_gcloud_path()
    
    def _get_gcloud_path(self) -> str:
        """Get the gcloud path, handling Windows PowerShell if needed."""
        if self.is_windows:
            try:
                # Use PowerShell to get gcloud path on Windows
                result = subprocess.run(
                    ["PowerShell", "-Command", "(Get-command gcloud).source"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    return result.stdout.strip()
                else:
                    logging.warning(f"Failed to get gcloud path via PowerShell: {result.stderr}")
                    return "gcloud"  # Fallback to default
            except Exception as e:
                logging.warning(f"Error getting gcloud path on Windows: {e}")
                return "gcloud"  # Fallback to default
        else:
            return "gcloud"  # Default for Unix-like systems
    
    def _build_gcloud_command(self, base_args: List[str]) -> List[str]:
        """Build gcloud command with platform-specific handling."""
        if self.is_windows and self.gcloud_path != "gcloud":
            return ["powershell", "-File", self.gcloud_path] + base_args
        else:
            return ["gcloud"] + base_args
    
    # === GCS Caching Methods for Multi-File Support ===
    
    def upload_workflow_data(self, local_data_path: Optional[Path], workflow_id: str) -> str:
        """Upload data directory to GCS once per workflow.
        
        Args:
            local_data_path: Local path to data directory (or None if copying from GCS)
            workflow_id: Unique workflow identifier
            
        Returns:
            GCS path where data is stored
        """
        gcs_data_path = f"gs://{self.bucket}/workflows/{workflow_id}/data/"
        gcloud_config = self.config.get('gcloud', {})
        
        # Check if data already in GCS
        if gcloud_config.get('data_gcs_path'):
            source_path = gcloud_config['data_gcs_path']
            logging.info(f"Copying data from existing GCS path: {source_path}")
            
            result = subprocess.run([
                'gsutil', '-m', 'rsync', '-r',
                source_path,
                gcs_data_path
            ], capture_output=True, text=True)
        else:
            # Upload from local
            logging.info(f"Uploading data from {local_data_path} to {gcs_data_path}")
            result = subprocess.run([
                'gsutil', '-m', 'rsync', '-r',
                '-x', '.*__pycache__.*|.*\\.DS_Store.*',
                str(local_data_path),
                gcs_data_path
            ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to upload data: {result.stderr}")
        
        # Calculate size
        size_result = subprocess.run([
            'gsutil', 'du', '-s', gcs_data_path
        ], capture_output=True, text=True)
        
        if size_result.returncode == 0:
            size_bytes = int(size_result.stdout.split()[0])
            size_mb = size_bytes / (1024 * 1024)
            logging.info(f"Data uploaded successfully ({size_mb:.1f} MB)")
        else:
            logging.info("Data uploaded successfully")
        
        return gcs_data_path
    
    def upload_baseline_repo(self, base_path: Path, workflow_id: str) -> Dict[str, Any]:
        """Upload full baseline repo to GCS once per workflow.
        
        Args:
            base_path: Local path to project root
            workflow_id: Unique workflow identifier
            
        Returns:
            Dict with dependency info: {'needs_deps': bool, 'dep_type': str}
        """
        gcs_baseline_path = f"gs://{self.bucket}/workflows/{workflow_id}/baseline/"
        
        logging.info(f"Uploading baseline repo from {base_path} to {gcs_baseline_path}")
        
        # Upload repo, excluding common patterns and checkpoint directories
        result = subprocess.run([
            'gsutil', '-m', 'rsync', '-r',
            '-x', r'.*__pycache__.*|.*\.git.*|.*\.venv.*|.*venv.*|.*\.env$|.*\.pyc$|.*co_datascientist_checkpoints.*|.*current_runs.*|.*\.DS_Store.*',
            str(base_path),
            gcs_baseline_path
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to upload baseline: {result.stderr}")
        
        logging.info("Baseline repo uploaded successfully")
        
        # Check for requirements/conda
        requirements_file = base_path / 'requirements.txt'
        conda_file = base_path / 'environment.yml'
        
        if requirements_file.exists():
            logging.info("Found requirements.txt - will install dependencies on first run")
            return {'needs_deps': True, 'dep_type': 'pip'}
        elif conda_file.exists():
            logging.info("Found environment.yml - will install conda dependencies on first run")
            return {'needs_deps': True, 'dep_type': 'conda'}
        else:
            logging.info("No requirements file found - assuming no dependencies")
            return {'needs_deps': False}
    
    def _upload_evolved_files(self, evolved_files: Dict[str, str], gcs_path: str):
        """Upload evolved files to GCS.
        
        Args:
            evolved_files: Dict mapping filepath -> content
            gcs_path: GCS destination path
        """
        # Create temp dir with evolved files
        with tempfile.TemporaryDirectory() as temp_dir:
            for filepath, content in evolved_files.items():
                full_path = Path(temp_dir) / filepath
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
            
            # Upload to GCS
            result = subprocess.run([
                'gsutil', '-m', 'cp', '-r',
                f'{temp_dir}/*',
                gcs_path
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"Failed to upload evolved files: {result.stderr}")
    
    async def _upload_batch_evolved_files(
        self, 
        code_versions: List[CodeVersion], 
        workflow_id: str
    ) -> List[str]:
        """Upload all evolved file sets to GCS in parallel.
        
        Args:
            code_versions: List of CodeVersion objects
            workflow_id: Workflow identifier
            
        Returns:
            List of GCS paths for each job
        """
        async def upload_one(cv, idx):
            job_id = f"job_{idx}_{cv.code_version_id[:8]}"
            gcs_path = f"gs://{self.bucket}/workflows/{workflow_id}/jobs/{job_id}/"
            
            # Create temp dir with evolved files
            with tempfile.TemporaryDirectory() as temp_dir:
                for filepath, content in cv.code.items():
                    full_path = Path(temp_dir) / filepath
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    full_path.write_text(content)
                
                # Upload to GCS
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    lambda: subprocess.run([
                        'gsutil', '-m', 'cp', '-r',
                        f'{temp_dir}/*',
                        gcs_path
                    ], capture_output=True, text=True, check=True)
                )
            
            return gcs_path
        
        # Upload all in parallel
        tasks = [upload_one(cv, i) for i, cv in enumerate(code_versions)]
        return await asyncio.gather(*tasks)
    
    def cleanup_workflow_storage(self, workflow_id: str):
        """Clean up all GCS storage for a workflow.
        
        Args:
            workflow_id: Workflow identifier
        """
        gcs_workflow_path = f"gs://{self.bucket}/workflows/{workflow_id}/"
        
        logging.info(f"Cleaning up GCS storage: {gcs_workflow_path}")
        
        result = subprocess.run([
            'gsutil', '-m', 'rm', '-r', gcs_workflow_path
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            logging.warning(f"Failed to cleanup GCS storage: {result.stderr}")
        else:
            logging.info("GCS storage cleaned up successfully")
    
    def execute(self, code: str | Dict[str, str], manifest: Optional[Dict] = None) -> CodeResult:
        """Execute Python code on Google Cloud Run Jobs.
        
        Supports two modes:
        1. Legacy single-file: code is str, executed directly
        2. Multi-file with GCS: code is Dict, uses GCS caching
        
        Args:
            code: Either Python code string (legacy) or Dict[str, str] (multi-file)
            manifest: Project manifest with GCS paths and run command (for multi-file)
            
        Returns:
            CodeResult containing stdout, stderr, return_code, and runtime_ms
        """
        # Detect mode
        if isinstance(code, dict) and manifest:
            # Multi-file mode with GCS caching
            return self._execute_multifile_gcs(code, manifest)
        else:
            # Legacy single-file mode
            return self._execute_legacy_single_file(code)
    
    def _execute_legacy_single_file(self, code: str) -> CodeResult:
        """Execute single-file code using legacy base64 injection method."""
        logging.info(f"GCloud Job Template: {self.job_template}")
        logging.info(f"GCloud Region: {self.region}")
        logging.info(f"GCloud Timeout: {self.timeout}")
        logging.info(f"Code injection method: {self.code_injection_method}")
        
        t0 = time.time()
        
        # Create unique execution identifier
        execution_id = f"{int(t0)}_{uuid.uuid4().hex[:8]}"
        
        # Encode code for safe transmission via command args
        code_b64 = base64.b64encode(code.encode('utf-8')).decode('ascii')
        
        logging.info(f"Injecting code via args (length: {len(code)} chars)")

        # Build args with Windows-specific escaping
        if self.is_windows:
            # Windows requires additional escaping and quotes
            args_param = f'--args=python,-c,\'import sys; import base64; exec(base64.b64decode(\\"{code_b64}\\").decode(\\"utf-8\\"))\''
        else:
            # Unix/Linux standard escaping
            args_param = f'--args=-c,import sys; import base64; exec(base64.b64decode("{code_b64}").decode("utf-8"))'

        # Execute GCloud job synchronously using platform-specific command
        base_cmd = [
            'run', 'jobs', 'execute', self.job_template,
            f'--region={self.region}',
            '--wait',  # Wait for job completion
            '--format=value(metadata.name)',  # Get the execution name
            args_param
        ]
        cmd = self._build_gcloud_command(base_cmd)

        logging.info(f"Executing gcloud command: {' '.join(cmd[:6])}... [code injection args hidden]")
        
        try:
            # Execute job and wait for completion
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout for job execution
            )

            runtime_ms = int((time.time() - t0) * 1000)

            if result.returncode != 0:
                # GCloud command failed - extract just the essential error info
                stderr_lines = result.stderr.strip().split('\n') if result.stderr else []
                # Look for the actual error message (usually contains "ERROR:")
                error_line = None
                for line in stderr_lines:
                    if "ERROR:" in line and "gcloud.run.jobs.execute" in line:
                        error_line = line.strip()
                        break
                
                if error_line:
                    error_msg = f"GCloud job execution failed: {error_line}"
                else:
                    error_msg = f"GCloud job execution failed (return code {result.returncode})"
                
                logging.error(f"GCloud execution failed with return code {result.returncode}")
                return CodeResult(
                    stdout=None, 
                    stderr=error_msg, 
                    return_code=result.returncode, 
                    runtime_ms=runtime_ms
                )

            # Extract execution name
            execution_name = result.stdout.strip()
            logging.info(f"GCloud job execution completed: {execution_name}")

            # Retrieve logs with retry logic for timing issues
            logs = self._get_job_logs_with_retry(execution_name, execution_id)

            if logs:
                logging.info(f"Successfully retrieved job logs: {logs[:100]}...")  # Log first 100 chars
                return CodeResult(
                    stdout=logs,
                    stderr=None,
                    return_code=0,
                    runtime_ms=runtime_ms
                )
            else:
                logging.warning("No logs retrieved from job execution after retries")
                return CodeResult(
                    stdout="Job completed successfully (no logs available)",
                    stderr=None,
                    return_code=0,
                    runtime_ms=runtime_ms
                )

        except subprocess.TimeoutExpired:
            # Handle timeout gracefully
            runtime_ms = int((time.time() - t0) * 1000)
            error_msg = f"GCloud job execution timed out after 30 minutes"
            logging.info(error_msg)
            return CodeResult(
                stdout=None, 
                stderr=error_msg, 
                return_code=-9, 
                runtime_ms=runtime_ms
            )
        
        except Exception as e:
            # Handle any other errors
            runtime_ms = int((time.time() - t0) * 1000)
            logging.error(f"GCloud job execution error: {e}")
            return CodeResult(
                stdout=None, 
                stderr=f"GCloud execution error: {e}", 
                return_code=1, 
                runtime_ms=runtime_ms
            )
    
    def _execute_multifile_gcs(self, evolved_files: Dict[str, str], manifest: Dict) -> CodeResult:
        """Execute multi-file code using GCS caching strategy.
        
        Args:
            evolved_files: Dict mapping filepath -> content
            manifest: Project manifest with workflow_id, gcs paths, run_command, etc.
            
        Returns:
            CodeResult containing stdout, stderr, return_code, and runtime_ms
        """
        t0 = time.time()
        
        workflow_id = manifest['workflow_id']
        gcs_baseline_path = f"gs://{self.bucket}/workflows/{workflow_id}/baseline/"
        gcs_venv_path = f"gs://{self.bucket}/workflows/{workflow_id}/venv/"
        gcs_data_path = manifest.get('gcs_data_path', '')
        
        # Upload evolved files if not baseline
        is_baseline = manifest.get('is_baseline', False)
        if not is_baseline:
            execution_id = f"job_{int(t0)}_{uuid.uuid4().hex[:8]}"
            gcs_evolved_path = f"gs://{self.bucket}/workflows/{workflow_id}/jobs/{execution_id}/"
            self._upload_evolved_files(evolved_files, gcs_evolved_path)
        else:
            gcs_evolved_path = ""
        
        # Generate execution script
        script = self._generate_execution_script(
            gcs_baseline_path=gcs_baseline_path,
            gcs_venv_path=gcs_venv_path,
            gcs_data_path=gcs_data_path,
            gcs_evolved_path=gcs_evolved_path,
            run_command=manifest['run_command'],
            is_baseline=is_baseline,
            needs_deps=manifest.get('needs_deps', False),
            dep_type=manifest.get('dep_type', 'pip'),
            data_mount_path=manifest.get('data_mount_path', '/tmp/data')
        )
        
        # Execute via base64 injection
        return self._execute_inline_script(script, t0)
    
    def _generate_execution_script(
        self,
        gcs_baseline_path: str,
        gcs_venv_path: str,
        gcs_data_path: str,
        gcs_evolved_path: str,
        run_command: str,
        is_baseline: bool,
        needs_deps: bool,
        dep_type: str,
        data_mount_path: str
    ) -> str:
        """Generate Python script for GCS-based multi-file execution."""
        
        # Parse bucket and path from GCS URLs
        bucket_name = self.bucket
        
        script = f"""
import os
import sys
import subprocess
from pathlib import Path

print("=" * 60, file=sys.stderr)
print("🚀 Co-DataScientist Cloud Execution", file=sys.stderr)
print("=" * 60, file=sys.stderr)

# Install google-cloud-storage if not available
try:
    from google.cloud import storage
except ImportError:
    print("📦 Installing google-cloud-storage...", file=sys.stderr)
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'google-cloud-storage'], check=True)
    from google.cloud import storage

def download_gcs_folder(bucket_name, prefix, local_dir):
    \"\"\"Download all files from a GCS prefix to local directory.\"\"\"
    try:
        print(f"Creating GCS client...", file=sys.stderr)
        client = storage.Client()
        print(f"Getting bucket: {{bucket_name}}", file=sys.stderr)
        bucket = client.bucket(bucket_name)
        
        print(f"Listing blobs with prefix: {{prefix}}", file=sys.stderr)
        blobs = list(bucket.list_blobs(prefix=prefix))
        print(f"Found {{len(blobs)}} files to download", file=sys.stderr)
        
        for i, blob in enumerate(blobs):
            if blob.name.endswith('/'):
                continue
            
            # Remove prefix to get relative path
            rel_path = blob.name[len(prefix):].lstrip('/')
            if not rel_path:
                continue
                
            local_file = Path(local_dir) / rel_path
            local_file.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"Downloading {{i+1}}/{{len(blobs)}}: {{rel_path}}", file=sys.stderr)
            blob.download_to_filename(str(local_file))
        
        print(f"Successfully downloaded {{len(blobs)}} files", file=sys.stderr)
    except Exception as e:
        print(f"ERROR downloading from GCS: {{e}}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

def run_cmd(cmd, check=True):
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    if check and result.returncode != 0:
        print(f"Command failed: {{cmd}}", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)
    return result

"""
        
        # Download data if specified
        if gcs_data_path:
            # Extract path from gs://bucket/path
            data_prefix = gcs_data_path.replace(f'gs://{bucket_name}/', '').rstrip('/')
            script += f"""
print("📊 Downloading data...", file=sys.stderr)
os.makedirs('{data_mount_path}', exist_ok=True)
download_gcs_folder('{bucket_name}', '{data_prefix}/', '{data_mount_path}')
print("   ✓ Data ready at {data_mount_path}", file=sys.stderr)

"""
        
        # Download baseline repo
        baseline_prefix = gcs_baseline_path.replace(f'gs://{bucket_name}/', '').rstrip('/')
        script += f"""
print("📥 Downloading baseline repo...", file=sys.stderr)
download_gcs_folder('{bucket_name}', '{baseline_prefix}/', '/tmp/project')
"""
        
        # Download evolved files if not baseline
        if not is_baseline and gcs_evolved_path:
            evolved_prefix = gcs_evolved_path.replace(f'gs://{bucket_name}/', '').rstrip('/')
            script += f"""
print("📝 Downloading evolved files...", file=sys.stderr)
download_gcs_folder('{bucket_name}', '{evolved_prefix}/', '/tmp/project')
"""
        
        script += """
os.chdir('/tmp/project')
"""
        
        # Handle dependencies
        if needs_deps:
            if is_baseline:
                # Install dependencies (first run)
                script += """
print("📦 Installing dependencies (first run)...", file=sys.stderr)
"""
                if dep_type == 'pip':
                    venv_prefix = gcs_venv_path.replace(f'gs://{bucket_name}/', '').rstrip('/')
                    script += f"""
run_cmd('python -m venv /tmp/venv')
if os.path.exists('requirements.txt'):
    run_cmd('/tmp/venv/bin/pip install -r requirements.txt')
print("💾 Caching dependencies to GCS...", file=sys.stderr)

# Upload venv to GCS using Python
client = storage.Client()
bucket = client.bucket('{bucket_name}')
import os
for root, dirs, files in os.walk('/tmp/venv'):
    for file in files:
        local_path = os.path.join(root, file)
        rel_path = os.path.relpath(local_path, '/tmp/venv')
        blob_name = f'{venv_prefix}/{{rel_path}}'
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(local_path)

activate_cmd = 'source /tmp/venv/bin/activate'
"""
                elif dep_type == 'conda':
                    venv_prefix = gcs_venv_path.replace(f'gs://{bucket_name}/', '').rstrip('/')
                    script += f"""
if os.path.exists('environment.yml'):
    run_cmd('conda env create -f environment.yml -p /tmp/conda_env')
else:
    run_cmd('conda create -p /tmp/conda_env python=3.11 -y')
print("💾 Caching conda environment to GCS...", file=sys.stderr)

# Upload conda env to GCS using Python
client = storage.Client()
bucket = client.bucket('{bucket_name}')
for root, dirs, files in os.walk('/tmp/conda_env'):
    for file in files:
        local_path = os.path.join(root, file)
        rel_path = os.path.relpath(local_path, '/tmp/conda_env')
        blob_name = f'{venv_prefix}/{{rel_path}}'
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(local_path)

activate_cmd = 'source activate /tmp/conda_env'
"""
            else:
                # Download cached dependencies
                venv_prefix = gcs_venv_path.replace(f'gs://{bucket_name}/', '').rstrip('/')
                script += f"""
print("📥 Loading cached dependencies...", file=sys.stderr)
download_gcs_folder('{bucket_name}', '{venv_prefix}/', '/tmp/venv')
"""
                if dep_type == 'pip':
                    script += """
activate_cmd = 'source /tmp/venv/bin/activate'
"""
                else:
                    script += """
activate_cmd = 'source activate /tmp/venv'
"""
        else:
            script += """
activate_cmd = ''
"""
        
        # Set environment variables for data path
        if gcs_data_path:
            script += f"""
# Set environment variable for data path
os.environ['DATA_PATH'] = '{data_mount_path}'
os.environ['CO_DATASCIENTIST_DATA_PATH'] = '{data_mount_path}'

"""
        
        # Run the command
        script += f"""
print("=" * 60, file=sys.stderr)
print("🚀 Running: {run_command}", file=sys.stderr)
"""
        if gcs_data_path:
            script += f"""
print("   DATA_PATH={data_mount_path}", file=sys.stderr)
"""
        script += """
print("=" * 60, file=sys.stderr)

"""
        
        script += f"""
full_cmd = f"{{activate_cmd}} && {run_command}" if activate_cmd else "{run_command}"

result = subprocess.run(
    full_cmd,
    capture_output=True,
    text=True,
    shell=True,
    executable='/bin/bash',
    env=os.environ
)

# Output results
if result.stdout:
    print(result.stdout, end='')
if result.stderr:
    print(result.stderr, end='', file=sys.stderr)

sys.exit(result.returncode)
"""
        
        return script
    
    def _execute_inline_script(self, script: str, t0: float = None) -> CodeResult:
        """Execute Python script via base64 injection.
        
        Args:
            script: Python script to execute
            t0: Start time (for runtime calculation)
            
        Returns:
            CodeResult
        """
        if t0 is None:
            t0 = time.time()
        
        # Create unique execution identifier
        execution_id = f"{int(t0)}_{uuid.uuid4().hex[:8]}"
        
        # Encode script for safe transmission
        code_b64 = base64.b64encode(script.encode('utf-8')).decode('ascii')
        
        # Build args with Windows-specific escaping
        if self.is_windows:
            args_param = f'--args=python,-c,\'import sys; import base64; exec(base64.b64decode(\\"{code_b64}\\").decode(\\"utf-8\\"))\''
        else:
            args_param = f'--args=-c,import sys; import base64; exec(base64.b64decode("{code_b64}").decode("utf-8"))'
        
        # Execute GCloud job synchronously
        base_cmd = [
            'run', 'jobs', 'execute', self.job_template,
            f'--region={self.region}',
            '--wait',
            '--format=value(metadata.name)',
            args_param
        ]
        cmd = self._build_gcloud_command(base_cmd)
        
        logging.info(f"Executing gcloud job: {self.job_template} in {self.region}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )
            
            runtime_ms = int((time.time() - t0) * 1000)
            
            # Extract execution name from stdout or stderr (gcloud sometimes returns it in stderr)
            execution_name = result.stdout.strip()
            if not execution_name and result.stderr:
                # Try to extract execution name from stderr (format: "job-name-xxxxx")
                for line in result.stderr.split('\n'):
                    if self.job_template in line and '-' in line:
                        # Look for pattern like "test-job-clean-xxxxx"
                        parts = line.split()
                        for part in parts:
                            if self.job_template in part and len(part) > len(self.job_template):
                                execution_name = part.strip('.,;:')
                                break
                    if execution_name:
                        break
            
            if not execution_name:
                error_msg = f"Failed to get execution name from gcloud command"
                if result.stderr:
                    error_msg += f": {result.stderr[:500]}"
                logging.error(error_msg)
                return CodeResult(
                    stdout=None,
                    stderr=error_msg,
                    return_code=1,
                    runtime_ms=runtime_ms
                )
            
            logging.info(f"GCloud job execution: {execution_name}")
            
            # Check actual job status (gcloud --wait sometimes returns 1 even when job succeeds)
            # Handle both sync and async contexts
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context, create a task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    actual_status = pool.submit(
                        lambda: self._check_job_status_sync(execution_name)
                    ).result()
            except RuntimeError:
                # No running loop, use asyncio.run
                actual_status = asyncio.run(self._check_job_status(execution_name))
            
            # Retrieve logs
            logs = self._get_job_logs_with_retry(execution_name, execution_id)
            
            if actual_status == "success":
                if logs:
                    return CodeResult(
                        stdout=logs,
                        stderr=None,
                        return_code=0,
                        runtime_ms=runtime_ms
                    )
                else:
                    return CodeResult(
                        stdout="Job completed successfully (no logs available)",
                        stderr=None,
                        return_code=0,
                        runtime_ms=runtime_ms
                    )
            elif actual_status == "unknown":
                # Can't determine status, return logs if available or use gcloud exit code
                if logs:
                    # If we got logs, assume success (logs usually only available on successful completion)
                    return CodeResult(
                        stdout=logs,
                        stderr=None,
                        return_code=0,
                        runtime_ms=runtime_ms
                    )
                else:
                    # No logs and unknown status - report as error
                    error_msg = f"Could not determine job status and no logs available"
                    return CodeResult(
                        stdout=None,
                        stderr=error_msg,
                        return_code=1,
                        runtime_ms=runtime_ms
                    )
            else:
                # Job failed
                error_msg = f"GCloud job failed with status: {actual_status}"
                if logs:
                    error_msg = logs  # Use logs as error message if available
                return CodeResult(
                    stdout=None,
                    stderr=error_msg,
                    return_code=1,
                    runtime_ms=runtime_ms
                )
        
        except subprocess.TimeoutExpired:
            runtime_ms = int((time.time() - t0) * 1000)
            return CodeResult(
                stdout=None,
                stderr="GCloud job execution timed out after 30 minutes",
                return_code=-9,
                runtime_ms=runtime_ms
            )
        
        except Exception as e:
            runtime_ms = int((time.time() - t0) * 1000)
            logging.error(f"GCloud job execution error: {e}")
            return CodeResult(
                stdout=None,
                stderr=f"GCloud execution error: {e}",
                return_code=1,
                runtime_ms=runtime_ms
            )
    
    def _check_job_status_sync(self, execution_name: str) -> str:
        """Check the actual status of a job execution (synchronous version).
        
        Args:
            execution_name: Name of the execution
            
        Returns:
            "success" if job completed successfully, "failed" if it failed, "unknown" if status can't be determined
        """
        try:
            # Query the execution status
            base_cmd = [
                'run', 'jobs', 'executions', 'describe', execution_name,
                f'--region={self.region}',
                '--format=value(status.conditions[0].type)'
            ]
            cmd = self._build_gcloud_command(base_cmd)
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                status = result.stdout.strip()
                # Cloud Run Job status types: "Completed" = success
                if status == "Completed":
                    return "success"
                else:
                    return "failed"
            else:
                logging.warning(f"Failed to check job status: {result.stderr}")
                return "unknown"
                
        except Exception as e:
            logging.warning(f"Error checking job status: {e}")
            return "unknown"
    
    async def _check_job_status(self, execution_name: str) -> str:
        """Check the actual status of a job execution (async for distributed execution).
        
        Args:
            execution_name: Name of the execution
            
        Returns:
            "success" if job completed successfully, "failed" if it failed, "unknown" if status can't be determined
        """
        try:
            # Query the execution status
            base_cmd = [
                'run', 'jobs', 'executions', 'describe', execution_name,
                f'--region={self.region}',
                '--format=value(status.conditions[0].type)'
            ]
            cmd = self._build_gcloud_command(base_cmd)
            
            # Run in executor to not block event loop
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            )
            
            if result.returncode == 0:
                status = result.stdout.strip()
                # Cloud Run Job status types: "Completed" = success
                if status == "Completed":
                    return "success"
                else:
                    return "failed"
            else:
                logging.warning(f"Failed to check job status: {result.stderr}")
                return "unknown"
                
        except Exception as e:
            logging.warning(f"Error checking job status: {e}")
            return "unknown"
    
    def _get_job_logs_with_retry(self, execution_name: str, execution_id: str) -> Optional[str]:
        """Retrieve logs with retry logic to handle timing issues.
        
        Args:
            execution_name: Name of the specific execution
            execution_id: Unique execution identifier for log filtering
            
        Returns:
            Job logs as string, or None if logs couldn't be retrieved after retries
        """
        max_retries = 3
        retry_delays = [2, 5, 10]  # seconds to wait between retries
        
        for attempt in range(max_retries):
            logs = self._get_job_logs(execution_name, execution_id)
            if logs:
                return logs
            
            if attempt < max_retries - 1:  # Don't sleep after last attempt
                delay = retry_delays[attempt]
                logging.info(f"No logs found on attempt {attempt + 1}/{max_retries}, retrying in {delay}s...")
                time.sleep(delay)
        
        logging.warning(f"Failed to retrieve logs after {max_retries} attempts")
        return None
    
    def _get_job_logs(self, execution_name: str, execution_id: str) -> Optional[str]:
        """Retrieve logs from a completed GCloud Run Job execution.

        Args:
            execution_name: Name of the specific execution (e.g., 'test-job-clean-abc123')
            execution_id: Unique execution identifier for log filtering

        Returns:
            Job logs as string, or None if logs couldn't be retrieved
        """
        try:
            logging.info(f"Retrieving logs for execution: {execution_name}")

            # Try multiple log retrieval strategies for better reliability
            logs = self._try_multiple_log_strategies(execution_name)
            if logs:
                return logs
            
            logging.warning("All log retrieval strategies failed")
            return None
            
        except Exception as e:
            logging.error(f"Error retrieving GCloud job logs: {e}")
            return None

    def _try_multiple_log_strategies(self, execution_name: str) -> Optional[str]:
        """Try multiple strategies to retrieve logs, as different approaches work better in different scenarios."""
        
        # Strategy 1: Standard approach with stdout filter
        logs = self._get_logs_with_filter(execution_name, "stdout")
        if logs:
            logging.info("Retrieved logs using stdout filter strategy")
            return logs
        
        # Strategy 2: Try stderr filter
        logs = self._get_logs_with_filter(execution_name, "stderr")
        if logs:
            logging.info("Retrieved logs using stderr filter strategy")
            return logs
        
        # Strategy 3: Try broader filter without log name restriction
        logs = self._get_logs_broad_filter(execution_name)
        if logs:
            logging.info("Retrieved logs using broad filter strategy")
            return logs
        
        # Strategy 4: Try with longer freshness window
        logs = self._get_logs_with_filter(execution_name, "stdout", freshness="1h")
        if logs:
            logging.info("Retrieved logs using extended freshness strategy")
            return logs
        
        return None
    
    def _get_logs_with_filter(self, execution_name: str, log_type: str = "stdout", freshness: str = "15m") -> Optional[str]:
        """Get logs with specific filter."""
        try:
            # Build log filter with Windows-specific escaping
            if self.is_windows:
                log_filter = f'resource.type="cloud_run_job" logName=~\\"{log_type}\\" labels.\\"run.googleapis.com/execution_name\\"=\\"{execution_name}\\"'
            else:
                log_filter = f'resource.type="cloud_run_job" logName=~"{log_type}" labels."run.googleapis.com/execution_name"="{execution_name}"'
            
            base_cmd = [
                'logging', 'read',
                log_filter,
                '--limit=100',
                '--format=value(textPayload)',
                f'--freshness={freshness}'
            ]
            cmd = self._build_gcloud_command(base_cmd)

            logging.info(f"Executing log command: {' '.join(cmd[:4])}...")
            logs_result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if logs_result.returncode == 0 and logs_result.stdout.strip():
                return logs_result.stdout.strip()
            else:
                return None
                
        except Exception as e:
            logging.error(f"Error in _get_logs_with_filter: {e}")
            return None
    
    def _get_logs_broad_filter(self, execution_name: str) -> Optional[str]:
        """Get logs with a broader filter that doesn't restrict log type."""
        try:
            # Broader filter - just match the execution name without log type restriction
            if self.is_windows:
                log_filter = f'resource.type="cloud_run_job" labels.\\"run.googleapis.com/execution_name\\"=\\"{execution_name}\\"'
            else:
                log_filter = f'resource.type="cloud_run_job" labels."run.googleapis.com/execution_name"="{execution_name}"'
            
            base_cmd = [
                'logging', 'read',
                log_filter,
                '--limit=100',
                '--format=value(textPayload)',
                '--freshness=30m'
            ]
            cmd = self._build_gcloud_command(base_cmd)

            logging.info(f"Executing broad log command: {' '.join(cmd[:4])}...")
            logs_result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if logs_result.returncode == 0 and logs_result.stdout.strip():
                return logs_result.stdout.strip()
            else:
                return None
                
        except Exception as e:
            logging.error(f"Error in _get_logs_broad_filter: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if gcloud CLI is available and configured."""
        try:
            cmd = self._build_gcloud_command(['version'])
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    # Distributed execution methods
    
    def supports_distributed_execution(self) -> bool:
        """Check if this executor supports distributed batch execution."""
        return self.is_available()

    async def execute_batch_distributed(self, code_versions: List[CodeVersion], manifest: Dict) -> List[CodeResult]:
        """Execute a batch of code versions using true distributed execution with GCS.
        
        This method:
        1. Uploads all evolved file sets to GCS in parallel
        2. Submits all jobs asynchronously to Google Cloud Run Jobs
        3. Each job downloads baseline + venv + its evolved files from GCS
        4. Polls for completion
        
        Args:
            code_versions: List of CodeVersion objects to execute
            manifest: Project manifest with workflow_id, gcs paths, run_command, etc.
            
        Returns:
            List of CodeResult objects in the same order as input
        """
        if not self.supports_distributed_execution():
            raise RuntimeError("Distributed execution not supported or gcloud not available")
        
        if len(code_versions) > self.max_concurrent_jobs:
            logging.warning(f"Batch size {len(code_versions)} exceeds max_concurrent_jobs {self.max_concurrent_jobs}")
        
        logging.info(f"Starting distributed execution of {len(code_versions)} jobs on Google Cloud")
        
        workflow_id = manifest['workflow_id']
        gcs_baseline_path = f"gs://{self.bucket}/workflows/{workflow_id}/baseline/"
        gcs_venv_path = f"gs://{self.bucket}/workflows/{workflow_id}/venv/"
        gcs_data_path = manifest.get('gcs_data_path', '')
        
        # Upload all evolved file sets to GCS (in parallel)
        logging.info(f"Uploading {len(code_versions)} evolved file sets to GCS...")
        job_paths = await self._upload_batch_evolved_files(code_versions, workflow_id)
        
        # Submit all jobs with their specific GCS paths
        job_submissions = []
        for cv, evolved_path in zip(code_versions, job_paths):
            try:
                execution_name = await self._submit_job_with_gcs_paths(
                    gcs_baseline_path=gcs_baseline_path,
                    gcs_venv_path=gcs_venv_path,
                    gcs_data_path=gcs_data_path,
                    gcs_evolved_path=evolved_path,
                    run_command=manifest['run_command'],
                    needs_deps=manifest.get('needs_deps', False),
                    dep_type=manifest.get('dep_type', 'pip'),
                    data_mount_path=manifest.get('data_mount_path', '/tmp/data')
                )
                start_time = time.time()
                job_submissions.append((cv.code_version_id, execution_name, start_time))
                logging.info(f"Submitted job {execution_name} for code version {cv.code_version_id[:8]}")
            except Exception as e:
                logging.error(f"Failed to submit job for code version {cv.code_version_id}: {e}")
                job_submissions.append((cv.code_version_id, None, time.time()))
        
        logging.info(f"Job submissions completed: {len(job_submissions)} jobs submitted")
        
        # Poll for results
        results = await self._poll_job_results(job_submissions)
        
        logging.info(f"Completed distributed execution of {len(results)} jobs")
        return results

    async def _submit_jobs_async(self, code_versions: List[CodeVersion]) -> List[Tuple[str, str, float]]:
        """Submit all jobs asynchronously and return job tracking information.
        
        Args:
            code_versions: List of CodeVersion objects to submit
            
        Returns:
            List of tuples: (code_version_id, execution_name, start_time)
        """
        job_submissions = []
        
        for cv in code_versions:
            try:
                execution_name = await self._submit_single_job(cv.code)
                start_time = time.time()
                job_submissions.append((cv.code_version_id, execution_name, start_time))
                logging.info(f"Submitted job {execution_name} for code version {cv.code_version_id}")
                
            except Exception as e:
                logging.error(f"Failed to submit job for code version {cv.code_version_id}: {e}")
                # Create a failed result for this job
                job_submissions.append((cv.code_version_id, None, time.time()))
        
        return job_submissions

    async def _submit_job_with_gcs_paths(
        self,
        gcs_baseline_path: str,
        gcs_venv_path: str,
        gcs_data_path: str,
        gcs_evolved_path: str,
        run_command: str,
        needs_deps: bool,
        dep_type: str,
        data_mount_path: str
    ) -> str:
        """Submit a single job asynchronously with GCS paths (without --wait flag).
        
        Args:
            gcs_baseline_path: GCS path to baseline repo
            gcs_venv_path: GCS path to venv cache
            gcs_data_path: GCS path to data
            gcs_evolved_path: GCS path to evolved files for this job
            run_command: Command to run
            needs_deps: Whether dependencies need to be loaded
            dep_type: Type of dependencies ('pip' or 'conda')
            data_mount_path: Where to mount data in VM
            
        Returns:
            execution_name: The name of the submitted execution
        """
        # Generate execution script for this job
        script = self._generate_execution_script(
            gcs_baseline_path=gcs_baseline_path,
            gcs_venv_path=gcs_venv_path,
            gcs_data_path=gcs_data_path,
            gcs_evolved_path=gcs_evolved_path,
            run_command=run_command,
            is_baseline=False,  # Never baseline in distributed mode
            needs_deps=needs_deps,
            dep_type=dep_type,
            data_mount_path=data_mount_path
        )
        
        # Encode script for safe transmission
        code_b64 = base64.b64encode(script.encode('utf-8')).decode('ascii')
        
        # Build args with Windows-specific escaping
        if self.is_windows:
            args_param = f'--args=python,-c,\'import sys; import base64; exec(base64.b64decode(\\"{code_b64}\\").decode(\\"utf-8\\"))\''
        else:
            args_param = f'--args=-c,import sys; import base64; exec(base64.b64decode("{code_b64}").decode("utf-8"))'
        
        # Submit job WITHOUT --wait flag for async execution
        base_cmd = [
            'run', 'jobs', 'execute', self.job_template,
            f'--region={self.region}',
            # Note: NO --wait flag here - this makes it asynchronous
            '--format=value(metadata.name)',
            args_param
        ]
        cmd = self._build_gcloud_command(base_cmd)
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            lambda: subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Job submission failed: {result.stderr}")
        
        execution_name = result.stdout.strip()
        return execution_name

    async def _poll_job_results(self, job_submissions: List[Tuple[str, str, float]]) -> List[CodeResult]:
        """Poll all submitted jobs until completion and collect results.
        
        Args:
            job_submissions: List of (code_version_id, execution_name, start_time) tuples
            
        Returns:
            List of CodeResult objects in the same order as job_submissions
        """
        results = {}
        failed_submissions = set()
        
        # Track jobs that failed to submit
        for cv_id, execution_name, start_time in job_submissions:
            if execution_name is None:
                results[cv_id] = CodeResult(
                    stdout=None,
                    stderr="Job submission failed",
                    return_code=1,
                    runtime_ms=0
                )
                failed_submissions.add(cv_id)
        
        # Poll remaining jobs
        pending_jobs = [(cv_id, exec_name, start_time) for cv_id, exec_name, start_time in job_submissions 
                       if cv_id not in failed_submissions]
        
        max_wait_time = 1800  # 30 minutes timeout
        start_polling_time = time.time()
        
        while pending_jobs:
            # Check for overall timeout
            if time.time() - start_polling_time > max_wait_time:
                logging.error(f"Polling timeout after {max_wait_time} seconds, marking remaining jobs as failed")
                for cv_id, execution_name, start_time in pending_jobs:
                    runtime_ms = int((time.time() - start_time) * 1000)
                    results[cv_id] = CodeResult(
                        stdout=None,
                        stderr="Job polling timeout",
                        return_code=-1,
                        runtime_ms=runtime_ms
                    )
                break
                
            completed_jobs = []
            
            logging.info(f"Polling {len(pending_jobs)} jobs...")
            
            for cv_id, execution_name, start_time in pending_jobs:
                try:
                    status = await self._check_job_status(execution_name)
                    logging.info(f"Job {execution_name}: status = {status}")
                    
                    if status in ['Ready', 'Succeeded', 'Completed']:
                        # Job completed successfully
                        logs = await self._get_job_logs_async(execution_name)
                        runtime_ms = int((time.time() - start_time) * 1000)
                        
                        # Extract KPI from logs
                        from ..kpi_extractor import extract_kpi_from_stdout
                        kpi_value = extract_kpi_from_stdout(logs)
                        
                        
                        results[cv_id] = CodeResult(
                            stdout=logs,
                            stderr=None,
                            return_code=0,
                            runtime_ms=runtime_ms,
                            kpi=kpi_value
                        )
                        completed_jobs.append((cv_id, execution_name, start_time))
                        logging.info(f"Job {execution_name} completed successfully")
                        
                    elif status in ['Failed', 'Error', 'Cancelled']:
                        # Job failed
                        runtime_ms = int((time.time() - start_time) * 1000)
                        error_logs = await self._get_job_logs_async(execution_name)
                        
                        results[cv_id] = CodeResult(
                            stdout=None,
                            stderr=error_logs or "Job execution failed",
                            return_code=1,
                            runtime_ms=runtime_ms
                        )
                        completed_jobs.append((cv_id, execution_name, start_time))
                        logging.error(f"Job {execution_name} failed with status {status}")
                        
                    elif status in ['Running', 'Executing', 'Unknown']:
                        # Job still running, continue polling
                        job_runtime = time.time() - start_time
                        if job_runtime > 1200:  # 20 minute individual job timeout
                            logging.warning(f"Job {execution_name} running for {job_runtime:.1f}s, marking as timeout")
                            results[cv_id] = CodeResult(
                                stdout=None,
                                stderr="Individual job timeout",
                                return_code=-1,
                                runtime_ms=int(job_runtime * 1000)
                            )
                            completed_jobs.append((cv_id, execution_name, start_time))
                        else:
                            logging.info(f"Job {execution_name} still running ({job_runtime:.1f}s)")
                    else:
                        logging.warning(f"Job {execution_name} has unexpected status: {status}")
                    
                except Exception as e:
                    logging.error(f"Error checking status for job {execution_name}: {e}")
                    # Continue polling this job
            
            # Remove completed jobs from pending list
            for completed_job in completed_jobs:
                pending_jobs.remove(completed_job)
            
            # Wait before next polling cycle
            if pending_jobs:
                logging.info(f"Waiting {self.polling_interval}s before next poll...")
                await asyncio.sleep(self.polling_interval)
        
        # Return results in the same order as job_submissions
        ordered_results = []
        for cv_id, _, _ in job_submissions:
            ordered_results.append(results[cv_id])
        
        return ordered_results

    async def _get_job_logs_async(self, execution_name: str) -> Optional[str]:
        """Asynchronously retrieve logs from a completed job execution.
        
        Args:
            execution_name: Name of the execution
            
        Returns:
            Job logs as string, or None if logs couldn't be retrieved
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._get_job_logs_with_retry(execution_name, "")
        )
