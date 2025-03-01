import uuid
from datetime import datetime
from pathlib import Path
import json
import pandas as pd
from fpdf import FPDF

class OrderManager:
    def __init__(self):
        self.orders = {}
        self.invoice_dir = Path("backend/invoices")  # Correct path to backend/invoices
        self.invoice_dir.mkdir(parents=True, exist_ok=True)  # Create invoices directory
        self.patient_records_path = Path("backend/patient_records.json")
        self.patient_records = self.load_patient_records()

    def load_patient_records(self):
        if self.patient_records_path.exists():
            with open(self.patient_records_path, "r") as f:
                return json.load(f)
        return []

    def save_patient_records(self):
        with open(self.patient_records_path, "w") as f:
            json.dump(self.patient_records, f, indent=4)

    def generate_order(self, order_data):
        order_id = str(uuid.uuid4())
        self.orders[order_id] = {
            "order_id": order_id,
            "patient_name": order_data.get("patient_name"),
            "doctor_name": order_data.get("doctor_name"),
            "medicines": order_data.get("medicines"),
            "status": "Pending",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.generate_invoice(order_id)
        

       
    # Generate invoice for the order
        self.patient_records.append(self.orders[order_id])
        self.save_patient_records()
        return order_id

    def track_order(self, order_id):
        return self.orders.get(order_id, {})

    def get_order_history(self):
        return list(self.orders.values())

    def generate_invoice(self, order_id):
        order = self.orders.get(order_id)
        if not order:
            return None

         # Invoice content
        invoice_content = f"""
        ==============================
        PharmAssist Pro - Invoice
        ==============================
        Order ID: {order['order_id']}
        Patient Name: {order['patient_name']}
        Doctor Name: {order['doctor_name']}
        Date: {order['timestamp']}
        ------------------------------
        Prescribed Medicines:
        """

        total_price = 0
        for med in order['medicines']:
            price = 12.99  # Example price per unit
            quantity = 1  # Example quantity
            total_price += price * quantity
            invoice_content += f"""
        - {med['name']} ({med['dosage']})
          Frequency: {med['frequency']}
          Duration: {med['duration']}
          Price: ${price:.2f} x {quantity} = ${price * quantity:.2f}
        """

        invoice_content += f"""
        ------------------------------
        Total Price: ${total_price:.2f}
        ==============================
        """

        # Save invoice to a file
        invoice_path = self.invoice_dir / f"invoice_{order_id}.txt"
        with open(invoice_path, "w") as f:
            f.write(invoice_content)

        return invoice_path


        # Save the PDF to the invoices directory
        invoice_path = self.invoice_dir / f"invoice_{order_id}.pdf"
        pdf.output(invoice_path)

        return invoice_path

    def get_invoice(self, order_id):
        invoice_path = self.invoice_dir / f"invoice_{order_id}.txt"
        if invoice_path.exists():
            with open(invoice_path, "r") as f:
                return f.read()
        return None