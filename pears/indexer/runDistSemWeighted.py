""" Make page representation as the WEIGHTED sum of the most 'important'
words in the page (obtained via entropy calculation)
"""

import math
import os
import re
import sys

import numpy as np
from pears.utils import load_entropies, normalise, cosine_similarity, readDM
from pears.models import Urls
from pears import app, db
from ast import literal_eval

num_dimensions = 400
stopwords = ["", "(", ")", "a", "about", "an", "and", "are", "around", "as", "at", "away", "be", "become", "became",
             "been", "being", "by", "did", "do", "does", "during", "each", "for", "from", "get", "have", "has", "had",
             "he", "her", "his", "how", "i", "if", "in", "is", "it", "its", "made", "make", "many", "most", "not", "of",
             "on", "or", "s", "she", "some", "that", "the", "their", "there", "this", "these", "those", "to", "under",
             "was", "were", "what", "when", "where", "which", "who", "will", "with", "you", "your"]

entropies_dict=load_entropies()

def weightFile(buff):
    word_dict = {}
    words = buff.split()
    for w in words:
        w = w.lower()
        if w in entropies_dict and w not in stopwords:
            if w in word_dict:
                word_dict[w] += 1
            else:
                word_dict[w] = 1
    for k, v in word_dict.items():
        if math.log(entropies_dict[k] + 1) > 0:
            word_dict[k] = float(v) / float(math.log(entropies_dict[k] + 1))
    return word_dict


def mkVector(word_dict, dm_dict):
  """ Make vectors from weights """
  vbase = np.zeros(num_dimensions)
  wordcloud = ""
  # Add vectors together
  if len(word_dict) > 0:
    c = 0
    for w in sorted(word_dict, key=word_dict.get, reverse=True):
      if c < 10:
        if w in dm_dict:
          vbase = vbase + float(word_dict[w]) * np.array(dm_dict[w])
          wordcloud+=w+" "
          c += 1

    vbase = normalise(vbase)

  # Make string version of document distribution
  doc_dist_str = ""
  for n in vbase:
    doc_dist_str = doc_dist_str + "%.6f" % n + " "

  return doc_dist_str, wordcloud[:-1]


def runScript():
    urls = Urls.query.all()
    dm_dict = readDM()
    buff = ""
    line_counter = 0
    for l in urls:
      if l.body != "--processed--":
        url = l.url
        title = l.title
        buff = l.body
        v = weightFile(buff)
        s,wordcloud = mkVector(v, dm_dict)
        l.wordclouds = wordcloud
        l.dists = s
        l.body = unicode("--processed--")
    db.session.commit()


# when executing as script
if __name__ == '__main__':
    runScript() 