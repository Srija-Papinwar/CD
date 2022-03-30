#!/bin/bash
string="${6}"
for(( p=0 ; p<${#6} ; p++)); do
    c=${string:$p:1}
    case "$c" in 
        [-_.~a-zA-Z0-9] ) o="${c}";;
        * )               printf -v o '%%%02x' "'$c"
    esac
    e+="${o}"
done
echo "${e}"
/home/venkatesh/home/ovftool/vmware-ovftool/ovftool  --noSSLVerify --powerOn -nw=$1 -ds=$2 -n=$3 $4  vi://$5:${e}@$7/$8/host/$9/${10}