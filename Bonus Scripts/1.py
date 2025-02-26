import base64
import json
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key='YOUR API KEY')

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your bill/receipt image
image_path = "images.jpg"  # Change this to the actual image path

# Encode image to base64
base64_image = encode_image(image_path)

# Send request to OpenAI GPT-4o with vision capabilities
response = client.chat.completions.create(
    model="gpt-4o",
    response_format={"type": "json_object"},  # ✅ Use 'json_object'
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Extract structured JSON data from this receipt image. "
                        "Ensure it contains: Date, Time, Total Amount, Currency, Store Name, Store Address, Store Contact, "
                        "Payment Method, receipt barcode number, Category, Total Items Count, and a Description summarizing the receipt (e.g., 'This is a grocery receipt for daily essentials.'). "
                        "Also extract an 'Items' list with: Product Name, Quantity, Price Per Unit, and Total Price."
                        "If any value is missing, return null."
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

# Extract and clean JSON response
json_response = response.choices[0].message.content

try:
    structured_data = json.loads(json_response)  # Parse JSON output
except json.JSONDecodeError:
    structured_data = {"error": "Failed to parse JSON response"}

# Print the formatted JSON output
print(json.dumps(structured_data, indent=4))
