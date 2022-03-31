#!/bin/bash

: '
This scripts uses OVFTOOL for for deployment of ova with specified parameters.
This shell script needs OVFTOOL to be setup before executing command and provide
complete path of .exe for using ovftool command

'


# This for loop is for encoding the string pswd

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

# OVFTOOL command

ovftool  --noSSLVerify --powerOn -nw=$1 -ds=$2 -n=$3 $4  vi://$5:${e}@$7/$8/host/$9/${10}