from bs4 import BeautifulSoup
import requests
import google.generativeai as genai
import re

# Configure the API client
GEMINI_API_KEY = 'AIzaSyB4F6HvvRElyKjxnRdZ5NvFIgdJH3Jzni8'
genai.configure(api_key=GEMINI_API_KEY)

# Define generation configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    # safety_settings = Adjust safety settings
    # See https://ai.google.dev/gemini-api/docs/safety-settings
)

# Dictionary for events
event_ids = {
    '3x3': '333',
    '2x2': '222',
    '4x4': '444',
    '5x5': '555',
    '6x6': '666',
    '7x7': '777',
    'megaminx': 'minx',
    '3x3 OH': '333oh',
    '3x3 blindfolded': '333bf',
    'FMC': '333fm',
    'clock': 'clock',
    'skewb': 'skewb'
}

def is_relevant_to_rubiks_cube(text):
    rubiks_keywords = ["3x3", "2x2", "4x4", "5x5", "6x6", "7x7", "rubik's", "cube", "solve", "solution", "algorithm", "scramble", "F2L", "OLL", "PLL",
                       "speedcubing", "record", "records", "oh", "blind", "megaminx", "pyraminx", "skewb", "one-handed"]
    return any(keyword in text.lower() for keyword in rubiks_keywords)

def fetch_event_records(event_type):
    event_id = event_ids.get(event_type)
    if not event_id:
        return f"Invalid event type: {event_type}"

    url = f'https://www.worldcubeassociation.org/results/records?event_id={event_id}&show=mixed+history'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    table_cd = soup.find_all('tr')

    records = []
    for row in table_cd:
        row_data = row.find_all('td')
        individual_row_data = [data.text.strip() for data in row_data]
        records.append(individual_row_data)

    return records

def extract_event_type(user_input):

    pattern = re.compile(r'\b(fetch|show|display|get)\b.*?\b(records|results)\b.*?\b(for|of)\b (.+)', re.IGNORECASE)
    match = pattern.search(user_input)
    if match:
        event_type = match.group(4).strip().lower()
        event_type = event_type.replace("rubik's cube", "").strip()
        return event_type
    return None

chat_session = model.start_chat(
    history=[]
)

while True:
    user_input = input("Prompt: ")
    if not is_relevant_to_rubiks_cube(user_input):
        print("Please ask questions related to Rubik's Cube.")
        continue

    event_type = extract_event_type(user_input)
    if event_type:
        records = fetch_event_records(event_type)
        if isinstance(records, str):
            print(records)
        else:
            for record in records:
                print(record)
        continue


    response = chat_session.send_message(user_input)
    print(response.text)
