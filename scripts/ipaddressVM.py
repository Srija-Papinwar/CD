"""
Before executing this script make sure that all packages are installed properly
and also vm is exsisting on vcenter if not is will not execute properly
purpose:
-------
This script writes all the ipv6 addresses for a given vm into a text file ipv6.txt. 

"""
import atexit
import sys
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ipaddress
import os
from auto_loader import load_from_file
def check_ipv6(address):
    """
    Purpose:
    --------
    This is a helper method which checks if provided address is instance of ipv6 or not.
    If it is a ipv6 address then it write that address into a ipv6.txt file
    parameters:
    ----------
    address: str
    ip address 
    returns:
    --------
    It returns nothing

    """

    ip = ipaddress.ip_address(address)
    if isinstance(ip, ipaddress.IPv6Address):
        file.write(address+"\n")

def connect(host1,user1,pswd,port1):
    """
    Purpose:
    --------
    This is a helper method which connects to vcenter.
    parameters:
    ----------
    host1: str
    ipaddress of vcenter
    user1 & pswd : str
    credentials of vcenter with which you want connect to vcenter.
    user1 format name@LAB.LOCAL
    port (optional): int
    port number of vcenter 
    By default it is 443

    returns:
    --------
    returns a service instance of vcenter 

    """
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

def ip_content(vmname):
    """
    Purpose:
    --------
    This method retrives network content of given vm using its name.

    parameters:
    ----------
    vmname : str
    Provide name of vm whose ipv6 address you want to fetch
    returns:
    --------
    It returns <class 'pyVmomi.VmomiSupport.vim.vm.GuestInfo.NicInfo[]'> (network attribute content of guest vm)

    """
    # print(sys.argv[1]+" "+sys.argv[2]+" "+" "+sys.argv[3]+" "+sys.argv[4])
    si = connect(config["vcenter_ip"],config["vcenter_username"],config["vcenter_password"],443)
    vm_view = si.content.viewManager.CreateContainerView(si.content.rootFolder,[vim.VirtualMachine],True)
    # Loop through the vms and print the ipAddress
    for vm in vm_view.view:
        if vm.name == vmname:
            return vm.guest.net

def get_ipv6ips(content):
    """
    Purpose:
    --------
    this method from the network attribute fetches the all the ipaddresses and
    then for each ip address checks if  it is an ipv6 address.
    For fetching the ipaddress it uses few string functions(like find()) and concepts (like slicing).
    parameters:
    ----------
    content: str
    content of network attribute.
    returns:
    --------
    none
    """
    output=""
    # variable 'a' index of start point of ipaddress1 attribute 
    a=content.find("ipAddress = (str) [")
    # variable 'b' index of end point of ipaddress1 attribute
    b=content.find("]",a)
    # variable 'c' index of start point of ipaddress2 attribute
    c=content.find("ipAddress = (str) [",b)
    # variable 'd' index of end point of ipaddress2 attribute
    d=content.find("]",c)
    output+=content[a+20:b]
    print("first "+output)
    for i in output.strip().split(",\n"):
        check_ipv6(i.strip(" ' "))
    output=""
    output+=content[c+20:d]
    print("second "+output)
    for i in output.strip().split(",\n"):
        check_ipv6(i.strip(" ' "))

# Execution starts from here...
config = load_from_file("auto_config")["deploy_ova"]
file = open("ipv6.txt", "w")
# print(str(ip_content(sys.argv[1])))
get_ipv6ips(str(ip_content(config["vmname"])))
