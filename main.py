import os
import shutil
import requests
from dotenv import load_dotenv
import sys
import logging
from datetime import datetime
import json
import re

# Load environment variables
load_dotenv()
OPEN_WEBUI_API_KEY = os.getenv("OPEN_WEBUI_API_KEY")
OPEN_WEBUI_ENDPOINT = "https://chat.tuzumkuru.com/api/chat/completions"

# Configure logging
log_file = f"movie_rename_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

def get_movie_info(folder_name):
    try:
        logging.info(f"Querying movie info for folder: {folder_name}")
        headers = {
            "Authorization": f"Bearer {OPEN_WEBUI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "grok-beta",
            "messages": [
                {
                    "role": "user",
                    "content": f"Identify the movie from this folder name: {folder_name}. Return only JSON with the keys 'movie_name' and 'release_year'."
                }
            ],
            "max_tokens": 200,
            "temperature": 0.5,
            "top_p": 1
        }
        response = requests.post(OPEN_WEBUI_ENDPOINT, headers=headers, json=data)
        response.raise_for_status()
        movie_info = response.json()['choices'][0]['message']['content'].strip()

        # Remove the ```json and ``` from the response
        movie_info = re.sub(r'^```json\s*|\s*```$', '', movie_info)
        logging.info(f"AI Response: {movie_info}")

        # Parse the JSON response
        movie_data = json.loads(movie_info)
        movie_name = movie_data.get('movie_name', None)
        year = movie_data.get('release_year', None)
        if movie_name and year:
            logging.info(f"Movie identified: {movie_name} ({year})")
            return movie_name, year
        else:
            logging.warning(f"Could not parse movie info from response: {movie_info}")
            return None, None
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while querying movie info: {e}")
        return None, None
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode JSON response: {e}")
        return None, None

def confirm_rename(old_name, new_name):
    answer = input(f"Do you want to rename '{old_name}' to '{new_name}'? (y/n): ").lower()
    logging.info(f"User response to rename '{old_name}' to '{new_name}': {answer}")
    return answer == 'y'

def rename_and_flatten_movie_folders(root_dir):
    logging.info(f"Starting folder rename and flatten process in directory: {root_dir}")
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        for dirname in list(dirnames):
            full_path = os.path.join(dirpath, dirname)
            if dirpath != root_dir:
                logging.info(f"Moving folder '{dirname}' from '{dirpath}' to root directory.")
                shutil.move(full_path, root_dir)
            
            movie_name, year = get_movie_info(dirname)
            if movie_name and year:
                new_name = f"{movie_name} [{year}]"
                if confirm_rename(dirname, new_name):
                    new_path = os.path.join(root_dir, new_name)
                    if full_path != new_path:
                        counter = 1
                        while os.path.exists(new_path):
                            new_name = f"{movie_name} [{year}] ({counter})"
                            new_path = os.path.join(root_dir, new_name)
                            counter += 1
                        shutil.move(os.path.join(root_dir, dirname), new_path)
                        logging.info(f"Renamed: {dirname} to {new_name}")
            else:
                logging.warning(f"Could not identify movie for folder: {dirname}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("Usage: python script_name.py <directory_path>")
        sys.exit(1)
    
    root_dir = sys.argv[1]
    if not os.path.isdir(root_dir):
        logging.error("The provided path is not a valid directory.")
        sys.exit(1)
    
    logging.info(f"Starting script with directory: {root_dir}")
    rename_and_flatten_movie_folders(root_dir)
    logging.info("Finished renaming and restructuring movie folders.")