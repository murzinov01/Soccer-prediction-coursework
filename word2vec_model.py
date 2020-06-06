import csv
import numpy as np
import pandas as pd
import seaborn as sb
import random
from gensim.test.utils import common_texts, get_tmpfile
from gensim.models import Word2Vec
from data_analytics import EmbeddingData as ed
import multiprocessing

# WORD2VEC
cores = multiprocessing.cpu_count() # Count the number of cores in a computer

assembler = ed()
assembler.make_sentences_list("Premier League (England)")
sentences = assembler.DATA

# w2v_model = Word2Vec(sentences, size=80, window=10, min_count=1, workers=4)
# w2v_model.save("w2v.model")
# w2v_model.build_vocab(sentences, progress_per=10000)

# w2v_model.train(sentences, total_examples=w2v_model.corpus_count, epochs=30)

w2v_model = Word2Vec.load("PL.model")
print("david_de_gea ", w2v_model.wv.most_similar(positive=["david_de_gea"]))
print("mohamed_salah ", w2v_model.wv.most_similar(positive=["mohamed_salah"]))
print("mesut_özil ", w2v_model.wv.most_similar(positive=["mesut_özil"]))
print("david_silva ", w2v_model.wv.most_similar(positive=["david_silva"]))

print("Simular: ", w2v_model.wv.similarity("david_de_gea", "fred"))
print("Not simular: ", w2v_model.wv.similarity("david_de_gea", "aymeric_laporte"))
print("Cesc Fàbregas and De Gea: ", w2v_model.wv.similarity("david_de_gea", "cesc_fàbregas"))

print("De Gea: ", w2v_model.wv['david_de_gea'])
print("Pogba: ", w2v_model.wv['paul_pogba'])
print("Salah: ", w2v_model.wv['mohamed_salah'])
print("Firmino: ", w2v_model.wv['roberto_firmino'])