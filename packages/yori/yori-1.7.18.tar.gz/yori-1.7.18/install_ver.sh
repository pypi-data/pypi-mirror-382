#!/usr/bin/env bash
if [[ -z $1 ]]; then
    echo "$0 <ver>"
    exit 1
fi
ver=$1
env=$PWD/${ver}

system=$(uname -s)
arch=$(uname -m)
if [[ $system == "Darwin" ]]; then
    system="MacOSX"
fi

curl -o miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-${system}-${arch}.sh
trap '{ rm -f miniconda.sh; }' EXIT
bash miniconda.sh -b -p ${env}
${env}/bin/conda install -y "python=3.9"

${env}/bin/pip install --no-cache-dir git+https://gitlab.ssec.wisc.edu/pveglio/yori.git@${ver}
