#!/usr/bin/env python
# pi_stress checks Priority Inheritence Mutexes and their ability to avoid
# Priority Inversion from occuring by running groups of threads that cause
# Priority Inversions.

import os
import sys
import argparse
import datetime
import shutil
import signal
from subprocess import call
import subprocess

sys.path.insert(0, '../../lib/')
import py_test_lib

WD = os.getcwd()
OUTPUT = '%s/output' % WD
RESULT_FILE = '%s/result.txt' % OUTPUT

parser=argparse.ArgumentParser()
parser.add_argument('-d', dest='DURATION', default='300',
                    help='length of the test run in seconds' )
parser.add_argument('-m', dest='mlockall', default=False, action='store_true',
                    help='lock current and future memory')
parser.add_argument('-r', dest='rr', default=False, action='store_true',
                    help='use SCHED_RR for test threads')
args = parser.parse_args()

if os.geteuid() != 0:
    print('ERROR: please run this script with root.')
    sys.exit(1)
if os.path.exists(OUTPUT):
    suffix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')    
    shutil.move(OUTPUT, '%s_%s' %(OUTPUT, suffix))
os.makedirs(OUTPUT)

ABI = py_test_lib.detect_abi()
command = ['./bin/%s/pi_stress' % ABI, '--duration', args.DURATION]
if args.mlockall:
    command.append('--mlockall')
if args.rr:
    command.append('--rr')
command.append('--group')
command.append('16')
print('Test command: %s\n' % command)

# Trap and ignore SIGTERM when pi_stress test fails.
signal.signal(signal.SIGTERM, signal.SIG_IGN)

# Test run.
if call(command) == 0:
    py_test_lib.add_result(RESULT_FILE, 'pi-stress pass')
else:
    py_test_lib.add_result(RESULT_FILE, 'pi-stress fail')
