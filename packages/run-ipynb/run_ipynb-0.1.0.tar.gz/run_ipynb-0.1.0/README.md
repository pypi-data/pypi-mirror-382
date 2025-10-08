### run-ipynb

Run Jupyter notebooks as plain Python scripts from the command line.

This tool converts a `.ipynb` to `.py`, removes IPython-only lines, ensures a non-interactive Matplotlib backend, optionally adjusts `sys.path` when `os.chdir(...)` is used, executes the script, and cleans up the generated file by default.

## Installation

- **Requirements**: Python >= 3.7

Install directly from Git using pip:

```bash
# HTTPS
pip install "git+https://github.com/dschaub95/run-ipynb"
```

After installation, a CLI named `run-ipynb` will be available.

## Usage

```bash
run-ipynb path/to/notebook.ipynb [--keep] [--yes]
```

- **notebook_path**: Path to the `.ipynb` notebook to run
- **-k, --keep**: Keep the generated `.py` file after execution
- **-y, --yes**: Automatically overwrite an existing `.py` file without prompting

### Examples

```bash
# Basic: convert, run, and remove the temporary .py file
run-ipynb notebooks/analysis.ipynb

# Keep the .py file for inspection and overwrite if it already exists
run-ipynb notebooks/analysis.ipynb --keep --yes
```

### What it does

- Converts the notebook with `jupyter nbconvert --to script`
- Removes `get_ipython().run_line_magic` lines
- Sets Matplotlib backend to `Agg` for headless environments
- If `os.chdir(...)` is detected, appends `os.getcwd()` to `sys.path` right after the change
- Executes the resulting script with your current Python interpreter
- Deletes the generated `.py` file unless `--keep` is passed

## Notes

- `jupyter` is installed as a dependency and must be available on your `PATH` for `nbconvert` to work.

