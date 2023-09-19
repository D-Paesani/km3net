import requests
import pandas as pd
import time
from datetime import datetime
import json
import os
import argparse

parser = argparse.ArgumentParser(description='JBDUMP')
parser.add_argument('--jbs',          type=int,   default=[1,2,3],              nargs="+",  help="list of jb to query separated by single space")
parser.add_argument('--pag',          type=str,   default=["psm", "ice"],       nargs="+",  help="list of jb pages to query separated by single space")
parser.add_argument('--dump',         type=bool,  default=1,                                help="enble json and excel dump")
parser.add_argument('--printonly',    type=bool,  default=0,                                help="print only parsed json data")
args = parser.parse_args()
if args.printonly: args.dump = 0

url = "http://arca-jb-%02d.lns.infn.it:5005/api/v1.0/%s"

timstamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

if args.dump: os.system(F"mkdir -p ./dump/xlsx")
if args.dump: os.system(F"mkdir -p ./dump/json")

print("\n############################### JB DUMP ###############################\n")

created = 0
for ii in args.jbs:    
    for pag in args.pag:
        
        shname = F'jb{ii:02d}_{pag}'
        uurl = url%(ii, pag.lower())

        print(F"\n-->  Querying JB{ii:02d}/{pag} at {uurl}")

        try:
            
            dataj = requests.get(uurl).json()
            dataf = pd.DataFrame.from_dict(dataj[pag.upper()])
            
            if args.dump:
                os.system(F"mkdir -p ./dump/json/{timstamp}/")
                jsonpath = F"dump/json/{timstamp}/{shname}_{timstamp}.json"
                xlsxpath = F"dump/xlsx/jb_{timstamp}.xlsx"
                with open(jsonpath, 'w') as fdump:
                    print(F"-->  Dumping json to {jsonpath}")
                    json.dump(dataj, fdump)    
                # with pd.ExcelWriter(xlsxpath, mode="w" if ii==args.jbs[0] and pag==args.pag[0] else "a") as writer:  
                with pd.ExcelWriter(xlsxpath, mode="w" if not created else "a") as writer:  
                    created = 1
                    print(F'-->  Dumping xlsx to {xlsxpath}/{shname}')
                    # writer.book.create_sheet(shname)
                    dataf.to_excel(writer, sheet_name=shname)
                    
            if args.printonly:
                print("")
                print(F"################### Start parsed data for JB{ii:02d}/{pag}: #########################################")
                pd.options.display.max_rows = 100
                pd.options.display.max_columns = 10
                print(dataf)
                # print(dataf.head(10000))
                print(F"################### End parsed data for JB{ii:02d}/{pag}: ###########################################")


        except Exception as ee:
                print(f"******* Error on JB{ii:02d}/{pag}: {str(ee)}")
                
print("\n############################### JB DUMP ###############################\n")
