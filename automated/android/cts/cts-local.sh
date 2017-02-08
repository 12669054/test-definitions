#!/bin/sh -e

# shellcheck disable=SC1091
. ../../lib/sh-test-lib
# shellcheck disable=SC1091
. ../../lib/android-test-lib

JDK="openjdk-8-jdk-headless"
JRE="openjdk-8-jre-headless"
CTS_URL="http://testdata.validation.linaro.org/cts/android-cts-7.1_r1.zip"
TEST_PARAMS="run cts -m CtsBionicTestCases --disable-reboot --skip-preconditions --skip-device-info"
PKG_DEPS="wget zip xz-utils python-lxml python-setuptools python-pexpect aapt android-tools-adb android-tools-fastboot libc6:i386 libncurses5:i386 libstdc++6:i386 lib32z1-dev libc6-dev-i386 lib32gcc1"

usage() {
    echo "Usage: $0 [-s <true|false>] [-n serialno] [-d jdk-version] [-r jre-version] [-c cts_url] [-t test_params]" 1>&2
    exit 1
}

while getopts ':s:n:d:r:c:t:' opt; do
    case "${opt}" in
        s) SKIP_INSTALL="${OPTARG}" ;;
        n) SN="${OPTARG}" ;;
        d) JDK="${OPTARG}" ;;
        r) JRE="${OPTARG}" ;;
        c) CTS_URL="${OPTARG}" ;;
        t) TEST_PARAMS="${OPTARG}" ;;
        *) usage ;;
    esac
done

test -z "${SN}" && export SN
initialize_adb

install_deps "${PKG_DEPS} ${JDK} ${JRE}" "${SKIP_INSTALL}"

# Increase the heap size. KVM devices in LAVA default to ~250M of heap
export _JAVA_OPTIONS="-Xmx350M"
java -version

if [ -d android-cts ]; then
    if [ -d android-cts/results ]; then
        mv android-cts/results "android-cts/results_$(date +%Y%m%d%H%M%S)"
    fi
else
    cp -r /home/chase/Downloads/android-cts ./
fi

./cts-runner.py -t "${TEST_PARAMS}" -n "${SN}"
