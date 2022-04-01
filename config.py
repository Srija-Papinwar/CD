import argparse
import json
openfile=open('auto_config.json', 'r')
config = json.load(openfile)
outfile= open("auto_config.json", "w")
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--deploy_ova", help="increase output verbosity")
parser.add_argument("-f", "--fts", help="increas")
parser.add_argument("-sd", "--pythonsdk", help="incre")
args = parser.parse_args()
objects=str(args)[10:-2].split(",")
for obj in objects :
    d=obj[:obj.find("=")].strip()
    if obj[obj.find("=")+1:] != "Non":
        li=obj[obj.find("=")+1:].split("?")
        for i in li:
            key,value=i.split(":")
            config[d][key.strip("'")]=value.strip("'")
json.dump(config,outfile,indent=4)
