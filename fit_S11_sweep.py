# change the file paths to your cst python libraries and cst project
cst_library_path = r"C:\Program Files (x86)\CST Studio Suite 2025\AMD64\python_cst_libraries" # default install location

cst_project_path = r"path\to\project.cst"

import os
import sys
sys.path.append(cst_library_path)
import cst.results
from matplotlib import pyplot as plt
import numpy as np
from resonator_tools import circuit
from pathlib import Path

s11_path = r"1D Results\S-Parameters\S1,1" # path to sim results relative to project
project = cst.results.ProjectFile(cst_project_path, allow_interactive=True)

dir = Path(__file__).parent
folder = input("Sweep Name: ")
folder = dir/f"{folder}"
try:
    os.mkdir(folder)
    os.mkdir(f"{folder}\\fit")
    os.mkdir(f"{folder}\\data")
    os.mkdir(f"{folder}\\plots")
except FileExistsError:
    print("folder already exists")
    sys.exit()
    
output_file = open(f"{folder}\\fit\\results.txt", 'w')

model = project.get_3d()
run_ids = model.get_run_ids(s11_path, skip_nonparametric=True)

set1 = set(model.get_parameter_combination(1).items())
set2 = set(model.get_parameter_combination(2).items())
sweep_param = list(dict(set1 - set2).keys())[0]

params = model.get_parameter_combination(0)
fp = open(f"{folder}\\params.txt", 'w')
for param in params:
    fp.write(f"{param} = {params[param]}\n")
fp.close()

Qi_arr = []
Qi_err_arr = []

param_arr = []
Qc_arr = []
Qc_err_arr = []

for id in run_ids[:]: # edit to fit [n:m] runs
    s11 = project.get_3d().get_result_item(s11_path, id)
    x_data = s11.get_xdata()
    y_data = s11.get_ydata()
    name = f'{sweep_param}={params[sweep_param]}'
    
    # write to file
    params = model.get_parameter_combination(id)
    path = f"{folder}\\data\\s11_{sweep_param}({params[sweep_param]}).txt"
    id_label = f"{sweep_param}={params[sweep_param]}"
    with open(path, 'w') as f:
        f.write(f"#{s11.title}\n")
        f.write(f'#"{s11.xlabel}"\t"{id_label}"\n')
        f.write("#-----------------------------------------------------------\n")
        for i in range(s11.length):
            f.write(f"{x_data[i]}\t{y_data[i]}\n")
    
    freq = x_data
    mag = np.abs(y_data)
    mag_db = 20*np.log10(np.abs(y_data))
    phase = np.angle(y_data)
    phase_deg = np.unwrap(phase)*180/np.pi
    
    # plot
    plt.figure()
    plt.plot(x_data, mag_db, label=id_label)
    plt.title("S11 Magnitude")
    plt.xlabel("f (GHz)")
    plt.ylabel("Magnitude (dB)")
    plt.legend(title='sweep param', loc="lower right")
    plt.savefig(f"{folder}\\plots\\S11_mag_{sweep_param}({params[sweep_param]}).png")
    plt.close()

    plt.figure()
    plt.plot(x_data, phase_deg, label=id_label)
    plt.title("S11 Phase")
    plt.xlabel("f (GHz)")
    plt.ylabel("Phase (degrees)")
    plt.legend(title='sweep param', loc="upper right")
    plt.savefig(f"{folder}\\plots\\S11_phase_{sweep_param}({params[sweep_param]}).png")
    plt.close()
    
    port1 = circuit.reflection_port()
    port1.add_data(freq, mag * np.exp(1j*phase))
    # port1.GUIfit()
    port1.autofit()
    port1.plotall(save_file=f'{folder}\\fit\\{sweep_param}={params[sweep_param]}.png')
    
    fr = port1.fitresults['fr'] 
    Qc = port1.fitresults['Qc']
    Qi = port1.fitresults['Qi']
    Ql = port1.fitresults['Ql']
    Qi_err = port1.fitresults['Qi_err']
    Qc_err = port1.fitresults['Qc_err']
    
    param_arr.append(params[sweep_param])
    Qi_arr.append(Qi)
    Qi_err_arr.append(Qi_err)
    Qc_arr.append(Qc)
    Qc_err_arr.append(Qc_err)
    
    text = f'{sweep_param}={params[sweep_param]}\n' + \
        '-------------------------\n' + \
        f'fr = {fr}\n' + \
        f'Qi = {Qi}\n' + \
        f'Qc = {Qc}\n' + \
        f'ki = {fr/Qi}\n' + \
        f'kl = {fr/Ql}\n' + \
        f'kc = {fr/Qc}\n' + \
        f'Qc/Qi = {Qc/Qi}\n' + \
        f'{port1.fitresults}\n' + \
        '-------------------------\n'
    
    output_file.write(text)
    
# sort arrays in case simulations runs are out of order
sort_idx = np.argsort(param_arr)
param_arr = np.sort(param_arr)
Qi_arr = [Qi_arr[i] for i in sort_idx]
Qi_err_arr = [Qi_err_arr[i] for i in sort_idx]
Qc_arr = [Qc_arr[i] for i in sort_idx]
Qc_err_arr = [Qc_err_arr[i] for i in sort_idx]
    
plt.figure()
plt.plot(param_arr, Qc_arr)
plt.errorbar(param_arr, Qc_arr, yerr=Qc_err_arr, fmt='x')
plt.title(f"{sweep_param} sweep")
plt.xlabel(f"{sweep_param} (mm)")
plt.ylabel("Qc")
plt.savefig(f'{folder}\\fit\\Qc_sweep.png')
plt.show()

plt.figure()
plt.plot(param_arr, Qi_arr)
plt.errorbar(param_arr, Qi_arr, yerr=Qi_err_arr, fmt='x')
plt.title(f"{sweep_param} sweep")
plt.xlabel(f"{sweep_param} (mm)")
plt.ylabel("Qi")
plt.savefig(f"{folder}\\fit\\Qi_sweep.png")
plt.show()