
import matplotlib.pyplot as plt
import csv

file = open("results.csv", "r")
reader = csv.reader(file, lineterminator="\n")

csvdata = []
for i, line in enumerate(reader):
    if i == 0: continue

    csvdata.append(
        [int(line[0]),
        int(line[1]),
        int(line[2])]
    )

csvxaxis = [i+1 for i in range(len(csvdata))]

csvdatanothing = [d[0] for d in csvdata]
csvdatabrute = [d[1] for d in csvdata]
csvdatadvanced = [d[2] for d in csvdata]

fig, ax = plt.subplots(figsize=(5, 2.7), layout='constrained')
ax.plot(csvdatanothing, label='Nothing (baseline)')
ax.plot(csvdatabrute, label='Brute force algorithm')
ax.plot(csvdatadvanced, label='aceynk\'s algorithm')


ax.set_xlabel('Length of input list')
ax.set_ylabel('Functions completed in 1 minute')
ax.set_title("functions completed vs Problems solved in 1 minute for various approaches") 
ax.legend()

plt.show() 
