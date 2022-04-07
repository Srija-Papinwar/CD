import argparse
import json
openfile=open('auto_config.json', 'r')
config = json.load(openfile)
outfile= open("auto_config.json", "w")
parser = argparse.ArgumentParser()
parser.add_argument("-do", "--deploy_ova", help="configuring deploy ova keys",default="none")
parser.add_argument("-f", "--fts", help="configuring dcs fts keys",default="none")
parser.add_argument("-py", "--python", help="configuring python keys",default="none")
parser.add_argument("-ovc", "--oneview_cred", help="configuring oneview cred keys",default="none")
parser.add_argument("-sdk", "--sdk", help="configuring sdk keys",default="none")
args = parser.parse_args()
objects=str(args)[10:-2].split(",")
for obj in objects :
    d=obj[:obj.find("=")].strip()
    if obj[obj.find("=")+1:].strip("'") != "none":
        li=obj[obj.find("=")+1:].split("?")
        for i in li:
            key,value=i.split(":")
            if(key.strip("'")=="ssl_certificate"):
                op=bool(value.strip("'"))
                config[d][key.strip("'")]=op
            else:
                config[d][key.strip("'")]=value.strip("'")
json.dump(config,outfile,indent=4)
