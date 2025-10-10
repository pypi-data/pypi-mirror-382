import argparse
import os
import shutil
import subprocess
import sys


def resolve_python_from_path(path_candidate):
    if not path_candidate:
        return None

    path_candidate = str(path_candidate)

    if path_candidate.endswith("python") or path_candidate.endswith("python.exe"):
        if os.path.exists(path_candidate) and os.access(path_candidate, os.X_OK):
            return path_candidate
        return None

    candidates = [
        os.path.join(path_candidate, "bin", "python"),
        os.path.join(path_candidate, "Scripts", "python"),
        os.path.join(path_candidate, "Scripts", "python.exe"),
        os.path.join(path_candidate, "python"),
        os.path.join(path_candidate, "python.exe"),
    ]
    for candidate in candidates:
        if os.path.exists(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


def resolve_python_executable(args):
    explicit = args.python_executable or os.environ.get("RUN_IPYNB_PYTHON")
    if explicit:
        return explicit

    env_root_vars = []

    conda_prefix = os.environ.get("CONDA_PREFIX") or os.environ.get("MAMBA_PREFIX")
    conda_prefixes = []
    if conda_prefix:
        conda_prefixes.append(conda_prefix)
    i = 1
    while True:
        stacked = os.environ.get(f"CONDA_PREFIX_{i}")
        if not stacked:
            break
        conda_prefixes.append(stacked)
        i += 1

    env_root_vars.extend(conda_prefixes)

    env_root_vars.extend(
        filter(
            None,
            [
                os.environ.get("PYENV_VIRTUAL_ENV"),
                os.environ.get("PIPENV_VENV"),
                os.environ.get("PDM_VENV_PATH"),
                os.environ.get("POETRY_VIRTUAL_ENV"),
                os.environ.get("RYE_ENV"),
                os.environ.get("VIRTUAL_ENV"),
            ],
        )
    )

    for env_root in env_root_vars:
        resolved = resolve_python_from_path(env_root)
        if resolved:
            return resolved

    interpreter_vars = [
        os.environ.get("RUN_IPYNB_ENV_PYTHON"),
        os.environ.get("CONDA_PYTHON_EXE"),
        os.environ.get("PYENV_PYTHON"),
        os.environ.get("PIPENV_RUNTIME"),
        os.environ.get("PIPENV_DEFAULT_PYTHON"),
        os.environ.get("PDM_PYTHON"),
        os.environ.get("POETRY_PYTHON"),
        os.environ.get("RYE_PYTHON"),
        os.environ.get("HATCH_PYTHON"),
    ]

    for candidate in interpreter_vars:
        resolved = resolve_python_from_path(candidate)
        if resolved:
            return resolved

    python_from_path = shutil.which("python")
    if python_from_path:
        return python_from_path

    return sys.executable


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
    parser.add_argument(
        "-p",
        "--python",
        dest="python_executable",
        help="Path to the Python interpreter that should run the converted script (defaults to the current interpreter)",
    )
    args = parser.parse_args()

    notebook_path = args.notebook_path
    python_file = notebook_path.replace(".ipynb", ".py")

    python_executable = resolve_python_executable(args)
    print(f"Using Python executable: {python_executable}")

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
        subprocess.run([python_executable, python_file], check=True)

        # Keep file only if requested
        if not args.keep:
            os.remove(python_file)
            print("Cleaned up temporary script file")
    else:
        print("Failed to convert notebook.")
        sys.exit(1)


if __name__ == "__main__":
    main()
