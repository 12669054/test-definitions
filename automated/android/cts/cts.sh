#!/bin/sh -e

# shellcheck disable=SC1091
. ../../lib/sh-test-lib
# shellcheck disable=SC1091
. ../../lib/android-test-lib

DEPENDENCIES="python-lxml python-setuptools python-pexpect aapt android-tools-adb android-tools-fastboot zip xz-utils libc6:i386 libncurses5:i386 libstdc++6:i386 lib32z1-dev libc6-dev-i386 lib32gcc1"
JDK="openjdk-8-jdk-headless"
JRE="openjdk-8-jre-headless"
CTS_URL="http://testdata.validation.linaro.org/cts/android-cts-7.1_r1.zip"
TEST_PARAMS="run cts -m CtsBionicTestCases --disable-reboot --skip-preconditions --skip-device-info"

while getopts ':s:' opt; do
    case "${opt}" in
        s) SKIP_INSTALL="${OPTARG}" ;;
        *) echo "Usage: $0 [-s <true|false>]" 1>&2 && exit 1 ;;
    esac
done

initialize_adb
install_deps "${DEPENDENCIES} ${JDK} ${JRE}" "${SKIP_INSTALL}"

[ -d "${OUTPUT}" ] && mv "${OUTPUT}" "${OUTPUT}_$(date +%Y%m%d%H%M%S)"
mkdir -p "${OUTPUT}"
cd "${OUTPUT}"

# Increase the heap size. KVM devices in LAVA default to ~250M of heap
export _JAVA_OPTIONS="-Xmx350M"
java -version

# TODO
# wget "${CTS_URL}"
# unzip "$(basename ${CTS_URL})"
cp -r /home/chase/Downloads/android-cts ./

./cts-runner.py "${TEST_PARAMS}"

info_msg "Processes running"
ps aux
