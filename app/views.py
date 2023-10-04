import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt')
@csrf_exempt
def process_text(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        content = uploaded_file.read().decode('utf-8')
        
        # Tokenize the text content
        tokens = word_tokenize(content)
        
        # Create an inverted index
        inverted_index = {}
        for idx, token in enumerate(tokens):
            if token not in inverted_index:
                inverted_index[token] = [idx]
            else:
                inverted_index[token].append(idx)

        # Serialize and return the inverted index
        return JsonResponse({'inverted_index': inverted_index})
