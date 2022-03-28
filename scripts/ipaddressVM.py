import atexit
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ipaddress
import os
from auto_loader import load_from_file
config = load_from_file("auto_config")["deploy_ova"]
def get_ipv6(address):
    ip = ipaddress.ip_address(address)
    if isinstance(ip, ipaddress.IPv6Address):
        file1.write(address+"\n")
def connect(host1,user1,pswd,port1):
    service_instance = None
    # form a connection...
    try:
        service_instance = SmartConnect(host=host1,user=user1,pwd=pswd,port=port1,disableSslCertValidation=True)
        # doing this means you don't need to remember to disconnect your script/objects
        atexit.register(Disconnect, service_instance)
    except IOError as io_error:
        print("IN IO ERORR")
        print(io_error)

    if not service_instance:
        raise SystemExit("Unable to connect to host with supplied credentials.")

    return service_instance
def ip(vmname):
    si = connect(config["vcenterip"],config["user"],config["password"],443)
    vm_view = si.content.viewManager.CreateContainerView(si.content.rootFolder,[vim.VirtualMachine],True)
    # Loop through the vms and print the ipAddress
    for vm in vm_view.view:
        if vm.name == vmname:
            return vm.guest.net
ipAdress=ip(config["vmname"])
file1 = open("ipv6.txt", "w")
output=""
content=str(ipAdress)
# print(content)
output+=content[content.find("ipAddress = (str) [")+20:content.find("]",content.find("ipAddress = (str) ["))]
print("first "+output)
for i in output.strip().split(",\n"):
    get_ipv6(i.strip(" ' "))
output=""
output+=content[content.find("ipAddress = (str) [",content.find("]",content.find("ipAddress = (str) [")))+20:content.find("]",content.find("ipAddress = (str) [",content.find("]",content.find("ipAddress = (str) ["))))]
print("second "+output)
for i in output.strip().split(",\n"):
    get_ipv6(i.strip(" ' "))