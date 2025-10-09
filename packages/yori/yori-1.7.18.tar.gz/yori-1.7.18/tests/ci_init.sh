if [[ ${BASH_SOURCE[0]} == ${0} ]]; then
    echo "ERROR: ci_init.sh script must be sourced, not run directly!":
    exit 1
fi

readonly cachedir=$HOME/yori-ci-cache
readonly condadir=${cachedir}/miniconda
readonly condaver=4.5.11

test -d ${cachedir} || mkdir -p ${cachedir}

# Install conda if it's not already
if [[ ! -d ${cachedir}/miniconda ]]; then
    curl -sSLf -o installer.sh https://repo.continuum.io/miniconda/Miniconda3-${condaver}-Linux-x86_64.sh
    trap '{rm -rf installer.sh;}' EXIT
    bash installer.sh -b -p ${cachedir}/miniconda
fi
export PATH=${condadir}/bin:$PATH

# remove conda environment if it already exists
if conda env remove -n yori -qy &> /dev/null; then
    echo "Removed old environment"
fi

# Install test environment requirements
conda create -n yori "python=3.9" libnetcdf

# make
source activate yori
pip install -e . -r requirements.txt pytest
