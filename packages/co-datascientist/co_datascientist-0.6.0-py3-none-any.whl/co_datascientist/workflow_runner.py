import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import time
import asyncio
import pathlib
import base64
from pathlib import Path
from datetime import datetime, timezone, timedelta
import uuid

from .models import Workflow, SystemInfo, CodeResult
from . import co_datascientist_api
from .executors import ExecutorFactory
from .kpi_extractor import extract_kpi_from_stdout
from .settings import settings
from .qa_cache import get_answers, QACache
from .user_steering import get_steering_handler, wrap_spinner_with_coordination
from .executors import BaseExecutor

OUTPUT_FOLDER = "co_datascientist_output"
CHECKPOINTS_FOLDER = "co_datascientist_checkpoints"
CURRENT_RUNS_FOLDER = "current_runs"


def print_workflow_info(message: str):
    """Print workflow info with consistent formatting"""
    print(f"   {message}")


def print_workflow_step(message: str):
    """Print workflow step with consistent formatting"""
    print(f"   {message}")


def print_workflow_success(message: str):
    """Print workflow success with consistent formatting"""
    print(f"   {message}")


def print_workflow_error(message: str):
    """Print workflow error with consistent formatting"""
    print(f"   {message}")



def ignore_dirs(dir, files):
    ignore_list = []
    for f in files:
        if f in ("current_runs", "co_datascientist_checkpoints"):
            ignore_list.append(f)
    return ignore_list


def move_to_tmp(code_base_directory):
    """
    Copy the code_base_directory to a temporary directory, ignoring
    'current_runs' and 'co_datascientist_checkpoints' directories.
    Returns the path to the copied code base directory in the temp location.
    """
    import shutil
    import tempfile
    # TODO: we should label the temp dir with the workflow id so its bertter to track...
    temp_dir = tempfile.mkdtemp(prefix="co-datascientist-")
    temp_code_base_directory = Path(temp_dir) / Path(code_base_directory).name

    shutil.copytree(code_base_directory, temp_code_base_directory, ignore=ignore_dirs)
    # print_info(f"Copied code base directory to temporary location: {temp_code_base_directory}")
    return temp_code_base_directory

def auto_detect_repository_structure(working_directory):
    """
    Auto detect the repository structure and return the code base directory and the docker file directory.
    """
    code_base_directory = Path(working_directory)
    dockerfile_path = Path(working_directory) / 'Dockerfile'

    return code_base_directory, dockerfile_path



class WorkflowRunner:
    def __init__(self):
        self.workflow: Workflow | None = None
        self.start_timestamp = 0
        self.should_stop_workflow = False
        self._checkpoint_counter: int = 0
        self._current_hypothesis: str | None = None
        self.steering_handler = get_steering_handler()
        self._steering_bar_started: bool = False

    def prep_workflow(self, working_directory: str):
        """Prep the workflow by moving the code to temp and getting the run command for the docker and the files to evolve out."""
        temp_code_base_directory = move_to_tmp(working_directory)
        code_base_directory, dockerfile_path = auto_detect_repository_structure(temp_code_base_directory)

        return code_base_directory, dockerfile_path
    

    def get_evolvable_files(self, working_dir_path: str) -> dict[str, str]:
        """
        Scan a directory for Python files containing CO_DATASCIENTIST blocks.
        Returns a dict of {filename: code} for files containing the blocks.

        Ignores any files inside directories named 'current_runs' or 'co-datascientist-checkpoints'.

        Args:
            working_dir_path: Path to the working directory to scan.

        Returns:
            Dict mapping filename (relative to working_dir_path) -> code content.

        Raises:
            ValueError: If no files with CO_DATASCIENTIST blocks are found.
        """
        import os

        start_block = "# CO_DATASCIENTIST_BLOCK_START"
        end_block = "# CO_DATASCIENTIST_BLOCK_END"
        code_files = {}

        # Normalize ignore dir names for comparison
        IGNORE_DIRS = {"current_runs", "co_datascientist_checkpoints"}

        for root, dirs, files in os.walk(working_dir_path):
            # Remove ignored dirs from traversal
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for fname in files:
                if fname.endswith(".py"):
                    # Check if this file is inside an ignored directory
                    rel_dir = os.path.relpath(root, working_dir_path)
                    # rel_dir == '.' for top-level, otherwise it's a path
                    # Split rel_dir into its parts and check for ignore dirs
                    if rel_dir != ".":
                        dir_parts = set(rel_dir.replace("\\", "/").split("/"))
                        if IGNORE_DIRS & dir_parts:
                            continue
                    fpath = os.path.join(root, fname)
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            content = f.read()
                        if start_block in content and end_block in content:
                            # Store relative path for clarity
                            rel_path = os.path.relpath(fpath, working_dir_path)
                            code_files[rel_path] = content
                    except Exception:
                        # Optionally log or print error, but skip unreadable files
                        continue
        if not code_files:
            raise ValueError(
                "ERROR: No CO_DATASCIENTIST blocks found in any Python file in the directory.\n"
                "Please add evolution blocks:\n"
                "  # CO_DATASCIENTIST_BLOCK_START\n"
                "  # Your code here\n"
                "  # CO_DATASCIENTIST_BLOCK_END\n\n"
                "These blocks mark code that will be evolved."
            )

        return code_files

    def compile_docker_image(self, dockerfile_path: str):
        """
        Build a Docker image from the Dockerfile in dockerfile_path,
        using code_base_directory as the build context.
        """
        import subprocess
        import uuid

        if not dockerfile_path.exists():
            raise FileNotFoundError(f"Dockerfile not found at {dockerfile_path}")

        # Generate a unique image tag
        image_tag = f"co-datascientist-{uuid.uuid4().hex[:8]}"
        print("Dockerfile path: ", dockerfile_path)
        # Build the docker image
        # The build context should be the directory containing the Dockerfile, not the Dockerfile itself
        build_context = dockerfile_path.parent
        build_cmd = [
            "docker", "build",
            "-t", image_tag,
            "-f", str(dockerfile_path),
            str(build_context)
        ]
        try:
            result = subprocess.run(
                build_cmd,
                check=True,
                capture_output=True,
                text=True
            )
            print(f"Docker image built successfully: {image_tag}")
        except subprocess.CalledProcessError as e:
            print(f"Error building Docker image:\n{e.stderr}")
            raise

        return image_tag

    def stitch_evolvable_files(self, evolvable_files: dict[str, str], temp_code_base_directory: str):
        """
        Stitch the evolvable files back into the directory where the docker file is (temp!)
        """
        # stitch the evolvable files back into the docker file directory
        for file_path, file_content in evolvable_files.items():
            with open(os.path.join(temp_code_base_directory, file_path), "w") as f:
                f.write(file_content)


    async def stich_compile_execute(self, evolvable_files: dict[str, str], temp_code_base_directory: str, docker_file_directory: str, executor: BaseExecutor):
        # compile the users docker image in temp now and then run it from temp early so we know if there are crashes before the preflight....
        self.stitch_evolvable_files(evolvable_files, temp_code_base_directory)
        docker_image_tag = self.compile_docker_image(docker_file_directory)   
        print("Executing the baseline docker image")
        # Run the blocking executor.execute() in a thread pool so it doesn't block the event loop
        code_result = await asyncio.to_thread(executor.execute, docker_image_tag)
        return code_result


    async def run_workflow(self, working_directory: str, config: dict, spinner=None):
        """Run a complete code evolution workflow.
        """
        self.workflow = Workflow(status_text="Workflow started", user_id="")
        
        # Get absolute path for checkpointing
        project_absolute_path = str(Path(working_directory).absolute())

        evolvable_files = self.get_evolvable_files(working_directory) # get a dict of python files from this dir ... 
        assert len(evolvable_files) > 0, "No blocks found in any Python file in the directory."
        temp_code_base_directory, docker_file_directory = self.prep_workflow(working_directory) # move the users workspace to temp and find the docker file.
        
        executor = ExecutorFactory.create_executor(python_path="python", config=config)
        print("Running your baseline to start")
        print("--------------------------------")
            
        result = await self.stich_compile_execute(evolvable_files, temp_code_base_directory, docker_file_directory, executor)
        assert result.return_code == 0, "Baseline docker image failed to execute"

        print(f"Baseline result: {result}")

        # TODO: get the types of all these parts of the model of what needs to be sent through! 

        # code_version = initial_response.code_to_run
        # code_version.result = result
        
        self.should_stop_workflow = False
        
        # Wrap spinner for coordination with status bar
        spinner = wrap_spinner_with_coordination(spinner)                
        # try:
            # if spinner:
            #     spinner.text = "Waking up the Co-DataScientist"
                
        self.start_timestamp = time.time()
        # system_info = get_system_info(python_path) #TODO: we may be able to get this from the docker ime... for now just go with None
        system_info = SystemInfo(python_libraries=["None"],python_version="3.13",os=sys.platform)
        # Start preflight: send full dict of evolvable files
        preflight = await co_datascientist_api.start_preflight(evolvable_files, system_info) 
        self.workflow = preflight.workflow
        # Stop spinner to allow clean input UX
        if spinner:
            spinner.stop()
        # Get observation text
        observation = getattr(preflight, 'observation', '') or ''
        # Clean questions
        questions = [re.sub(r'^\d+\.\s*', '', q.strip()) for q in preflight.questions]
        # Get answers (cached or interactive)
        use_cache = config.get('use_cached_qa', False)
        answers = get_answers(questions, str(working_directory), observation, use_cache)
        # Complete preflight: engine summarizes and starts baseline
        initial_response = await co_datascientist_api.complete_preflight(self.workflow.workflow_id, answers)
        self.workflow = initial_response.workflow

        # Exception: Failed to process batch results: Code version baseline not found in batch! DEBUG.
        # TODO: ok so we really need to understnad the exact thing that needs to be posted back... this is the sticking piint now.
        code_version = initial_response.code_to_run
        code_version.result = result
        # Submit baseline results
        await co_datascientist_api.finished_running_batch(
            self.workflow.workflow_id,
            "baseline_batch",
            [(code_version.code_version_id, result)],
        )

        # Unified batch system: batch_size=1 for sequential, >1 for parallel
        batch_size = int(config.get('parallel', 1) or 1)
    
        while (not self.workflow.finished and not self.should_stop_workflow):

            # break
            await self._check_user_direction()

            if spinner:
                spinner.text = f"Running {batch_size} programs in parallel..."
                spinner.start()
            
            ###WHY DONT WE GET HERE!!!!???  i does some v weerid thing in the finished runnign batch first one!!!!!
            print(f"Batch size: {batch_size}")
            # Check for both None and empty list - backend returns [] when generation fails
            batch_to_run = await co_datascientist_api.get_batch_to_run(self.workflow.workflow_id, batch_size=batch_size)
            self.workflow = batch_to_run.workflow
            # We have a batch to run!
            code_versions = batch_to_run.batch_to_run
            batch_id = batch_to_run.batch_id

            # Run the executor in parallel for the batch using asyncio.gather
            import asyncio
            import shutil

            temp_dirs = []
            tasks = []
            for code_version in code_versions:
                evolvable_files = code_version.code  # dict of files to use for this candidate
                # Create a unique temp directory for each code version to avoid race conditions
                temp_dir_for_version = tempfile.mkdtemp(prefix=f"co-datascientist-{code_version.code_version_id[:8]}-")
                temp_dirs.append(temp_dir_for_version)
                temp_code_dir_for_version = Path(temp_dir_for_version) / Path(temp_code_base_directory).name
                shutil.copytree(temp_code_base_directory, temp_code_dir_for_version, ignore=ignore_dirs)
                # docker_file_directory is the path to the Dockerfile within the temp dir
                docker_file_path_for_version = temp_code_dir_for_version / Path(docker_file_directory).relative_to(temp_code_base_directory)
                
                tasks.append(
                    self.stich_compile_execute(evolvable_files, temp_code_dir_for_version, docker_file_path_for_version, executor)
                )
            code_results = await asyncio.gather(*tasks)
            for code_result in code_results:
                print(f"Code result: {code_result}")
            # Cleanup temp dirs after execution
            for temp_dir in temp_dirs:
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    logging.warning(f"Failed to cleanup temp dir {temp_dir}: {e}")
            # if spinner:
            #     spinner.stop()

            # try:
            #     self.steering_handler.suspend_bar() ##TODO why? 
            # except Exception:
            #     pass

            # await self._display_batch_info(code_versions, batch_size)
            # executor = ExecutorFactory.create_executor(python_path, config) # We need to maek an execter each and ever time? can we not make one at the start???
            # results = await self._execute_batch(
            #     executor, code_versions, spinner, batch_size, python_path, config
            # ) # feels weird we wrap this again -- surely it just int he executer? ...

            # results = await executor.execute_batch(executor, code_versions, spinner, batch_size, python_path, config)

            if spinner:
                spinner.stop()

            tuples: list[tuple[str, CodeResult]] = []
            for cv, res in zip(code_versions, code_results):
                if res.kpi is None:
                    res.kpi = extract_kpi_from_stdout(res.stdout)
                tuples.append((cv.code_version_id, res))

            await self._display_batch_results(code_versions, code_results, batch_size)

            # try:
            #     self.steering_handler.resume_bar()
            # except Exception:
            #     pass

            # if not self._steering_bar_started:
            #     try:
            #         await self.steering_handler.start_listening()
            #         self._steering_bar_started = True
            #     except Exception:
            #         pass

            try:
                if code_versions and code_results:
                    last_cv = code_versions[-1]
                    last_cv.result = code_results[-1]
                    await self._save_current_run_snapshot(last_cv, project_absolute_path, config)
            except Exception as e:
                logging.warning(f"Failed saving current run snapshot (parallel): {e}")

            # Submit results (workflow will be updated on next get_batch_to_run call)
            await co_datascientist_api.finished_running_batch(
                self.workflow.workflow_id, batch_id, tuples
            )

            has_meaningful_results = any(
                cv.retry_count == 0 or cv.hypothesis_outcome in ["supported", "refuted", "failed"]
                for cv in code_versions
            )
            if has_meaningful_results:
                try:
                    best_info = await co_datascientist_api.get_workflow_population_best(
                        self.workflow.workflow_id
                    )
                    best_kpi = best_info.get("best_kpi") if best_info else None
                    if best_kpi is not None and spinner:
                        spinner.write(f"Current best KPI: {best_kpi}")

                    best_cv = best_info.get("best_code_version") if best_info else None
                    if best_cv and best_kpi is not None:
                        await self._save_population_best_checkpoint(
                            best_cv, best_kpi, project_absolute_path, config
                        )
                    elif best_kpi is not None and spinner:
                        spinner.write(f"No code version available for checkpoint (KPI: {best_kpi})")
                except Exception:
                    pass
            # pass
    
            # import ipdb; ipdb.set_trace()
            
        
        
            # Stop user steering handler
            # await self.steering_handler.stop_listening()

            if self.should_stop_workflow:
                # Check if this was a baseline failure (already handled) or user stop
                if (hasattr(self.workflow, 'baseline_code') and 
                    self.workflow.baseline_code.result is not None and 
                    self.workflow.baseline_code.result.return_code != 0):
                    # Baseline failure - already handled in _handle_baseline_result, just clean up
                    try:
                        await co_datascientist_api.stop_workflow(self.workflow.workflow_id)
                    except Exception as e:
                        logging.warning(f"Failed to stop workflow on backend: {e}")
                    if spinner:
                        spinner.text = "Workflow failed"
                else:
                    # User-initiated stop
                    await co_datascientist_api.stop_workflow(self.workflow.workflow_id)
                    print_workflow_info("Workflow stopped!.")
                    if spinner:
                        spinner.text = "Workflow stopped"
            # else:
            #     # Normal successful completion
            #     print_workflow_success("Workflow completed successfully.")
            #     if spinner:
            #         spinner.text = "Workflow completed"
        
        # except Exception as e:
        #     if spinner:
        #         spinner.stop()

        #     err_msg = str(e)
        #     # Detect user-facing validation errors coming from backend
        #     if err_msg.startswith("ERROR:"):
        #         # Show concise guidance without stack trace
        #         print_workflow_error(err_msg)
        #         return  # Do not re-raise, end gracefully

        #     # Otherwise, show generic workflow error and re-raise for full trace
        #     print_workflow_error(f"Workflow error: {err_msg}")
        #     raise



    async def _check_user_direction(self):
        """Check for new user direction and update the workflow if needed."""
        try:
            latest_direction = await self.steering_handler.get_latest_direction()
            current_direction = getattr(self.workflow, 'user_direction', None)
            
            # Only update if direction has changed
            if latest_direction != current_direction:
                await co_datascientist_api.update_user_direction(
                    self.workflow.workflow_id, 
                    latest_direction
                )
                # Update local workflow state
                self.workflow.user_direction = latest_direction
                
                # Silent: no echo after steering to keep UI clean
                    
        except Exception as e:
            logging.warning(f"Failed to check user direction: {e}")
    
    async def _display_batch_info(self, code_versions: list, batch_size: int):
        """Silenced: avoid verbose batch info prints."""
        return

    # async def _execute_batch(self, executor, code_versions: list, spinner, batch_size: int, python_path: str, config: dict):
    #     """Execute batch with appropriate concurrency."""
    #     if batch_size == 1:
    #         # Sequential execution with adapted spinner
    #         cv = code_versions[0]
    #         if cv.name != "baseline" and cv.retry_count > 0:
    #             if spinner:
    #                 spinner.text = f"Debugging attempt {cv.retry_count}"
    #                 spinner.start()
    #         elif cv.name != "baseline":
    #             if spinner:
    #                 spinner.text = "Testing hypothesis"
    #                 spinner.start()
            
    #         manifest = config.get('manifest', None)
    #         # MULTI-FILE READY: Use evolved dict directly (already contains all files)
    #         results = []
    #         for cv in code_versions:
    #             # Execute with evolved dict (backend already stitched files)
    #             results.append(executor.execute(cv.code, manifest))
    #         return results
    #     else:
    #         # Parallel execution (existing logic)
    #         if hasattr(executor, 'supports_distributed_execution') and executor.supports_distributed_execution():
    #             if spinner:
    #                 spinner.text = f"Submitting {len(code_versions)} jobs to {executor.platform_name}..."
    #                 spinner.start()
    #             manifest = config.get('manifest', {})
    #             return await executor.execute_batch_distributed(code_versions, manifest)
    #         else:
    #             if spinner:
    #                 spinner.text = f"Running {len(code_versions)} programs in parallel..."
    #                 spinner.start()
    #             manifest = config.get('manifest', None)
    #             def _execute(cv):
    #                 single_executor = ExecutorFactory.create_executor(python_path, config)
    #                 return single_executor.execute(cv.code, manifest)

    #             tasks = [asyncio.to_thread(_execute, cv) for cv in code_versions]
    #             return await asyncio.gather(*tasks, return_exceptions=False)

    async def _display_batch_results(self, code_versions: list, results: list, batch_size: int):
        """Display results adapted to batch size."""
        if batch_size == 1:
            # Sequential mode: existing sequential display logic.
            cv, result = code_versions[0], results[0]
            kpi_value = getattr(result, 'kpi', None) or extract_kpi_from_stdout(result.stdout)
            
            if cv.name != "baseline":
                if kpi_value is not None and result.return_code == 0:
                    baseline_kpi = self._get_baseline_kpi()
                    hypothesis_outcome = baseline_kpi < kpi_value if baseline_kpi is not None else None
                    print()
                    print(f"Hypothesis: {cv.hypothesis or 'Unknown hypothesis'}")
                    print(f" - Result: {hypothesis_outcome}, KPI: {kpi_value}")
                    print("--------------------------------")
                else:
                    # Handle failed executions like parallel mode
                    print()
                    print(f"Hypothesis: {cv.hypothesis or 'Unknown hypothesis'}")
                    if getattr(cv, 'hypothesis_outcome', None) == "failed":
                        print(" - Failed after all retries - moving on")
                    else:
                        print(" - Debugging and queuing for retry...")
                    print("--------------------------------")
        else:
            # Parallel mode: existing parallel display logic
            baseline_kpi = self._get_baseline_kpi()
            successful_results = []
            failed_results = []
            
            for cv, res in zip(code_versions, results):
                kpi_value = getattr(res, 'kpi', None) or extract_kpi_from_stdout(res.stdout)
                if hasattr(res, 'kpi') and res.kpi is None:
                    res.kpi = kpi_value
                    
                if kpi_value is not None and res.return_code == 0:
                    hypothesis_outcome = baseline_kpi < kpi_value if baseline_kpi is not None else None
                    successful_results.append((cv, kpi_value, hypothesis_outcome))
                else:
                    failed_results.append((cv, res))
            
            # Display successful results
            for cv, kpi_value, hypothesis_outcome in successful_results:
                print()
                print(f"Hypothesis: {cv.hypothesis or 'Unknown hypothesis'}")
                if hypothesis_outcome is not None:
                    print(f" - Result: {hypothesis_outcome}, KPI: {kpi_value}")
                else:
                    print(f" - Result: KPI = {kpi_value}")
            
            # Display failed results - show debugging status
            for cv, res in failed_results:
                print()
                print(f"Hypothesis: {cv.hypothesis or 'Unknown hypothesis'}")
                if getattr(cv, 'hypothesis_outcome', None) == "failed":
                    print(" - Failed after all retries - moving on")
                else:
                    print(" - Debugging and queuing for retry...")
            
            if code_versions:
                print("--------------------------------")

    def _get_baseline_kpi(self):
        """Get baseline KPI for comparison."""
        if self.workflow.baseline_code and self.workflow.baseline_code.result:
            return extract_kpi_from_stdout(self.workflow.baseline_code.result.stdout)
        return None

    async def _handle_baseline_result(self, result: CodeResult, response, spinner=None):
        """Handle result in standard mode (original behavior)"""
        # Check if code execution failed and provide clear feedback
        if result.return_code != 0:
            # Code failed - show error details
            print_workflow_error(f"'{response.code_to_run.name}' failed with exit code {result.return_code}")
            print(f"   DEBUG: stderr = {repr(result.stderr)}")
            print(f"   DEBUG: stdout = {repr(result.stdout)}")
            if result.stderr:
                print("   Error details:")
                # Print each line of stderr with proper indentation
                for line in result.stderr.strip().split('\n'):
                    if spinner:
                        spinner.write(f"      {line}")
                    else:
                        print(f"      {line}")
            
            # For baseline failures, give specific guidance and STOP immediately
            if response.code_to_run.name == "baseline":
                print("   The baseline code failed to run. This will stop the workflow.")
                print("   Check the error above and fix your script before running again.")
                if "ModuleNotFoundError" in (result.stderr or ""):
                    print("   Missing dependencies? Try: pip install <missing-package>")
                
                # Set flag to stop workflow immediately - don't wait for backend
                self.should_stop_workflow = True
                print_workflow_error("Workflow terminated due to baseline failure.")
                return

        else:
            # print("stdout:",result) 
            # Code succeeded - show success message
            kpi_value = extract_kpi_from_stdout(result.stdout)
            if kpi_value is not None:
                msg = f"Completed '{response.code_to_run.name}' | KPI = {kpi_value}"
                if spinner:
                    spinner.write(msg)
                    print("--------------------------------")
                else:
                    print_workflow_success(msg)
            elif response.code_to_run.name == "baseline": ### SO THE QUESTION IS WHY SOMETIMES WE DONT GET the output from the gcloud run... 
                # Debug: baseline succeeded but no KPI extracted
                logging.info(f"Baseline succeeded but no KPI found. Stdout: {result.stdout[:200] if result.stdout else 'None'}...")
                msg = f"Completed '{response.code_to_run.name}' (no KPI found)"
                self.should_stop_workflow = True
                return
            else:
                msg = f"Completed '{response.code_to_run.name}'"
                if spinner:
                    spinner.write(msg)
                else:
                    print_workflow_success(msg)

    async def _save_population_best_checkpoint(self, best_cv, best_kpi: float, project_absolute_path: str, config: dict):
        """Persist best code/KPI - to Databricks volume if using Databricks, locally otherwise."""
        try:
            if not best_cv or best_kpi is None:
                return

            # Convert best_cv to CodeVersion model if it is raw dict
            from .models import CodeVersion, CodeResult
            if isinstance(best_cv, dict):
                try:
                    # Nested result may also be dict – handle gracefully
                    if isinstance(best_cv.get("result"), dict):
                        # Ensure runtime_ms field may be missing; allow extra
                        best_cv["result"] = CodeResult.model_validate(best_cv["result"])  # type: ignore
                    best_cv = CodeVersion.model_validate(best_cv)  # type: ignore
                except Exception as e:
                    logging.warning(f"Cannot parse best_code_version payload: {e}")
                    return

            safe_name = _make_filesystem_safe(best_cv.name or "best")
            base_filename = f"best_{self._checkpoint_counter}_{safe_name}"

            # Prepare metadata
            meta = {
                "code_version_id": best_cv.code_version_id,
                "name": best_cv.name,
                "kpi": best_kpi,
                "stdout": getattr(best_cv.result, "stdout", None) if best_cv.result else None,
            }

            # Check if using Databricks
            is_databricks = config and config.get('databricks')
            if is_databricks:
                # Save directly to Databricks volume using CLI (no local storage)
                await self._save_checkpoint_to_databricks_volume(
                    best_cv.code, 
                    json.dumps(meta, indent=4), 
                    base_filename, 
                    config
                )
            else:
                # Save checkpoints for local runs (handles both single and multi-file)
                checkpoints_base = Path(project_absolute_path) / CHECKPOINTS_FOLDER
                checkpoints_base.mkdir(parents=True, exist_ok=True)
                
                # Create directory for this checkpoint
                checkpoint_dir = checkpoints_base / base_filename
                checkpoint_dir.mkdir(parents=True, exist_ok=True)
                
                # Save each file in the code dict
                code_dict = best_cv.code if isinstance(best_cv.code, dict) else {"main.py": best_cv.code}
                for filename, content in code_dict.items():
                    file_path = checkpoint_dir / filename
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(content, encoding="utf-8")
                
                # Save metadata in the checkpoint directory
                meta_path = checkpoint_dir / "metadata.json"
                meta["files"] = list(code_dict.keys())  # Add file list to metadata
                meta_path.write_text(json.dumps(meta, indent=4))

            self._checkpoint_counter += 1
        except Exception as e:
            logging.warning(f"Failed saving best checkpoint: {e}")


    async def _save_current_run_snapshot(self, code_version, project_absolute_path: str, config: dict):
        """Persist the most recent run (code + minimal meta) to `current_runs`.

        Keeps it simple: always overwrite `latest.py` and `latest.json`.
        Mirrors Databricks behavior if configured.
        """
        try:
            if not code_version:
                return

            from .models import CodeVersion, CodeResult
            if isinstance(code_version, dict):
                try:
                    if isinstance(code_version.get("result"), dict):
                        code_version["result"] = CodeResult.model_validate(code_version["result"])  # type: ignore
                    code_version = CodeVersion.model_validate(code_version)  # type: ignore
                except Exception as e:
                    logging.warning(f"Cannot parse code_version payload for current run: {e}")
                    return

            meta = {
                "code_version_id": code_version.code_version_id,
                "name": code_version.name,
                "kpi": getattr(code_version.result, "kpi", None) if code_version.result else None,
                "stdout": getattr(code_version.result, "stdout", None) if code_version.result else None,
            }

            is_databricks = config and config.get('databricks')
            unique_id = getattr(code_version, 'code_version_id', None) or str(uuid.uuid4())
            uid_safe = _make_filesystem_safe(unique_id)
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
            ts_safe = _make_filesystem_safe(timestamp)
            if is_databricks:
                await self._save_current_run_to_databricks_volume(
                    code_version.code,
                    json.dumps(meta, indent=4),
                    config,
                    unique_id,
                    timestamp
                )
            else:
                current_runs_base = Path(project_absolute_path) / CURRENT_RUNS_FOLDER
                current_runs_base.mkdir(parents=True, exist_ok=True)

                # Create directories for current runs (handles both single and multi-file)
                latest_dir = current_runs_base / "latest"
                latest_dir.mkdir(parents=True, exist_ok=True)
                
                run_dir = current_runs_base / f"run_{ts_safe}_{uid_safe}"
                run_dir.mkdir(parents=True, exist_ok=True)
                
                # Save each file in the code dict
                code_dict = code_version.code if isinstance(code_version.code, dict) else {"main.py": code_version.code}
                meta["files"] = list(code_dict.keys())  # Add file list to metadata
                
                # Save to latest/ directory
                for filename, content in code_dict.items():
                    file_path = latest_dir / filename
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(content, encoding="utf-8")
                (latest_dir / "metadata.json").write_text(json.dumps(meta, indent=4))
                
                # Save to timestamped run directory
                for filename, content in code_dict.items():
                    file_path = run_dir / filename
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(content, encoding="utf-8")
                (run_dir / "metadata.json").write_text(json.dumps(meta, indent=4))
        except Exception as e:
            logging.warning(f"Failed saving current run: {e}")


def _make_filesystem_safe(name):
    return re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", '_', name)

def get_system_info(python_path: str) -> SystemInfo:
    return SystemInfo(
        python_libraries=_get_python_libraries(python_path),
        python_version=_get_python_version(python_path),
        os=sys.platform
    )

def _get_python_libraries(python_path: str) -> list[str]:
    try:
        # Use importlib.metadata to get installed packages (works in all Python 3.8+ environments)
        python_code = """
import importlib.metadata
for dist in importlib.metadata.distributions():
    print(f"{dist.metadata['Name']}=={dist.version}")
"""
        installed_libraries = subprocess.check_output(
            [python_path, "-c", python_code],
            universal_newlines=True
        ).strip()
        return [lib.strip() for lib in installed_libraries.split("\n") if lib.strip()]
    except subprocess.CalledProcessError:
        # If that fails, return empty list
        return []


def _get_python_version(python_path: str) -> str:
    return subprocess.check_output(
        [python_path, "--version"],
        universal_newlines=True
    ).strip()


workflow_runner = WorkflowRunner()
    
