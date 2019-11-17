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
# Name: tweetsByLanguage
# Description: 
#    Given an initial Twitter user and a language, it endlessly looks for tweets in the
#    given language, downloading and storing each one - preprocessed, normalized and
#    anonymized - as single line in a file named "tweets_{language}" (always appending)
#    (Stop it with ctrl+C)
#
# In order to have this script working (if it is currently not), install pip (Python package
# installer) using your package manager, then, with pip, install its ...
#
# DEPENDENCIES: lxml, twitter_scraper, nltk, iso-639, polyglot.
#
# =============================================================================================

import sys, os, re, math, random, traceback
from pickle import dump as dumpPickle, load as loadPickle, PickleError
from unicodedata import category as ucategory, normalize as unormalize
from urllib.request import urlopen
from urllib.error import HTTPError
from lxml import etree
from twitter_scraper import get_tweets as getTweets
from nltk.tokenize import word_tokenize as tokenize
from iso639 import languages as ISO639
from polyglot.detect import base as langId

junk = {r'Cc', r'Cf', r'Co', r'Cs', r'Zl', r'Zp', r'Zs'}
_s = '\t \n\r\f\v'
def isJunk( c ): return ((ucategory(chr(c)) in junk) or (chr(c) in _s))
junkToSpace = dict.fromkeys(i for i in range(sys.maxunicode) if (isJunk(i)))
junkToSpace = {cat:r' ' for cat in junkToSpace}
twitterUserRegex = r'@[0-9A-Za-z_]{1,15}'

def saveEverything( tweets, previousTweets, language ):
    with open(('.visited_tweets_' + language), 'wb') as pickle:
        dumpPickle(previousTweets, pickle, protocol=2)
    random.shuffle(tweets)
    buffer = "Saving " + str(len(tweets)) + " tweets..."
    sys.stdout.write("\r\x1B[0m" + buffer.ljust(78, r' ') + "\n")
    outputFile = open('tweets_' + language, 'a')
    for t in tweets: outputFile.write(t + '\n')
    outputFile.close()

def fullUserName( user ):
    try:
        full = urlopen(r'https://twitter.com/' + user).read().decode('utf-8')
        full = etree.fromstring(full, etree.HTMLParser()).xpath(r'.//a[@href="/' + user + r'"]')
        if (len(full) < 1): return r''
        else: return full[0].text.strip()
    except:
        return "";
        
def userExists( user ):
    try: urlopen(r'https://twitter.com/' + currentUser)
    except HTTPError: return False
    except: pass
    return True

def treatedTweet( tweetText ):
    result = unormalize('NFC', tweetText.translate(junkToSpace))
    return re.sub(r'\s+', r' ', re.sub('\uFFFD+', r'', result)).strip()
    
def anonymizedTweet( treatedtweetText, user ):
    result = re.sub(r'pic\.twitter\.com/[^\s]*', r' pic.twitter.com/ ', treatedtweetText)
    result = re.sub('https?://[^\s]+', r' https://t.co/ ', result)
    result = re.sub(twitterUserRegex, r' @ ', result)
    result = re.sub(re.sub(r'_+', r'[\W_]+', user), r'___', result, flags=re.IGNORECASE)
    fullName = fullUserName(user)
    if (len(re.findall(r'[^\W0-9_]', fullName)) < 2): return re.sub(r'\s+', r' ', result).strip()
    fullName = re.sub(r'[\W_]+', r'_', fullName.translate(junkToSpace))
    fullNameRegex = re.sub(r'[\W_]+', r'[\W_]+', fullName.translate(junkToSpace))
    #fullNameParts = [part for part, _ in re.findall(r'([^\W\d_]([^\W_]*[^\W\d_])?)', fullName)]
    result = re.sub(fullNameRegex, r'___', result, flags=re.IGNORECASE)
    #for part in fullNameParts: 
    #    result = re.sub(part, r'___', result, flags=re.IGNORECASE)
    return re.sub(r'\s+', r' ', result).strip()
    
def isDesiredLanguage( anonymizedTweetText, language ):
    try:
        tmpText = re.sub(r'#\w+', r'', re.sub(r'https://t\.co/', r'', anonymizedTweetText))
        tmpText = re.sub(r'pic\.twitter\.com/', r'', tmpText)
        detectedLanguage = langId.cld2.detect(tmpText)[2][0][1]
        if (detectedLanguage == r'un'): return False #random.choice([True, False, False])
        if (not (len(detectedLanguage) == 2)): return (detectedLanguage == language)
        else: return (ISO639.get(part1=detectedLanguage).part2b == language)
    except:
        return False
    
def mentionedUsers( treatedtweetText ):
    mentioned = [u[1:] for u in re.findall(twitterUserRegex, treatedtweetText)]
    for user in mentioned: 
        user = re.sub(r'pic\.twitter\.com.*$', r'', user).lower()
    return set(mentioned)

if ((len(sys.argv) > 4) or (len(sys.argv) < 3) or (not (sys.argv[-1] in ISO639.part1))):
    sys.stderr.write("Usage: '" + sys.argv[0] + "' [TWEET_COUNT_TO_AUTOSAVE] INITIAL_USER LANGUAGE")
    exit(1)
user = sys.argv[-2].strip()
if (user.startswith((r'http', r'twitter.com'))): user = user.split('/')[-1].strip()
elif (user.startswith(r'@')): user = user[1:].strip()
lang = sys.argv[-1].casefold().strip()
if ((len(lang) > 3) and (lang.title() in ISO639.name)): 
    lang = ISO639.get(name=lang.title()).part2b
howMuchToAutoSave = 200 if (len(sys.argv) < 4) else int(sys.argv[-3])

previousTweets = set()    
if (os.path.isfile('.visited_tweets_' + lang)): 
    with open(('.visited_tweets_' + lang), 'rb') as pickle: 
        try: previousTweets = loadPickle(pickle)
        except: pass
try:
    tweets = []
    usersPool = {user}
    n = 9999
    while (len(usersPool) > 0):
        currentUser = random.sample(usersPool, 1)[0]
        usersPool.discard(currentUser)
        if (not userExists(currentUser)): continue
        sys.stdout.write("@" + currentUser + " ...\n")
        try: 
            for t in getTweets(currentUser, n):
                tweet = treatedTweet(t['text'])
                usersPoolBuffer = mentionedUsers(tweet)
                if (t['tweetId'] in previousTweets): continue
                previousTweets.add(t['tweetId'])
                tweet = anonymizedTweet(tweet, user)
                if (not isDesiredLanguage(tweet, lang)): continue
                usersPool = usersPool.union(usersPoolBuffer)
                tweets += [tweet]
                buffer = "@" + currentUser + ": " + tweet
                if (len(buffer) > 80): buffer = buffer[:77] + "..."
                sys.stdout.write("\r" + buffer.ljust(78, r' ') + "\n")
                sys.stdout.write(str(len(tweets)) + " tweets, ")
                sys.stdout.write(str(len(usersPool)) + " queued users... ")
                sys.stdout.flush()
        except (etree.Error, IndexError, ValueError): pass
        sys.stdout.write("\n")
        n = 10
        if (len(tweets) > howMuchToAutoSave):
            saveEverything(tweets, previousTweets, lang)
            tweets = []
except KeyboardInterrupt:
    sys.stdout.write("\r" + str(len(tweets)) + " tweets, ")
    sys.stdout.write(str(len(usersPool)) + " queued users\nDone.\n")
except Exception as e:
    sys.stdout.write("\r" + str(len(tweets)) + " tweets, ")
    sys.stdout.write(str(len(usersPool)) + " queued users\n\x1B[2m")
    traceback.print_last()
    
sys.stdout.flush()
saveEverything(tweets, previousTweets, lang)

