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
from django.db.models import Q
from django.db.models.expressions import RawSQL
from django.shortcuts import get_object_or_404
import os
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
# bibliotheque de tokenization
#nltk.download('punkt')

# Get the French stop words list
#nltk.download('stopwords')

# Define the French stop words set
french_stopwords = set(stopwords.words('french'))
nlp = spacy.load('fr_core_news_md')
# Ignore CSRF security measures


def process_text_file(file_content,file_name,file_path):
    
    if file_path.endswith('.pdf'):
        try:
            with open(file_path, 'rb') as file:  # Open in binary mode
                reader = PdfReader(file)
                text = ''
                for page in reader.pages:
                    text += page.extract_text() or ''
        except Exception as e:
            print(f"Error processing PDF file {file_path}: {e}")
            return
    elif file_path.endswith('.html') or file_path.endswith('.htm'):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')
                text = soup.get_text()  # Extract text from HTML
        except Exception as e:
            print(f"Error processing HTML file {file_path}: {e}")
            return None
    
    if(len(file_content)==0):
        content=text
    else:
        content=file_content
    # Calcul du hash du fichier
    file_hash = hashlib.sha256(file_path.encode('utf-8')).hexdigest()
    print(">>>>>>>>>> "+file_name+" <<<<<< "+ file_path)
    # Lecture et traitement des stop words
    with open('app/stop_words_french.txt', 'r', encoding='utf-8') as file:
        stop_words = set(unidecode.unidecode(word).strip().lower() for word in file)

    # Tokenisation du contenu
    tokens = word_tokenize(content, language='french')  # Utilisez le contenu original ici

    # Filtrage des stop words et des tokens non alphabétiques
    filtered_tokens = [token for token in tokens if token.isalpha() and unidecode.unidecode(token).lower() not in stop_words]

    # Initialisation de l'index inversé
    inverted_index = {}

    # Traitement de chaque token pour la lemmatisation
    for position, token in enumerate(filtered_tokens):
        doc = nlp(token.lower())  # Lemmatisation sur la version en minuscule
        for word in doc:
            if not word.pos_ == 'VERB' and not word.pos_=='AUX':
                lemma = word.lemma_
                pos = word.pos_  # Type de mot

                # Vérifiez si le lemme existe dans l'index
                if lemma not in inverted_index:
                    inverted_index[lemma] = {'positions': [position], 'pos': pos, 'original': token}  # Conservez le mot original
                else:
                    inverted_index[lemma]['positions'].append(position)

    # Sauvegarde de l'analyse du fichier
    file_analysis = FileAnalysis(file_path=file_path,file_name=file_name, file_hash=file_hash, file_content=content, inverted_index=inverted_index)
    file_analysis.save()

    return 


@csrf_exempt
def analyze_directory(request):
    directory_path = 'C:/Users/saber/Desktop/work'  # Set the directory path

    for root, _, files in os.walk(directory_path):
        for file_name in files:
            file_path = os.path.abspath(os.path.join(root, file_name))
            print(file_path)

            if file_path.endswith('.pdf'):
                # For PDF files, use a different approach
                process_text_file("", file_name,file_path)
            elif file_path.endswith('.html') or file_path.endswith('.htm'):
                # Process HTML files
                process_text_file("", file_name,file_path)
            else:
                # Process other text files
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    process_text_file(content, file_name, file_path)

    return JsonResponse({'status': 'Analysis complete'})
@csrf_exempt
def process_text(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>",uploaded_file.name)
        content = uploaded_file.read().decode('utf-8')

        # Créez une version normalisée pour le traitement des stopwords
        normalized_content = unidecode.unidecode(content).lower()

        # Calcul du hash du fichier
        file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

        # Lecture et traitement des stop words
        with open('app/stop_words_french.txt', 'r', encoding='utf-8') as file:
            stop_words = set(unidecode.unidecode(word).strip().lower() for word in file)

        # Tokenisation du contenu
        tokens = word_tokenize(content, language='french')  # Utilisez le contenu original ici

        # Filtrage des stop words et des tokens non alphabétiques
        filtered_tokens = [token for token in tokens if token.isalpha() and unidecode.unidecode(token).lower() not in stop_words]

        # Initialisation de l'index inversé
        inverted_index = {}

        # Traitement de chaque token pour la lemmatisation
        for position, token in enumerate(filtered_tokens):
            doc = nlp(token.lower())  # Lemmatisation sur la version en minuscule
            for word in doc:
                if not word.pos_ == 'VERB' and not word.pos_=='AUX':
                    lemma = word.lemma_
                    pos = word.pos_  # Type de mot

                    # Vérifiez si le lemme existe dans l'index
                    if lemma not in inverted_index:
                        inverted_index[lemma] = {'positions': [position], 'pos': pos, 'original': token}  # Conservez le mot original
                    else:
                        inverted_index[lemma]['positions'].append(position)

        # Sauvegarde de l'analyse du fichier
        file_analysis = FileAnalysis(file_name=uploaded_file, file_hash=file_hash, file_content=content, inverted_index=inverted_index)
        file_analysis.save()

        return JsonResponse({'inverted_index': inverted_index})


def index(request):
    return HttpResponse("Welcome to My Django App")


@csrf_exempt
def get_file_names(request):
    file_names = [result.file_name for result in FileAnalysis.objects.all()]
    return JsonResponse(file_names, safe=False)


@csrf_exempt
def get_inverted_index(request, file_name):
    try:
        lemmatization_result = FileAnalysis.objects.get(file_name=file_name)
        inverted_index = lemmatization_result.inverted_index  # Access the correct attribute
        return JsonResponse(inverted_index, safe=False)
    except FileAnalysis.DoesNotExist:
        return JsonResponse({'error': 'File not found'}, status=404)


# ... rest of your imports and code ...

csrf_exempt
def autocomplete(request):
    # Get the query from the request
    query = request.GET.get('q', '').lower()

    # Initialize the suggestions list
    suggestions = []

    # Search for files where the inverted_index contains the query
    results = FileAnalysis.objects.all()
    for result in results:
        # Deserialize the JSON field into a Python dictionary
        inverted_index = result.inverted_index
        # Iterate over the keys in the inverted_index to find partial matches
        for word in inverted_index.keys():
            if query in word:  # Check if the query is a substring of the word
                # Get the positions where the word occurs
                positions = inverted_index[word]
                
                # Split the file_content into words
                words = result.file_content.split()
                # Generate previews for each occurrence of the word
                previews = []
                for pos in positions:
                    # Calculate the range for words around the found position
                    start = max(0, pos - 3)
                    end = min(len(words), pos + 4)
                    # Extract the preview and join it into a string
                    preview = {'text':' '.join(words[start:end]),'position':pos}
                    print(word,pos)
                    previews.append(preview)
                # Add the result to the suggestions list
                suggestions.append({
                    'id': result.id,
                    'name': result.file_path,
                    'content_previews': previews  # List of previews
                })
                break  # Break if a match is found to avoid duplicate entries

    # Return the suggestions as JSON
    return JsonResponse(suggestions, safe=False)

@csrf_exempt
def document_preview(request):
    word = request.GET.get('word', '')
    if word:
        # Fetch documents containing the word and create previews
        documents = FileAnalysis.objects.filter(
            inverted_index__has_key=word
        )
        previews = [
            {
                'title': doc.file_path,
                'text': '...'.join(doc.inverted_index[word][:3])  # Just an example, adjust as needed
            }
            for doc in documents
        ]
        return JsonResponse(previews, safe=False)
    return JsonResponse([], safe=False)

import re

@csrf_exempt
def search_word(request):
    query = request.GET.get('q', '').lower()
    search_results = []

    results = FileAnalysis.objects.filter(file_content__icontains=query)
    for result in results:
        content_previews = []

        # Find all occurrences of the query in the file content
        start_positions = [m.start() for m in re.finditer(query, result.file_content.lower())]

        # Generate previews for each occurrence
        for pos in start_positions:
            start = max(pos - 50, 0)  # Get 20 characters before the query
            end = min(pos + 50 + len(query), len(result.file_content))  # Get 20 characters after the query
            preview = result.file_content[start:end]
            content_previews.append({
                'text': preview,
                'position': pos
            })
            print(pos)

        search_results.append({
            'id': result.id,
            'name': result.file_name,
            'path':result.file_path,
            'content_previews': content_previews
        })

    return JsonResponse(search_results, safe=False)


@csrf_exempt
def get_document(request, document_id):
    document = get_object_or_404(FileAnalysis, id=document_id)
    return JsonResponse({
        'id': document.id,
        'content': document.file_content,
        'name':document.file_name,
        'path':document.file_path,
        # include any other fields you might need
    })