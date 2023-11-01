
from django.contrib import admin
from django.urls import path
from app import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/process-text/', views.process_text, name='process_text'),
    path('', views.index, name='index'),  # Add this line for the root URL
    path('api/get-file-names/', views.get_file_names, name='get_file_names'),
    path('api/get-inverted-index/<str:file_name>', views.get_inverted_index, name='get_inverted_index'),

]   
