#!/bin/bash
# Simple script to run xpython 3.1-3.3 bytecode
if (( $# > 0 )); then
    # FIXME
    print "Arg not handled yet"
    exit 1
fi
mydir=$(dirname ${BASH_SOURCE[0]})
set -e

source ../admin-tools/pyenv-3.1-3.2-versions

for version in $PYVERSIONS; do
    echo "Testing bytecode for $version"
    first_two=$(echo $version | cut -d'.' -f 1-2)
    for file in bytecode-${first_two}/*.pyc; do
	echo ======= $file ========
	xpython "$file"
	echo ------- $file --------
    done
done
