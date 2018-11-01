#!/bin/bash

# tests if the site works by getting the html for its homepage
wget -q $1 -O ./tmp/indexes/$1.html >/dev/null

#tests if the site supports TLS by getting its cert
echo -n | openssl s_client -connect $1:443 | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > ./tmp/certs/$1.cert
