"""Local executor: stitch evolved files into repo and run."""

import os
import subprocess
import tempfile
import time
import logging
import shlex
import shutil
from typing import Dict, Any, Optional
from pathlib import Path

from .base_executor import BaseExecutor
from ..models import CodeResult
from ..settings import settings
from ..kpi_extractor import extract_kpi_from_stdout


class LocalExecutor(BaseExecutor):
    """Execute code locally: copy repo → stitch evolved files → run → collect KPI."""
    
    @property
    def platform_name(self) -> str:
        return "local"
    
    def execute(self, evolved_files: Dict[str, str], manifest: Optional[Dict] = None) -> CodeResult:
        """Execute code by stitching evolved files back into original repo.
        
        ULTRA-SIMPLE:
        1. Copy entire original repo to temp directory
        2. Overwrite evolved files in temp directory
        3. Run command → Extract KPI → Cleanup
        
        Args:
            evolved_files: Dict mapping file paths to evolved contents
            manifest: Project manifest with base_path and run_command
                
        Returns:
            CodeResult containing stdout, stderr, return_code, runtime_ms, and kpi
        """
        start_time = time.time()
        temp_dir = None
        
        try:
            # Create temp directory for execution
            temp_dir = tempfile.mkdtemp(prefix="co_datascientist_")
            
            # Get base path and run command from manifest
            if not manifest or not manifest.get('base_path'):
                raise ValueError("Manifest with base_path required for execution")
            
            base_path = Path(manifest['base_path'])
            run_command = manifest.get('run_command', 'python main.py')
            
            # Copy entire original repo to temp
            logging.info(f"Copying repo from {base_path} to {temp_dir}")
            for item in base_path.iterdir():
                if item.name in ['__pycache__', '.git', '.pytest_cache', '.venv', 'venv']:
                    continue
                src = str(item)
                dst = str(Path(temp_dir) / item.name)
                if item.is_dir():
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            
            # Overwrite with evolved files
            logging.info(f"Stitching in {len(evolved_files)} evolved file(s)")
            for rel_path, content in evolved_files.items():
                target_file = Path(temp_dir) / rel_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                target_file.write_text(content)
                logging.info(f"  - Wrote {rel_path}")
            
            # Parse and adjust run command
            command_parts = shlex.split(run_command)
            if command_parts[0] == 'python' and len(command_parts) > 1:
                command_parts[0] = self.python_path
            
            logging.info(f"Running command in {temp_dir}: {command_parts}")
            
            # Execute the command
            try:
                output = subprocess.run(
                    command_parts,
                    capture_output=True,
                    text=True,
                    cwd=temp_dir,
                    timeout=settings.script_execution_timeout
                )
                return_code = output.returncode
                out = output.stdout
                err = output.stderr
            except subprocess.TimeoutExpired:
                return_code = -9
                out = None
                err = f"Process timed out after {settings.script_execution_timeout} seconds"
                logging.info(f"Process timed out after {settings.script_execution_timeout} seconds")
            
            # Clean up empty strings
            if isinstance(out, str) and out.strip() == "":
                out = None
            if isinstance(err, str) and err.strip() == "":
                err = None

            logging.info(f"Local execution stdout: {out}")
            logging.info(f"Local execution stderr: {err}")
                
            runtime_ms = int((time.time() - start_time) * 1000)
            kpi = extract_kpi_from_stdout(out) if out else None
            
            return CodeResult(
                stdout=out, 
                stderr=err, 
                return_code=return_code, 
                runtime_ms=runtime_ms,
                kpi=kpi
            )
        
        finally:
            # Always cleanup temp directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except OSError as e:
                    logging.warning(f"Failed to cleanup temp directory {temp_dir}: {e}")
    
    def is_available(self) -> bool:
        """Check if Python interpreter is available."""
        try:
            result = subprocess.run(
                [self.python_path, "--version"], 
                capture_output=True, 
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
