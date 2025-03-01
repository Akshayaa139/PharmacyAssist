import streamlit as st
import requests
from pdf2image import convert_from_bytes
from pathlib import Path
import os
import pandas as pd

# Path to Poppler for PDF conversion
POPPLER_PATH = r"C:/poppler-24.08.0/Library/bin"
BASE_URL = "http://127.0.0.1:8000"

# Load medicine database
@st.cache_data
def load_medicine_data():
    return pd.read_csv(r"backend\Medicine_Details.csv")

medicine_df = load_medicine_data()

# Title and Navigation
st.sidebar.title("PharmAssist Pro")
page = st.sidebar.radio("Go to", ["New Order", "Order History", "Track Order", "Customer Support & Compliance"])

# Function to upload and process prescription
def upload_prescription():
    st.header("Prescription Order Generator")
    st.subheader("Prescription Details")
    
    # File uploader
    file = st.file_uploader("Upload Prescription Image", type=["pdf", "png", "jpg", "jpeg"])
    
    if file:
        # Display uploaded file
        st.subheader("Your Prescription")
        if file.type == "application/pdf":
            pages = convert_from_bytes(file.getvalue(), poppler_path=POPPLER_PATH)
            st.image(pages[0], caption="First Page of the Prescription", use_column_width=True)
        else:
            st.image(file, caption="Uploaded Prescription", use_column_width=True)

        # Extract prescription details
        if st.button("Extract Information"):
            with st.spinner("Extracting prescription details..."):
                try:
                    # Send request to backend
                    response = requests.post(
                        f"{BASE_URL}/extract_from_doc",
                        files={"file": file.getvalue()},
                        data={"file_format": "prescription"}
                    )
                    response.raise_for_status()
                    data = response.json()

                    # Validate medicines against CSV
                    invalid_meds = []
                    for med in data.get("medicines", []):
                        if not medicine_df['Medicine Name'].str.contains(med['name'], case=False).any():
                            invalid_meds.append(med['name'])
                    
                    # Store extracted data in session state
                    st.session_state["prescription_data"] = data
                    st.session_state["invalid_meds"] = invalid_meds
                    
                    st.success("Prescription details extracted successfully!")
                    
                    # Show validation warnings
                    if invalid_meds:
                        st.warning(f"Unrecognized medications detected: {', '.join(invalid_meds)}. Please verify with pharmacist.")

                except Exception as e:
                    st.error(f"Error: {str(e)}")

        # Display extracted information
        if "prescription_data" in st.session_state:
            data = st.session_state["prescription_data"]
            
            st.subheader("Extracted Information")
            st.write(f"**Patient Name:** {data.get('patient_name', 'N/A')}")
            st.write(f"**Doctor Name:** {data.get('doctor_name', 'N/A')}")
            st.write(f"**Date:** {data.get('date', 'N/A')}")
            st.write(f"**Address:** {data.get('patient_address', 'N/A')}")

            st.subheader("Prescribed Medicines")
            for med in data.get("medicines", []):
                # Get medicine details from CSV
                med_details = medicine_df[medicine_df['Medicine Name'].str.contains(med['name'], case=False)]
                
                st.write(f"**Medicine:** {med.get('name', 'N/A')}")
                st.write(f"**Dosage:** {med.get('dosage', 'N/A')}")
                st.write(f"**Frequency:** {med.get('frequency', 'N/A')}")
                st.write(f"**Duration:** {med.get('duration', 'N/A')}")
                
                # Display additional info from CSV
                if not med_details.empty:
                    st.write(f"**Composition:** {med_details.iloc[0]['Composition']}")
                    st.write(f"**Manufacturer:** {med_details.iloc[0]['Manufacturer']}")
                    st.write(f"**Common Side Effects:** {med_details.iloc[0]['Side_effects']}")
                
                # Display stock and pricing
                st.write(f"**Available Stock:** 100")
                st.write(f"**Price per Unit:** $12.99")
                quantity = st.number_input(f"Quantity for {med.get('name')}", min_value=1, max_value=100, value=1)
                total_price = quantity * 12.99
                st.write(f"**Total Price:** ${total_price:.2f}")
                st.write("---")

            # Generate order
            if st.button("Generate Order"):
                order_data = {
                    "patient_name": data.get("patient_name"),
                    "doctor_name": data.get("doctor_name"),
                    "medicines": data.get("medicines")
                }
                try:
                    order_response = requests.post(f"{BASE_URL}/generate_order", json=order_data)
                    if order_response.status_code == 200:
                        st.success("Order generated successfully!")
                        st.session_state["order_id"] = order_response.json().get("order_id")
                        st.session_state["order_data"] = order_data
                        st.info("Go to 'Order History' to view and download the invoice.")
                    else:
                        st.error("Failed to generate order.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Order History Page
def view_order_history():
    st.header("Order History")
    if st.button("Refresh History"):
        try:
            response = requests.get(f"{BASE_URL}/order_history")
            if response.status_code == 200:
                orders = response.json()
                for order in orders:
                    order_id = order.get('order_id')
                    st.write(f"**Order ID:** {order_id}")
                    st.write(f"**Patient Name:** {order.get('patient_name')}")
                    st.write(f"**Doctor Name:** {order.get('doctor_name')}")
                    st.write(f"**Status:** {order.get('status')}")
                    st.write("**Prescribed Medicines:**")
                    for med in order.get("medicines", []):
                        st.write(f"- {med.get('name')} ({med.get('dosage')})")
                    st.write("---")

                    # Download invoice using Streamlit's native button
                    invoice_response = requests.get(f"{BASE_URL}/download_invoice/{order_id}")
                    if invoice_response.status_code == 200:
                        st.download_button(
                            label=f"Download Invoice for Order {order_id}",
                            data=invoice_response.content,
                            file_name=f"invoice_{order_id}.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error("Failed to fetch invoice")
            else:
                st.error("Failed to fetch order history")
        except Exception as e:
            st.error(f"Error: {str(e)}")


    
# Track Order Page
def track_order():
    st.header("Track Order")
    order_id = st.text_input("Enter Order ID")
    if st.button("Track Order"):
        try:
            response = requests.get(f"{BASE_URL}/track_order/{order_id}")
            if response.status_code == 200:
                order_data = response.json()
                st.write(f"**Order ID:** {order_data.get('order_id')}")
                st.write(f"**Patient Name:** {order_data.get('patient_name')}")
                st.write(f"**Doctor Name:** {order_data.get('doctor_name')}")
                st.write(f"**Status:** {order_data.get('status')}")
                st.write("**Prescribed Medicines:**")
                for med in order_data.get("medicines", []):
                    st.write(f"- {med.get('name')} ({med.get('dosage')})")
                st.write("---")

                # Download invoice button
                invoice_response = requests.get(f"{BASE_URL}/download_invoice/{order_id}")
                if invoice_response.status_code == 200:
                    st.download_button(
                        label="Download Invoice",
                        data=invoice_response.content,
                        file_name=f"invoice_{order_id}.txt",
                        mime="text/plain"
                    )
                else:
                    st.error("Failed to fetch invoice")
            else:
                st.error("Order not found")
        except Exception as e:
            st.error(f"Error: {str(e)}")



# Customer Support & Compliance Page
def customer_support():
    st.header("Customer Support & Compliance")
    
    tab1, tab2 = st.tabs(["Support Ticket", "Compliance Information"])
    
    with tab1:
        st.subheader("Submit Support Request")
        with st.form("support_form"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            order_id = st.text_input("Order ID (if applicable)")
            issue_type = st.selectbox("Issue Type", ["Order Related", "Medicine Information", "Billing", "Other"])
            message = st.text_area("Message", height=150)
            
            if st.form_submit_button("Submit Request"):
                # Here you would typically send to a database or ticketing system
                st.success("Request submitted successfully! We'll respond within 24 hours.")
                st.write(f"**Name:** {name}")
                st.write(f"**Email:** {email}")
                st.write(f"**Order ID:** {order_id}")
                st.write(f"**Issue Type:** {issue_type}")
                st.write(f"**Message:** {message}")
    
    with tab2:
        st.subheader("Compliance Guidelines")
        st.write("""
        ### Pharmaceutical Compliance Standards
        1. All orders verified against registered medical practitioners
        2. Controlled substances require additional validation
        3. Patient privacy protected under HIPAA regulations
        4. Medication dispensing follows FDA guidelines
        5. Regular audits conducted for quality assurance
        """)
        
    pdf_path = os.path.join(os.path.dirname(__file__), "compliance_handbook.pdf")
    
    with open(pdf_path, "rb") as f:
        st.download_button(
            label="📘 Download Compliance Handbook",
            data=f,
            file_name="compliance_handbook.pdf",
            mime="application/pdf"
        )
        
        st.write("For compliance inquiries:")
        st.write("📞 Compliance Hotline: 1-800-COMPLY-NOW")
        st.write("📧 Email: compliance@pharmassistpro.com")

# Main app logic
if page == "New Order":
    upload_prescription()
elif page == "Order History":
    view_order_history()
elif page == "Track Order":
    track_order()
elif page == "Customer Support & Compliance":
    customer_support()