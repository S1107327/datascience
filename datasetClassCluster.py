import pandas as pd
legit = []
with open("./legit/list/5000.txt", "r") as fin:
    line = fin.readline().strip('\n')
    while line:
        legit.append(line)
        line = fin.readline().strip('\n')

labels = [0 for i in range(5000)]

legit_df = pd.DataFrame({'label': pd.Series(labels),'label_multiclass': pd.Series(labels), 'domain': pd.Series(legit)})

# dga part
dga = []
labels_dga = [1 for i in range(5000)]
labels_dga_families = [1 for i in range(
    1000)]+[2 for i in range(1000)]+[3 for i in range(1000)]+[4 for i in range(1000)]+[5 for i in range(1000)]

for family in ["cryptolocker", "dircrypt", "dyre", "padcrypt", "zeus-newgoz"]:
    with open(f"./{family}/list/1000.txt", "r") as fin:
        line = fin.readline().strip('\n')
        while line:
            dga.append(line)
            line = fin.readline().strip('\n')

dga_df = pd.DataFrame({'label': pd.Series(labels_dga),'label_multiclass': pd.Series(labels_dga_families), 'domain': pd.Series(dga)})
complete = pd.concat([legit_df, dga_df]).reset_index(drop=True)
no_dots = [x.replace(".", "") for x in complete["domain"]]
bigrams_column = [" ".join([x[i:i+2] for i in range(0, len(x)-1, 1)]) for x in no_dots]
complete['no_dots'] = pd.Series(no_dots)
complete['bigrams'] = pd.Series(bigrams_column)
complete.to_csv('example_dataset.csv', index=False)
'''
with open("bigrams.txt", 'w') as fout:
    for name in complete['bigrams']:
        fout.write(f"{name}\n")
'''