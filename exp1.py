# Qiskit patterns step 1: Map your problem to quantum circuit
# Import some generic packages
 
import numpy as np
from qiskit import QuantumCircuit
import matplotlib.pyplot as plt 
 
# Set up a random number generator and a quantum circuit. We choose to start with 20 bits, though any number <30 should be fine.
 
rng = np.random.default_rng()
bit_num = 20
qc = QuantumCircuit(bit_num, bit_num)
 
# QKD step 1: Random bits and bases for Alice
# generate Alice's random bits
 
abits = np.round(rng.random(bit_num))
 
# generate Alice's random measurement bases. Here we will associate a "0" with the Z basis, and a "1" with the X basis.
 
abase = np.round(rng.random(bit_num))
 
# Alice's state preparation. Check that this creates states according to table 1
 
for n in range(bit_num):
    if abits[n] == 0:
        if abase[n] == 1:
            qc.h(n)
    if abits[n] == 1:
        if abase[n] == 0:
            qc.x(n)
        if abase[n] == 1:
            qc.x(n)
            qc.h(n)
 
qc.barrier()
 
# QKD step 2: Random bases for Bob
# generate Bob's random measurement bases.
 
bbase = np.round(rng.random(bit_num))
 
# Note that if Bob measures in Z no gates are necessary, since IBM Quantum computers measure in Z by default.
# If Bob measures in the X basis, we implement a hadamard gate qc.h to facilitate the measurement.
 
for m in range(bit_num):
    if bbase[m] == 1:
        qc.h(m)
    qc.measure(m, m)
print("Alice's bits are ", abits)
print("Alice's bases are ", abase)
print("Bob's bases are ", bbase)
qc.draw("mpl")
plt.show()

from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService(channel="ibm_cloud", token="IBM_token")
backend = service.backend("ibm_brisbane")
print(backend.name)

# Load the backend sampler
from qiskit.primitives import BackendSamplerV2
 
# Load the Aer simulator and generate a noise model based on the currently-selected backend.
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
 
# Load the qiskit runtime sampler
from qiskit_ibm_runtime import SamplerV2 as Sampler
 
 
noise_model = NoiseModel.from_backend(backend)
 
# Define a simulator using Aer, and use it in Sampler.
backend_sim = AerSimulator(noise_model=noise_model)
sampler_sim = BackendSamplerV2(backend=backend_sim)
# Qiskit patterns step 2: Transpile
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
 
target = backend.target
pm = generate_preset_pass_manager(target=target, optimization_level=3)
qc_isa = pm.run(qc)

# This required 5 s to run on ibm_torino on 10-28-24
sampler = Sampler(mode=backend)
job = sampler.run([qc_isa], shots=1)
# job = sampler_sim.run([qc], shots = 1)
counts = job.result()[0].data.c.get_counts()
countsint = job.result()[0].data.c.get_int_counts()

# Get an array of bits
 
keys = counts.keys()
key = list(keys)[0]
bmeas = list(key)
bmeas_ints = []
for n in range(bit_num):
    bmeas_ints.append(int(bmeas[n]))
 
# Reverse the order to match our input. See "little endian" notation.
 
bbits = bmeas_ints[::-1]
 
print(bbits)

# QKD step 3: Public discussion of bases
 
agoodbits = []
bgoodbits = []
match_count = 0
for n in range(bit_num):
    # Check whether bases matched.
    if abase[n] == bbase[n]:
        agoodbits.append(int(abits[n]))
        bgoodbits.append(bbits[n])
        # If bits match when bases matched, increase count of matching bits
        if int(abits[n]) == bbits[n]:
            match_count += 1
 
print(agoodbits)
print(bgoodbits)
print("fidelity = ", match_count / len(agoodbits))
print("loss = ", 1 - match_count / len(agoodbits))
