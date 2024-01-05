import os
import csv
import tkinter as tk
from tkinter import filedialog
import json
from google.cloud import dialogflow_v2 as dialogflow
from google.cloud import resourcemanager_v3
from gcloud import resource_manager
from google.api_core.exceptions import InvalidArgument, PermissionDenied
from googleapiclient.discovery import build
from google.oauth2 import service_account
import googleapiclient.errors
import uuid
import re

#use for service account
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\linds\\Desktop\\private_key.json"

def enable_api(project_id):
    service = build('serviceusage', 'v1')

    # Construct the service name
    service_name = 'dialogflow.googleapis.com'
    request = service.services().enable(
        name=f'projects/{project_id}/services/{service_name}'
    )
    response = request.execute()
    print(f"Enabled {service_name} for {project_id}")

def query_text(text, proj_id):
    DIALOGFLOW_LANGUAGE_CODE = 'en'
    SESSION_ID = 'me'
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(proj_id, SESSION_ID)
    text_input = dialogflow.types.TextInput(text=text_to_be_analyzed, language_code=DIALOGFLOW_LANGUAGE_CODE)
    query_input = dialogflow.types.QueryInput(text=text_input)
    try:
        response = session_client.detect_intent(session=session, query_input=query_input)
    except InvalidArgument:
        raise

    print("Query text:", response.query_result.query_text)
    print("Detected intent:", response.query_result.intent.display_name)
    print("Detected intent confidence:", response.query_result.intent_detection_confidence)
    print("Fulfillment text:", response.query_result.fulfillment_text)

def list_intents(proj_id):
    user_choice = input("Do you want to include training phrases? (yes/no): ").strip().lower()

    client = dialogflow.IntentsClient()

    parent_val = f"projects/{DIALOGFLOW_PROJECT_ID}/agent"
    request = dialogflow.ListIntentsRequest(
        parent=parent_val,
        intent_view="INTENT_VIEW_FULL"
    )

    intents_data_csv = []  # List for storing intents and training phrases for CSV
    intents_data_json = {}  # Dictionary for storing intents and training phrases for JSON

    try:
        page_result = client.list_intents(request=request)
        for intent in page_result:
            intent_name = intent.display_name
            training_phrases = []
            ivr_curr_text = None
            c2c_curr_text = None

            if user_choice == 'yes':
                training_phrases = [phrase.parts[0].text for phrase in intent.training_phrases] if intent.training_phrases else []

            # Extract 'ivr-curr-text' parameter value
            # for parameter in intent.parameters:
            #     if parameter.display_name == 'ivr-curr-text':
            #         ivr_curr_text = parameter.value
            #         #print(f'{intent_name}: {ivr_curr_text}')
            #         break
                
            for parameter in intent.parameters:
                if parameter.display_name == 'ivr-curr-text':
                    ivr_curr_text = parameter.value.strip()
                elif parameter.display_name == 'c2c-curr-text':
                    c2c_curr_text = parameter.value.strip()
            
            # Populate data for CSV
            # if training_phrases:
            #     for phrase in training_phrases:
            #         intents_data_csv.append([intent_name, phrase])
            # elif user_choice == 'yes':
            #     intents_data_csv.append([intent_name, ''])
            # else:
            #     intents_data_csv.append([intent_name])
            
            if user_choice == 'yes':
                if training_phrases:
                    for phrase in training_phrases:
                        intents_data_csv.append([intent_name, phrase, ivr_curr_text, c2c_curr_text])
                else:
                    intents_data_csv.append([intent_name, '', ivr_curr_text, c2c_curr_text])
            else:
                intents_data_csv.append([intent_name, ivr_curr_text, c2c_curr_text])

            # Populate data for JSON
            intents_data_json[intent_name] = training_phrases

        # Write to JSON file
        json_output_file_path = "intents_data.json"
        with open(json_output_file_path, 'w') as json_file:
            json.dump(intents_data_json, json_file, indent=2)

        # Write to CSV file
        csv_output_file_path = "intents_data.csv"
        with open(csv_output_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            headers = ['Intent Name', 'Training Phrase', 'IVR-curr-text', 'C2C-curr-text'] if user_choice == 'yes' else ['Intent Name', 'IVR-curr-text', 'C2C-curr-text']
            writer.writerow(headers)
            writer.writerows(intents_data_csv)

        print("Writing data...")
        print(f"Intents with training phrases written to {json_output_file_path} and {csv_output_file_path}")

    except PermissionDenied as e:
        print(f"Permission denied error: {e}")

def create_environments(environment_type, proj_name):
    valid_env_options = {'dev', 'preprod', 'prod'}
    while environment_type.lower() not in valid_env_options:
        print("Invalid environment option. Please choose from: dev, preprod, prod")
        environment_type = input("Enter the environment for the new project: ").lower()
        

    project_id = create_project(proj_name, environment_type)

    if project_id is None:
        raise Exception("Failed to create project.")
    
    # Set up the environment-specific configurations here
    if environment_type == 'dev':
        # Set up configurations for the development environment
        print("Creating dev environment...")
    elif environment_type == 'preprod':
        # Set up configurations for the pre-production environment
        print("Creating preprod environment...")
    elif environment_type == 'prod':
        # Set up configurations for the production environment
        print("Creating prod environment...")

    create_agent(project_id, environment_type)

def create_project(proj_display_name, env):
    proj_display_name = re.sub(r'[^a-z0-9-]', '-', proj_display_name.lower())
    env = env.lower()

    valid_env_options = {'dev', 'preprod', 'prod'}
    while env.lower() not in valid_env_options:
        print("Invalid environment option. Please choose from: dev, preprod, prod")
        env = input("Enter the environment for the new project: ").lower()

    unique_id = str(uuid.uuid4())[:8]
    project_id = f"{proj_display_name}-{env}-{unique_id}"
    if len(project_id) > 30:
        excess_length = len(project_id) - 30
        project_id = project_id[:-excess_length]
    
    client = resourcemanager_v3.ProjectsClient()

    # Initialize request argument(s)
    request = resourcemanager_v3.CreateProjectRequest(
        project=resourcemanager_v3.Project(
            project_id=project_id,
        )
    )

    print("Creating Google Cloud project...")
    operation = client.create_project(request=request)

    print("Waiting for operation to complete...")

    response = operation.result()
    print(f"Project created: {response}")
    #print(response)

    print(f"Enabling Dialogflow API for project {project_id}...")
    try:
        enable_api(project_id)
        print("Dialogflow API enabled successfully.")
    except Exception as e:
        print(f"Error enabling Dialogflow API: {e}")
        return

    return project_id

def set_agent(proj_id, proj_display_name):
    client = dialogflow.AgentsClient()
    
    parent = f"projects/{proj_id}"
    
    agent = dialogflow.Agent(
        parent=parent,
        display_name=proj_display_name,
        default_language_code='en',
        time_zone='America/Barbados'
    )
    
    print("Creating agent...")
    try:
        response = client.set_agent(request={"agent": agent})
        print(response)
        print(f"Agent '{proj_display_name}' created.")
    except Exception as e:
        print(f"Error creating agent: {e}")

def create_agent(proj_display_name, env):
    #Create new google cloud project
    project_id = create_project(proj_display_name, env)

    if not project_id:
        print("Failed to create a Google Cloud project.")
        return
    
    set_agent(project_id, proj_display_name)
        
def batch_create_intent_from_csv(project_id):
    client = dialogflow.IntentsClient()

    #Initialize a Tkinter root widget
    root = tk.Tk()
    root.withdraw()

    root.attributes("-topmost", True)

    #Display file explorer and return the path to the selected file
    csv_file_path = filedialog.askopenfilename(
        title="Select a CSV File",
        filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
    )

    # Check if a file was selected
    if not csv_file_path:
        print("No file selected.")
        return

# Read the CSV file
    with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # Skip the header row
        for row in csv_reader:
            display_name = row[0]
            training_phrases = []

            #Iterate through columns and stop reading in training phrases if column is empty
            for phrase in row[1:]:
                if not phrase:
                    break
                training_phrases.append(phrase)

            # Create an Intent object
            intent = dialogflow.Intent()
            intent.display_name = display_name

            # Add training phrases to the intent
            for phrase in training_phrases:
                part = dialogflow.Intent.TrainingPhrase.Part(text=phrase.strip())
                training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
                intent.training_phrases.append(training_phrase)

            # Create the CreateIntentRequest
            parent = f'projects/{project_id}/agent'
            request = dialogflow.CreateIntentRequest(
                parent=parent,
                intent=intent,
            )

            # Make the request
            response = client.create_intent(request=request)
            print(f'Intent created: {response.display_name}')
    
if __name__ == "__main__":
    while True:
        print("\nSelect an option:")
        print("1. Pull Intents/Training data")
        print("2. Query Text")
        print("3. Create Environments")
        #print("4. Set Agent")
        print("4. Create Agent")
        print("5. Batch Upload Intent")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == "1":
            user_project_id = input("Enter the Dialogflow project ID: ")
            DIALOGFLOW_PROJECT_ID = user_project_id
            list_intents(user_project_id)
        elif choice == "2":
            text_to_be_analyzed = input("Enter text to be analyzed: ")
            user_project_id = input("Enter the Dialogflow project ID: ")
            DIALOGFLOW_PROJECT_ID = user_project_id
            query_text(text_to_be_analyzed, user_project_id)
        elif choice == "3":
            user_env = input("Enter the environment for the new agent (dev, preprod, prod): ")
            user_display_name = input("Create a name for the new agent: ")
            create_environments(user_env, user_display_name)
        # elif choice == "4":
        #     user_project_id = input("Enter the Dialogflow project ID: ")
        #     DIALOGFLOW_PROJECT_ID = user_project_id
        #     user_display_name = input("Enter the display name for the new agent: ")
        #     set_agent(user_project_id, user_display_name)
        elif choice == "4":
            user_display_name = input("Enter the display name for the new agent: ")
            user_env = input("Enter the environment for the new agent (dev, preprod, prod): ")
            create_agent(user_display_name, user_env)
        elif choice == "5":
            user_project_id = input("Enter the Dialogflow project ID: ")
            DIALOGFLOW_PROJECT_ID = user_project_id
            batch_create_intent_from_csv(user_project_id)
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")