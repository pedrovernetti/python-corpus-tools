#!/usr/bin/python3

# =============================================================================================
#
# This program is free software: you can redistribute it and/or modify it under the terms of
# the GNU General Public License as published by the Free Software Foundation, either version
# 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# This script must/should come together with a copy of the GNU General Public License. If not,
# access <http://www.gnu.org/licenses/> to find and read it.
#
# Author: Pedro Vernetti G.
# Name: clc
# Description: 
#    "clc" stands for "Continuous Line Counting" and it essentially keeps on endlessly
#    displaying the current line count of the given file, until stopped by ctrl+C or 
#    killed anyhow. Useful for monitoring the "growth" of corpora being generated in 
#    "real time" by some of the other scripts (probably) packed with this one
#
# In order to have this script working (if it is currently not), install pip (Python package
# installer) using your package manager, then, with pip, install its ...
#
# DEPENDENCIES: ***actually none***
#
# =============================================================================================

import sys, os, time

if ((len(sys.argv) > 3) or (len(sys.argv) < 2) or (not os.path.isfile(sys.argv[1]))):
    sys.stderr.write("Usage: '" + sys.argv[0] + "' FILE [LINE_OFFSET]\n")
    exit(1)

try:
    with open(sys.argv[1], 'r') as f:
        try:
            offset = 0 if (len(sys.argv) != 3) else int(sys.argv[2])
            while True:
                time.sleep(0.5)
                f.seek(0)
                for i, l in enumerate(f): pass
                sys.stdout.write("\r" + str(i + 1 + offset))
        except KeyboardInterrupt: pass
        sys.stdout.write("\r                           \r")
except:
    sys.stdout.write("?\n")
