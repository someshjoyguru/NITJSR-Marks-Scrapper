import json
from openpyxl import Workbook
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)


# Load the JSON data
with open("structured_all_students_data.json", "r") as file:
    data = json.load(file)

# Create a new workbook and select the active sheet
wb = Workbook()
ws = wb.active
ws.title = "Student Results"

# Add headers to the Excel sheet
headers = ["Name", "Roll No", "SGPA", "CGPA"]
ws.append(headers)

# Populate the rows with student data
for student_id, student_data in data.items():
    try:
        # Extract relevant fields and handle missing or None values
        name = student_data.get("name", "N/A") or "N/A"
        roll_no = student_data.get("roll_number", "N/A") or "N/A"
        sgpa = student_data.get("sgpa", "N/A") or "N/A"
        cgpa = student_data.get("cgpa", "N/A") or "N/A"

        # Append the data to the sheet
        ws.append([name, roll_no, sgpa, cgpa])
    except Exception as e:
        print(f"Skipping {student_id} due to error: {e}")

# Save the workbook to an Excel file
output_file = "student_results.xlsx"
wb.save(output_file)

print(f"Excel file generated successfully: {output_file}")
