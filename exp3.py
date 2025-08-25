from qiskit_ibm_runtime import SamplerV2 as Sampler
import numpy as np
from qiskit import QuantumCircuit
 
# This calculation was run on ibm_sherbrooke on 11-7-24 and required 3 s to run, with 127 qubits.
# Qiskit patterns step 1: Mapping your problem to a quantum circuit
 
bit_num = 127
qc = QuantumCircuit(bit_num, bit_num)
 
# QKD step 1: Generate Alice's random bits and bases
rng = np.random.default_rng()
abits = np.round(rng.random(bit_num))
abase = np.round(rng.random(bit_num))
 
# Alice's state preparation
 
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
 
# QKD step 2: Random bases for Bob
 
bbase = np.round(rng.random(bit_num))
 
for m in range(bit_num):
    if bbase[m] == 1:
        qc.h(m)
    qc.measure(m, m)

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
 
 
# Qiskit patterns step 2: Transpilation
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
target = backend.target
pm = generate_preset_pass_manager(target=target, optimization_level=3)
qc_isa = pm.run(qc)
 
# Load the Runtime primitive and session
sampler = Sampler(mode=backend)
 
# Qiskit patterns step 3: Execute
 
job = sampler.run([qc_isa], shots=1)
counts = job.result()[0].data.c.get_counts()
countsint = job.result()[0].data.c.get_int_counts()
 
# Qiskit patterns step 4: Post-processing
# Extract Bob's bits
 
keys = counts.keys()
key = list(keys)[0]
bmeas = list(key)
bmeas_ints = []
for n in range(bit_num):
    bmeas_ints.append(int(bmeas[n]))
bbits = bmeas_ints[::-1]
 
# Compare Alice's and Bob's measurement bases and collect usable bits
 
agoodbits = []
bgoodbits = []
match_count = 0
for n in range(bit_num):
    if abase[n] == bbase[n]:
        agoodbits.append(int(abits[n]))
        bgoodbits.append(bbits[n])
        if int(abits[n]) == bbits[n]:
            match_count += 1
 
# Print some results
 
print("Alice's bits = ", agoodbits)
print("Bob's bits = ", bgoodbits)
print("fidelity = ", match_count / len(agoodbits))
print("loss = ", 1 - match_count / len(agoodbits))

from qiskit_ibm_runtime import SamplerV2 as Sampler
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

 
# This calculation was run on ibm_nazca on 11-7-24 and required 2 s to run, with 127 qubits.
# Qiskit patterns step 1: Mapping your problem to a quantum circuit
 
bit_num = 127
qr = QuantumRegister(bit_num, "q")
cr = ClassicalRegister(bit_num, "c")
qc = QuantumCircuit(qr, cr)
 
# QKD step 1: Generate Alice's random bits and bases
 
abits = np.round(rng.random(bit_num))
abase = np.round(rng.random(bit_num))
 
# Alice's state preparation
 
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
 
 
# Eavesdropping happens here!
# Generate Eve's random measurement bases
 
ebase = np.round(rng.random(bit_num))
 
for m in range(bit_num):
    if ebase[m] == 1:
        qc.h(m)
    qc.measure(qr[m], cr[m])
 
# Qiskit patterns step 2: Transpile
 
target = backend.target
pm = generate_preset_pass_manager(target=target, optimization_level=3)
qc_isa = pm.run(qc)
 
sampler = Sampler(mode=backend)
 
# Qiskit patterns step 3: Execute
 
job = sampler.run([qc_isa], shots=1)
counts = job.result()[0].data.c.get_counts()
countsint = job.result()[0].data.c.get_int_counts()
 
# Qiskit patterns step 4: Post-processing
# Extract Eve's bits
 
keys = counts.keys()
key = list(keys)[0]
emeas = list(key)
emeas_ints = []
for n in range(bit_num):
    emeas_ints.append(int(emeas[n]))
ebits = emeas_ints[::-1]
 
# print(ebits)
 
# Restart process
# Qiskit patterns step 1: Mapping your problem to a quantum circuit
 
# QKD step 1: Eve uses her measurements above to prepare best guess states to send on to Bob
 
qr = QuantumRegister(bit_num, "q")
cr = ClassicalRegister(bit_num, "c")
qc = QuantumCircuit(qr, cr)
 
 
# Eve's state preparation
 
for n in range(bit_num):
    if ebits[n] == 0:
        if ebase[n] == 1:
            qc.h(n)
    if ebits[n] == 1:
        if ebase[n] == 0:
            qc.x(n)
        if ebase[n] == 1:
            qc.x(n)
            qc.h(n)
 
# QKD step 2: Random bases for Bob
 
bbase = np.round(rng.random(bit_num))
 
for m in range(bit_num):
    if bbase[m] == 1:
        qc.h(m)
    qc.measure(qr[m], cr[m])
 
# Qiskit patterns step 2: Transpile
 
target = backend.target
pm = generate_preset_pass_manager(target=target, optimization_level=3)
qc_isa = pm.run(qc)
 
# Qiskit patterns step 3: Execute
 
job = sampler.run([qc_isa], shots=1)
counts = job.result()[0].data.c.get_counts()
countsint = job.result()[0].data.c.get_int_counts()
 
# Qiskit Patterns step 4: Post-processing
# Extract Bob's bits
 
keys = counts.keys()
key = list(keys)[0]
bmeas = list(key)
bmeas_ints = []
for n in range(bit_num):
    bmeas_ints.append(int(bmeas[n]))
bbits = bmeas_ints[::-1]
 
# Compare Alice's and Bob's bases, when they are the same, keep the bits.
 
agoodbits = []
bgoodbits = []
match_count = 0
for n in range(bit_num):
    if abase[n] == bbase[n]:
        agoodbits.append(int(abits[n]))
        bgoodbits.append(bbits[n])
        if int(abits[n]) == bbits[n]:
            match_count += 1
 
# Print some results
 
print("Alice's bits = ", agoodbits)
print("Bob's bits = ", bgoodbits)
print("fidelity = ", match_count / len(agoodbits))
print("loss = ", 1 - match_count / len(agoodbits))