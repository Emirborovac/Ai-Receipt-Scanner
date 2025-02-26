# Computer Vision Receipt Scanner

## Overview

The Computer Vision Receipt Scanner is a sophisticated Django-based application that leverages advanced AI and computer vision technologies to extract, process, and analyze receipt data from various image formats. This system operates as a full-stack solution with a robust backend powered by Django REST Framework and OpenAI's GPT-4o, coupled with a responsive frontend built with Alpine.js and Tailwind CSS.

The application is designed to process receipts of any quality, format, or condition - from pristine digital receipts to crumpled, faded, or partially damaged physical receipts - making it an enterprise-grade solution for financial record-keeping, expense management, and data extraction.

## Key Features

- **Multi-format Receipt Processing**: Accepts JPG, PNG, and PDF files up to 5MB.
- **Advanced Computer Vision**: Uses OpenCV for image preprocessing and barcode detection.
- **AI-Powered Data Extraction**: Leverages OpenAI's GPT-4o for context-aware information extraction.
- **Barcode Detection & Generation**: Automatically identifies, decodes, and regenerates barcodes from receipts.
- **Concurrent Processing**: Implements multi-threading for simultaneous AI analysis and barcode processing.
- **Structured Data Output**: Provides standardized JSON output with comprehensive receipt information.
- **REST API Integration**: Offers RESTful endpoints for seamless integration with other services.
- **Modern Responsive UI**: Features an intuitive drag-and-drop interface with real-time processing feedback.

## Architecture

### Backend Components

The system employs a layered architecture:

#### Data Acquisition Layer
- Handles file uploads through `django.core.files.storage` for temporary file management
- Implements size validation and type checking for security
- Provides both web and API interfaces for receipt submission

#### Image Processing Layer
- Uses OpenCV (`cv2`) for image preprocessing
- Converts images to grayscale for enhanced processing
- Utilizes `pyzbar` for barcode detection and decoding

#### AI Processing Layer
- Implements parallel processing with `ThreadPoolExecutor` for concurrent operations
- Encodes images to base64 for OpenAI API compatibility
- Communicates with GPT-4o for advanced image recognition and data extraction

#### Data Structuring Layer
- Standardizes extracted information into a consistent JSON schema
- Provides validation for data integrity
- Associates decoded barcodes with extracted receipt data

#### Storage and Retrieval Layer
- Generates unique identifiers with `uuid` for file management
- Implements secure file handling for generated barcodes and JSON data
- Provides download endpoints for processed data

### Frontend Architecture

The modern UI is built using:

- **Alpine.js**: For reactive data binding and component logic
- **Tailwind CSS**: For responsive, utility-first styling
- **GSAP**: For smooth animations and transitions
- **Glass Morphism Design**: For an elegant, modern aesthetic

## Technical Implementation

### Receipt Processing Workflow

1. **Image Acquisition**:
   - The system accepts images through either a web interface or REST API
   - Files are temporarily stored using Django's storage system
   - Path references are generated for processing

2. **Parallel Processing**:
   - The application initiates two concurrent processes:
     - AI-based receipt analysis with OpenAI
     - Computer vision-based barcode detection with OpenCV/pyzbar

3. **OpenAI Integration**:
   - The image is encoded to base64 format
   - A structured prompt is sent to GPT-4o requesting specific data fields
   - The response is parsed into a standardized JSON format

4. **Barcode Processing**:
   - Images are converted to grayscale for enhanced barcode detection
   - The `pyzbar` library detects and decodes any barcodes present
   - If found, Code128 barcodes are regenerated using the `python-barcode` library

5. **Data Combination**:
   - Results from both processes are merged into a unified response
   - Barcode information is appended to the AI-extracted data
   - A comprehensive analysis is prepared for presentation

6. **Data Delivery**:
   - Processed data is returned via the appropriate channel (UI or API)
   - Optional file generation for JSON and barcode images

### Error Handling and Resilience

The system implements robust error handling:

- **Timeout Management**: Processing operations have configurable timeouts
- **Graceful Degradation**: Partial results are returned if specific components fail
- **Cleanup Procedures**: Temporary files are removed regardless of success or failure
- **User Feedback**: Clear error messages are provided for troubleshooting

## Advanced Capabilities

### Receipt Condition Handling

The system can process receipts in various conditions:

- **Lighting Variations**: Adapts to different lighting conditions and shadows
- **Damaged Receipts**: Extracts data from torn, crumpled, or folded receipts
- **Low Contrast**: Processes faded or low-ink receipts
- **Skewed Orientation**: Handles rotated or angled images
- **Partial Information**: Extracts available data even from incomplete receipts

### Data Extraction Capabilities

The system extracts a comprehensive set of information including:

- Store name, address, and contact information
- Transaction date and time
- Total amount, subtotal, and tax
- Payment method
- Individual item details (name, quantity, unit price, total price)
- Receipt category classification
- Barcode information
- Transaction description

## Deployment and Scaling

### Requirements

- Python 3.8+
- Django 4.0+
- OpenCV
- pyzbar
- python-barcode
- OpenAI API access
- Redis (recommended for production deployments)

### Configuration

The system can be configured via environment variables or Django settings:

- `OPENAI_API_KEY`: Your OpenAI API key
- `MAX_UPLOAD_SIZE`: Maximum file size for uploads (default: 5MB)
- `MEDIA_ROOT`: Path for storing temporary files and generated assets

### Production Considerations

For production deployment, consider:

- Implementing a Celery task queue for asynchronous processing
- Adding Redis for caching and task management
- Configuring a CDN for media file serving
- Implementing rate limiting and API authentication
- Setting up monitoring for OpenAI API usage

## API Documentation

### Receipt Processing Endpoint

```
POST /api/receipts/
```

**Request:**
- Content-Type: multipart/form-data
- Body: `receipt` (file)

**Response:**
```json
{
  "Date": "2023-05-15",
  "Time": "14:30",
  "Total Amount": 42.99,
  "Currency": "USD",
  "Store Name": "Sample Store",
  "Store Address": "123 Main St, Anytown, USA",
  "Store Contact": "+1 (555) 123-4567",
  "Payment Method": "Credit Card",
  "Subtotal": 39.99,
  "Tax": 3.00,
  "Category": "Electronics",
  "Total Items Count": 2,
  "Description": "Purchase of electronic accessories",
  "Barcode Number": "123456789012",
  "barcode_detected": true,
  "barcode_image": "/media/barcodes/barcode_uuid.png",
  "Items": [
    {
      "Product Name": "USB Cable",
      "Quantity": 1,
      "Price Per Unit": 12.99,
      "Total Price": 12.99
    },
    {
      "Product Name": "Phone Charger",
      "Quantity": 1,
      "Price Per Unit": 27.00,
      "Total Price": 27.00
    }
  ]
}
```

### Download Endpoint

```
POST /api/download/
```

**Request:**
- Content-Type: application/json
- Body: Receipt data object

**Response:**
```json
{
  "json_url": "/media/downloads/receipt_data_uuid.json",
  "barcode_url": "/media/barcodes/barcode_uuid.png"
}
```

## Security Considerations

- Implements CSRF protection for web forms
- Uses secure file handling practices
- Validates input file types and sizes
- Implements proper error handling to prevent information leakage
- Uses environment variables for sensitive configuration

## Future Enhancements

- Receipt categorization with machine learning
- Historical receipt analysis and trends
- Integration with accounting software
- Multi-language receipt support
- OCR fallback for when AI processing is unavailable
- Receipt fraud detection capabilities

## Conclusion

The Computer Vision Receipt Scanner represents a sophisticated integration of modern AI and computer vision technologies, providing an enterprise-grade solution for receipt processing regardless of condition or format. Its robust architecture ensures reliable operation even with challenging inputs, while the comprehensive data extraction capabilities make it suitable for financial, accounting, and record-keeping applications.

## License

[MIT License](LICENSE)
