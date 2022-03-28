import subprocess
import urllib.parse
import os
from auto_loader import load_from_file
config = load_from_file("auto_config")["deploy_ova"]
command = "ovftool --powerOn -nw="+config["network"]+" -ds="+config["datastore"]+" -n="+config["vmname"]+" /home/venkatesh/latestbuildfile.ova vi://"+config["user"]+":"+urllib.parse.quote(config["password"])+"@"+config["vcenterip"]+"/"+config["datacenter"]+"/host/"+config["cluster"]+"/"+config["host"]
result = subprocess.run(command,shell = True ,stdout = subprocess.PIPE )
print(result.stdout.decode())