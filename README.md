# Dialogflow-Menu
The primary purpose of this code is to automate interactions with Dialogflow specifically focusing on the
following functionalities:
1. Querying Text: The first function of this script (‘query_text’) allows a user to input text for
analysis. This feature facilitates quick and accurate detection of an intent, providing insights into
the detected intent, confidence level, and fulfillment text.
2. Listing Intents: Another function, ‘list_intents’, automates the process of pulling down intents
and their associated training phrases from Dialogflow. This function was the original goal of this
project as manually extracting intents/training phrases is not only time-consuming but also
prone to human error.
3. Creating Environments (in progress): This is a placeholder function for creating environments.
While this function is currently under development, it is designed to support the creation of
different environments, enhancing our ability to manage projects effectively. In our current
Dialogflow project set up, we do not have different environments for our bots. However, we
would like to eventually create dev, preprod, and production environments for all bots.
4. Setting Agent Properties: This function is mainly a helper function that allows users to set
properties for a Dialogflow agent, streamlining the configuration process.
5. Creating New Agents: The function ‘create_agent’ handles the creation of a new
Google Cloud project and Dialogflow Agent. This function supports the dynamic creation agents based on user inputs, such as display name and
environment.
----------------------------------------------------------------------------------------------
The automation of tasks such as pulling down intents and creating new agents eliminates manual
efforts, saving hours of work. Additionally, the ability to create environments and agents
dynamically provides greater flexibility in managing projects across different stages.

## Installation

Before running the `DF-menu.py` script, ensure you have the following prerequisites installed and set up:

1. **Python**: The script is written in Python, so make sure you have Python installed on your system. You can download it from [Python's official website](https://www.python.org/downloads/).

2. **Google Cloud SDK**: Since the script interacts with Dialogflow, which is a part of Google Cloud, you'll need to install the Google Cloud SDK. Follow the instructions [here](https://cloud.google.com/sdk/docs/install) to install it.

3. **Python Packages**: Install the necessary Python packages using pip. Run the following command:

    ```bash
    pip install google-cloud-dialogflow google-cloud-resourcemanager google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
    ```

4. **Environment Variables**: Set up the necessary environment variables. For instance, you'll need to set up the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to authenticate with Google Cloud. Replace `/path/to/your/service-account-file.json` with the path to your JSON service account key file.

    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-file.json"
    ```

5. **Running the Script**: Once everything is set up, you can run the `DF-menu.py` script using Python:

    ```bash
    python DF-menu.py
    ```

Follow these steps to set up and run the `DF-menu.py` script successfully.
