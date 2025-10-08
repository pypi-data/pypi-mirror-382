import argparse
import os
import sys
import subprocess


def main():
    parser = argparse.ArgumentParser(
        description="Run Jupyter notebooks as Python scripts"
    )
    parser.add_argument("notebook_path", help="Path to the notebook file")
    parser.add_argument(
        "-k",
        "--keep",
        action="store_true",
        help="Keep the generated Python script after execution",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Automatically overwrite existing Python file without asking",
    )
    args = parser.parse_args()

    notebook_path = args.notebook_path
    python_file = notebook_path.replace(".ipynb", ".py")

    # Check if file exists and handle overwrite
    if os.path.exists(python_file) and not args.yes:
        response = input(f"{python_file} already exists. Overwrite? [y/N] ").lower()
        if response != "y":
            print("Operation cancelled.")
            sys.exit(0)

    print(f"Converting {notebook_path} to script...")
    subprocess.run(
        ["jupyter", "nbconvert", "--to", "script", notebook_path], check=True
    )

    if os.path.exists(python_file):
        print(f"Notebook successfully converted to {python_file}")

        # Remove unwanted lines
        with open(python_file, "r") as f:
            lines = f.readlines()
        with open(python_file, "w") as f:
            # Add matplotlib backend configuration at the start
            f.write("try:\n")
            f.write("    import matplotlib\n")
            f.write("    matplotlib.use('Agg')\n")
            f.write("except ImportError:\n")
            f.write("    pass\n\n")

            for line in lines:
                if "get_ipython().run_line_magic" not in line:
                    f.write(line)

        # Add sys.path if os.chdir is present
        with open(python_file, "r") as f:
            content = f.read()
        if "os.chdir(" in content:
            with open(python_file, "w") as f:
                lines = content.split("\n")
                for line in lines:
                    f.write(line + "\n")
                    if "os.chdir(" in line:
                        f.write("import sys\n")
                        f.write("sys.path.append(os.getcwd())\n")

        # Run the Python script
        subprocess.run([sys.executable, python_file], check=True)

        # Keep file only if requested
        if not args.keep:
            os.remove(python_file)
            print("Cleaned up temporary script file")
    else:
        print("Failed to convert notebook.")
        sys.exit(1)


if __name__ == "__main__":
    main()
