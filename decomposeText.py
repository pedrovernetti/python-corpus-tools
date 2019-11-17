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
# Name: decomposeText
# Description: 
#    Turns a text file into a shuffled sequence of its original words, all normalized and
#    casefolded IN-PLACE (so be careful, back things up...), also removing everything that
#    doesn't seem like a word in the strict sense (a sequence of letters, essentially)
#    If argument passed is " - ", it does the same thing to input received through a pipe
#    and prints the result to the standard output
#    (The frequency of each word remains the same through the process)
#
# In order to have this script working (if it is currently not), install pip (Python package
# installer) using your package manager, then, with pip, install its ...
#
# DEPENDENCIES: nltk, hangul_jamo
#
# =============================================================================================

import sys, re, random
from unicodedata import category as ucategory, normalize
from nltk.tokenize import word_tokenize as tokenize
import hangul_jamo

ucats = {r'Cc', r'Cf', r'Co', r'Cs', r'Pe', r'Po', r'Ps', r'Nd', r'Sc', r'Sm', r'So', r'Zl', r'Zp'}
junkToSpace = dict.fromkeys(i for i in range(sys.maxunicode) if (ucategory(chr(i)) in ucats))
junkToSpace = { cat:r' ' for cat in junkToSpace}

def isGoodToken( token ):
    #if (ucategory(token[0]) in {r'Lt', r'Lu'} and (lang != 'de')): return False
    if ((ucategory(token[0])[0] != r'L') and (ucategory(token[-1])[0] != r'L')): return False
    return token

if ((len(sys.argv) != 2) or ((not os.path.isfile(sys.argv[1]) and (sys.argv[1] != r'-')))):
    sys.stderr.write("Usage: '" + sys.argv[0] + "' TEXT_FILE|-\n")
    exit(1)
elif (sys.argv[1] == r'-'):
    bulk = sys.stdin.buffer.read().decode(errors='ignore').translate(junkToSpace)
    bulk = hangul_jamo.decompose(normalize('NFC', bulk.casefold()))
    bulk = [t for t in tokenize(re.sub(r'\s+', r' ', bulk)) if isGoodToken(t)]
    out = sys.__stdout__
else:  
    bulk = re.sub(r'\s+', r' ', open(sys.argv[1], 'rb').read().decode(errors='ignore'))
    bulk = [t for t in tokenize(bulk.translate(junkToSpace).casefold()) if isGoodToken(t)]
    bulk = [hangul_jamo.decompose(t) for t in bulk]
    out = open(sys.argv[1], 'w')
  
random.shuffle(bulk)
sys.stderr.write(str(len(bulk)) + "\n")
out.write(re.sub(r'\s+', r' ', (r' ' + r' '.join(bulk) + r' ')))

