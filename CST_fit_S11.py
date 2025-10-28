import sys, subprocess, json
from cst.interface import get_current_project
import cst.results
from pathlib import Path
import numpy as np
import csv
from datetime import datetime

project = get_current_project()

# filepaths
results_path = Path(project.filename()).with_suffix('')
export_file = results_path / "S11_temp.txt"
fit_results_file = results_path / "fit_results_temp.json"
results_log = results_path / "fit_results_log.csv"
fitting_script = Path(__file__).parent / "fit_S11.py"

# save S11 results
project_file = cst.results.ProjectFile(project.filename(), allow_interactive=True)
s11 = project_file.get_3d().get_result_item(r"1D Results\S-Parameters\S1,1")
np.savetxt(
    export_file, 
    np.column_stack([np.real(s11.get_xdata()), np.real(s11.get_ydata()), np.imag(s11.get_ydata())]), 
    header="Frequency (Hz)   Re(S11)   Im(S11)"
)

# curve fitting must be run in a separate process to avoid libiomp5md.dll conficts
cmd = [sys.executable, str(fitting_script), str(export_file), str(fit_results_file)]
subprocess.run(cmd, check=True)

try:
    with open(fit_results_file, 'r') as f:
        fit_results = json.load(f)
except FileNotFoundError:
    sys.exit(f"Error: fit results not found")

Qi = fit_results["Qi"]
Qc = fit_results["Qc"]
Ql = fit_results["Ql"]
fr = fit_results["fr"]
print(f"fr = {fr}, Qi = {Qi}, Qc = {Qc}, Ql = {Ql}")

# save results to log
parameters = s11.get_parameter_combination()

fit_keys = fit_results.keys()
param_keys = parameters.keys()
fieldnames = list(fit_keys) + list(param_keys) + ["date"]
row = [fit_results[k] for k in fit_keys] + [parameters[k] for k in param_keys] + \
    [datetime.now().strftime(r"%Y-%m-%d %H:%M:%S")]

write_header = not results_log.exists()
with open(results_log, "a", newline="") as f:
    writer = csv.writer(f)
    if write_header:
        writer.writerow(fieldnames)
    writer.writerow(row)