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

def normalize_folder_name(name):
    """
    Normalize the folder name to comply with OS restrictions:
    - Remove or replace invalid characters.
    - Ensure the name doesn't start with a dot or space.
    - Limit the length of the name if necessary.
    """
    # Remove leading/trailing spaces
    name = name.strip()
    
    # Remove or replace invalid characters
    invalid_chars = r'[\\/*?:"<>|]'
    name = re.sub(invalid_chars, '_', name)
    
    # Ensure name doesn't start with a dot or space
    if name.startswith('.') or name.startswith(' '):
        name = '_' + name.lstrip('. ')
    
    # Limit the length (example: Windows limits to 255 characters)
    max_length = 255
    if len(name) > max_length:
        name = name[:max_length]
    
    # Ensure the name ends with a valid character (some OS don't allow ending with a period or space)
    if name.endswith('.') or name.endswith(' '):
        name = name.rstrip('. ') + '_'
    
    return name

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
                    "content": f"Is this a movie folder? If yes, identify the movie from this folder name: {folder_name}. Return only JSON with keys 'is_movie', 'movie_name', and 'release_year'."
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
        is_movie = movie_data.get('is_movie', False)
        if is_movie:
            movie_name = movie_data.get('movie_name', None)
            year = movie_data.get('release_year', None)
            if movie_name and year:
                movie_name = normalize_folder_name(movie_name)
                logging.info(f"Movie identified: {movie_name} ({year})")
                return movie_name, year, is_movie
        else:
            logging.info(f"Folder {folder_name} does not seem to contain a movie.")
            return None, None, False
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while querying movie info: {e}")
        return None, None, False
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode JSON response: {e}")
        return None, None, False

def confirm_rename(old_name, new_name, parent_dir):
    if old_name.lower() == new_name.lower():
        logging.info(f"Folder name '{old_name}' is already normalized. No renaming needed.")
        return True
    answer = input(f"Do you want to rename '{old_name}' to '{new_name}' in directory '{parent_dir}'? (Y/n): ").lower().strip() or 'y'
    logging.info(f"User response to rename '{old_name}' to '{new_name}' in '{parent_dir}': {answer}")
    return answer == 'y'

def rename_movie_folders(root_dir):
    logging.info(f"Starting folder rename process in directory: {root_dir}")
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for dirname in dirnames:
            full_path = os.path.join(dirpath, dirname)
            movie_name, year, is_movie = get_movie_info(dirname)
            if is_movie and movie_name and year:
                new_name = f"{movie_name} [{year}]"
                new_name = normalize_folder_name(new_name)
                if confirm_rename(dirname, new_name, dirpath):
                    new_path = os.path.join(dirpath, new_name)
                    if full_path != new_path:
                        shutil.move(full_path, new_path)
                        logging.info(f"Renamed: {dirname} to {new_name} in {dirpath}")
            else:
                logging.info(f"Skipping rename for folder: {dirname}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("Usage: python script_name.py <directory_path>")
        sys.exit(1)
    
    root_dir = sys.argv[1]
    if not os.path.isdir(root_dir):
        logging.error("The provided path is not a valid directory.")
        sys.exit(1)
    
    logging.info(f"Starting script with directory: {root_dir}")
    rename_movie_folders(root_dir)
    logging.info("Finished renaming movie folders.")