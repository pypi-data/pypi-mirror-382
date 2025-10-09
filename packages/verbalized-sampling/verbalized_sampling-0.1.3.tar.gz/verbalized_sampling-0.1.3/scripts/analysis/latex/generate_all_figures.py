#!/usr/bin/env python3
# Copyright 2025 CHATS-Lab. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Master script to generate all LaTeX figures and tables.
Runs all plotting scripts with standardized output directories.
"""

import subprocess
import sys
from pathlib import Path


def run_script(script_path, description):
    """Run a script and handle errors gracefully"""
    print(f"\n🔄 {description}")
    print(f"   Running: {script_path}")

    try:
        result = subprocess.run(
            [sys.executable, script_path], capture_output=True, text=True, check=True
        )
        print(f"✅ {description} completed successfully")
        if result.stdout:
            # Print only the summary lines, not all debug output
            for line in result.stdout.split("\n"):
                if any(marker in line for marker in ["✓", "📁", "📊", "📋", "📈", "🎉"]):
                    print(f"   {line}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"   Error: {e}")
        if e.stdout:
            print(f"   Output: {e.stdout}")
        if e.stderr:
            print(f"   Error details: {e.stderr}")
        return False


def main():
    print("🎯 LaTeX Figures Generation Pipeline")
    print("=" * 50)

    # Get the directory containing this script
    script_dir = Path(__file__).parent

    # Define all scripts to run
    scripts = [
        {
            "path": script_dir / "generate_latex_tables.py",
            "description": "Generating LaTeX tables for poem and story experiments",
        },
        {
            "path": script_dir / "generate_plots.py",
            "description": "Generating standard plots for poem and story experiments",
        },
        {
            "path": script_dir / "ablation" / "model_size_ablation.py",
            "description": "Generating model size ablation study plots",
        },
        {
            "path": script_dir / "ablation" / "plot_creative_ablation.py",
            "description": "Generating training progression ablation plots",
        },
    ]

    # Track success/failure
    results = []

    # Run each script
    for script_info in scripts:
        script_path = script_info["path"]
        description = script_info["description"]

        if not script_path.exists():
            print(f"⚠️  Script not found: {script_path}")
            results.append(False)
            continue

        success = run_script(str(script_path), description)
        results.append(success)

    # Summary
    print("\n📊 Generation Summary")
    print("=" * 30)

    successful = sum(results)
    total = len(results)

    if successful == total:
        print(f"🎉 All {total} scripts completed successfully!")
    else:
        print(f"⚠️  {successful}/{total} scripts completed successfully")
        failed_scripts = [
            scripts[i]["description"] for i, success in enumerate(results) if not success
        ]
        print(f"   Failed: {', '.join(failed_scripts)}")

    # Output directory summary
    print("\n📁 Output Directory Structure:")
    print("   latex_figures/")
    print("   ├── poem/")
    print("   │   ├── individual_models/")
    print("   │   ├── method_averages/")
    print("   │   └── model_comparisons/")
    print("   ├── story/")
    print("   │   ├── individual_models/")
    print("   │   ├── method_averages/")
    print("   │   └── model_comparisons/")
    print("   └── ablation/")
    print("       ├── model_size/")
    print("       └── training_progression/")

    # Check if output directory exists and show file count
    latex_figures_dir = Path("latex_figures")
    if latex_figures_dir.exists():
        # Count all generated files
        png_files = list(latex_figures_dir.rglob("*.png"))
        pdf_files = list(latex_figures_dir.rglob("*.pdf"))

        print("\n📈 Generated Files:")
        print(f"   PNG files: {len(png_files)}")
        print(f"   PDF files: {len(pdf_files)}")
        print(f"   Total figures: {len(png_files)}")  # PNG and PDF are same figures

        if successful == total:
            print("\n🎊 All figures ready for LaTeX inclusion!")
            print(
                "   Use \\includegraphics{latex_figures/path/to/figure.pdf} in your LaTeX document"
            )

    return successful == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
