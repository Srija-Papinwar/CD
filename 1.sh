#!/bin/bash
echo $1 $2 $3 $4 $5 $6 $7 $8 $9 ${10}
/home/venkatesh/home/ovftool/vmware-ovftool/ovftool  --noSSLVerify --powerOn -nw=$1 -ds=$2 -n=$3 $4  vi://$5:$6@$7/$8/host/$9/${10}