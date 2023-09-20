import requests
import pandas as pd
import time
from datetime import datetime
import json
import os
import argparse

print("\n############################### JB DUMP ###############################\n")

parsw = [F"swm/{iii}/{ii}" for iii in ["primary", "secondary"] for ii in range(1,12+1) ]
paredfa = [F"edfa/{ii}" for ii in range(1,4+1)]
pardef = ["psm", "ice", *paredfa, *parsw]
dumpformats = ["json", "xlsx"]
url = "http://arca-jb-%02d.lns.infn.it:5005/api/v1.0/%s"

parser = argparse.ArgumentParser(description='JBDUMP')
parser.add_argument('--jbs',          type=int,   default=[1,2,3],             nargs="+",  help="list of jb to query separated by single space")
parser.add_argument('--pag',          type=str,   default=pardef,              nargs="+",  help="list of jb pages to query separated by single space")
parser.add_argument('--dump',         type=bool,  default=1,                               help="enble json and excel dump")
parser.add_argument('--printonly',    type=bool,  default=0,                               help="print only parsed json data")
args = parser.parse_args()
if args.printonly: args.dump = 0

timstamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

for ii in args.jbs:    
    created=0
    jbdata = dict()
    
    for pag in args.pag:
        
        namejb = F"jb{ii:02d}"
        namejbpag = namejb + F"_{pag}"
        uurl = url%(ii, pag.lower())
    
        try:
            
            print(F"-->  Querying JB{ii:02d}/{pag} at {uurl}")
            dataj = requests.get(uurl).json()
            toparse = pag.split("/")[0].upper() + (" status" if pag.split("/")[0] in ["edfa", "swm"] else "")
            print(F"-->  Parsing [{toparse}]")
            dataf = pd.DataFrame.from_dict(dataj)[toparse] if toparse.lower() in ["edfa status"] else pd.DataFrame.from_dict(dataj[toparse]) 
            jbdata.update(dataj) 
            
            if args.dump:
                paths = []
                for jj, kk in zip(dumpformats, [namejbpag, namejb]):
                    # os.system(F"mkdir -p ./dump/{jj}/{timstamp}/")
                    paths.append(F"dump/{jj}/{timstamp}/{kk.replace('/', '')}.{jj}")
                os.system(F"mkdir -p ./dump/xlsx/{timstamp}/")
                
                # with open(paths[0], 'w') as fdump:
                #     print(F"-->  Dumping json to {paths[0]}")
                #     json.dump(dataj, fdump)    
                with pd.ExcelWriter(paths[1], mode="w" if not created else "a") as writer:  
                    created = 1
                    print(F"-->  Dumping xlsx to {paths[1]} sheet={pag.replace('/','')}")
                    # writer.book.create_sheet(namejbpag)
                    dataf.to_excel(writer, sheet_name=pag.replace('/',''))
                    
            if args.printonly:
                print("")
                print(F"################### Start parsed data for JB{ii:02d}/{pag}: #########################################")
                pd.options.display.max_rows = 100
                pd.options.display.max_columns = 10
                print(dataf)
                # print(dataf.head(10000))
                print(F"################### End parsed data for JB{ii:02d}/{pag} ############################################")  

        except Exception as ee:
                print(f"******* Error on JB{ii:02d}/{pag}: {str(ee)}")
    
    os.system(F"mkdir -p ./dump/json/")
    jsonp = F"dump/json/{timstamp}_{namejb}.json"
    with open(jsonp, "w") as fdump:
        print(F"-->  Dumping json to {jsonp}")
        json.dump(jbdata, fdump)  
                
print("\n############################### JB DUMP'D #############################\n")
