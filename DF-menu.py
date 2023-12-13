import os
import csv
import tkinter as tk
from tkinter import filedialog
import json
from google.cloud import dialogflow_v2 as dialogflow
from gcloud import resource_manager
from google.api_core.exceptions import InvalidArgument, PermissionDenied

#Change depending on location
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\linds\\Desktop\\private_key.json"

#Global variable to store the last used project ID
last_project_id = 1

def query_text(text):
    DIALOGFLOW_PROJECT_ID = 'test-agent-oren'
    DIALOGFLOW_LANGUAGE_CODE = 'en'
    SESSION_ID = 'me'
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(DIALOGFLOW_PROJECT_ID, SESSION_ID)
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
    client = dialogflow.IntentsClient()

    parent_val = f"projects/{DIALOGFLOW_PROJECT_ID}/agent"
    request = dialogflow.ListIntentsRequest(
        parent=parent_val,
        intent_view="INTENT_VIEW_FULL"
    )

    intents_data = {}  # Dictionary to store intents and training phrases

    try:
        page_result = client.list_intents(request=request)
        for intent in page_result:
            intent_name = intent.display_name
            training_phrases = [phrase.parts[0].text for phrase in intent.training_phrases] if intent.training_phrases else []

            intents_data[intent_name] = {
                'display_name': intent.display_name,
                'training_phrases': training_phrases
            }

        # Write the dictionary to a JSON file
        output_file_path = "intents_with_training_phrases.json"
        with open(output_file_path, 'w') as json_file:
            json.dump(intents_data, json_file, indent=2)

        print("Writing intents with training phrases...")
        print(f"Intents with training phrases written to {output_file_path}")

    except PermissionDenied as e:
        print(f"Permission denied error: {e}")

def create_environments():
    print("Creating environments...")

def set_agent(proj_id, proj_display_name):
    client = dialogflow.AgentsClient()
    
    parent = f"projects/{proj_id}"
    
    agent = dialogflow.Agent(
        parent=parent,
        display_name=proj_display_name,
        default_language_code='en',
        time_zone='America/Barbados'
    )

    #request = dialogflow.SetAgentRequest(agent=agent)
    
    print("Creating agent...")
    try:
        response = client.set_agent(request={"agent": agent})
        print(response)
        print(f"Agent '{proj_display_name}' created.")
    except Exception as e:
        print(f"Error creating agent: {e}")

def create_agent(proj_display_name, env):
    #Create a new google cloud project
    global last_project_id
    last_project_id += 1
    
    valid_env_options = {'dev', 'preprod', 'prod'}
    env = env.lower()

    while env not in valid_env_options:
        print("Invalid environment option. Please choose from: dev, preprod, prod")
        env = input("Enter the environment for the new agent: ").lower()

    client = resource_manager.Client()
    project = client.new_project(f'project-id-{last_project_id}', name=proj_display_name,
                             labels={'environment': env})
    project.create()

    #Extract the project ID from the newly created project
    project_id = project.project_id

    #Create a new Dialogflow project
    dialogflow_client = dialogflow.ProjectsClient()
    parent = f"projects/{project_id}"  # Use the extracted project ID

    dialogflow_project = dialogflow_client.create_project(
        parent=parent,
        project=dialogflow.Project(display_name=proj_display_name)
    )

    # Set roles for Dialogflow API Admin and Dialogflow API Client
    policy = dialogflow_client.get_iam_policy(resource=parent)
    policy.bindings.append(
        dialogflow.Binding(
            role="roles/dialogflow.apiAdmin",
            members=[f"serviceAccount:service-{project.project_number}@dialogflow.iam.gserviceaccount.com"]
        )
    )
    policy.bindings.append(
        dialogflow.Binding(
            role="roles/dialogflow.apiClient",
            members=[f"serviceAccount:service-{project.project_number}@dialogflow.iam.gserviceaccount.com"]
        )
    )
    dialogflow_client.set_iam_policy(resource=parent, policy=policy)

    # Create a new Dialogflow agent
    dialogflow_agent_client = dialogflow.AgentsClient()
    dialogflow_parent = f"projects/{project_id}"

    dialogflow_agent = dialogflow.Agent(
        parent=dialogflow_parent,
        display_name=proj_display_name,
        default_language_code='en',
        time_zone='America/Barbados'
    )

    print("Creating Dialogflow agent...")
    try:
        response = dialogflow_agent_client.set_agent(request={"agent": dialogflow_agent})
        print(response)
        print(f"Dialogflow agent '{proj_display_name}' created.")
    except Exception as e:
        print(f"Error creating Dialogflow agent: {e}")
        
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
            # Each row in the CSV represents an intent
            display_name, training_phrases_string = row

            # Split the training phrases string by comma
            training_phrases = training_phrases_string.split(',')

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
        print("4. Set Agent")
        print("5. Create Agent")
        print("6. Batch Upload Intent")
        print("7. Exit")

        choice = input("Enter your choice (1-7): ")

        if choice == "1":
            user_project_id = input("Enter the Dialogflow project ID: ")
            DIALOGFLOW_PROJECT_ID = user_project_id
            list_intents(user_project_id)
        elif choice == "2":
            text_to_be_analyzed = input("Enter text to be analyzed: ")
            query_text(text_to_be_analyzed)
        elif choice == "3":
            create_environments()
        elif choice == "4":
            user_project_id = input("Enter the Dialogflow project ID: ")
            DIALOGFLOW_PROJECT_ID = user_project_id
            user_display_name = input("Enter the display name for the new agent: ")
            set_agent(user_project_id, user_display_name)
        elif choice == "5":
            user_display_name = input("Enter the display name for the new agent: ")
            user_env = input("Enter the environment for the new agent (dev, preprod, prod): ")
            create_agent(user_display_name, user_env)
        elif choice == "6":
            user_project_id = input("Enter the Dialogflow project ID: ")
            DIALOGFLOW_PROJECT_ID = user_project_id
            batch_create_intent_from_csv(user_project_id)
        elif choice == "7":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")