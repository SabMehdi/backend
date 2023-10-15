import json
import string
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import spacy
# bibliotheque de tokenization
# nltk.download('punkt')

# Get the French stop words list
# nltk.download('stopwords')

# Define the French stop words set
french_stopwords = set(stopwords.words('french'))
nlp = spacy.load('fr_core_news_md')
# Ignore CSRF security measures


@csrf_exempt
def process_text(request):
    contractions = ["l'", "d'", "j'", "m'", "n'", "s'", "t'", "qu'"]
    if request.method == 'POST':

        uploaded_file = request.FILES['file']

        content = uploaded_file.read().decode('utf-8')

        tokens = list(enumerate(word_tokenize(content)))
        lemmas = {}
       # content = content.translate(str.maketrans('', '', string.punctuation))

        with open('app\stop_words_french.json', 'r') as json_file:
            stp_words = set(json.load(json_file))

        inverted_index = {}
        for idx, (position, token) in enumerate(tokens):
            for item in contractions:  # suppression des détermiants
                if token.startswith(item):
                    token = token[len(item):]
            if token.lower() not in stp_words and token.lower() not in ['»', '«', 'à'] and token.lower() not in string.punctuation:
                doc = nlp(token)
                for word in doc:
                    lemmas[word.text] = word.lemma_
                for token, lemma in lemmas.items():
                   # print(f"{token} : {lemma}")
                    if lemma not in inverted_index:
                        inverted_index[lemma] = [position]
                    else:
                        inverted_index[lemma].append(position)
            lemmas.clear()            
           
        return JsonResponse({'inverted_index': inverted_index})
