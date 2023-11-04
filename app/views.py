import json
import string
import unidecode
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import spacy
import re
from django.http import HttpResponse
from .models import FileAnalysis
import hashlib

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
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        content = uploaded_file.read().decode('utf-8')

        file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        if FileAnalysis.objects.filter(file_hash=file_hash).exists():
            return JsonResponse({'error': 'File has already been analyzed'}, status=400)


        with open('app/stop_words_french.json', 'r') as json_file:
            stp_words = set(json.load(json_file))
            stp_words = set(unidecode.unidecode(word).lower() for word in stp_words)

        tokens = content.split()
        inverted_index = {}

        for position, token in enumerate(tokens):
            cleaned_token = token.lower().strip(string.punctuation)
            unaccented_token = unidecode.unidecode(cleaned_token)  # Normalize for comparison

            if cleaned_token.isalpha():
                doc = nlp(cleaned_token)
                lemma = [word.lemma_ for word in doc if not word.pos_ == 'VERB']

                if lemma:
                    lemma = lemma[0]
                    if lemma not in inverted_index:
                        inverted_index[lemma] = [position]
                    else:
                        inverted_index[lemma].append(position)

        file_analysis = FileAnalysis(file_path=uploaded_file, file_hash=file_hash,inverted_index=inverted_index)
        file_analysis.save()

        return JsonResponse({'inverted_index': inverted_index})

def index(request):
    return HttpResponse("Welcome to My Django App")


@csrf_exempt
def get_file_names(request):
    file_names = [result.file_path for result in FileAnalysis.objects.all()]
    return JsonResponse(file_names, safe=False)


@csrf_exempt
def get_inverted_index(request, file_name):
    try:
        lemmatization_result = FileAnalysis.objects.get(file_path=file_name)
        inverted_index = lemmatization_result.inverted_index  # Access the correct attribute
        return JsonResponse(inverted_index, safe=False)
    except FileAnalysis.DoesNotExist:
        return JsonResponse({'error': 'File not found'}, status=404)
