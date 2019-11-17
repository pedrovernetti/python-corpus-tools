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
# Name: NGrams
# Description:
#    Prints a list of the top letter N-Grams (3-Grams by default) (with count) from the 
#    given text (last argument), which can be a text file or " - " (to read from pipe)
#
# In order to have this script working (if it is currently not), install pip (Python package
# installer) using your package manager, then, with pip, install its ...
#
# DEPENDENCIES: nltk.
#
# =============================================================================================

import sys, os, re
from unicodedata import category as ucategory, normalize
from nltk.tokenize import word_tokenize as tokenize

ucats = {r'Cc', r'Cf', r'Co', r'Cs', r'Pe', r'Po', r'Ps', r'Nd', r'Sc', r'Sm', r'So', r'Zl', r'Zp'}
junkToSpace = dict.fromkeys(i for i in range(sys.maxunicode) if (ucategory(chr(i)) in ucats))
junkToSpace = { cat:r' ' for cat in junkToSpace}

argc = len(sys.argv)
if ((argc > 4) or (argc < 3) or ((not os.path.isfile(sys.argv[-1]) and (sys.argv[-1] != r'-')))):
    sys.stderr.write("Usage: '" + sys.argv[0] + "' [N] HOW_MANY TEXT_FILE|-\n")
    exit(1)
elif (sys.argv[-1] == r'-'): bulk = sys.stdin.buffer.read().decode(errors='ignore')
else: bulk = open(sys.argv[-1], 'rb').read().decode(errors='ignore')
bulk = re.sub(r'\s+', r' ', normalize('NFC', bulk.translate(junkToSpace)).casefold())
bulk = [re.sub(r'\s+', '_', (' ' + t + ' ')) for t in tokenize(bulk.strip())]
try: howMany = int(sys.argv[-2])
except ValueError: howMany = 1
N = 3 if (argc < 4) else int(sys.argv[-3])
N = N if (N > 0) else 3

ngrams = dict()

for i in bulk:
    for j in range(0, (len(i) - (N - 1))):
        ngram = i[j:(j+N)]
        if (ngrams.get(ngram)): ngrams[ngram] += 1
        else: ngrams[ngram] = 1

ngrams = [(freq, ngram) for ngram, freq in ngrams.items() if (not '-' in ngram)]
ngrams = sorted(ngrams, reverse=True)
for i in ngrams[0:howMany]: print (i[1] + " : " + str(i[0]))
    
