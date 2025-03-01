from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import uvicorn
from extractor import extract
import uuid
import os
from pathlib import Path
from order_manager import OrderManager
import pandas as pd

# Initialize FastAPI app
app = FastAPI()
order_manager = OrderManager()

# Load medicine database
MEDICINE_DB_PATH = Path(__file__).resolve().parent.parent / "Medicine_Details.csv"
try:
    medicine_df = pd.read_csv(MEDICINE_DB_PATH)
except FileNotFoundError:
    print("Medicine database not found. Please ensure 'Medicine_Details.csv' is in the backend directory.")
    medicine_df = pd.DataFrame(columns=["Medicine Name", "Composition", "Manufacturer", "Side_effects"])

# Get the absolute path to the project root directory
BASE_DIR = Path(__file__).resolve().parent.parent  # Points to the 'backend' directory
UPLOADS_DIR = BASE_DIR / "uploads"  # Absolute path to the 'uploads' directory

# Create the 'uploads' directory if it doesn't exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/extract_from_doc")
def extract_from_doc(
    file: UploadFile = File(...),
    file_format: str = Form(...)
):
    # Read the file content
    content = file.file.read()

    # Generate a unique file name
    FILE_PATH = UPLOADS_DIR / f"{uuid.uuid4()}.pdf"

    # Save the uploaded file to the 'uploads' directory
    try:
        with open(FILE_PATH, "wb") as f:
            f.write(content)
    except Exception as e:
        return {"error": f"Failed to save the file: {str(e)}"}

    # Extract data from the file
    try:
        data = extract(FILE_PATH, file_format)
        
        # Validate medicines against CSV
        invalid_meds = []
        for med in data.get("medicines", []):
            if not medicine_df['Medicine Name'].str.contains(med['name'], case=False).any():
                invalid_meds.append(med['name'])
        
        data["invalid_meds"] = invalid_meds

    except Exception as e:
        data = {
            'error': str(e)
        }

    # Delete the file after processing
    if os.path.exists(FILE_PATH):
        os.remove(FILE_PATH)

    return data

# ... (rest of the code remains unchanged)

@app.post("/generate_order")
def generate_order(order_data: dict):
    order_id = order_manager.generate_order(order_data)
    return {"order_id": order_id}

@app.get("/track_order/{order_id}")
def track_order(order_id: str):
    order = order_manager.track_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/order_history")
def order_history():
    history = order_manager.get_order_history()
    return history

@app.get("/download_invoice/{order_id}")
def download_invoice(order_id: str):
    invoice_path = order_manager.generate_invoice(order_id)
    if not invoice_path or not invoice_path.exists():
        raise HTTPException(status_code=404, detail="Invoice not found")
    return FileResponse(invoice_path, filename=f"invoice_{order_id}.txt")

@app.post("/submit_support_request")
def submit_support_request(request_data: dict):
    # Here you would typically save the request to a database or ticketing system
    return {"message": "Support request submitted successfully!"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)