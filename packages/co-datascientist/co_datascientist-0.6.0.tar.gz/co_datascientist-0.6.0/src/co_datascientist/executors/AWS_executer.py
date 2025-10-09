"""AWS ECS Fargate executor."""

import asyncio
import base64
import json
import logging
import platform
import subprocess
import time
import uuid
from typing import Dict, Any, Optional, List, Tuple

from .base_executor import BaseExecutor
from ..models import CodeResult, CodeVersion


class AWSExecutor(BaseExecutor):
    """Executor for running Python code on AWS ECS Fargate."""
    
    @property
    def platform_name(self) -> str:
        return "aws"
    
    def __init__(self, python_path: str = "python", config: Dict[str, Any] = None):
        super().__init__(python_path, config)

        # Extract AWS ECS configuration with sensible defaults
        aws_config = config.get('aws', {}) if config else {}

        self.cluster = aws_config.get('cluster', 'my-cluster')
        self.task_definition = aws_config.get('task_definition', 'my-job-taskdef')
        self.launch_type = aws_config.get('launch_type', 'FARGATE')
        self.region = aws_config.get('region', 'us-east-1')

        # Network configuration
        network_config = aws_config.get('network_configuration', {})
        self.subnets = network_config.get('subnets', ['subnet-abc'])
        self.security_groups = network_config.get('security_groups', ['sg-123'])
        self.assign_public_ip = network_config.get('assign_public_ip', 'ENABLED')

        self.timeout = aws_config.get('timeout', 1800)  # seconds
        self.code_injection_method = aws_config.get('code_injection_method', 'environment')

        # Distributed execution configuration (auto-enabled for parallel execution)
        self.polling_interval = aws_config.get('polling_interval', 10)
        self.max_concurrent_jobs = aws_config.get('max_concurrent_jobs', 50)

        # Platform-specific configuration
        self.is_windows = platform.system().lower() == 'windows'
        self.aws_path = self._get_aws_path()
    
    def _get_aws_path(self) -> str:
        """Get the AWS CLI path, handling Windows PowerShell if needed."""
        if self.is_windows:
            try:
                # Use PowerShell to get aws path on Windows
                result = subprocess.run(
                    ["PowerShell", "-Command", "(Get-command aws).source"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    return result.stdout.strip()
                else:
                    logging.warning(f"Failed to get aws path via PowerShell: {result.stderr}")
                    return "aws"  # Fallback to default
            except Exception as e:
                logging.warning(f"Error getting aws path on Windows: {e}")
                return "aws"  # Fallback to default
        else:
            return "aws"  # Default for Unix-like systems
    
    def _build_aws_command(self, base_args: List[str]) -> List[str]:
        """Build aws command with platform-specific handling."""
        if self.is_windows and self.aws_path != "aws":
            return ["powershell", "-File", self.aws_path] + base_args
        else:
            return ["aws"] + base_args
    
    def execute(self, code: str) -> CodeResult:
        """Execute Python code on AWS ECS Fargate.

        Args:
            code: Python code to execute

        Returns:
            CodeResult containing stdout, stderr, return_code, and runtime_ms
        """
        logging.info(f"AWS ECS Cluster: {self.cluster}")
        logging.info(f"AWS Task Definition: {self.task_definition}")
        logging.info(f"AWS Region: {self.region}")
        logging.info(f"AWS Launch Type: {self.launch_type}")
        logging.info(f"Code injection method: {self.code_injection_method}")

        t0 = time.time()

        # Create unique execution identifier
        task_id = f"{int(t0)}-{uuid.uuid4().hex[:8]}"

        # Encode code for safe transmission via environment variables
        code_b64 = base64.b64encode(code.encode('utf-8')).decode('ascii')

        logging.info(f"Injecting code via environment variable (length: {len(code)} chars)")

        # Build network configuration JSON
        network_config = {
            "awsvpcConfiguration": {
                "subnets": self.subnets,
                "securityGroups": self.security_groups,
                "assignPublicIp": self.assign_public_ip
            }
        }

        # Build container overrides with environment variable
        overrides = {
            "containerOverrides": [{
                "name": "job",  # Container name as defined in task definition
                "command": ["python", "-c", "import base64,os;code=base64.b64decode(os.getenv('CODE_B64')).decode();exec(code)"],
                "environment": [{"name": "CODE_B64", "value": code_b64}]
            }]
        }

        # Execute ECS task using aws ecs run-task command
        base_cmd = [
            'ecs', 'run-task',
            '--cluster', self.cluster,
            '--launch-type', self.launch_type,
            '--network-configuration', json.dumps(network_config),
            '--task-definition', self.task_definition,
            '--overrides', json.dumps(overrides),
            '--region', self.region,
            '--query', 'tasks[0].taskArn',
            '--output', 'text'
        ]
        cmd = self._build_aws_command(base_cmd)

        logging.info(f"Executing AWS ECS command: {' '.join(cmd[:8])}... [overrides hidden]")

        try:
            # Execute task
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            runtime_ms = int((time.time() - t0) * 1000)

            if result.returncode != 0:
                # AWS command failed
                error_msg = f"AWS ECS task execution failed: {result.stderr.strip()}"
                logging.error(f"AWS execution failed with return code {result.returncode}")
                return CodeResult(
                    stdout=None,
                    stderr=error_msg,
                    return_code=result.returncode,
                    runtime_ms=runtime_ms
                )

            # Extract task ARN
            task_arn = result.stdout.strip()
            if not task_arn or task_arn == 'None':
                error_msg = "Failed to get task ARN from AWS response"
                logging.error(error_msg)
                return CodeResult(
                    stdout=None,
                    stderr=error_msg,
                    return_code=1,
                    runtime_ms=runtime_ms
                )

            logging.info(f"AWS ECS task started: {task_arn}")

            # Wait for task completion and get logs
            logs = self._wait_for_task_completion_and_get_logs(task_arn)

            if logs:
                logging.info(f"Successfully retrieved task logs: {logs[:100]}...")  # Log first 100 chars
                return CodeResult(
                    stdout=logs,
                    stderr=None,
                    return_code=0,
                    runtime_ms=runtime_ms
                )
            else:
                logging.warning("No logs retrieved from task execution")
                return CodeResult(
                    stdout="Task completed successfully (no logs available)",
                    stderr=None,
                    return_code=0,
                    runtime_ms=runtime_ms
                )

        except subprocess.TimeoutExpired:
            # Handle timeout gracefully
            runtime_ms = int((time.time() - t0) * 1000)
            error_msg = f"AWS ECS task execution timed out after {self.timeout} seconds"
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
            logging.error(f"AWS ECS task execution error: {e}")
            return CodeResult(
                stdout=None,
                stderr=f"AWS ECS execution error: {e}",
                return_code=1,
                runtime_ms=runtime_ms
            )

    def _wait_for_task_completion_and_get_logs(self, task_arn: str) -> Optional[str]:
        """Wait for ECS task completion and retrieve logs.

        Args:
            task_arn: ARN of the ECS task

        Returns:
            Task logs as string, or None if logs couldn't be retrieved
        """
        start_time = time.time()
        max_wait_time = self.timeout

        while time.time() - start_time < max_wait_time:
            # Check task status
            status = self._check_task_status(task_arn)

            if status == 'STOPPED':
                # Task completed, get logs
                return self._get_task_logs(task_arn)
            elif status == 'RUNNING':
                # Task still running, wait a bit
                time.sleep(self.polling_interval)
            else:
                # Task failed or has unknown status
                logging.warning(f"Task {task_arn} has status: {status}")
                return None

        logging.warning(f"Task {task_arn} timed out after {max_wait_time} seconds")
        return None

    def _check_task_status(self, task_arn: str) -> str:
        """Check the status of an ECS task.

        Args:
            task_arn: ARN of the ECS task

        Returns:
            Task status ('RUNNING', 'STOPPED', etc.)
        """
        base_cmd = [
            'ecs', 'describe-tasks',
            '--cluster', self.cluster,
            '--tasks', task_arn,
            '--region', self.region,
            '--query', 'tasks[0].lastStatus',
            '--output', 'text'
        ]
        cmd = self._build_aws_command(base_cmd)

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            status = result.stdout.strip()
            return status
        else:
            logging.warning(f"Failed to check task status: {result.stderr}")
            return "UNKNOWN"

    def _get_task_logs(self, task_arn: str) -> Optional[str]:
        """Retrieve logs from an ECS task.

        Args:
            task_arn: ARN of the ECS task

        Returns:
            Task logs as string, or None if logs couldn't be retrieved
        """
        # First, get the task details to find the log group and log stream
        base_cmd = [
            'ecs', 'describe-tasks',
            '--cluster', self.cluster,
            '--tasks', task_arn,
            '--region', self.region,
            '--query', 'tasks[0].attachments[0].details',
            '--output', 'json'
        ]
        cmd = self._build_aws_command(base_cmd)

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            logging.warning(f"Failed to get task details for logs: {result.stderr}")
            return None

        try:
            details = json.loads(result.stdout)
            log_group = None
            log_stream = None

            for detail in details:
                if detail.get('name') == 'logGroup':
                    log_group = detail.get('value')
                elif detail.get('name') == 'logStream':
                    log_stream = detail.get('value')

            if not log_group or not log_stream:
                logging.warning("Could not find log group/stream in task details")
                return None

            # Get logs from CloudWatch
            base_cmd = [
                'logs', 'get-log-events',
                '--log-group-name', log_group,
                '--log-stream-name', log_stream,
                '--region', self.region,
                '--output', 'text',
                '--query', 'events[*].message'
            ]
            cmd = self._build_aws_command(base_cmd)

            logs_result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if logs_result.returncode == 0:
                logs = '\n'.join(logs_result.stdout.strip().split('\n'))
                return logs if logs.strip() else None
            else:
                logging.warning(f"Failed to get logs from CloudWatch: {logs_result.stderr}")
                return None

        except (json.JSONDecodeError, KeyError) as e:
            logging.warning(f"Error parsing task details: {e}")
            return None

    def _get_job_logs_with_retry(self, execution_name: str, execution_id: str) -> Optional[str]:
        """Retrieve logs with retry logic to handle timing issues.

        Args:
            execution_name: Name of the specific execution
            execution_id: Unique execution identifier for log filtering

        Returns:
            Task logs as string, or None if logs couldn't be retrieved after retries
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
        """Retrieve logs from a completed ECS task execution.

        Args:
            execution_name: ARN of the ECS task
            execution_id: Unique execution identifier for log filtering

        Returns:
            Task logs as string, or None if logs couldn't be retrieved
        """
        try:
            logging.info(f"Retrieving logs for task: {execution_name}")

            # For ECS, we use the task ARN to get logs directly
            logs = self._get_task_logs(execution_name)
            if logs:
                return logs

            logging.warning("Failed to retrieve task logs")
            return None

        except Exception as e:
            logging.error(f"Error retrieving ECS task logs: {e}")
            return None

    def is_available(self) -> bool:
        """Check if AWS CLI is available and configured."""
        try:
            cmd = self._build_aws_command(['--version'])
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

    async def execute_batch_distributed(self, code_versions: List[CodeVersion]) -> List[CodeResult]:
        """Execute a batch of code versions using true distributed execution.

        This method submits all tasks asynchronously to AWS ECS Fargate,
        then polls for completion. Each task runs on a separate container.

        Args:
            code_versions: List of CodeVersion objects to execute

        Returns:
            List of CodeResult objects in the same order as input
        """
        if not self.supports_distributed_execution():
            raise RuntimeError("Distributed execution not supported or AWS CLI not available")

        if len(code_versions) > self.max_concurrent_jobs:
            logging.warning(f"Batch size {len(code_versions)} exceeds max_concurrent_jobs {self.max_concurrent_jobs}")

        logging.info(f"Starting distributed execution of {len(code_versions)} tasks on AWS ECS")


        # Submit all tasks asynchronously
        task_submissions = await self._submit_tasks_async(code_versions)

        logging.info(f"Task submissions completed: {len(task_submissions)} tasks submitted")

        # Poll for results
        results = await self._poll_task_results(task_submissions)

        logging.info(f"Completed distributed execution: {len(results)} results")

        logging.info(f"Completed distributed execution of {len(results)} tasks")
        return results

    async def _submit_tasks_async(self, code_versions: List[CodeVersion]) -> List[Tuple[str, str, float]]:
        """Submit all tasks asynchronously and return task tracking information.

        Args:
            code_versions: List of CodeVersion objects to submit

        Returns:
            List of tuples: (code_version_id, task_arn, start_time)
        """
        task_submissions = []

        for cv in code_versions:
            try:
                task_arn = await self._submit_single_task(cv.code)
                start_time = time.time()
                task_submissions.append((cv.code_version_id, task_arn, start_time))
                logging.info(f"Submitted task {task_arn} for code version {cv.code_version_id}")

            except Exception as e:
                logging.error(f"Failed to submit task for code version {cv.code_version_id}: {e}")
                # Create a failed result for this task
                task_submissions.append((cv.code_version_id, None, time.time()))

        return task_submissions

    async def _submit_single_task(self, code: str) -> str:
        """Submit a single task asynchronously.

        Args:
            code: Python code to execute

        Returns:
            task_arn: The ARN of the submitted task
        """
        code_b64 = base64.b64encode(code.encode('utf-8')).decode('ascii')

        # Build network configuration JSON
        network_config = {
            "awsvpcConfiguration": {
                "subnets": self.subnets,
                "securityGroups": self.security_groups,
                "assignPublicIp": self.assign_public_ip
            }
        }

        # Build container overrides with environment variable
        overrides = {
            "containerOverrides": [{
                "name": "job",  # Container name as defined in task definition
                "command": ["python", "-c", "import base64,os;code=base64.b64decode(os.getenv('CODE_B64')).decode();exec(code)"],
                "environment": [{"name": "CODE_B64", "value": code_b64}]
            }]
        }

        # Submit task for async execution
        base_cmd = [
            'ecs', 'run-task',
            '--cluster', self.cluster,
            '--launch-type', self.launch_type,
            '--network-configuration', json.dumps(network_config),
            '--task-definition', self.task_definition,
            '--overrides', json.dumps(overrides),
            '--region', self.region,
            '--query', 'tasks[0].taskArn',
            '--output', 'text'
        ]
        cmd = self._build_aws_command(base_cmd)

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        )

        if result.returncode != 0:
            raise RuntimeError(f"Task submission failed: {result.stderr}")

        task_arn = result.stdout.strip()
        return task_arn

    async def _poll_task_results(self, task_submissions: List[Tuple[str, str, float]]) -> List[CodeResult]:
        """Poll all submitted tasks until completion and collect results.

        Args:
            task_submissions: List of (code_version_id, task_arn, start_time) tuples

        Returns:
            List of CodeResult objects in the same order as task_submissions
        """
        results = {}
        failed_submissions = set()

        # Track tasks that failed to submit
        for cv_id, task_arn, start_time in task_submissions:
            if task_arn is None:
                results[cv_id] = CodeResult(
                    stdout=None,
                    stderr="Task submission failed",
                    return_code=1,
                    runtime_ms=0
                )
                failed_submissions.add(cv_id)

        # Poll remaining tasks
        pending_tasks = [(cv_id, task_arn, start_time) for cv_id, task_arn, start_time in task_submissions
                       if cv_id not in failed_submissions]

        max_wait_time = 1800  # 30 minutes timeout
        start_polling_time = time.time()

        while pending_tasks:
            # Check for overall timeout
            if time.time() - start_polling_time > max_wait_time:
                logging.error(f"Polling timeout after {max_wait_time} seconds, marking remaining tasks as failed")
                for cv_id, task_arn, start_time in pending_tasks:
                    runtime_ms = int((time.time() - start_time) * 1000)
                    results[cv_id] = CodeResult(
                        stdout=None,
                        stderr="Task polling timeout",
                        return_code=-1,
                        runtime_ms=runtime_ms
                    )
                break

            completed_tasks = []

            logging.info(f"Polling {len(pending_tasks)} tasks...")

            for cv_id, task_arn, start_time in pending_tasks:
                try:
                    status = await self._check_task_status_async(task_arn)
                    logging.info(f"Task {task_arn}: status = {status}")

                    if status == 'STOPPED':
                        # Task completed successfully
                        logs = await self._get_task_logs_async(task_arn)
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
                        completed_tasks.append((cv_id, task_arn, start_time))
                        logging.info(f"Task {task_arn} completed successfully")

                    elif status == 'RUNNING':
                        # Task still running, continue polling
                        task_runtime = time.time() - start_time
                        if task_runtime > 1200:  # 20 minute individual task timeout
                            logging.warning(f"Task {task_arn} running for {task_runtime:.1f}s, marking as timeout")
                            results[cv_id] = CodeResult(
                                stdout=None,
                                stderr="Individual task timeout",
                                return_code=-1,
                                runtime_ms=int(task_runtime * 1000)
                            )
                            completed_tasks.append((cv_id, task_arn, start_time))
                        else:
                            logging.info(f"Task {task_arn} still running ({task_runtime:.1f}s)")
                    else:
                        # Task failed or has unknown status
                        runtime_ms = int((time.time() - start_time) * 1000)
                        error_logs = await self._get_task_logs_async(task_arn)

                        results[cv_id] = CodeResult(
                            stdout=None,
                            stderr=error_logs or "Task execution failed",
                            return_code=1,
                            runtime_ms=runtime_ms
                        )
                        completed_tasks.append((cv_id, task_arn, start_time))
                        logging.error(f"Task {task_arn} failed with status {status}")

                except Exception as e:
                    logging.error(f"Error checking status for task {task_arn}: {e}")
                    # Continue polling this task

            # Remove completed tasks from pending list
            for completed_task in completed_tasks:
                pending_tasks.remove(completed_task)

            # Wait before next polling cycle
            if pending_tasks:
                logging.info(f"Waiting {self.polling_interval}s before next poll...")
                await asyncio.sleep(self.polling_interval)

        # Return results in the same order as task_submissions
        ordered_results = []
        for cv_id, _, _ in task_submissions:
            ordered_results.append(results[cv_id])

        return ordered_results

    async def _check_task_status_async(self, task_arn: str) -> str:
        """Check the status of a specific ECS task.

        Args:
            task_arn: ARN of the task to check

        Returns:
            Status string ('RUNNING', 'STOPPED', etc.)
        """
        base_cmd = [
            'ecs', 'describe-tasks',
            '--cluster', self.cluster,
            '--tasks', task_arn,
            '--region', self.region,
            '--query', 'tasks[0].lastStatus',
            '--output', 'text'
        ]
        cmd = self._build_aws_command(base_cmd)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        )

        if result.returncode == 0:
            status = result.stdout.strip()
            return status
        else:
            logging.warning(f"Failed to check status for {task_arn}: {result.stderr}")
            return "UNKNOWN"

    async def _get_task_logs_async(self, task_arn: str) -> Optional[str]:
        """Asynchronously retrieve logs from a completed ECS task.

        Args:
            task_arn: ARN of the task

        Returns:
            Task logs as string, or None if logs couldn't be retrieved
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._get_task_logs(task_arn)
        )
