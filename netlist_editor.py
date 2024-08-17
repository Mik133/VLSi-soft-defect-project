import os
import random
from copy import deepcopy

files_dict = {}
file_num = 1
for n_file in os.listdir(os.curdir):
    files_dict[file_num] = n_file
    file_num += 1

print("Please select your netlist file:")
for file_index, n_file in files_dict.items():
    print("%d: %s" % (file_index, n_file))

file_index = input("Enter the netlist file index as shown on console:")
while True:
    if int(file_index) < len(files_dict) and files_dict[int(file_index)].find('netlist') >= 0:
        netlist_file = files_dict[int(file_index)]
        break
    else:
        file_index = input("Your input is invalid please try again")

print("The netlist file selected is: ", netlist_file)

# Extracting transistors for netlist file
with open(netlist_file, "r") as netlist:
    print("Starting the netlist editor...")
    netlist_data = netlist.read()

transistors_ports = {"DRAIN": "", "GATE": "", "SOURCE": "", "BULK": ""}
all_transitors = {}

for line in netlist_data.split("\n"):
    if line.find("MM") != -1 and line.find("MM") == 0:
        line = line.split(" ")
        for i, port in enumerate(transistors_ports):
            transistors_ports[port] = line[i + 1]
        all_transitors[line[0]] = deepcopy(transistors_ports)

netlist_data = netlist_data.replace(".ENDS", "\n")
# End of transistor extraction

# Defines for transistors insert

transistor_iterator = 1
all_resistors = []
# End of transistors insert


res_name = f"res_for_mc"
res_mean = random.randrange(10, 1000)
res_limits = random.randrange(0, res_mean)
res_std = 1

res_def = ("simulator lang = spice\n\n"
           f".subckt {res_name} a b\n"
           f" .param rs = agauss({res_mean}K,{res_limits}K,{res_std})\n"
           f" .param res = abs(rs)\n"
           f" R{res_name} a b res\n"
           f".ends {res_name}\n\n"
           )

# Creating resistors with gaussian distribution
for transistor in all_transitors:
    drain = all_transitors[transistor]["DRAIN"]
    gate = all_transitors[transistor]["GATE"]
    source = all_transitors[transistor]["SOURCE"]

    res_inst_dg = f"Xn{transistor_iterator}_{drain}_{gate}_drain_to_gate {drain} {gate} {res_name}"
    res_inst_ds = f"Xn{transistor_iterator}_{drain}_{source}_drain_to_source {drain} {source} {res_name}"
    res_inst_gs = f"Xn{transistor_iterator}_{gate}_{source}_gate_to_source {gate} {source} {res_name}"

    all_resistors.append(res_inst_dg)
    all_resistors.append(res_inst_ds)
    all_resistors.append(res_inst_gs)
    transistor_iterator += 1
# End of transistor creation

# Write new netlist with transistors
with open(netlist_file+"_with_soft_defects", "w") as netlist_with_defects:
    netlist_with_defects.write(f"{res_def}")
    for resistor in all_resistors:
        netlist_with_defects.write(f"{resistor}\n\n")
    # netlist_with_defects.write(".ENDS") MAY BE UNNECESSARY
    netlist_with_defects.close()
# End of writing new netlist
