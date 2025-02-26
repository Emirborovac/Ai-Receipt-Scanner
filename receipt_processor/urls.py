# receipt_processor/urls.py
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [

    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('process/', views.process_receipt, name='process_receipt'),
    path('download/', views.download_json, name='download_json'),
    
  
    path('api/process/', views.receipt_api, name='receipt_api'),
    path('api/download/', views.download_json_api, name='download_json_api'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)