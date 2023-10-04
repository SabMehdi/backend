import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from nltk.tokenize import word_tokenize
import nltk

#bibliotheque de tokenization
nltk.download('punkt')
#ignorer les mesures de securité csrf
@csrf_exempt
def process_text(request):
    if request.method == 'POST':

        #lecture des données depuis la méthode POST en assument que le fichier=file
        uploaded_file = request.FILES['file']
        
        #transformation du binaire vers string
        content = uploaded_file.read().decode('utf-8')
        
        # transformation du texte vers des tokens (tokenize the text), le resultat est une liste de mots
        tokens = word_tokenize(content)
        
        # creation du inverted index
        inverted_index = {} #dictionnaire
        for idx, token in enumerate(tokens):
            if token not in inverted_index:
                inverted_index[token] = [idx]
            else:
                inverted_index[token].append(idx)

        # Serialisation et renvoie de inverted_index
        return JsonResponse({'inverted_index': inverted_index})
