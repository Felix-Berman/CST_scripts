import sys, json
import numpy as np
from pathlib import Path
from resonator_tools import circuit

dir = Path(__file__).parent

try:
    from resonator_tools import circuit
except ImportError:
    sys.exit(f"Error: 'resonator_tools' library not found. Add resonator_tools \
             https://github.com/sebastianprobst/resonator_tools to '{dir}'.")
    
def main(infile, outfile):
    data = np.loadtxt(infile)
    
    freqs, re_s11, im_s11 = data[:, 0], data[:, 1], data[:, 2]
    
    port1 = circuit.reflection_port()
    port1.add_data(freqs, re_s11 + 1j*im_s11)
    port1.autofit()
    port1.plotall()
    
    fit = port1.fitresults
    results = {key: float(val) for key, val in fit.items()}
    
    with open(outfile, 'w') as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])