from nltk.probability import FreqDist
from nltk.corpus import stopwords
import nltk.tag, nltk.util, nltk.stem
import re
import math
from decimal import *
import sys
import json
import string
from nltk.tokenize import SpaceTokenizer, WhitespaceTokenizer
from bs4 import BeautifulSoup
import string
import re
from TextStatistics import TextStatistics


porter = nltk.PorterStemmer()

# List of Personal Words from LIWC dictionary
with open("personal.txt") as f:
    personal_words = f.read().splitlines()

def NormalizeContraction(text):
    text = text.replace("can't", "can not")
    text = text.replace("couldn't", "could not")
    text = text.replace("don't", "do not")
    text = text.replace("didn't", "did not")
    text = text.replace("doesn't", "does not")
    text = text.replace("shouldn't", "should not")
    text = text.replace("haven't", "have not")
    text = text.replace("aren't", "are not")
    text = text.replace("weren't", "were not")
    text = text.replace("wouldn't", "would not")
    text = text.replace("hasn't", "has not")
    text = text.replace("hadn't", "had not")
    text = text.replace("won't", "will not")
    text = text.replace("wasn't", "was not")
    text = text.replace("can't", "can not")
    text = text.replace("isn't", "is not")
    text = text.replace("ain't", "is not")
    text = text.replace("it's", "it is")
    text = text.replace("i'm", "i am")
    text = text.replace("i'm", "i am")
    text = text.replace("i've", "i have")
    text = text.replace("i'll", "i will")
    text = text.replace("i'd", "i would")
    text = text.replace("we've", "we have")
    text = text.replace("we'll", "we will")
    text = text.replace("we'd", "we would")
    text = text.replace("we're", "we are")
    text = text.replace("you've", "you have")
    text = text.replace("you'll", "you will")
    text = text.replace("you'd", "you would")
    text = text.replace("you're", "you are")
    text = text.replace("he'll", "he will")
    text = text.replace("he'd", "he would")
    text = text.replace("he's", "he has")
    text = text.replace("she'll", "she will")
    text = text.replace("she'd", "she would")
    text = text.replace("she's", "she has")
    text = text.replace("they've", "they have")
    text = text.replace("they'll", "they will")
    text = text.replace("they'd", "they would")
    text = text.replace("they're", "they are")
    text = text.replace("that'll", "that will")
    text = text.replace("that's", "that is")
    text = text.replace("there's", "there is")
    return text

def CleanAndTokenize(text):
    # Strip URLs and replace with token "URLURLURL"
    r = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
    text = re.sub(r, " URLURLURL", text)
    # Strip html tags
    soup = BeautifulSoup(text)
    for tag in soup.findAll(True):
        tag.replaceWithChildren()
        text = soup.get_text()
    # Normalize everything to lower case
    text = text.lower()
    # Strip line breaks and endings \r \n
    r = re.compile(r"[\r\n]+")
    text = re.sub(r, "", text)
    # get rid of em dashes
    # table = {
    #     ord(u'\u2018') : u"'",
    #     ord(u'\u2019') : u"'",
    #     ord(u'\u201C') : u'"',
    #     ord(u'\u201d') : u'"',
    #     ord(u'\u2026') : u'',
    #     ord(u'\u2014') : u'',
    # }
    # text = text.translate(table)

    # Normalize contractions
    # e.g. can't => can not, it's => it is, he'll => he will
    text = NormalizeContraction(text)

    # Strip punctuation (except for a few)
    punctuations = string.punctuation
    # includes following characters: !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~
    excluded_punctuations = ["$", "%"]
    for p in punctuations:
        if p not in excluded_punctuations:
            text = text.replace(p, " ")

    # Condense double spaces
    text = text.replace("  ", " ")

    # Tokenize the text
    tokenizer = WhitespaceTokenizer()
    text_tokens = tokenizer.tokenize(text)
    return text_tokens



def escape_string(string):
    res = string
    res = res.replace('\\','\\\\')
    res = res.replace('\n','\\n')
    res = res.replace('\r','\\r')
    res = res.replace('\047','\134\047') # single quotes
    res = res.replace('\042','\134\042') # double quotes
    res = res.replace('\032','\134\032') # for Win32
   
    return res

def error_name():
    exc_type, exc_obj, exc_tb = sys.exc_info()
    msg = str(exc_type)
    error = re.split(r'[.]',msg)
    error = re.findall(r'\w+',error[1])
    error_msg = str(error[0])
    return error_msg



def calcPersonalXPScore(comment_text):
    # comment_text = comment_text.decode("utf-8")
    # tokenizer = WhitespaceTokenizer()
    personal_xp_score = 0
    text = comment_text.lower()

    #filter out punctuations
    punctuations = string.punctuation # includes following characters: !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~
    excluded_punctuations = ["$", "%", "'"]
    for p in punctuations:
        if p not in excluded_punctuations:
            text = text.replace(p, " ")

    # tokenize it
    token_list = CleanAndTokenize(comment_text)
    text_tokens = token_list
    # comment_stemmed_tokens = [porter.stem(token) for token in token_list]
    # if the tokens are in the personal_words List then increment score
    for tok in text_tokens:
        tok_stem = porter.stem(tok)
        if tok_stem in personal_words:
            personal_xp_score = personal_xp_score + 1

    # normalize by number of tokens
    if len(text_tokens) > 0:
        personal_xp_score = float(personal_xp_score) / float(len(text_tokens))
    else:
        personal_xp_score = 0.0
    return personal_xp_score

def calcReadability(comment_text):

    textstat = TextStatistics("")
    text = comment_text.lower()

    #filter out punctuations
    punctuations = string.punctuation # includes following characters: !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~
    excluded_punctuations = ["$", "%", "'"]
    for p in punctuations:
        if p not in excluded_punctuations:
            text = text.replace(p, " ")

    readability_score = textstat.smog_index(text=text)
    return readability_score

def calcLength(comment_text):
    token = CleanAndTokenize(comment_text)
    return len(token)



