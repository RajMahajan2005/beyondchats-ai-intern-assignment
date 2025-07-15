import os
import re
import praw
import google.generativeai as genai
from dotenv import load_dotenv

def get_username_from_url(url):
    """
    Extracts the Reddit username from a given profile URL.
    """
    match = re.search(r'reddit\.com/user/([^/]+)', url)
    if match:
        return match.group(1)
    return None

def scrape_reddit_data(username, reddit_instance):
    """
    Scrapes comments and posts for a given Reddit username.
    """
    print(f"Fetching data for user: {username}...")
    redditor = reddit_instance.redditor(username)
    comments_data = []
    posts_data = []

    try:
        # Fetch comments (adjust limit as needed, be mindful of API rate limits)
        for comment in redditor.comments.new(limit=50):
            comments_data.append({
                "type": "comment",
                "id": comment.id,
                "body": comment.body,
                "permalink": f"https://www.reddit.com{comment.permalink}"
            })
        print(f"Found {len(comments_data)} comments.")

        # Fetch posts (submissions) (adjust limit as needed)
        for submission in redditor.submissions.new(limit=50):
            posts_data.append({
                "type": "post",
                "id": submission.id,
                "title": submission.title,
                "body": submission.selftext if submission.is_self else "", # selftext for text posts
                "permalink": f"https://www.reddit.com{submission.permalink}"
            })
        print(f"Found {len(posts_data)} posts.")

    except Exception as e:
        print(f"Error fetching Reddit data for {username}: {e}")
        # Consider specific PRAW exceptions for better error handling
    
    return comments_data, posts_data

def build_user_persona(comments_data, posts_data, llm_model):
    """
    Builds a user persona using an LLM based on scraped Reddit data.
    IMPORTANT: You NEED to refine the LLM prompt and parsing logic here.
    """
    all_text_for_llm = []
    source_map = {} # To map IDs back to full permalinks for citations

    for item in comments_data:
        text_entry = f"COMMENT_ID_{item['id']}: {item['body']}"
        all_text_for_llm.append(text_entry)
        source_map[f"COMMENT_ID_{item['id']}"] = item['permalink']

    for item in posts_data:
        post_content = item['body'] if item['body'] else item['title'] # Use body if present, else title
        text_entry = f"POST_ID_{item['id']}: Title: {item['title']}. Content: {post_content}"
        all_text_for_llm.append(text_entry)
        source_map[f"POST_ID_{item['id']}"] = item['permalink']

    combined_text = "\n\n".join(all_text_for_llm)

    if not combined_text.strip():
        return "No sufficient content found for this user to build a persona."

    # --- START: YOUR CRITICAL LLM PROMPT AND PARSING LOGIC HERE ---
    # This is the most crucial part you MUST customize and test.
    # The prompt should clearly ask the LLM to provide characteristics AND their citations.
    # Example persona structure: https://i.imgur.com/example.png (from PDF)
    # The LLM output MUST be parseable to extract both characteristic and citation.

    prompt = f"""
    You are an AI assistant tasked with creating a user persona based on their Reddit activity.
    Analyze the following Reddit comments and posts.
    For each characteristic identified, you MUST cite the exact original text from the comment or post that supports it.
    The source ID (e.g., COMMENT_ID_xyz or POST_ID_abc) must be included directly before the supporting text.

    Format the user persona as follows:

    **User Persona Overview:**
    [A brief summary of the user's overall persona]

    **Key Characteristics:**
    * **[Characteristic Category/Name]**: [Detailed description of the characteristic].
        (Source: [SOURCE_ID_xyz] - "[Exact supporting text from the original Reddit content]")
    * **[Characteristic Category/Name]**: [Detailed description of the characteristic].
        (Source: [SOURCE_ID_abc] - "[Exact supporting text from the original Reddit content]")
    ...

    Consider aspects like:
    - Interests/Hobbies
    - Tone and communication style (e.g., humorous, serious, sarcastic, helpful, formal, informal)
    - Common topics discussed
    - Engagement patterns (e.g., frequent commenter, poster)
    - Demographics (if strongly inferable from explicit statements, be cautious)
    - Values or opinions (if clearly expressed)

    ---
    Reddit Data:
    {combined_text}
    ---

    Please generate the User Persona now:
    """

    try:
        print("Sending data to LLM for persona generation...")
        response = llm_model.generate_content(prompt)
        llm_output = response.text
        print("LLM response received. Now parsing...")

        # --- Example Parsing Logic (You will likely need to adjust this based on LLM's actual output) ---
        # This is a basic example. Robust parsing might require more complex regex or a state machine.
        parsed_persona = []
        lines = llm_output.split('\n')
        current_section = ""
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if "**User Persona Overview:**" in line:
                current_section = "overview"
                parsed_persona.append(line)
            elif "**Key Characteristics:**" in line:
                current_section = "characteristics"
                parsed_persona.append(line)
            elif current_section == "overview":
                parsed_persona.append(line)
            elif current_section == "characteristics" and line.startswith("*"):
                # Try to extract characteristic and citation
                match = re.match(r'\* \*\*(.+?)\*\*:\s*(.+?)\s*\(Source:\s*(.+?)\s*-\s*"(.+?)"\)', line)
                if match:
                    char_name = match.group(1).strip()
                    char_desc = match.group(2).strip()
                    source_id_key = match.group(3).strip()
                    exact_text = match.group(4).strip()

                    # Resolve original permalink for citation
                    original_permalink = source_map.get(source_id_key, "Permalink not found")
                    
                    parsed_persona.append(
                        f"* **{char_name}**: {char_desc}.\n"
                        f"    (Source: {original_permalink} - \"{exact_text}\")"
                    )
                else:
                    # If parsing fails for a line, include it as-is or handle as an error
                    parsed_persona.append(f"    (Unparsable line): {line}")
            else:
                # Catch anything else not fitting the expected format
                parsed_persona.append(line)
        # --- END: YOUR CRITICAL LLM PROMPT AND PARSING LOGIC HERE ---

        return "\n".join(parsed_persona)

    except Exception as e:
        return f"Error generating persona with LLM or parsing response: {e}"

def output_persona_to_file(username, persona_text):
    """
    Writes the generated user persona to a text file.
    """
    filename = f"user_persona_{username}.txt"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(persona_text)
        print(f"User persona saved to {filename}")
    except IOError as e:
        print(f"Error saving persona to file {filename}: {e}")

if __name__ == "__main__":
    load_dotenv() # Load environment variables from .env file

    # Initialize Reddit API
    reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
    reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    reddit_user_agent = os.getenv("REDDIT_USER_AGENT")

    if not all([reddit_client_id, reddit_client_secret, reddit_user_agent]):
        print("Error: Reddit API credentials (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT) are not set in .env")
        print("Please refer to README.md for setup instructions.")
        exit(1)

    try:
        reddit_instance = praw.Reddit(
            client_id=reddit_client_id,
            client_secret=reddit_client_secret,
            user_agent=reddit_user_agent
        )
    except Exception as e:
        print(f"Error initializing Reddit PRAW instance: {e}")
        exit(1)

    # Initialize Google Generative AI
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        print("Error: GOOGLE_API_KEY is not set in .env")
        print("Please refer to README.md for setup instructions.")
        exit(1)
    
    try:
        genai.configure(api_key=google_api_key)
        llm_model = genai.GenerativeModel('gemini-pro') # Or 'gemini-1.0-pro'
    except Exception as e:
        print(f"Error initializing Google Generative AI model: {e}")
        exit(1)

    # Sample Reddit profile URLs from the assignment [cite: 10, 11, 12]
    reddit_profile_urls = [
        "https://www.reddit.com/user/kojied/",
        "https://www.reddit.com/user/Hungry-Move-6603/"
    ]

    for url in reddit_profile_urls:
        username = get_username_from_url(url)
        if username:
            print(f"\n--- Starting persona generation for user: {username} ---")
            comments, posts = scrape_reddit_data(username, reddit_instance)
            persona_text = build_user_persona(comments, posts, llm_model)
            output_persona_to_file(username, persona_text)
            print(f"--- Finished persona generation for user: {username} ---\n")
        else:
            print(f"Skipping invalid URL: {url} - Could not extract username.")