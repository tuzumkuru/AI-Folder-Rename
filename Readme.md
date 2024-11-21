# Movie Folder Renamer

This script renames movie folders based on the movie name and release year identified from their current names using an external API.

## Requirements

- Python 3.6+
- `requests`
- `python-dotenv`
- `shutil`
- `logging`

Install required packages:
```sh
pip install requests python-dotenv
```

## Setup

1. **API Key**: You need to have an API key for the Open WebUI service. Set it as an environment variable:
   ```sh
   export OPEN_WEBUI_API_KEY=your_api_key_here
   ```

   Alternatively, create a `.env` file in the same directory as the script with:
   ```plaintext
   OPEN_WEBUI_API_KEY=your_api_key_here
   ```

2. **Permissions**: Ensure the script has the necessary permissions to rename folders in the target directory.

## Usage

Run the script from the command line, providing the directory path where movie folders reside:

```sh
python movie_rename.py /path/to/movies
```

## Features

- **Folder Name Normalization**: The script normalizes folder names to comply with OS restrictions:
  - Removes or replaces invalid characters.
  - Ensures the name doesn't start with a dot or space.
  - Limits the length of the name if necessary.
  
- **User Confirmation**: 
  - The script prompts for confirmation before renaming any folder.
  - If the new and old names are the same (case-insensitive), no renaming is attempted.
  - Default answer for renaming is 'Y'. Pressing enter without typing anything will proceed with renaming.

- **Logging**: All operations are logged to a file named `movie_rename_log_YYYYMMDD_HHMMSS.log` and to the console.

- **Error Handling**: Catches and logs errors related to API requests and JSON parsing.

## Limitations

- **API Dependency**: The script depends on an external API to identify movies. If the API service is down or the API key is invalid, the script will fail.
- **Naming Conventions**: The script assumes that movie names and years are identifiable from the current folder names. Variations or ambiguities might lead to incorrect renaming.

## Example

```sh
python movie_rename.py ~/Movies
```

This will scan the `~/Movies` directory, attempt to identify movies, and offer to rename the folders accordingly.

## License

[Insert License Information Here]

