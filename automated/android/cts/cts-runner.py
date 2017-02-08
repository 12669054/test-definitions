#!/usr/bin/env python

import datetime
import os
import sys
import shlex
import shutil
import subprocess
import xml.etree.ElementTree as ET
import pexpect
import argparse

sys.path.insert(0, '../../lib/')
import py_test_lib

OUTPUT = '%s/output' % os.getcwd()
RESULT_FILE = '%s/result.txt' % OUTPUT
CTS_STDOUT = '%s/cts-stdout.txt' % OUTPUT
CTS_LOGCAT = '%s/cts-logcat.txt' % OUTPUT
TEST_PARAMS = ''
SN = ''

parser = argparse.ArgumentParser()
parser.add_argument('-t', dest='TEST_PARAMS', required=True,
                    help="cts test parameters")
parser.add_argument('-n', dest='SN', required=True,
                    help='Target device serial no.')
args = parser.parse_args()
TEST_PARAMS = args.TEST_PARAMS
SN = args.SN


if os.path.exists(OUTPUT):
    suffix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    shutil.move(OUTPUT, '%s_%s' % (OUTPUT, suffix))
os.makedirs(OUTPUT)


def result_parser(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    print('Test packages in %s: %s' % (xml_file,
                                       str(len(root.findall('TestPackage')))))
    # testcase_counter = 0
    for elem in root.findall('Module'):
        # Naming: Package Name + Test Case Name + Test Name
        if 'abi' in elem.attrib.keys():
            package_name = '.'.join([elem.attrib['abi'], elem.attrib['name']])
        else:
            package_name = elem.attrib['name']

        tests_executed = len(elem.findall('.//Test'))
        tests_passed = len(elem.findall('.//Test[@result="pass"]'))
        tests_failed = len(elem.findall('.//Test[@result="fail"]'))

        result = '%s_executed pass %s' % (package_name, str(tests_executed))
        py_test_lib.add_result(RESULT_FILE, result)

        result = '%s_passed pass %s' % (package_name, str(tests_passed))
        py_test_lib.add_result(RESULT_FILE, result)

        failed_result = 'pass'
        if tests_failed > 0:
            failed_result = 'fail'
        result = '%s_failed %s %s' % (package_name, failed_result,
                                      str(tests_failed))
        py_test_lib.add_result(RESULT_FILE, result)


# Run CTS test.
cts_stdout = open(CTS_STDOUT, 'w')
# command = 'android-cts/tools/cts-tradefed ' + TEST_PARAMS
# print('Test command: %s' % command)

cts_logcat_out = open(CTS_LOGCAT, 'w')
cts_logcat_command = "adb logcat"
cts_logcat = subprocess.Popen(shlex.split(cts_logcat_command),
                              stdout=cts_logcat_out)

print('Test params: %s' % TEST_PARAMS)
test_name = TEST_PARAMS.split(' ')[3]
print('Starting CTS %s test...' % test_name)
print('Start time: %s' % datetime.datetime.now())

child = pexpect.spawn('android-cts/tools/cts-tradefed', logfile=cts_stdout)
try:
    child.expect('cts-tf >', timeout=60)
    child.sendline(TEST_PARAMS)
except pexpect.TIMEOUT:
    result = 'lunch-cts-rf-shell fail'
    py_test_lib.add_result(RESULT_FILE, result)

while child.isalive():
    adb_command = "adb -s %s shell echo 'Checking adb connectivity...'" % SN
    adb_check = subprocess.Popen(shlex.split(adb_command))
    if adb_check.wait() != 0:
        print('Terminating CTS test as adb connection is lost!')
        child.terminate(force=True)
        result = 'check-adb-connectivity fail'
        py_test_lib.add_result(RESULT_FILE, result)
        break
    else:
        # It might be an issue in lava/local dispatcher, issue in pexpect most
        # likely, it prints the messages from print() last, not by sequence.
        # Using subprocess.call() as a work around.
        # print('adb device is alive.')
        subprocess.call('echo')
        subprocess.call('date')
        subprocess.call(['echo', 'adb device is alive'])
    try:
        # Check if all tests finished every minute.
        child.expect('I/ResultReporter: Full Result:', timeout=60)
        # Once all tests finshed, exit from tf shell and throws EOF.
        child.sendline('exit')
        child.expect(pexpect.EOF, timeout=60)
    except pexpect.TIMEOUT:
        # print('%s is running...' % test_name)
        subprocess.call(['echo', test_name + ' is running...'])

print('End time: %s' % datetime.datetime.now())
cts_logcat.kill()
cts_logcat_out.close()
cts_stdout.close()

# TODO: result zip file attaching.
# locate and parse the test result
result_dir = 'android-cts/results'
test_result = 'test_result.xml'
if os.path.exists(result_dir) and os.path.isdir(result_dir):
    for root, dirs, files in os.walk(result_dir):
        for name in files:
            if name == test_result:
                result_parser(xml_file=os.path.join(root, name))
