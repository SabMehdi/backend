
from django.contrib import admin
from django.urls import path
from app import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/process-text/', views.process_text, name='process_text'),
    path('', views.index, name='index'),  # Add this line for the root URL
    path('api/get-file-names/', views.get_file_names, name='get_file_names'),
    path('api/get-inverted-index/<str:file_name>', views.get_inverted_index, name='get_inverted_index'),
    path('api/autocomplete/', views.autocomplete, name='autocomplete'),
    path('api/document-preview/', views.document_preview, name='document_preview'),
    path('api/search-word', views.search_word, name='search'),
    path('api/document/<int:document_id>/', views.get_document, name='get_document'),
    path('api/analyze_directory/', views.analyze_directory, name='analyze_directory'),
    path('api/get-suggestions', views.get_suggestions, name='get_suggestions'),
    path('api/process-single-file/', views.process_single_file, name='process_single_file'),

]   
