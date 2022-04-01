#!/bin/bash

: '
This scripts uses OVFTOOL for for deployment of ova with specified parameters.
This shell script needs OVFTOOL to be setup before executing command and provide
complete path of .exe for using ovftool command

'


# This for loop is for encoding the string pswd

string=$(jq -r '.deploy_ova.vcenter_password' auto_config.json)
for(( p=0 ; p<${#string} ; p++)); do
    c=${string:$p:1}
    case "$c" in 
        [-_.~a-zA-Z0-9] ) o="${c}";;
        * )               printf -v o '%%%02x' "'$c"
    esac
    e+="${o}"
done
echo "${e}"

# OVFTOOL command

cd /var/lib/jenkins/workspace/ovftool/
vmware-ovftool/ovftool  --noSSLVerify --powerOn -nw=$(jq -r '.deploy_ova.network' auto_config.json) -ds=$(jq -r '.deploy_ova.datastore' auto_config.json) -n=$(jq -r '.deploy_ova.vmname' auto_config.json) $(jq -r '.deploy_ova.ova_path' auto_config.json)  vi://$(jq -r '.deploy_ova.vcenter_username' auto_config.json):${e}@$(jq -r '.deploy_ova.vcenter_ip' auto_config.json)/$(jq -r '.deploy_ova.datacenter' auto_config.json)/host/$(jq -r '.deploy_ova.cluster' auto_config.json)/$(jq -r '.deploy_ova.host' auto_config.json)


