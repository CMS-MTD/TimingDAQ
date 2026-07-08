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

for br in t1.GetListOfBranches():
    name = br.GetName()
    leaf = br.GetLeaf(name)

    if leaf.GetTypeName() == "Float_t" and leaf.GetLen() == 8:
        if name == "x_dut":continue
        if name == "y_dut":continue
        replace_branches.append(name)
print("Will replace:", replace_branches)
# -------------------------
# PASS 2: disable BEFORE clone
# -------------------------
for name in replace_branches:
    t1.SetBranchStatus(name, 0)

# now clone clean schema
fout = ROOT.TFile(args.output, "RECREATE")
tout = t1.CloneTree(0)

# Re-enable branches for reading
for name in replace_branches:
    t1.SetBranchStatus(name, 1)
# -------------------------
# PASS 3: re-add merged branches
# -------------------------
buffers = {}

for name in replace_branches:
    buf = array.array('f', [0]*16)
    tout.Branch(name, buf, f"{name}[16]/F")
    buffers[name] = buf

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

        for j in range(8):
            buf[j] = a1[j]
            buf[8 + j] = a2[j]

    tout.Fill()

fout.Write()
fout.Close()

print("Done:", args.output)
