import csv
import re
from collections import defaultdict
# This file takes all the variables from the sciencekeywords that are relevant to identifying datasets. For now,
# to minimize noise it will take all of the atmosphereic variables. The variables are saved in  variables.csv

# Take all of atmosphere
variables = {}
with open("data/csv/sciencekeywords.csv", newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        if row[1] != "ATMOSPHERE":
            continue
        if not row[2] in variables:
            variables[row[2]] = defaultdict(list)
        for i in range(4, 7):
            if row[i] and not re.search(r"(/|\()", row[i]):
                variables[row[2]][row[3]].append(row[i].lower())
atmos = variables["ATMOSPHERIC CHEMISTRY"]

vals = []
for key in atmos.keys():
    val = []
    for var in atmos[key]:
        if len(val) == 0:
            val.append(var)
        elif len(val) == 1:
            if len(var) < 6 and var != "ozone":
                val.append(var)
                vals.append(val)
                val = []
            else:
                val.append("")
                vals.append(val)
                val = [var]
with open("data/csv/test_variables.csv") as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        if [row[1].lower(), row[0].lower()] not in vals:
            vals.append([row[1], row[0]])
with open("data/csv/variables.csv", "w") as csvfile:
    for row in vals:
        if row[1]:
            csvfile.write(row[1].upper()+","+row[0].upper()+"\n")
        else:
            csvfile.write(row[0].upper()+","+row[1].upper()+"\n")
csvfile.close()


