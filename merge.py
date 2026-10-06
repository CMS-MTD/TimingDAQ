import ROOT
import array
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--input1", required=True)
parser.add_argument("--input2", required=True)
parser.add_argument("--output", default="combined.root")
args = parser.parse_args()

f1 = ROOT.TFile.Open(args.input1)
f2 = ROOT.TFile.Open(args.input2)

t1 = f1.Get("pulse")
t2 = f2.Get("pulse")

# -------------------------
# PASS 1: identify branches
# -------------------------
replace_branches = []
waveform_branches = {}

N_INPUT_CHANNELS = 8
N_OUTPUT_CHANNELS = 2 * N_INPUT_CHANNELS
N_SAMPLES = 2002

for br in t1.GetListOfBranches():
    name = br.GetName()
    leaf = br.GetLeaf(name)

    if name in ("channel", "time"):
        # channel is [8][2002], while time may have fewer shared time axes.
        waveform_branches[name] = leaf.GetLen() // N_SAMPLES
    elif leaf.GetTypeName() == "Float_t" and leaf.GetLen() == N_INPUT_CHANNELS:
        if name == "x_dut":continue
        if name == "y_dut":continue
        replace_branches.append(name)
print("Will replace:", replace_branches)
print("Will merge waveforms:", list(waveform_branches))
# -------------------------
# PASS 2: disable BEFORE clone
# -------------------------
for name in replace_branches + list(waveform_branches):
    t1.SetBranchStatus(name, 0)

# now clone clean schema
fout = ROOT.TFile(args.output, "RECREATE")
tout = t1.CloneTree(0)

# Re-enable branches for reading
for name in replace_branches + list(waveform_branches):
    t1.SetBranchStatus(name, 1)
# -------------------------
# PASS 3: re-add merged branches
# -------------------------
buffers = {}

for name in replace_branches:
    buf = array.array('f', [0] * N_OUTPUT_CHANNELS)
    tout.Branch(name, buf, f"{name}[{N_OUTPUT_CHANNELS}]/F")
    buffers[name] = buf

waveform_buffers = {}

for name, input_rows in waveform_branches.items():
    output_rows = 2 * input_rows
    buf = array.array('f', [0] * output_rows * N_SAMPLES)
    tout.Branch(name, buf, f"{name}[{output_rows}][{N_SAMPLES}]/F")
    waveform_buffers[name] = buf

# -------------------------
# event loop
# -------------------------
n = t1.GetEntries()
print(f"Processing {n} events...")

for i in range(n):
    t1.GetEntry(i)
    t2.GetEntry(i)

    for name, buf in buffers.items():
        a1 = getattr(t1, name)
        a2 = getattr(t2, name)

        for j in range(N_INPUT_CHANNELS):
            buf[j] = a1[j]
            buf[N_INPUT_CHANNELS + j] = a2[j]

    for name, buf in waveform_buffers.items():
        a1 = getattr(t1, name)
        a2 = getattr(t2, name)
        input_rows = waveform_branches[name]

        for j in range(input_rows):
            for k in range(N_SAMPLES):
                input_index = j * N_SAMPLES + k
                buf[input_index] = a1[input_index]
                buf[input_rows * N_SAMPLES + input_index] = a2[input_index]

    tout.Fill()

fout.Write()
fout.Close()

print("Done:", args.output)
