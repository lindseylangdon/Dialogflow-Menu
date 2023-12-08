# Dialogflow-Menu
The primary purpose of this code is to automate interactions with Dialogflow specifically focusing on the
following functionalities:
**1**. Querying Text: The first function of this script (‘query_text’) allows a user to input text for
analysis. This feature facilitates quick and accurate detection of an intent, providing insights into
the detected intent, confidence level, and fulfillment text.
**2**. Listing Intents: Another function, ‘list_intents’, automates the process of pulling down intents
and their associated training phrases from Dialogflow. This function was the original goal of this
project as manually extracting intents/training phrases is not only time-consuming but also
prone to human error.
**3**. Creating Environments (in progress): This is a placeholder function for creating environments.
While this function is currently under development, it is designed to support the creation of
different environments, enhancing our ability to manage projects effectively. In our current
Dialogflow project set up, we do not have different environments for our bots. However, we
would like to eventually create dev, preprod, and production environments for all bots.
**4**. Setting Agent Properties: This function is mainly a helper function that allows users to set
properties for a Dialogflow agent, streamlining the configuration process.
**5**. Creating New Agents (in progress): The function ‘create_agent’ handles the creation of a new
Google Cloud project, Dialogflow project, and agents inside the new project. This functions
supports the dynamic creation agents based on user inputs, such as display name and
environment.
----------------------------------------------------------------------------------------------
The automation of tasks such as pulling down intents and creating new agents eliminates manual
efforts, saving hours of work. Additionally, the ability to create environments and agents
dynamically provides greater flexibility in managing projects across different stages, from
development to production.

**Important Note:**
Before running code, make sure the necessary dependencies are installed (Python, Google Cloud SDK,
pip, pip google-cloud-dialogflow, pip gcloud, pip google-api-core). Additionally, update the
‘GOOGLE_APPLICATION_CREDENTIALS’ environment variable to the path of the service account key file
on your local machine.
