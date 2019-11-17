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
# Name: topWords
# Description: 
#    Prints a list of the top occurring words (with count) from the given text
#    (last argument), which can be a text file or " - " (to read from pipe)
#
# In order to have this script working (if it is currently not), install pip (Python package
# installer) using your package manager, then, with pip, install its ...
#
# DEPENDENCIES: nltk.
#
# =============================================================================================

import os, sys, re
from unicodedata import category as ucategory, normalize
from nltk.tokenize import word_tokenize as tokenize

ucats = {r'Cc', r'Cf', r'Co', r'Cs', r'Pe', r'Po', r'Ps', r'Nd', r'Sc', r'Sm', r'So', r'Zl', r'Zp'}
junkToSpace = dict.fromkeys(i for i in range(sys.maxunicode) if (ucategory(chr(i)) in ucats))
junkToSpace = { cat:r' ' for cat in junkToSpace}

argc = len(sys.argv)
if ((argc != 3) or ((not os.path.isfile(sys.argv[-1]) and (sys.argv[-1] != r'-')))):
    sys.stderr.write("Usage: '" + sys.argv[0] + "' HOW_MANY TEXT_FILE|-\n")
    exit(1)
elif (sys.argv[-1] == r'-'): bulk = sys.stdin.buffer.read().decode(errors='ignore')
else: bulk = open(sys.argv[-1], 'rb').read().decode(errors='ignore')
bulk = re.sub(r'\s+', r' ', normalize('NFC', bulk.translate(junkToSpace)).casefold())
bulk = tokenize(bulk.strip())
try: howMany = int(sys.argv[-2])
except ValueError: howMany = 1

topWords = dict()

maxLength = 0
for word in bulk:
    if (topWords.get(word)): topWords[word] += 1
    else: topWords[word] = 1
    
topWords = sorted([(freq, word) for word, freq in topWords.items()], reverse=True)

for freq, word in topWords[0:howMany]:
    if (maxLength < len(word)): maxLength = len(word)
for i in topWords[0:howMany]: print (i[1].ljust(maxLength) + " : " + str(i[0]))

