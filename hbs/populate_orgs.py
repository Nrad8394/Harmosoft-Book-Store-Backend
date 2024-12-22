import pandas as pd
import requests
import json

BASE_URL = 'http://127.0.0.1:8000/'  # Replace with your actual base URL
REGISTER_URL = f"{BASE_URL}/register/"

def generate_organizations(file_path):
    # Determine file type and read data
    if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        df = pd.read_excel(file_path)
    elif file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file format. Please use .xlsx or .csv")

    for index, row in df.iterrows():
        school_name = row.get('SCHOOL_NAME')
        level = row.get('LEVEL')
        county = row.get('COUNTY')
        sub_county = row.get('SUB_COUNTY')
        ward = row.get('WARD')

        # Construct the address in the required format
        address = f"{ward},{sub_county},{county}"

        # Prepare the payload for the request
        payload = {
            "email": f"{school_name.replace(' ', '').lower()}@example.com",  # Example email generation # type: ignore
            "first_name": school_name,
            "password1": "user@12345",  # Set a default password or modify as needed
            "password2": "user@12345",  # Same as above
            "location": county,
            "level": level,
            "curriculum": "CBC",  # Set a default curriculum if needed
            "user_type": "organization",
            "organization_name": school_name,
            "address": address
        }

        # Send the POST request
        try:
            response = requests.post(REGISTER_URL, json=payload)
            if response.status_code == 201:  # Assuming 201 is the created response
                print(f"Successfully registered: {school_name}")
            else:
                print(f"Failed to register {school_name}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"An error occurred while registering {school_name}: {str(e)}")

if __name__ == '__main__':
    file_path = input("Enter the path to your file: ")
    generate_organizations(file_path)
