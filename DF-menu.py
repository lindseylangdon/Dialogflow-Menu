import os
import json
from google.cloud import dialogflow_v2 as dialogflow
from google.api_core.exceptions import InvalidArgument, PermissionDenied

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\linds\\Desktop\\private_key.json"

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

def create_agent(proj_id, proj_display_name):
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

if __name__ == "__main__":
    while True:
        print("\nSelect an option:")
        print("1. Pull Intents/Training data")
        print("2. Query Text")
        print("3. Create Environments")
        print("4. Create Agent")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

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
            create_agent(user_project_id, user_display_name)
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")