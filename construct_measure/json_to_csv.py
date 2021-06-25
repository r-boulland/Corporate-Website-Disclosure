# -*- coding: cp1252 -*-
import json
import csv
import os

#set the directory where the JSON files are located
directory='C:/Users/Boulland/json/'
#set the directory where the CSV files will be created
outdir='C:/Users/Boulland/csv/'
s=""
for filename in os.listdir(directory):
    out=os.path.join(outdir,os.path.splitext(filename)[0])
    seq=(out,".csv")
    out=s.join(seq)
    ticker=os.path.join(directory,filename)
    print(ticker)
    data_file=open(ticker)
    try:
       data=json.load(data_file)
    except:
        continue
    data_file.close
    csv_file=open(out,'w',newline='')
    print(out)
    writer=csv.writer(csv_file)
    for element in data:
        try:
            writer.writerow(element)
        except:
            continue
    csv_file.close()


