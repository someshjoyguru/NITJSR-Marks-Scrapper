import json
from fpdf import FPDF

# Load the JSON data
with open("structured_all_students_data.json", "r") as file:
    data = json.load(file)

# Initialize the PDF object
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Student Results", border=0, ln=1, align="C")

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

# Create a PDF instance
pdf = PDF()
pdf.add_page()
pdf.set_font("Arial", size=10)

# Add table headers
pdf.set_fill_color(200, 220, 255)
pdf.cell(60, 10, "Name", border=1, align="C", fill=True)
pdf.cell(40, 10, "Roll No", border=1, align="C", fill=True)
pdf.cell(40, 10, "SGPA", border=1, align="C", fill=True)
pdf.cell(40, 10, "CGPA", border=1, align="C", fill=True)
pdf.ln()

# Populate table rows
for student_id, student_data in data.items():
    try:
        # Extract fields and ensure they are not None
        name = student_data.get("name", "N/A") or "N/A"
        roll_no = student_data.get("roll_number", "N/A") or "N/A"
        sgpa = student_data.get("sgpa", "N/A") or "N/A"
        cgpa = student_data.get("cgpa", "N/A") or "N/A"
        
        # Convert all fields to strings
        name = str(name)
        roll_no = str(roll_no)
        sgpa = str(sgpa)
        cgpa = str(cgpa)

        # Add a row to the table
        pdf.cell(60, 10, name, border=1, align="C")
        pdf.cell(40, 10, roll_no, border=1, align="C")
        pdf.cell(40, 10, sgpa, border=1, align="C")
        pdf.cell(40, 10, cgpa, border=1, align="C")
        pdf.ln()
    except Exception as e:
        # Log any unexpected error
        print(f"Skipping {student_id} due to error: {e}")

# Save the PDF
output_file = "student_results.pdf"
pdf.output(output_file)

print(f"PDF generated successfully: {output_file}")
