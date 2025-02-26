import base64
import json
import os
import logging
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import barcode
from barcode.writer import ImageWriter
import uuid
from concurrent.futures import ThreadPoolExecutor
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from openai import OpenAI


def index(request):
    """Render the main page"""
    return render(request, 'core/index.html')

def detect_and_generate_barcode(image_path):
    """Process barcode detection and generation"""
    try:
       
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        barcodes = decode(gray)
        
        for barcode_data in barcodes:
            barcode_text = barcode_data.data.decode("utf-8")
            
           
            barcode_filename = f"barcode_{uuid.uuid4()}.png"
            barcode_path = os.path.join(settings.MEDIA_ROOT, 'barcodes', barcode_filename)
            
            
            os.makedirs(os.path.dirname(barcode_path), exist_ok=True)
            
           
            barcode_type = "code128"
            generated_barcode = barcode.get_barcode_class(barcode_type)(
                barcode_text, writer=ImageWriter()
            )
            
            
            generated_barcode.save(barcode_path.replace(".png", ""), 
                                 {"write_text": False})
            
            return {
                'barcode_text': barcode_text,
                'barcode_path': f'/media/barcodes/{barcode_filename}'
            }
        
        return None
        
    except Exception as e:
        
        return None

@csrf_exempt
def process_receipt(request):
    """Handle receipt upload and processing"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    if 'receipt' not in request.FILES:
        return JsonResponse({'error': 'No receipt file provided'}, status=400)
    
    receipt_file = request.FILES['receipt']
    
    
    if receipt_file.size > settings.MAX_UPLOAD_SIZE:
        return JsonResponse({
            'error': f'File too large. Maximum size is {settings.MAX_UPLOAD_SIZE/1024/1024}MB'
        }, status=400)
    
    try:
        
        file_path = default_storage.save(
            f'receipts/{receipt_file.name}',
            ContentFile(receipt_file.read())
        )
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        
       
        with ThreadPoolExecutor() as executor:
            future_openai = executor.submit(process_with_openai, full_path)
            future_barcode = executor.submit(detect_and_generate_barcode, full_path)
            
            try:
               
                result = future_openai.result(timeout=30)
                barcode_result = future_barcode.result(timeout=30)
                
                if barcode_result:
                    result['barcode_image'] = barcode_result['barcode_path']
                    result['barcode_number'] = barcode_result['barcode_text']
                    result['barcode_detected'] = True
                else:
                    result['barcode_detected'] = False
                    result['barcode_number'] = None
                    result['barcode_image'] = None
                
            except TimeoutError:
                raise Exception("Processing timeout exceeded")
        
        # Clean up the temporary file
        default_storage.delete(file_path)

        
        
        return JsonResponse(result, safe=False)
    
    except Exception as e:
        if 'file_path' in locals():
            default_storage.delete(file_path)
       
        return JsonResponse({'error': str(e)}, status=500)
    
    

def process_with_openai(image_path):
    """Process the receipt image with OpenAI's API"""
    try:
        
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
     
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
      
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Extract structured JSON data from this receipt image. "
                                "Return the response as a JSON object **strictly** matching this schema: "
                                "{"
                                "  'Date': 'string or null',"
                                "  'Time': 'string or null',"
                                "  'Total Amount': 'float or null',"
                                "  'Currency': 'string',"
                                "  'Store Name': 'string',"
                                "  'Store Address': 'string',"
                                "  'Store Contact': 'string',"
                                "  'Payment Method': 'string',"
                                "  'Subtotal': 'float or null',"
                                "  'Tax': 'float or null',"
                                "  'Category': 'string or null',"
                                "  'Total Items Count': 'int',"
                                "  'Description': 'string',"
                                "  'Barcode Number': 'string or null',"
                                "  'Items': ["
                                "    {"
                                "      'Product Name': 'string',"
                                "      'Quantity': 'int',"
                                "      'Price Per Unit': 'float',"
                                "      'Total Price': 'float'"
                                "    }"
                                "  ]"
                                "}"
                                "Ensure every key is present and return `null` for missing values. "
                                "The 'Description' should provide an overview of the receipt contents, "
                                "summarizing the purchase. "
                                "The 'Category' should classify the receipt based on the type of purchase, "
                                "such as 'Groceries', 'Electronics', 'Clothing', 'Restaurant', etc."
                                "The 'Barcode Number' should be the numeric sequence typically found directly above "
                                "or below the barcode on the receipt."
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            },
                        },
                    ],
                }
            ],
        )


       

       
        json_response = response.choices[0].message.content

        

        structured_data = json.loads(json_response)

       

        return structured_data
        
    except Exception as e:
      
        
        raise Exception(f"Error processing receipt: {str(e)}")
    
    
@csrf_exempt
def download_json(request):
    """Handle JSON and barcode image download"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    try:
        receipt_data = json.loads(request.body)
        
      
        response_data = {
            'json_url': None,
            'barcode_url': None
        }

      
        json_filename = f"receipt_data_{uuid.uuid4()}.json"
        json_path = os.path.join(settings.MEDIA_ROOT, 'downloads', json_filename)
        
   
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        
      
        with open(json_path, 'w') as f:
            json.dump(receipt_data, f, indent=4)
        response_data['json_url'] = f'/media/downloads/{json_filename}'

       
        if receipt_data.get('barcode_image'):
            response_data['barcode_url'] = receipt_data['barcode_image']

        return JsonResponse(response_data)
            
    except Exception as e:
        
        return JsonResponse({'error': str(e)}, status=500)
    
    

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os
from concurrent.futures import ThreadPoolExecutor

@api_view(['POST'])
def receipt_api(request):
    """
    API endpoint for receipt processing
    Accepts multipart/form-data with a 'receipt' file
    Returns JSON response with processed receipt data
    """
    if 'receipt' not in request.FILES:
        return Response(
            {'error': 'No receipt file provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    receipt_file = request.FILES['receipt']
    

    if receipt_file.size > settings.MAX_UPLOAD_SIZE:
        return Response({
            'error': f'File too large. Maximum size is {settings.MAX_UPLOAD_SIZE/1024/1024}MB'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
      
        file_path = default_storage.save(
            f'receipts/{receipt_file.name}',
            ContentFile(receipt_file.read())
        )
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        
      
        with ThreadPoolExecutor() as executor:
            future_openai = executor.submit(process_with_openai, full_path)
            future_barcode = executor.submit(detect_and_generate_barcode, full_path)
            
            try:
         
                result = future_openai.result(timeout=30)
                barcode_result = future_barcode.result(timeout=30)
                
                if barcode_result:
                    result['barcode_image'] = barcode_result['barcode_path']
                    result['barcode_number'] = barcode_result['barcode_text']
                    result['barcode_detected'] = True
                else:
                    result['barcode_detected'] = False
                    result['barcode_number'] = None
                    result['barcode_image'] = None
                
            except TimeoutError:
                raise Exception("Processing timeout exceeded")
        
        # Clean up the temporary file
        default_storage.delete(file_path)
        
        return Response(result, status=status.HTTP_200_OK)
    
    except Exception as e:
        if 'file_path' in locals():
            default_storage.delete(file_path)
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def download_json_api(request):
    """
    API endpoint for downloading JSON and barcode
    Accepts JSON data in request body
    Returns URLs for the generated files
    """
    try:
        receipt_data = request.data
        
        
        response_data = {
            'json_url': None,
            'barcode_url': None
        }

       
        json_filename = f"receipt_data_{uuid.uuid4()}.json"
        json_path = os.path.join(settings.MEDIA_ROOT, 'downloads', json_filename)
        
       
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        
       
        with open(json_path, 'w') as f:
            json.dump(receipt_data, f, indent=4)
        response_data['json_url'] = f'/media/downloads/{json_filename}'

        
        if receipt_data.get('barcode_image'):
            response_data['barcode_url'] = receipt_data['barcode_image']

        return Response(response_data, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )