#!/usr/bin/env python3
"""
Script to plot KPI (RMSE) progression from checkpoint JSON files.
Extracts iteration numbers and KPI values from JSON files in the checkpoints directory
and creates a clean line plot showing the progression over iterations.

Usage:
    python plot_kpi_progression.py --max-iteration 350 --title "MPPE2"
    python plot_kpi_progression.py --help
"""

import os
import json
import re
import argparse
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.dates as mdates
import numpy as np
from pathlib import Path
from datetime import datetime

def extract_iteration_from_filename(filename):
    """Extract iteration number from filename like 'best_123_explore.json'"""
    match = re.search(r'best_(\d+)_', filename)
    if match:
        return int(match.group(1))
    return None

def load_kpi_data(checkpoint_dir, max_iteration=None):
    """Load KPI data from all JSON files in the checkpoint directory"""
    data = []
    
    # Get all JSON files
    json_files = [f for f in os.listdir(checkpoint_dir) if f.endswith('.json')]
    
    for filename in json_files:
        iteration = extract_iteration_from_filename(filename)
        if iteration is None:
            continue
        
        # Filter by max iteration if specified
        if max_iteration is not None and iteration > max_iteration:
            continue
            
        filepath = os.path.join(checkpoint_dir, filename)
        try:
            # Get file creation timestamp
            file_stat = os.stat(filepath)
            timestamp = datetime.fromtimestamp(file_stat.st_mtime)
            
            with open(filepath, 'r') as f:
                json_data = json.load(f)
                kpi = json_data.get('kpi')
                if kpi is not None:
                    # Smart KPI processing: always make values positive for better interpretation
                    processed_kpi = abs(kpi)  # This ensures all values are positive
                    
                    data.append((iteration, processed_kpi, timestamp))
        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            print(f"Warning: Could not process {filename}: {e}")
            continue
    
    return data

def create_plot(data, title="KPI Progression Over Iterations", kpi_label="RMSE", output_path=None):
    """Create a clean line plot of iteration vs KPI with custom styling"""
    if not data:
        print("No data to plot!")
        return
    
    # Sort by iteration
    data.sort(key=lambda x: x[0])
    
    iterations = [point[0] for point in data]
    kpi_values = [point[1] for point in data]
    timestamps = [point[2] for point in data] if len(data[0]) > 2 else None
    
    # Convert timestamps to relative time (starting from 0)
    if timestamps:
        start_time = min(timestamps)
        relative_times = [(ts - start_time).total_seconds() / 3600 for ts in timestamps]  # Convert to hours
    
    # Set up Montserrat font using direct file path
    try:
        # Use the known Montserrat Regular font path
        montserrat_path = '/usr/share/fonts/truetype/montserrat/Montserrat-Regular.ttf'
        
        if os.path.exists(montserrat_path):
            montserrat = fm.FontProperties(fname=montserrat_path)
            # print("✅ Using Montserrat font successfully from system fonts!")
        else:
            # Fallback: try to find any Montserrat Regular font
            font_path = None
            for font in fm.findSystemFonts():
                if 'montserrat' in font.lower() and ('Regular' in font or 'regular' in font.lower()):
                    font_path = font
                    break
            
            if font_path:
                montserrat = fm.FontProperties(fname=font_path)
                # print(f"✅ Using Montserrat font from: {font_path}")
            else:
                # Last resort: try family name
                montserrat = fm.FontProperties(family='DejaVu Sans')
                # print("⚠️ Montserrat not found, using DejaVu Sans as fallback")
                
    except Exception as e:
        montserrat = fm.FontProperties(family='DejaVu Sans')
        # print(f"⚠️ Font setup error: {e}, using DejaVu Sans as fallback")
    
    # Create the plot with dual x-axis
    fig, ax1 = plt.subplots(figsize=(14, 9))
    
    # Plot the main data on primary axis (iterations)
    line = ax1.plot(iterations, kpi_values, 'o-', color='#2d3ddbff', linewidth=2, markersize=4, alpha=0.8)
    
    # Customize primary axis (iterations)
    ax1.set_xlabel('Iteration', fontsize=14, fontproperties=montserrat, color='black')
    ax1.set_ylabel(f'{kpi_label} (KPI)', fontsize=14, fontproperties=montserrat, color='black')
    ax1.grid(True, alpha=0.3)
    
    # Set font for primary axis tick labels
    ax1.tick_params(axis='both', which='major', labelsize=12, colors='black')
    for label in ax1.get_xticklabels() + ax1.get_yticklabels():
        label.set_fontproperties(montserrat)
        label.set_color('black')
    
    # Create secondary x-axis for relative timestamps if available
    if timestamps:
        ax2 = ax1.twiny()  # Create a second x-axis that shares the same y-axis
        
        # Plot invisible line to set up the time axis with relative times
        ax2.plot(relative_times, kpi_values, alpha=0)
        
        # Format the time axis for relative hours
        max_hours = max(relative_times)
        if max_hours < 2:
            # For short durations, show in minutes
            relative_minutes = [rt * 60 for rt in relative_times]
            ax2.clear()
            ax2.plot(relative_minutes, kpi_values, alpha=0)
            ax2.set_xlabel('Elapsed Time (minutes)', fontsize=14, fontproperties=montserrat, color='black')
            ax2.tick_params(axis='x', which='major', labelsize=11, rotation=45, colors='black')
            
            # Format minutes nicely
            ax2.xaxis.set_major_locator(plt.MaxNLocator(nbins=8))
            ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.0f}m'))
        else:
            # For longer durations, show in hours
            ax2.set_xlabel('Elapsed Time (hours)', fontsize=14, fontproperties=montserrat, color='black')
            ax2.tick_params(axis='x', which='major', labelsize=11, rotation=45, colors='black')
            
            # Format hours nicely
            ax2.xaxis.set_major_locator(plt.MaxNLocator(nbins=8))
            ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1f}h'))
        
        # Set font for secondary axis tick labels
        for label in ax2.get_xticklabels():
            label.set_fontproperties(montserrat)
            label.set_color('black')
        
        # Add duration information
        min_time = min(timestamps)
        max_time = max(timestamps)
        duration = max_time - min_time
        start_date = min_time.strftime('%Y-%m-%d %H:%M')
        time_info = f"Started: {start_date} | Total Duration: {duration}"
        plt.figtext(0.02, 0.02, time_info, fontsize=10, fontproperties=montserrat, color='black', alpha=0.8)
    
    # Add larger title positioned higher
    plt.suptitle(title, fontsize=20, fontweight='bold', fontproperties=montserrat, y=0.98, color='black')
    
    # Add baseline annotation to the starting point
    if iterations and kpi_values:
        baseline_kpi = kpi_values[0]  # First KPI value
        baseline_iteration = iterations[0]  # First iteration (should be 0)
        
        # Add annotation for baseline
        ax1.annotate('Baseline', 
                    xy=(baseline_iteration, baseline_kpi), 
                    xytext=(baseline_iteration + max(iterations) * 0.1, baseline_kpi + (max(kpi_values) - min(kpi_values)) * 0.1),
                    arrowprops=dict(arrowstyle='->', color='#666666', alpha=0.8, lw=1.5),
                    fontsize=12, 
                    fontproperties=montserrat,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='#666666', alpha=0.9),
                    color='black')
    
    # Add some statistics to the plot
    best_kpi = min(kpi_values) if kpi_label != "Loss" else min(kpi_values)  # Assuming lower is better
    best_iteration = iterations[kpi_values.index(best_kpi)]
    
    ax1.axhline(y=best_kpi, color='red', linestyle='--', alpha=0.7, 
                label=f'Best {kpi_label}: {best_kpi:.4f} (Iteration {best_iteration})')
    ax1.legend(prop=montserrat, loc='upper right')
    
    # Improve layout
    plt.tight_layout()
    
    # Save or show the plot
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {output_path}")
    else:
        plt.show()
    
    # Print some statistics
    print(f"\nStatistics:")
    print(f"Total iterations: {len(data)}")
    print(f"Iteration range: {min(iterations)} to {max(iterations)}")
    print(f"{kpi_label} range: {min(kpi_values):.4f} to {max(kpi_values):.4f}")
    print(f"Best {kpi_label}: {best_kpi:.4f} at iteration {best_iteration}")
    
    if timestamps:
        print(f"Time range: {min_time.strftime('%Y-%m-%d %H:%M:%S')} to {max_time.strftime('%Y-%m-%d %H:%M:%S')}")
        duration = max_time - min_time
        print(f"Total duration: {duration}")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Plot KPI (RMSE) progression from checkpoint JSON files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python plot_kpi_progression.py --max-iteration 350 --title "MPPE2" --kpi-label "RMSE"
  python plot_kpi_progression.py -c /path/to/checkpoints -t "My Experiment" -k "Loss"
  python plot_kpi_progression.py -c /home/user/MPPE1/checkpoints -m 500 -t "MPPE1" -k "MAE"
  python plot_kpi_progression.py  # Use all data with default settings (auto-converts negatives to positive)
        """
    )
    
    parser.add_argument(
        '--max-iteration', '-m',
        type=int,
        default=None,
        help='Maximum iteration to include in the plot (default: include all iterations)'
    )
    
    parser.add_argument(
        '--title', '-t',
        type=str,
        default='RMSE Progression Over Iterations',
        help='Title for the plot (default: "RMSE Progression Over Iterations")'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Output file path for the plot (default: auto-generated based on parameters)'
    )
    
    parser.add_argument(
        '--checkpoints-dir', '-c',
        type=str,
        default='/home/ozkilim/MPPE/MPPE2/co_datascientist_checkpoints',
        help='Directory containing the checkpoint JSON files (default: /home/ozkilim/MPPE/MPPE2/co_datascientist_checkpoints)'
    )
    
    parser.add_argument(
        '--kpi-label', '-k',
        type=str,
        default='RMSE',
        help='Label for the KPI metric (default: "RMSE")'
    )
    
    
    return parser.parse_args()

def main():
    """Main function to run the plotting script"""
    args = parse_arguments()
    
    # Use the provided checkpoint directory
    checkpoint_dir = args.checkpoints_dir
    
    if not os.path.exists(checkpoint_dir):
        print(f"Error: Checkpoint directory not found: {checkpoint_dir}")
        return
    
    print(f"Loading KPI data from: {checkpoint_dir}")
    if args.max_iteration:
        print(f"Limiting to iterations <= {args.max_iteration}")
    # print("✅ Auto-converting negative KPI values to positive for better visualization")
    
    data = load_kpi_data(checkpoint_dir, args.max_iteration)
    
    if not data:
        print("No valid data found in JSON files!")
        return
    
    print(f"Found {len(data)} data points")
    
    # Generate output filename if not provided
    if args.output is None:
        base_name = "kpi_progression"
        if args.max_iteration:
            base_name += f"_max{args.max_iteration}"
        # Clean title for filename
        title_clean = "".join(c for c in args.title if c.isalnum() or c in (' ', '-', '_')).strip()
        title_clean = title_clean.replace(' ', '_').lower()
        if title_clean and title_clean != "rmse_progression_over_iterations":
            base_name += f"_{title_clean}"
        output_path = f"/home/ozkilim/MPPE/{base_name}_plot.png"
    else:
        output_path = args.output
    
    # Create the plot
    create_plot(data, args.title, args.kpi_label, output_path)

if __name__ == "__main__":
    main()
