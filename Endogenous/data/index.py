from datetime import datetime
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def ms_to_date(_ms):
    return datetime.fromtimestamp(_ms / 1000).date()

def save_to_csv_file(filename, content):
    with open(filename, "w") as file:
        file.write(content)

# --------------------------------------------------------------------------

with open(os.path.join(BASE_DIR, "ism-pmi.json"), "r") as file:
    pmiData = json.load(file)

pmiOut = 'DATE,ISM(PMI)'

for item in pmiData:
    pmiOut += f"\n{ms_to_date(item[0])},{item[1]}"

save_to_csv_file(os.path.join(BASE_DIR, "ISM-PMI.csv"), pmiOut)

# --------------------------------------------------------------------------

with open(os.path.join(BASE_DIR, "ism-nmi.json"), "r") as file:
    nmiData = json.load(file)

nmiOut = 'DATE,ISM(NMI)'

for item in nmiData:
    nmiOut += f"\n{ms_to_date(item[0])},{item[1]}"

save_to_csv_file(os.path.join(BASE_DIR, "ISM-NMI.csv"), nmiOut)