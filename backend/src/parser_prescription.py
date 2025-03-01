import re
import pandas as pd
from pathlib import Path
from parser_generic import MedicalDocParser

# Load medicine database from CSV
MEDICINE_DB_PATH = Path(__file__).resolve().parent.parent / "Medicine_Details.csv"
try:
    medicine_df = pd.read_csv(MEDICINE_DB_PATH)
except FileNotFoundError:
    print("Medicine database not found. Please ensure 'Medicine_Details.csv' is in the backend directory.")
    medicine_df = pd.DataFrame(columns=["Medicine Name", "Composition", "Manufacturer", "Side_effects"])

class PrescriptionParser(MedicalDocParser):
    def __init__(self, text):
        MedicalDocParser.__init__(self, text)

    def parse(self):
        return {
            "patient_name": self.get_field("patient_name"),
            "doctor_name": self.get_field("doctor_name"),
            "date": self.get_field("date"),
            "patient_address": self.get_field("patient_address"),
            "medicines": self.get_medicines()
        }

    def get_field(self, field_name):
        pattern_dict = {
            "patient_name": {"pattern": "Name:(.*)Date", "flags": re.IGNORECASE},
            "doctor_name": {"pattern": "Dr (.*),", "flags": re.IGNORECASE},
            "date": {"pattern": "Date:(.*)", "flags": re.IGNORECASE},
            "patient_address": {"pattern": "Address:(.*)\n", "flags": re.IGNORECASE}
        }
        pattern_object = pattern_dict.get(field_name)
        if pattern_object:
            matches = re.findall(pattern_object["pattern"], self.text, flags=pattern_object["flags"])
            if len(matches) > 0:
                return matches[0].strip()

    def get_medicines(self):
        # Extract medicines using regex
        medicines = []
        medicine_pattern = r"(\b\w+\b)\s+(\d+mg|\d+\.\d+\sgram)\b"
        matches = re.findall(medicine_pattern, self.text, re.IGNORECASE)
        print("Regex matches:", matches)  # Debugging: Print regex matches

        for match in matches:
            medicine_name = match[0].lower()
            dosage = match[1]

            # Check if the medicine exists in the CSV database (case-insensitive)
            med_details = medicine_df[medicine_df['Medicine Name'].str.contains(medicine_name, case=False, na=False)]
            
            if not med_details.empty:
                # If the medicine is found in the CSV, add it with details
                medicines.append({
                    "name": medicine_name.capitalize(),
                    "dosage": dosage,
                    "frequency": "N/A",  # Frequency is not explicitly mentioned
                    "duration": "N/A",  # Duration is not explicitly mentioned
                    "composition": med_details.iloc[0]['Composition'],
                    "manufacturer": med_details.iloc[0]['Manufacturer'],
                    "side_effects": med_details.iloc[0]['Side_effects']
                })
            else:
                # If the medicine is not in the CSV, still add it with the extracted dosage
                medicines.append({
                    "name": medicine_name.capitalize(),
                    "dosage": dosage,
                    "frequency": "N/A",
                    "duration": "N/A",
                    "composition": "N/A",
                    "manufacturer": "N/A",
                    "side_effects": "N/A"
                })

        return medicines