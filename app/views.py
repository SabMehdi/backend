import json
import string
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import spacy
import re
from django.http import HttpResponse
from .models import FileAnalysis
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

        token_pattern =r"\w+(?:-\w+)*|\."

        
        tokens = list(enumerate(re.findall(token_pattern, content)))
        #print(tokens)

        lemmas = {}
       # content = content.translate(str.maketrans('', '', string.punctuation))

        with open('app\stop_words_french.json', 'r') as json_file:
            stp_words = set(json.load(json_file))
        inverted_index = {}
        for idx, (position, token) in enumerate(tokens):
            token=token.lower()
            if token not in stp_words and token not in ['»', '«', 'à'] and token not in string.punctuation and token.isalpha():
                doc = nlp(token)
                for word in doc:
                    if(not word.pos_=='VERB'):
                        lemmas[word.text] = word.lemma_
                for token, lemma in lemmas.items():
                    #print(f"{token} : {lemma}")
                    if lemma not in inverted_index:
                        inverted_index[lemma] = [position]
                    else:
                        inverted_index[lemma].append(position)
            lemmas.clear() 
        file_analysis = FileAnalysis(file_path=uploaded_file, inverted_index=inverted_index)
        file_analysis.save()          
        return JsonResponse({'inverted_index': inverted_index})

def index(request):
    return HttpResponse("Welcome to My Django App")

@csrf_exempt
def get_file_names(request):
    file_names = [result.file_path for result in FileAnalysis.objects.all()]
    print(file_names)
    return JsonResponse(file_names, safe=False)
    
@csrf_exempt
def get_inverted_index(request, file_name):
    try:
        lemmatization_result = FileAnalysis.objects.get(file_path=file_name)
        inverted_index = lemmatization_result.inverted_index  # Access the correct attribute
        print(inverted_index)  # This line is for debugging
        return JsonResponse(inverted_index, safe=False)
    except FileAnalysis.DoesNotExist:
        return JsonResponse({'error': 'File not found'}, status=404)
