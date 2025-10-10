def q1():
    print("""# !pip install nltk pandas numpy
import pandas as pd
import nltk
import string
from nltk.tokenize import sent_tokenize, ToktokTokenizer
from nltk.corpus import stopwords
from collections import Counter

nltk.download('punkt')
nltk.download('stopwords')

#https://www.kaggle.com/datasets/hammadjavaid/football-news-articles   
#Download allfootball.csv
df = pd.read_csv("allfootball.csv", nrows=5000)
df = df[['title']].astype(str)

df['sentences'] = df['title'].apply(sent_tokenize)
punkt_st = nltk.tokenize.PunktSentenceTokenizer()
df['descriptions'] = df['title'].apply(punkt_st.tokenize)

df['text_wo_punct'] = df['title'].str.lower().str.translate(str.maketrans('', '', string.punctuation))
STOPWORDS = set(stopwords.words('english'))
df['text_wo_stop'] = df['text_wo_punct'].apply(lambda x: " ".join([w for w in x.split() if w not in STOPWORDS]))


cnt = Counter(word for text in df['text_wo_stop'] for word in text.split())
FREQWORDS = set([w for w,_ in cnt.most_common(10)])
df['text_wo_stopfreq'] = df['text_wo_stop'].apply(lambda x: " ".join([w for w in x.split() if w not in FREQWORDS]))

pd.set_option('display.max_columns', None)
df[['title','sentences','descriptions','text_wo_punct','text_wo_stop','text_wo_stopfreq']]
""")

def q2():
    print("""# !pip install pandas scikit-learn
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, TfidfVectorizer

#Dataset Link : https://www.kaggle.com/datasets/nileshmalode1/samsum-dataset-text-summarization?select=samsum-train.csv
#Download samsum-train.csv
df = pd.read_csv("samsum-train.csv", nrows=5000)  # dataset in current folder
corpus = df['summary'].astype(str)

# Bag-of-Words (unigrams)
cv = CountVectorizer()
cv_matrix = cv.fit_transform(corpus).toarray()
cv_df = pd.DataFrame(cv_matrix, columns=cv.get_feature_names_out())
cv_df.head()
# Bag-of-Words (bigrams)
bv = CountVectorizer(ngram_range=(2,2))
bv_matrix = bv.fit_transform(corpus).toarray()
bv_df = pd.DataFrame(bv_matrix, columns=bv.get_feature_names_out())
bv_df.head()
# TF-IDF from CountVectorizer + TfidfTransformer
tt = TfidfTransformer()
tt_matrix = tt.fit_transform(cv_matrix).toarray()
tt_df = pd.DataFrame(tt_matrix, columns=cv.get_feature_names_out())
# TF-IDF directly from TfidfVectorizer
tv = TfidfVectorizer()
tv_matrix = tv.fit_transform(corpus).toarray()
tv_df = pd.DataFrame(tv_matrix, columns=tv.get_feature_names_out())

tv_df""")

def q3():
    print("""# !pip install nltk pandas
import pandas as pd, nltk
from nltk.corpus import treebank
from nltk.tag import UnigramTagger, BigramTagger, TrigramTagger, RegexpTagger

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('treebank')

#Dataset Link : https://www.kaggle.com/datasets/nileshmalode1/samsum-dataset-text-summarization?select=samsum-train.csv
#Download samsum-train.csv
df = pd.read_csv("samsum-train.csv", nrows=5000)
sentence = df['dialogue'][0]
tokens = nltk.word_tokenize(sentence)

nltk_pos = nltk.pos_tag(tokens)
data = [ [w for w,_ in nltk_pos], [t for _,t in nltk_pos], [t for _,t in nltk_pos] ]
pos_table = pd.DataFrame(data, index=['Word','POS tag','Tag type'], columns=range(1,len(tokens)+1))
print(pos_table)

nltk_array = [f"{w},{t}" for w,t in nltk_pos]
print("\n".join(nltk_array))

regex = RegexpTagger([(r'.*ing$', 'VBG'), (r'.*ed$', 'VBD'), (r'.*es$', 'VBZ'),
                      (r'.*ould$', 'MD'), (r'.*\'s$', 'NN$'), (r'.*s$', 'NNS'),
                      (r'^-?[0-9]+(.[0-9]+)?$', 'CD'), (r'.*', 'NN')])
print(regex.tag(tokens))

data_tb = treebank.tagged_sents()
ut, bt, tt = UnigramTagger(data_tb[:3500]), BigramTagger(data_tb[:3500]), TrigramTagger(data_tb[:3500])
print("\n\n")
print("Unigram:", ut.tag(tokens))
print("\n\n")
print("Bigram:", bt.tag(tokens))
print("\n\n")
print("Trigram:", tt.tag(tokens))
""")

def q4():
    print("""
# !pip install pandas numpy nltk gensim scikit-learn

import pandas as pd, numpy as np, nltk, gensim
from nltk.tokenize import word_tokenize
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import SGDClassifier

nltk.download('punkt')

#Dataset Link : https://www.kaggle.com/datasets/avishi/bbc-news-train-data?select=BBC+News+Train.csv
#Download BBC News Train.csv
df = pd.read_csv("BBC News Train.csv").dropna()
X_train, X_test, y_train, y_test = train_test_split(df['Text'], df['Category'], test_size=0.33, random_state=42)

train_tokens = [word_tokenize(t) for t in X_train]
test_tokens  = [word_tokenize(t) for t in X_test]

w2v_model = gensim.models.Word2Vec(train_tokens, vector_size=1000, window=100, min_count=2, sg=1, workers=4)

def doc_vec(corpus, model, n=1000):
    vocab = set(model.wv.index_to_key)
    return np.array([np.mean([model.wv[w] for w in s if w in vocab] or [np.zeros(n)], axis=0) for s in corpus])

X_train_vec, X_test_vec = doc_vec(train_tokens, w2v_model), doc_vec(test_tokens, w2v_model)

svm = SGDClassifier(loss='hinge', penalty='l2', random_state=42, max_iter=500)
svm.fit(X_train_vec, y_train)

cv_scores = cross_val_score(svm, X_train_vec, y_train, cv=5)
print("CV Scores:", cv_scores)
print("Mean CV Accuracy:", np.mean(cv_scores))
print("Test Accuracy:", svm.score(X_test_vec, y_test))
""")
def q5():
    print( '''
# !pip install --upgrade pandas numpy nltk gensim
import pandas as pd, numpy as np, nltk, re
nltk.download('punkt'); nltk.download('stopwords')

#Dataset Link : https://www.kaggle.com/datasets/nileshmalode1/samsum-dataset-text-summarization?select=samsum-train.csv
#Download samsum-train.csv
df = pd.read_csv("samsum-train.csv")
DOCUMENT = ' '.join(df['summary']).replace('\n',' ').replace('\r',' ')
DOCUMENT = re.sub(' +',' ', DOCUMENT).strip()

print("----- ORIGINAL PASSAGE -----\n")
print(DOCUMENT[:1000], "...")

sentences = nltk.sent_tokenize(DOCUMENT)
stop_words = set(nltk.corpus.stopwords.words('english'))

def normalize(doc):
    tokens = [w.lower() for w in nltk.word_tokenize(re.sub(r'[^a-zA-Z\s]','',doc)) if w.lower() not in stop_words]
    return ' '.join(tokens)

norm_sentences = np.vectorize(normalize)(sentences)
print("\n----- NORMALIZED SENTENCES -----\n")
print(norm_sentences[:5])
''')
def q6():
    print('''# !pip install nltk gensim --upgrade

import nltk, numpy as np
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from gensim import corpora, models

nltk.download('punkt')
nltk.download('stopwords')

text = """Here's a step-by-step breakdown of the Latent Semantic Analysis (LSA) algorithm:
Latent Semantic Analysis (LSA), also known as Latent Semantic Indexing (LSI), is a 
technique in natural language processing used to analyze relationships between a set of 
documents or terms. Summarize the text by extracting important sentences based on their 
similarity scores.
Let's implement LSA for automatic text summarization using the gensim library in 
Python."""

sentences = sent_tokenize(text)

stop_words = set(stopwords.words('english'))
preprocessed_sentences = []
for sentence in sentences:
    words = [w.lower() for w in word_tokenize(sentence) if w.isalnum() and w.lower() not in stop_words]
    preprocessed_sentences.append(words)

dictionary = corpora.Dictionary(preprocessed_sentences)
corpus = [dictionary.doc2bow(sentence) for sentence in preprocessed_sentences]

lsa_model = models.LsiModel(corpus, id2word=dictionary, num_topics=2)

similarity_scores = []
for i, sentence in enumerate(sentences):
    vec_bow = dictionary.doc2bow(preprocessed_sentences[i])
    vec_lsa = lsa_model[vec_bow]
    score = sum([val[1] ** 2 for val in vec_lsa])  # squared magnitude
    similarity_scores.append((sentence, score))

summary_sentences = [s[0] for s in sorted(similarity_scores, key=lambda x: x[1], reverse=True)[:2]]

print("----- ORIGINAL TEXT -----\n")
print(text)
print("\n----- SUMMARY -----\n")
print(" ".join(summary_sentences))
''')

def q7():
    print("""# !pip install numpy pandas --upgrade

import numpy as np
import pandas as pd

def vectorize_terms(terms):
    return [np.array([ord(char) for char in term.lower()]) for term in terms]

root = 'Believe'
term1 = 'beleive'
term2 = 'bargain'
term3 = 'Elephant'
terms = [root, term1, term2, term3]

term_vectors = vectorize_terms(terms)

vec_df = pd.DataFrame(term_vectors, index=terms)
print("Vector representations of terms:\n", vec_df, "\n")

def hamming_distance(u, v, norm=False):
    if u.shape != v.shape:
        raise ValueError('Vectors must have equal lengths.')
    return (u != v).sum() if not norm else (u != v).mean()

def manhattan_distance(u, v, norm=False):
    if u.shape != v.shape:
        raise ValueError('Vectors must have equal lengths.')
    return abs(u - v).sum() if not norm else abs(u - v).mean()

def euclidean_distance(u, v):
    if u.shape != v.shape:
        raise ValueError('Vectors must have equal lengths.')
    return np.sqrt(np.sum((u - v) ** 2))

def cosine_distance(u, v):
    return 1 - (np.dot(u, v) / (np.sqrt(np.sum(u ** 2)) * np.sqrt(np.sum(v ** 2))))

root_vec = vec_df.loc[root].values
other_vecs = {term: vec_df.loc[term].values for term in [term1, term2, term3]}

distances = []
for term, vec in other_vecs.items():
    distances.append({
        'Term': term,
        'Hamming': hamming_distance(root_vec, vec, norm=True),
        'Manhattan': manhattan_distance(root_vec, vec, norm=True),
        'Euclidean': euclidean_distance(root_vec, vec),
        'Cosine': cosine_distance(root_vec, vec)
    })

dist_df = pd.DataFrame(distances).set_index('Term')
print("Distance measures relative to root term '{}':\n".format(root))
print(dist_df)""")
def q8():
    print("""# !pip install SpeechRecognition --upgrade
# !pip install pydub --upgrade

import speech_recognition as sr

print("SpeechRecognition version:", sr.__version__)

r = sr.Recognizer()

#Audio Path : https://www.kaggle.com/datasets/pavanelisetty/sample-audio-files-for-speech-recognition?select=harvard.wav
audio_file_path = "harvard.wav"
harvard = sr.AudioFile(audio_file_path)

with harvard as source:
    audio = r.record(source)

try:
    text = r.recognize_google(audio)
    print("Recognized Speech:\n", text)
except sr.UnknownValueError:
    print("Speech recognition could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e))""")


def q9():
    print("""#Delete this cell after running one time
# !curl -L -o ffmpeg.zip https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip

import zipfile
import os
import glob

with zipfile.ZipFile("ffmpeg.zip", "r") as zip_ref:
    zip_ref.extractall("ffmpeg_dir")

ffmpeg_bin_path = glob.glob("ffmpeg_dir/ffmpeg-*/bin")[0]
os.environ["PATH"] += os.pathsep + os.path.abspath(ffmpeg_bin_path)



#main code
# !pip install pydub --upgrade
from pydub import AudioSegment

#Audio Path : https://www.kaggle.com/datasets/pavanelisetty/sample-audio-files-for-speech-recognition?select=harvard.wav
audio = AudioSegment.from_file("harvard.wav")

audio.export("output_audio.mp3", format="mp3")
print("Audio file converted to MP3 format.")

start_time = 5000 
end_time = 10000
extracted_audio = audio[start_time:end_time]
extracted_audio.export("extracted_audio.wav", format="wav")
extracted_audio.export("extracted_audio.mp3", format="mp3")
print("Extracted audio saved in WAV and MP3 formats.")

louder_audio = audio + 10
louder_audio.export("louder_audio.wav", format="wav")
louder_audio.export("louder_audio.mp3", format="mp3")
print("Louder audio saved in WAV and MP3 formats.")
""")


def q10():
    print("""# !pip install SpeechRecognition pyaudio

import speech_recognition as sr

recognizer = sr.Recognizer()

with sr.Microphone() as source:
    print("Listening...")
    recognizer.adjust_for_ambient_noise(source)
    audio_data = recognizer.listen(source)
    print("Processing...")

try:
    text = recognizer.recognize_google(audio_data)
    print("Recognized speech:", text)
except sr.UnknownValueError:
    print("Sorry, I couldn't understand what you said.")
except sr.RequestError as e:
    print("Error accessing Google Web Speech API:", e)
""")