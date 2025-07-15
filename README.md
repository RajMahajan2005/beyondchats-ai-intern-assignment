# Reddit User Persona Generator

This project develops a Python script to generate a user persona for a given Reddit profile, leveraging the Reddit API for data extraction and a Google Large Language Model (LLM) for persona generation. Each characteristic identified in the user persona is cited with the original Reddit post or comment that supports it. This project was developed as part of an AI/LLM Engineer Intern assignment, demonstrating problem-solving and coding expertise.

## Features

* **Input Handling**: Takes a Reddit user's profile URL as input.
* **Data Scraping**: Scrapes comments and posts created by the specified Redditor using the [PRAW](https://praw.readthedocs.io/en/stable/) library.
* **Persona Generation**: Builds a user persona based on details found in their Reddit activity using a Google LLM (Gemini-Pro).
* **Citation**: For each characteristic in the user persona, the script cites the specific Reddit content (posts or comments) used to extract that information.
* **Output**: Outputs the generated user persona for the input profile into a text file.

## Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YourGitHubUsername/your_repo_name.git](https://github.com/YourGitHubUsername/your_repo_name.git)
    cd your_repo_name
    ```
    *(Replace `YourGitHubUsername/your_repo_name.git` with your actual GitHub repository URL after you've created it.)*

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    ```
    * **Activate the virtual environment:**
        * On Windows:
            ```bash
            .\venv\Scripts\activate
            ```
        * On macOS/Linux:
            ```bash
            source venv/bin/activate
            ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **API Key Configuration:**
    This project requires API credentials for both Reddit and Google Generative AI.

    * **Reddit API Credentials:**
        1.  Go to [Reddit's developer page](https://www.reddit.com/prefs/apps) (you might need to log in to your Reddit account).
        2.  Click "create app" (or "create another app" if you have existing ones).
        3.  Select "script" as the application type.
        4.  Provide a **Name** (e.g., "BeyondChatsPersonaGenerator"), a brief **Description**, and set the `redirect uri` to `http://localhost:8080`.
        5.  After creation, you will see your "client ID" (usually a string below the app name) and a "secret" (a string labeled "secret").
        6.  Also, choose a descriptive `user_agent` string for your application (e.g., "BeyondChatsPersonaGenerator/1.0 by YourRedditUsername").

    * **Google Generative AI API Key:**
        Your Google API Key is `AIzaSyDljnXii9zOawhMwpwussOleKZ1Ssk7i94`.

    * **Environment Variables (`.env` file):**
        Create a file named `.env` (it should **NOT** be committed to your public repository) in the root directory of your project (the same directory as `main.py`).

        Populate your `.env` file with the following, replacing the placeholder values with your actual keys:

        ```
        REDDIT_CLIENT_ID="YOUR_REDDIT_CLIENT_ID_HERE"
        REDDIT_CLIENT_SECRET="YOUR_REDDIT_CLIENT_SECRET_HERE"
        REDDIT_USER_AGENT="YourAppName/1.0 by YourRedditUsername" # Use the user agent you decided on
        GOOGLE_API_KEY="AIzaSyDljnXii9zOawhMwpwussOleKZ1Ssk7i94"
        ```
        Refer to `.env.example` (also in this repository) for the required variable names.

## Execution Instructions

To run the script and generate personas for the sample users provided in the assignment (`kojied` and `Hungry-Move-6603`):

```bash
python main.py
