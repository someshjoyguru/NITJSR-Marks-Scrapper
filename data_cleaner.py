import json
from bs4 import BeautifulSoup

# Load the HTML data from the file
with open("student_data.json", "r") as file:
    data = json.load(file)

all_students_data = {}

for i in range(1, 118):
    student_id = f"2022UGEC{i:03}"
    html_content = data.get(student_id, "")

    print(len(html_content))
    if not html_content:
        print(f"No data found for {student_id}, skipping.")
        continue

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract relevant details
    structured_data = {}

    # Helper function to safely extract text
    def safe_extract(element):
        return element.text.strip() if element else None

    # Extract student information
    structured_data["registration_number"] = safe_extract(soup.find(id="txtRegno"))
    structured_data["name"] = safe_extract(soup.find(id="lblSName"))
    structured_data["roll_number"] = safe_extract(soup.find(id="lblSRollNo"))
    structured_data["branch"] = safe_extract(soup.find(id="lblSBranch"))
    structured_data["semester"] = safe_extract(soup.find(id="lblSemester"))
    structured_data["father_name"] = safe_extract(soup.find(id="lblFatherName"))

    # Extract marks details
    subjects = []
    result_table = soup.find("table", {'style': 'background-color: #ffffff;'})
    if result_table:
        rows = result_table.find_all("tr")[1:]  # Skip header row
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 9:  # Ensure there are enough columns
                subject = {
                    "subject_code": cols[0].text.strip(),
                    "subject_name": cols[1].text.strip(),
                    "test_1": cols[2].text.strip(),
                    "test_2": cols[3].text.strip(),
                    "assignment": cols[4].text.strip(),
                    "quiz_avg": cols[5].text.strip(),
                    "end_sem": cols[6].text.strip(),
                    "total": cols[7].text.strip(),
                    "grade": cols[8].text.strip()
                }
                subjects.append(subject)

    structured_data["subjects"] = subjects

    # Extract SGPA, CGPA, and result status
    structured_data["result"] = safe_extract(soup.find(id="lblResult"))
    structured_data["sgpa"] = safe_extract(soup.find(id="lblSPI"))
    structured_data["cgpa"] = safe_extract(soup.find(id="lblCPI"))
    structured_data["result_publish_date"] = safe_extract(soup.find(id="lblPublishDate"))

    # Add structured data to the main dictionary
    all_students_data[student_id] = structured_data

# Save all students' structured data to a new JSON file
with open("structured_all_students_data.json", "w") as output_file:
    json.dump(all_students_data, output_file, indent=4)

print("Structured data for all students saved to 'structured_all_students_data.json'")
