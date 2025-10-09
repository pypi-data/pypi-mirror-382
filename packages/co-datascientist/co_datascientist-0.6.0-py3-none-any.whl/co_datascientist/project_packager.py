"""
Project packaging utilities for handling single-file and multi-file projects.

NEW CLEAN ARCHITECTURE:
- Frontend extracts ONLY files with CO_DATASCIENTIST blocks
- Sends small dict of evolvable files to backend
- Backend evolves just those files and returns them
- Frontend stitches evolved files back into original repo for execution
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple


IGNORE_PATTERNS = [
    "__pycache__",
    ".git",
    ".pytest_cache",
    ".venv",
    "venv",
    ".env",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".DS_Store",
    "co_datascientist_output",
    "co_datascientist_checkpoints",
    "current_runs",  # Ignore saved run snapshots
]


def should_ignore_file(file_path: Path, base_path: Path) -> bool:
    """
    Check if a file should be ignored based on ignore patterns.
    
    Args:
        file_path: Path to the file
        base_path: Base directory path
        
    Returns:
        True if file should be ignored
    """
    relative_path = str(file_path.relative_to(base_path))
    
    for pattern in IGNORE_PATTERNS:
        if pattern in relative_path:
            return True
        if pattern.startswith("*.") and relative_path.endswith(pattern[1:]):
            return True
    
    return False


def find_files_with_blocks(base_path: Path) -> List[str]:
    """
    Find all Python files containing CO_DATASCIENTIST blocks.
    
    Args:
        base_path: Base directory to search
        
    Returns:
        List of relative file paths containing blocks
    """
    files_with_blocks = []
    
    for py_file in base_path.rglob("*.py"):
        if should_ignore_file(py_file, base_path):
            continue
            
        try:
            content = py_file.read_text()
            if "CO_DATASCIENTIST_BLOCK_START" in content:
                rel_path = py_file.relative_to(base_path)
                files_with_blocks.append(str(rel_path))
        except Exception as e:
            logging.warning(f"Could not read {py_file}: {e}")
    
    return files_with_blocks


def detect_run_command(base_path: Path, files_with_blocks: List[str]) -> Optional[str]:
    """
    Auto-detect the appropriate run command for a project.
    
    Only detects well-known entry points. Returns None if uncertain,
    which will trigger an error asking the user to specify --run-command.
    
    Args:
        base_path: Base directory path
        files_with_blocks: List of files with evolution blocks (unused, kept for compatibility)
        
    Returns:
        Run command string or None if no clear entry point found
    """
    # Check for common entry point files in priority order
    if (base_path / "run.sh").exists():
        return "bash run.sh"
    
    if (base_path / "main.py").exists():
        return "python main.py"
    
    if (base_path / "run.py").exists():
        return "python run.py"
    
    # If we don't find a standard entry point, return None
    # This will trigger the helpful error message asking user to specify --run-command
    return None


def extract_evolvable_files(path: Path) -> Dict[str, str]:
    """
    Extract ONLY files containing CO_DATASCIENTIST blocks from a project.
    
    This is the new clean approach - only send files that need evolution.
    
    Args:
        path: Path to Python file or directory
        
    Returns:
        Dict mapping relative file paths to their contents
        
    Raises:
        ValueError: If no evolvable blocks are found
    """
    evolvable_files = {}
    
    if path.is_file():
        # Single file case
        content = path.read_text()
        if "CO_DATASCIENTIST_BLOCK_START" not in content:
            raise ValueError(f"No CO_DATASCIENTIST blocks found in {path.name}")
        evolvable_files[path.name] = content
    else:
        # Multi-file case: find all files with blocks
        files_with_blocks = find_files_with_blocks(path)
        if not files_with_blocks:
            raise ValueError(f"No Python files with CO_DATASCIENTIST blocks found in {path}")
        
        for rel_path in files_with_blocks:
            full_path = path / rel_path
            try:
                content = full_path.read_text()
                evolvable_files[rel_path] = content
            except Exception as e:
                logging.warning(f"Could not read {full_path}: {e}")
    
    return evolvable_files


def create_manifest(
    base_path: Path,
    is_directory: bool,
    run_command: Optional[str] = None
) -> Dict:
    """
    Create a project manifest describing how to run the project.
    
    FRONTEND ONLY - tells frontend how to execute the project.
    Backend never sees this.
    
    Args:
        base_path: Base path (file or directory)
        is_directory: True if base_path is a directory
        run_command: Optional explicit run command
        
    Returns:
        Manifest dictionary
    """
    if is_directory:
        files_with_blocks = find_files_with_blocks(base_path)
        
        if not run_command:
            run_command = detect_run_command(base_path, files_with_blocks)
        
        # Validate that we have a run command
        if not run_command:
            error_msg = (
                f"Could not auto-detect how to run your project in: {base_path}\n\n"
                f"No run.sh, main.py, or run.py found in the project root.\n"
                f"Please specify a custom run command using --run-command.\n\n"
                f"Examples:\n"
                f"  co-datascientist run --script-path . --run-command 'python my_script.py'\n"
                f"  co-datascientist run --script-path . --run-command 'bash scripts/train.sh'\n"
                f"  co-datascientist run --script-path . --run-command 'python -m my_package.main'\n"
            )
            raise ValueError(error_msg)
        
        manifest = {
            "project_type": "multi-file",
            "run_command": run_command,
            "base_path": str(base_path),
            "files_with_blocks": files_with_blocks,
            "requirements": "requirements.txt" if (base_path / "requirements.txt").exists() else None
        }
    else:
        manifest = {
            "project_type": "single-file",
            "run_command": run_command or f"python {base_path.name}",
            "base_path": str(base_path.parent),
            "files_with_blocks": [base_path.name],
            "requirements": None
        }
    
    return manifest


def package_project(
    path: Path,
    run_command: Optional[str] = None
) -> Tuple[Dict[str, str], Dict]:
    """
    Extract evolvable files and generate manifest for a project.
    
    - Extracts ONLY files with CO_DATASCIENTIST blocks
    - Returns small dict.
    - Manifest stays frontend-only
    
    Args:
        path: Path to Python file or directory
        run_command: Optional explicit run command
        
    Returns:
        Tuple of (evolvable_files_dict, manifest_dict)
        
    Raises:
        ValueError: If no evolvable blocks are found
    """
    path = Path(path).resolve()
    
    if not path.exists():
        raise ValueError(f"Path does not exist: {path}")
    
    # Extract only evolvable files (NEW!)
    evolvable_files = extract_evolvable_files(path)
    
    # Generate manifest (frontend-only metadata)
    is_directory = path.is_dir()
    manifest = create_manifest(path, is_directory, run_command)
    
    logging.info(f"Extracted {len(evolvable_files)} evolvable file(s) from {path.name}")
    for filename in evolvable_files.keys():
        logging.info(f"  - {filename} ({len(evolvable_files[filename])} bytes)")
    
    return evolvable_files, manifest
