#!/bin/sh

#set -m

# shellcheck disable=SC1091
. ../../lib/sh-test-lib

OUTPUT="$(pwd)/output"
RESULT_FILE="${OUTPUT}/result.txt"

! check_root && error_msg "Please run this script as root."
[ -d "${OUTPUT}" ] && mv "${OUTPUT}" "${OUTPUT}_$(date +%Y%m%d%H%M%S)"
mkdir -p "${OUTPUT}"

trap '' TERM

detect_abi
./bin/"${abi}"/pi_stress --duration 30 --group 16
check_return 'pi-stress'
