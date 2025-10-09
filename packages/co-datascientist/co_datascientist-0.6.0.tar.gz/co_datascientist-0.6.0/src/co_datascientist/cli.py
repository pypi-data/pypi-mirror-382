import asyncio
import logging
import sys
from pathlib import Path

import click
from yaspin import yaspin
import yaml
from . import co_datascientist_api, mcp_local_server
from .settings import settings
from .workflow_runner import workflow_runner
from .cloud_utils.databricks_utils import get_code_from_databricks_config
from .plotting.plot_kpi_progression import main as plot_kpi_main, parse_arguments as plot_kpi_parse_args
from .plotting.python_diff_pdf_simple import SimpleDiffPDFGenerator
from .project_packager import package_project





def ensure_keyring_works():
    """
    Ensure that keyring backend works; fall back to plaintext file if not.
    """
    try:
        import keyring
        test_service = "test_service"
        test_username = "test_user"
        test_password = "test_password"
        keyring.set_password(test_service, test_username, test_password)
        retrieved = keyring.get_password(test_service, test_username)
        keyring.delete_password(test_service, test_username)
        if retrieved == test_password:
            return
    except Exception:
        pass
    try:
        import keyring
        import keyrings.alt.file
        keyring.set_keyring(keyrings.alt.file.PlaintextKeyring())
        click.echo("Using file-based keyring for secure storage")
    except ImportError:
        click.echo("Please install keyrings.alt: pip install keyrings.alt")
        sys.exit(1)


def print_section_header(title: str):
    click.echo(f"\n{title}")
    click.echo("─" * len(title))


def print_success(message: str):
    click.echo(f"SUCCESS: {message}")


def print_info(message: str):
    click.echo(f"INFO: {message}")


def print_warning(message: str):
    click.echo(f"WARNING: {message}")


def print_error(message: str):
    click.echo(f"ERROR: {message}")


def print_logo():
    """Print the awesome Tropiflo ASCII logo in blue with tagline"""
    # Use print() instead of click.echo() to preserve ANSI colors
    BLUE = '\033[94m'
    RESET = '\033[0m'

    print(f"""
{BLUE}$$$$$$$$\\                            $$\\  $$$$$$\\  $$\\           
\\__$$  __|                           \\__|$$  __$$\\ $$ |          
   $$ | $$$$$$\\   $$$$$$\\   $$$$$$\\  $$\\ $$ /  \\__|$$ | $$$$$$\\  
   $$ |$$  __$$\\ $$  __$$\\ $$  __$$\\ $$ |$$$$\\     $$ |$$  __$$\\ 
   $$ |$$ |  \\__|$$ /  $$ |$$ /  $$ |$$ |$$  _|    $$ |$$ /  $$ |
   $$ |$$ |      $$ |  $$ |$$ |  $$ |$$ |$$ |      $$ |$$ |  $$ |
   $$ |$$ |      \\$$$$$$  |$$$$$$$  |$$ |$$ |      $$ |\\$$$$$$  |
   \\__|\\__|       \\______/ $$  ____/ \\__|\\__|      \\__| \\______/ 
                           $$ |                                  
                           $$ |                                  
                           \\__|{RESET}

{BLUE}>{RESET} lets explore this problem!""")


@click.group()
@click.option('--reset-openai-key', is_flag=True, help='Reset the OpenAI API key')
@click.pass_context
def main(ctx, reset_openai_key: bool):
    """Co-DataScientist: AI-Powered Code Evolution for ML & Data Science
    
    Automatically evolves your Python code to maximize KPIs through intelligent
    hypothesis-driven optimization. Works with both single files and multi-file projects.
    
    Getting Started:
        1. co-datascientist set-token --token YOUR_TOKEN
        2. co-datascientist run --script-path your_project/
        3. co-datascientist deploy co_datascientist_checkpoints/best_X/
    
    Core Commands:
        run         - Evolve your code to maximize KPIs
        deploy      - Deploy optimized checkpoints to production
        status      - Check your usage and API status
    
    Analysis Tools:
        plot-kpi    - Visualize KPI progression over time
        diff-pdf    - Generate beautiful code comparison PDFs
    
    Setup:
        set-token   - Configure your API key
        openai-key  - Add OpenAI key for unlimited usage
    
    Use 'co-datascientist COMMAND --help' for detailed info on any command.
    """
    # Initialize keyring and logging
    ensure_keyring_works()
    logging.basicConfig(level=settings.log_level)
    logging.info(f"settings: {settings.model_dump()}")

    print_logo()

    # Reset OpenAI key if requested
    if reset_openai_key:
        settings.delete_openai_key()
        print_success("OpenAI key removed. Using free tier.")

    # Ensure API key exists for all commands except token management
    if ctx.invoked_subcommand not in ('set-token', 'openai-key'):
        try:
            settings.get_api_key()
            if not settings.api_key or not settings.api_key.get_secret_value():
                print_error("No API key found. Please run 'set-token' to configure your API key.")
                sys.exit(1)
        except Exception as e:
            print_error(f"Error loading API key: {e}")
            sys.exit(1)


@main.command()
def mcp_server():
    """Start the local MCP server for IDE integration
    
    Enables integration with IDEs that support the Model Context Protocol (MCP).
    This allows Co-DataScientist to be used directly from your editor.
    """
    print_section_header("MCP Server")
    print_info("Starting MCP server... Press Ctrl+C to exit.")
    asyncio.run(mcp_local_server.run_mcp_server())
 

@main.command()
@click.option('--token', required=False, help='Your API key (if not provided, you will be prompted)')
def set_token(token):
    """Set your Co-DataScientist API key (required for first use)
    
    Get your API token from your Co-DataScientist account dashboard.
    This only needs to be done once - the key is securely stored.
    
    Example:
        co-datascientist set-token --token YOUR_TOKEN_HERE
    """
    from pydantic import SecretStr

    print_section_header("Set API Key")
    if not token:
        # import ipdb; ipdb.set_trace()
        token = click.prompt("Please enter your API key", hide_input=True)
    if not token:
        print_error("No API key provided. Aborting.")
        return

    settings.api_key = SecretStr(token)
    try:
        asyncio.run(co_datascientist_api.test_connection())
        print_success("Token validated successfully!")
    except Exception as e:
        print_error(f"Token validation failed: {e}")
        return

    try:
        import keyring
        keyring.set_password(settings.service_name, "user", token)
        print_success("API key saved and will be remembered between sessions!")
    except Exception as e:
        print_error(f"Failed to save API key: {e}")
        print_info("You can set the CO_DATASCIENTIST_API_KEY environment variable for persistence.")


@main.command(context_settings=dict(
    ignore_unknown_options=True,
))

# The idea is that we auto detect everything fdrom the working dir for the most simple usage and then if the stuff we need is not found then we tell the user to define it 

@click.argument('command', nargs=-1, type=click.UNPROCESSED, required=False)
@click.option('--working-directory', 'working_directory', required=False, type=click.Path(exists=True), default='.', show_default=True, help='Path to python file or directory to improve (defaults to current directory)')
### Cloud config should have just the devops stuff not the running docker file...
@click.option('--cloud-config', required=False, type=click.Path(exists=True), help='Path to cloud config file (mutually exclusive with --script-path)')
# @click.option('--python-path', required=False, type=click.Path(), default=sys.executable, show_default=True, help='Path to the python interpreter to use')
@click.option('--parallel', required=False, type=int, default=1, show_default=True, help='Number of code versions to run concurrently')
# @click.option('--run-command', required=False, type=str, help='Custom command to run the project (e.g., "bash run.sh")')
@click.option('--use-cached-qa', is_flag=True, help='Use cached Q&A answers instead of prompting (implies preflight enabled)')
# @click.option('--dockerfile', required=False, type=click.Path(), help='Path to your Dockerfile everything will now be docker based execution.')






def run(command, working_directory, parallel, cloud_config, use_cached_qa):
    """Evolve your code to maximize KPIs through AI-powered optimization
    
    Results are saved in:
    - co_datascientist_checkpoints/ (best versions only)
    - current_runs/ (all executed versions)
    """
    
    # Load cloud config from YAML file if provided
    config_dict = {}
    if cloud_config:
        print_info(f"Loading cloud config from: {cloud_config}")
        with open(cloud_config, 'r') as file:
            config_dict = yaml.safe_load(file)
        
        # Validate that it contains a recognized cloud platform
        if 'gcloud' in config_dict:
            print_info(f"Using GCloud executor with project: {config_dict['gcloud'].get('project_id')}")
        elif 'aws' in config_dict:
            print_info(f"Using AWS executor")
        elif 'databricks' in config_dict:
            print_info(f"Using Databricks executor")
        else:
            print_error("Cloud config must contain 'gcloud', 'aws', or 'databricks' configuration. Aborting.")
            return
    else:
        print_info("No cloud config provided, using local executor")
        
    click.echo()
    spinner = None
    asyncio.run(
        workflow_runner.run_workflow(
            working_directory, 
            {**config_dict, 'parallel': max(1, int(parallel or 1)), 'use_cached_qa': use_cached_qa},
            spinner, 
        )
        )
        # click.echo()
    # except Exception as e:
    #     msg = str(e)
        
    #     # Handle specific error cases with clean messages
    #     if "Unauthorized" in msg or "401" in msg:
    #         print_error("Authentication failed. Please run 'set-token' again.")
    #     else: 
    #         print_error(msg)
        

def _costs_disabled():
    return None


@main.command()
def status():
    """Show current usage status and API health
    
    Displays:
    - API connection status
    - Current usage statistics
    - OpenAI key configuration (if set)
    
    Example:
        co-datascientist status
    """
    try:
        with yaspin(text="Checking status...", color="yellow") as spinner:
            status = asyncio.run(co_datascientist_api.get_user_usage_status())
        print_section_header("Usage Status")
    except Exception as e:
        msg = str(e)
        if "Unauthorized" in msg or "401" in msg:
            print_error("Authentication failed. Please run 'set-token' again.")
        else:
            print_error(f"Error fetching status: {e}")


@main.command()
@click.option('--remove', is_flag=True, help='Remove stored OpenAI key')
def openai_key(remove):
    """Manage your OpenAI API key for unlimited usage
    
    Add your own OpenAI key to bypass Co-DataScientist usage limits.
    With your own key, you have unlimited code evolution runs.
    
    Examples:
        # Add OpenAI key
        co-datascientist openai-key
        
        # Remove OpenAI key (revert to Co-DataScientist limits)
        co-datascientist openai-key --remove
    """
    print_section_header("OpenAI Key Management")
    if remove:
        settings.delete_openai_key()
        print_success("OpenAI key removed. Using free tier.")
    else:
        current = settings.get_openai_key(prompt_if_missing=False)
        if current:
            print_success("OpenAI key is currently configured.")
            print_info("Your requests use your OpenAI account for unlimited usage.")
            print_info("Use '--remove' flag to switch back to free tier.")
        else:
            print_info("No OpenAI key configured. Using free tier.")
            settings.get_openai_key(prompt_if_missing=True)


@main.command()
@click.option('--checkpoints-dir', '-c', required=True, type=click.Path(exists=True), 
              help='Directory containing the checkpoint JSON files')
@click.option('--max-iteration', '-m', type=int, default=None,
              help='Maximum iteration to include in the plot (default: include all iterations)')
@click.option('--title', '-t', type=str, default='RMSE Progression Over Iterations',
              help='Title for the plot')
@click.option('--output', '-o', type=str, default=None,
              help='Output file path for the plot (default: auto-generated based on parameters)')
@click.option('--kpi-label', '-k', type=str, default='RMSE',
              help='Label for the KPI metric (default: "RMSE")')
def plot_kpi(checkpoints_dir, max_iteration, title, output, kpi_label):
    """Generate visualization of KPI progression over evolution generations
    
    Creates a line plot showing how your KPI improved across iterations.
    Reads metadata.json files from checkpoint directories.
    
    Examples:
        # Basic usage
        co-datascientist plot-kpi -c co_datascientist_checkpoints/
        
        # Custom title and KPI label
        co-datascientist plot-kpi -c checkpoints/ --title "Model Accuracy" --kpi-label "Accuracy"
        
        # Limit to first 100 iterations
        co-datascientist plot-kpi -c checkpoints/ --max-iteration 100
        
        # Custom output file
        co-datascientist plot-kpi -c checkpoints/ --output my_progress.png
    """
    print_section_header("KPI Progression Plot")
    
    try:
        # Import the plotting functions
        from .plotting.plot_kpi_progression import load_kpi_data, create_plot
        import os
        
        # Validate checkpoint directory
        if not os.path.exists(checkpoints_dir):
            print_error(f"Checkpoint directory not found: {checkpoints_dir}")
            return
        
        print_info(f"Loading KPI data from: {checkpoints_dir}")
        if max_iteration:
            print_info(f"Limiting to iterations <= {max_iteration}")
        print_info("Auto-converting negative KPI values to positive for better visualization")
        
        # Load data
        data = load_kpi_data(checkpoints_dir, max_iteration)
        
        if not data:
            print_error("No valid data found in JSON files!")
            return
        
        print_info(f"Found {len(data)} data points")
        
        # Generate output filename if not provided
        if output is None:
            base_name = "kpi_progression"
            if max_iteration:
                base_name += f"_max{max_iteration}"
            # Clean title for filename
            title_clean = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
            title_clean = title_clean.replace(' ', '_').lower()
            if title_clean and title_clean != "rmse_progression_over_iterations":
                base_name += f"_{title_clean}"
            output_path = f"{base_name}_plot.png"
        else:
            output_path = output
        
        # Create the plot
        create_plot(data, title, kpi_label, output_path)
        print_success(f"KPI progression plot saved to: {output_path}")
        
    except Exception as e:
        print_error(f"Error creating KPI plot: {e}")


@main.command()
@click.argument('file1', type=click.Path(exists=True))
@click.argument('file2', type=click.Path(exists=True))
@click.option('--output', '-o', type=str, default=None,
              help='Output PDF file path (default: auto-generated from title)')
@click.option('--title', '-t', type=str, default='Beautiful Python Diff',
              help='Custom title for the diff report')
def diff_pdf(file1, file2, output, title):
    """Generate professional PDF comparison report between two code versions
    
    Creates a side-by-side diff visualization highlighting changes.
    Perfect for documentation, presentations, or code reviews.
    
    Examples:
        # Compare baseline with optimized version
        co-datascientist diff-pdf baseline.py optimized.py
        
        # Custom output filename
        co-datascientist diff-pdf old.py new.py --output improvements.pdf
        
        # Custom title for the report
        co-datascientist diff-pdf v1.py v2.py --title "XOR Optimization Results"
        
        # Compare checkpoints
        co-datascientist diff-pdf \\
            co_datascientist_checkpoints/best_0_baseline/model.py \\
            co_datascientist_checkpoints/best_6_explore/model.py \\
            --title "Model Evolution" --output model_diff.pdf
    """
    print_section_header("Python Diff PDF Generator")
    
    try:
        # Validate files exist
        file1_path = Path(file1)
        file2_path = Path(file2)
        
        if not file1_path.exists():
            print_error(f"File '{file1}' not found")
            return
        
        if not file2_path.exists():
            print_error(f"File '{file2}' not found")
            return
        
        print_info(f"Comparing files:")
        print_info(f"   Baseline: {file1}")
        print_info(f"   Modified: {file2}")
        print_info(f"Generating beautiful PDF diff...")
        
        # Create diff
        generator = SimpleDiffPDFGenerator()
        output_path = generator.create_pdf_diff(str(file1_path), str(file2_path), output, title)
        
        print_success(f"PDF diff saved as '{output_path}'")
        
    except Exception as e:
        print_error(f"Error creating PDF diff: {e}")


@main.command()
@click.argument('checkpoint_path', type=click.Path(exists=True))
@click.option('--original-path', '-p', type=click.Path(exists=True), default=None,
              help='Path to original project directory (auto-detected if not provided)')
@click.option('--output-dir', '-o', type=str, default=None,
              help='Custom output directory name (auto-generated if not provided)')
def deploy(checkpoint_path, original_path, output_dir):
    """Deploy a checkpoint as a complete, runnable project
    
    Takes a checkpoint directory (e.g., co_datascientist_checkpoints/best_6_explore/)
    and creates a full copy of your project with the evolved code integrated.
    
    Examples:
    
        # Basic usage - auto-detect original project
        co-datascientist deploy co_datascientist_checkpoints/best_6_explore/
        
        # Specify original project location
        co-datascientist deploy best_6_explore/ --original-path /path/to/my_project
        
        # Custom output directory name
        co-datascientist deploy best_6_explore/ --output-dir my_optimized_pipeline
    """
    import shutil
    import json
    from datetime import datetime
    
    print_section_header("Deploy Checkpoint")
    
    try:
        checkpoint_path = Path(checkpoint_path).resolve()
        
        # Validate checkpoint directory
        if not checkpoint_path.is_dir():
            print_error(f"Checkpoint path must be a directory: {checkpoint_path}")
            return
        
        metadata_path = checkpoint_path / "metadata.json"
        if not metadata_path.exists():
            print_error(f"No metadata.json found in checkpoint: {checkpoint_path}")
            print_info("Make sure you're pointing to a checkpoint directory like 'best_6_explore/'")
            return
        
        # Load metadata
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        files_in_checkpoint = metadata.get('files', [])
        checkpoint_name = checkpoint_path.name
        kpi = metadata.get('kpi', 'unknown')
        
        print_info(f"📦 Checkpoint: {checkpoint_name}")
        print_info(f"📊 KPI: {kpi}")
        print_info(f"📄 Files: {', '.join(files_in_checkpoint)}")
        
        # Determine original project path
        if original_path:
            original_path = Path(original_path).resolve()
        else:
            # Try to auto-detect: go up from checkpoint to find project root
            # checkpoint is typically in: project/co_datascientist_checkpoints/best_X/
            if checkpoint_path.parent.name == "co_datascientist_checkpoints":
                original_path = checkpoint_path.parent.parent
                print_info(f"🔍 Auto-detected original project: {original_path}")
            else:
                print_error("Could not auto-detect original project path.")
                print_info("Please specify with --original-path")
                return
        
        if not original_path.exists():
            print_error(f"Original project path not found: {original_path}")
            return
        
        # Determine output directory name
        if output_dir:
            output_path = Path(output_dir).resolve()
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            project_name = original_path.name
            output_path = original_path.parent / f"{project_name}_deployed_{checkpoint_name}_{timestamp}"
        
        # Check if output already exists
        if output_path.exists():
            print_error(f"Output directory already exists: {output_path}")
            if not click.confirm("Overwrite?"):
                print_info("Deployment cancelled.")
                return
            shutil.rmtree(output_path)
        
        print_info(f"🚀 Deploying to: {output_path}")
        
        # Copy entire original project
        print_info("📋 Copying original project...")
        shutil.copytree(original_path, output_path, 
                       ignore=shutil.ignore_patterns(
                           'co_datascientist_checkpoints', 
                           'current_runs',
                           'qa_cache.json',
                           '__pycache__',
                           '*.pyc',
                           '.git'
                       ))
        
        # Overwrite with checkpoint files
        print_info("✨ Integrating evolved code...")
        for filename in files_in_checkpoint:
            src_file = checkpoint_path / filename
            dst_file = output_path / filename
            
            if src_file.exists():
                # Create parent directories if needed
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dst_file)
                print_info(f"   ✓ {filename}")
            else:
                print_error(f"   ✗ {filename} (not found in checkpoint)")
        
        # Copy metadata for reference
        shutil.copy2(metadata_path, output_path / "deployment_info.json")
        
        print_success(f"\n✅ Deployment complete!")
        print_success(f"📁 Location: {output_path}")
        print_info(f"\nTo test your deployed project:")
        print_info(f"   cd {output_path}")
        
        # Try to detect run command from project
        if (output_path / "run.sh").exists():
            print_info(f"   bash run.sh")
        elif (output_path / "main.py").exists():
            print_info(f"   python main.py")
        else:
            print_info(f"   <your run command>")
        
    except Exception as e:
        print_error(f"Error deploying checkpoint: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
