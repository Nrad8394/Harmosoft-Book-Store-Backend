import os
import pandas as pd
import requests
import logging
from pathlib import Path
from urllib.parse import urlparse

# Set the base URL for API requests
BASE_URL = 'http://127.0.0.1:8000/items/'  # Replace with your actual base URL
BASE_IMAGE_URL = 'https://textbookcentre.com'  # Base URL for images (modify if necessary)

# Initialize logging
LOG_FILE = 'failed_books.log'
ISBN_LOG_FILE = 'isbn_log.txt'
logging.basicConfig(filename=LOG_FILE, level=logging.ERROR, format='%(asctime)s - %(message)s')

# Path to data directory
DATA_FOLDER = Path("C:\\Users\\karan\\Documents\\Github\\Harmosoft-Book-Store-Backend\\hbs\\data\\Books")  # Change this to your actual data folder path

GRADE_FOLDERS = [
    "ECDE","Pre-Primary1","grade1", "grade2", "grade3", "grade4", "grade5", "grade6", "grade7", "grade8"
]
GRADE_MAPPING = {
    "ECDE": "Play Group",
    "Pre-Primary1": "Pre-Primary 1",
    "grade1": "Grade 1",
    "grade2": "Grade 2",
    "grade3": "Grade 3",
    "grade4": "Grade 4",
    "grade5": "Grade 5",
    "grade6": "Grade 6",
    "grade7": "Grade 7",
    "grade8": "Grade 8",
    "grade9": "Grade 9",
    "grade10": "Grade 10",
    "grade11": "Grade 11",
    "grade12": "Grade 12"
}

# Study level mapping based on grades
STUDY_LEVEL_MAPPING = {
    "ECDE & Pre-Primary": ["Playgroup", "PP1", "PP2"],
    "Primary School": ["Grade 1", "Grade 2", "Grade 3", "Grade 4"],
    "Junior School": ["Grade 5", "Grade 6", "Grade 7", "Grade 8"],
    "Secondary School": ["Grade 9", "Grade 10", "Grade 11", "Grade 12"]
}

# Store processed ISBNs to avoid duplicates
processed_isbns = set()

def load_processed_isbns():
    """Load previously processed ISBNs from an external file."""
    if os.path.exists(ISBN_LOG_FILE):
        with open(ISBN_LOG_FILE, 'r') as file:
            return set(file.read().splitlines())
    return set()

def save_isbn_to_log(isbn):
    """Save an ISBN to the external log file."""
    with open(ISBN_LOG_FILE, 'a') as file:
        file.write(f"{isbn}\n")

# Load processed ISBNs
processed_isbns = load_processed_isbns()

def get_excel_files_from_folder(folder):
    """Retrieve all Excel files from the specified folder."""
    excel_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith('.xlsx') or file.endswith('.xls'):
                excel_files.append(os.path.join(root, file))
    return excel_files

def map_subject(name):
    """Map subject from the item name (this could be expanded for more precise mapping)."""
    subject_map = {
        "Maths": "Mathematics",
        "Math": "Mathematics",
        "Mathematics": "Mathematics",
        "Science": "Science",
        "English": "English",
        "History": "History",
        "Geography": "Geography",
        "Biology": "Biology",
        "Chemistry": "Chemistry",
        "Physics": "Physics",
        "Kiswahili": "Kiswahili",
        "Religious Studies": "Religious Studies",
        "Christian Religious Education": "Christian Religious Education",
        "Islamic Religious Education": "Islamic Religious Education",
        "Social Studies": "Social Studies",
        "Civics": "Civics",
        "Business Studies": "Business Studies",
        "Computer Studies": "Computer Studies",
        "Information Technology": "Information Technology",
        "Physical Education": "Physical Education",
        "Art": "Art and Craft",
        "Craft": "Art and Craft",
        "Music": "Music",
        "Home Science": "Home Science",
        "Agriculture": "Agriculture",
        "French": "French",
        "German": "German",
        "Arabic": "Arabic",
        "Spanish": "Spanish",
        "Literature": "Literature",
        "Economics": "Economics",
        "Psychology": "Psychology",
        "Sociology": "Sociology",
        "Law": "Law",
        "Environmental Science": "Environmental Science",
        "General Knowledge": "General Knowledge",
        "Technical Drawing": "Technical Drawing",
        "Woodwork": "Woodwork",
        "Metalwork": "Metalwork",
        "Electronics": "Electronics",
        "Building and Construction": "Building and Construction",
        "Accounting": "Accounting",
        "Commerce": "Commerce",
        "Entrepreneurship": "Entrepreneurship"
    }
    for key, value in subject_map.items():
        if key.lower() in name.lower():
            return value
    return "General"

def map_grade_from_folder(folder_name):
    """Map grade based on the folder name."""
    return GRADE_MAPPING.get(folder_name, "ALL")

def map_category_from_folder(folder_name):
    """Map the category based on the folder name. If it's not a grade folder, use the folder name as category."""
    return "Textbooks" if folder_name in GRADE_FOLDERS else folder_name.capitalize()

def map_study_level_from_grade(grade):
    """Map study level from the grade."""
    for study_level, grades in STUDY_LEVEL_MAPPING.items():
        if grade in grades:
            return study_level
    return "ALL"

def download_image(image_url):
    """Download the image from the URL if available."""
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            image_name = urlparse(image_url).path.split('/')[-1]
            return (image_name, response.content)
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to download image: {e}")
    return None

def generate_items(file_path):
    folder_name = Path(file_path).parent.name  # Extract folder name
    grade = map_grade_from_folder(folder_name)  # Map grade based on folder name
    study_level = map_study_level_from_grade(grade)  # Map study level
    category = map_category_from_folder(folder_name)  # Set category based on folder name

    try:
        # Load the Excel file
        df = pd.read_excel(file_path)
        total_items = len(df)
        processed_items = 0

        for index, row in df.iterrows():
            item_name = row.get('name', None)
            if not item_name:
                logging.error(f"Item without name found in {file_path}")
                continue  # Skip rows without item names

            # Extract and clean the ISBN
            ISBN = str(row.get('ISBN', '')).replace('ISBN:', '').strip()

            # Check for duplicate ISBN
            if ISBN in processed_isbns:
                print(f"Duplicate ISBN {ISBN} found. Skipping {item_name}.")
                continue

            # Prepare data for sending
            subject = map_subject(item_name)
            price = str(row.get('price', '0')).replace('KES', '').replace(',', '').strip()

            payload = {
                "name": item_name,
                "description": row.get('description', 'No description provided.'),
                "price": price,
                "visibility": bool(row.get('visibility', False)),
                "stock_availability": bool(row.get('stock_availability', False)),
                "subject": subject,
                "publisher": row.get('Author', 'N/A'),
                "category": category,
                "grade": grade,
                "study_level": study_level,
                "curriculum": row.get('curriculum', 'CBC'),
                "ISBN": ISBN,
            }

            # Handle image if available
            image_path = row.get('image-src')
            files = None
            if image_path:
                image_url = f"{BASE_IMAGE_URL}{image_path}"
                image = download_image(image_url)
                if image:
                    image_name, image_data = image
                    files = {'image': (image_name, image_data, 'application/octet-stream')}  # Prepare image for upload

            try:
                # Send a POST request to the API
                if files:
                    response = requests.post(BASE_URL, data=payload, files=files)
                else:
                    response = requests.post(BASE_URL, json=payload)

                if response.status_code == 201:
                    processed_items += 1
                    remaining_items = total_items - processed_items
                    print(f"Successfully added: {item_name}. Processed {processed_items}/{total_items}. Remaining: {remaining_items}")
                    save_isbn_to_log(ISBN)  # Save successful ISBN to log
                    processed_isbns.add(ISBN)
                elif response.status_code == 400 and "ISBN" in response.json():
                    # Log ISBN duplication error
                    logging.error(f"Failed to add {item_name} - ISBN already exists: {ISBN}")
                    save_isbn_to_log(ISBN)  # Save ISBN that caused error to log
                else:
                    logging.error(f"Failed to add {item_name} - {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as e:
                logging.error(f"Error adding {item_name} from {file_path}: {str(e)}")

    except Exception as e:
        logging.error(f"Error processing file {file_path}: {str(e)}")

if __name__ == '__main__':
    excel_files = get_excel_files_from_folder(DATA_FOLDER)
    
    if not excel_files:
        print("No Excel files found in the data folder.")
    else:
        for file in excel_files:
            generate_items(file)

    print(f"Logs can be found in {LOG_FILE}.")
