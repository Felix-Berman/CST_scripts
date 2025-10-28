# %%
import numpy as np
from resonator_tools import circuit
from pathlib import Path

dir = Path(__file__).parent

file = dir/"S11.txt"

file_data = np.loadtxt(file, delimiter='\t',skiprows=3)

freq = file_data[:,0]*1e9
data = file_data[:,1] + 1j*file_data[:,2]

port1 = circuit.reflection_port()
port1.add_data(freq,data)
port1.GUIfit()
# port1.autofit()
port1.plotall()
fr = port1.fitresults['fr']
Qc = port1.fitresults['Qc']
Qi = port1.fitresults['Qi']
Ql = port1.fitresults['Ql']
print(f'fr = {fr}')
print(f'Qi = {Qi}')
print(f'Qc = {Qc}')
print(f'ki = {fr/Qi}')
print(f'kl = {fr/Ql}')
print(f'kc = {fr/Qc}')
print(f'Qc/Qi = {Qc/Qi}')
print(port1.fitresults)


# %%
