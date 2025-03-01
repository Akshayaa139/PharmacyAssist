# Pharmacist Assistant App 📋💊

A Streamlit-based web application integrated with Tesseract OCR and FastAPI to automate handwritten prescription processing, order generation, and invoice management for pharmacies.


## Features ✨
- **Handwritten Prescription Recognition**: Uses **Tesseract OCR** and OpenCV for text extraction.
- **Order Generation**: Automatically matches prescriptions to medicines and creates patient orders.
- **Invoice Management**: Download invoices directly from the app.
- **Compliance Register**: Track patient history and compliance.
- **Patient Database**: Securely store patient details without manual input.
- **Queue Reduction**: Integrates with pill dispensers to minimize waiting time.

## Technologies Used 🛠️
- **OCR Engine**: Tesseract
- **Frontend**: Streamlit
- **Backend**: FastAPI
- **Image Processing**: OpenCV
- **Testing**: Pytest, Postman
- **Data Handling**: Python (Pandas, JSON)

## Installation 🚀

### Prerequisites
- Install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (add to PATH).
  
### Steps
1. Clone the repository:
   git clone [text][(https://github.com/Akshayaa139/PharmacyAssist)]
  
   **Install dependencies:**
    pip install -r requirements.txt

   **Requirements:**
streamlit fastapi uvicorn opencv-python pytesseract pdf2image requests pytest python-multipart

**Usage 📖**
# Start Backend Server:
    uvicorn main:app --reload
# Run Streamlit Frontend:
    streamlit run app.py

**Upload a handwritten prescription (PDF/Image).**

**View extracted medicines, dosage, and patient details.**

**Generate and track orders, download invoices.
Book your complaints and any support if needed****

**Project Execution Steps ⚙️**
PDF/Image Upload: Accept prescriptions via Streamlit UI.

**OCR Processing:**

Convert PDF to images using pdf2image.

Preprocess images with OpenCV (thresholding, noise removal).

Extract text using Tesseract.

Data Validation: Match extracted medicines against a Kaggle medical dataset.

**Backend Integration:**

FastAPI processes data and returns JSON.

Streamlit frontend displays results and generates orders.

Storage: Save patient details and invoices in a database.

**What I Learned 🎓**
Implemented Tesseract OCR with adaptive thresholding for handwritten text.

Built a RESTful API using FastAPI and tested endpoints with Postman.

Connected Streamlit frontend to backend using requests module.

Improved Python skills via OOP and modular code design.

Debugged path-related issues in Pytest and configured VSCode for testing.

**Challenges Faced 🚧**
OCR Thresholding:

Experimented with block sizes and constants in OpenCV's adaptiveThreshold to optimize text extraction.

Pytest Configuration:

Resolved VSCode integration issues by manually setting test discovery paths.

Streamlit-FastAPI File Transfer:

Solved using requests.post with files parameter to send images to the backend.

Path Errors:

Fixed by using absolute paths and Python's os module for cross-platform compatibility.

Future Enhancements 🔮
Integrate IoT pill dispensers for automated dispensing.

Train a custom OCR model for better handwriting accuracy.

Add multilingual support and mobile app compatibility.

**Acknowledgements**

Kaggle medical dataset for medicine validation.

Tesseract OCR and Streamlit communities for documentation support.



**This README provides a clear overview of the project, highlights technical depth, and addresses the problem-solving steps. Customize placeholder links (e.g., repo URL, demo image) before deployment.**

**Video link of how it works:
     [text](https://youtu.be/NRjakuIJkg4)**Demo!!
