import json
import os
import requests
from PIL import Image
import logging
from requests.exceptions import RequestException
from PIL import UnidentifiedImageError
from bs4 import BeautifulSoup
import argparse
import sys

# ArgParse
parser = argparse.ArgumentParser(description='WavenDB-Spell-Scraper')
parser.add_argument('--rename_folder','-mv', dest='rename_folder', action='store_true', help='Rename folders by god and weapon name', required=False)
parser.add_argument('--language','-l', dest='language', action='store', default="en", help='set the language preference.\nAvailable language : en, fr, es, de, pt', required=False)


def process_spells_data(json_filename):
    """
    Process spell data from a JSON file, create configuration files, and download spell images.

    This function performs the following tasks:
    1. Loads spell data from a JSON file.
    2. Creates a configuration file for each spell.
    3. Organizes spells into folders based on their family and weapon.
    4. Downloads and converts spell images.

    The function assumes the existence of a 'spells.json' file in the same directory.
    """
    try:
        # Load the content from the JSON file
        with open(os.path.join(THIS_FOLDER_PATH, json_filename), encoding="utf8") as file:
            data = json.load(file)
        
        language = args.language
        # Process each spell in the data
        for spell in data['props']['spells']:
            try:
                # Extract spell information
                name = spell[f'name_{language}']
                weapon = spell['specific_to_weapon']
                familie = spell['families']
                img_id = spell['img']

                logging.info(f"Processing spell: {name}")

                # Create directory structure and save configuration
                cwd = create_directory_structure(familie, weapon)
                save_spell_config(spell, cwd, name)

                # Download and process spell image
                download_and_process_image(img_id, cwd, name)
            except KeyError as e:
                logging.error(f"Missing key in spell data: {e}")
            except Exception as e:
                logging.error(f"Error processing spell {name if 'name_en' in locals() else 'unknown'}: {e}")
    except FileNotFoundError:
        logging.error(f"JSON file not found: {json_filename}")
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in file: {json_filename}")
    except Exception as e:
        logging.error(f"Unexpected error in process_spells_data: {e}")

def create_directory_structure(familie, weapon):
    """
    Create the directory structure for storing spell data.

    Args:
        familie : Family of the spell.
        weapon : Weapon associated with the spell.

    Returns:
        str: Path to the directory where the spell data will be stored.
    """
    try:
        cwd = os.path.join(RESULT_FOLDER_PATH, str(familie))  # Convert to str
        if not os.path.exists(cwd):
            os.makedirs(cwd)
        
        if weapon is not None:
            cwd = os.path.join(cwd, str(weapon))  # Convert to str
            if not os.path.exists(cwd):
                os.makedirs(cwd)
        
        logging.info(f"Created directory: {cwd}")
        return cwd
    except OSError as e:
        logging.error(f"Error creating directory structure: {e}")
        raise

def save_spell_config(spell, cwd, name):
    """
    Save the spell configuration to a .json file.

    Args:
        config (configparser.ConfigParser): Configuration object for the spell.
        cwd (str): Directory path where the file will be saved.
        name (str): name of the spell (used for the filename).
    """
    try:
        with open(os.path.join(cwd, f"{name}.json"), 'w') as configfile:
            json.dump(spell, configfile, indent=4)
        logging.info(f"Saved configuration for spell: {name}")
    except IOError as e:
        logging.error(f"Error saving configuration for spell {name}: {e}")

def download_and_process_image(img_id, cwd, name):
    """
    Download, convert, and save the spell image.

    Args:
        img_id (str): ID of the image to download.
        cwd (str): Directory path where the image will be saved.
        name (str): name of the spell (used for the filename).
    """
    url = f"https://wavendb.com/img/spells/{img_id}.png.webp"
    webp_path = os.path.join(cwd, f'{name}.png.webp')
    png_path = os.path.join(cwd, f'{name}.png')

    try:
        # Download the image
        response = requests.get(url)
        response.raise_for_status()
        img = response.content

        # Save the downloaded WebP image
        with open(webp_path, 'wb') as handler:
            handler.write(img)
        
        # Convert WebP to PNG
        im = Image.open(webp_path, 'r').convert("RGB")
        im.save(png_path, "png")
        
        # Delete the WebP image file
        os.remove(webp_path)
        
        logging.info(f"Successfully processed image for spell: {name}")
    except RequestException as e:
        logging.error(f"Error downloading image for spell {name}: {e}")
    except UnidentifiedImageError as e:
        logging.error(f"Error processing image for spell {name}: {e}")
    except OSError as e:
        logging.error(f"Error saving or deleting image for spell {name}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error processing image for spell {name}: {e}")

def fetch_data_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching URL: {e}")
        return None

def extract_data_page(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        data_page_div = soup.find('div', id='app')
        if data_page_div and 'data-page' in data_page_div.attrs:
            data_page_json = data_page_div['data-page']
            return json.loads(data_page_json)
        else:
            logging.error("data-page attribute not found in the div")
            return None
    except Exception as e:
        logging.error(f"Error extracting data-page: {e}")
        return None

def rename_folder(json_file):
    """
    Renames folders and subfolders based on the data from a JSON file.

    This function reads the content of a JSON file, iterates through the folders in a specified directory, and renames them based on the 'id' and 'name_language' attributes of the 'gods' and 'weapons' in the JSON data. The function logs each step of the process for debugging purposes.

    Parameters:
    - json_file (str): The path to the JSON file containing the data for renaming folders.

    Returns:
    - None
    """
    language = args.language
    
    # Load the content from the JSON file
    with open(os.path.join(json_file), encoding="utf8") as file:
        data = json.load(file)
            
    logging.debug(f"Loaded JSON data from {json_file}")
            
    for folder in os.listdir(RESULT_FOLDER_PATH):
        logging.debug(f"Checking folder: {folder}")
        for god in data['props']['gods']:
            logging.debug(f"Checking god: {god['id']}")
            if folder == str(god['id']):
                new_folder_name = str(god[f'name_{language}'])
                logging.info(f"Renaming folder {folder} to {new_folder_name}")
                os.rename(os.path.join(RESULT_FOLDER_PATH, folder), os.path.join(RESULT_FOLDER_PATH, new_folder_name))
                logging.info(f"Renamed folder {folder} to {new_folder_name}")
                
                for sub_folder in [f for f in os.listdir(os.path.join(RESULT_FOLDER_PATH, new_folder_name)) if os.path.isdir(os.path.join(RESULT_FOLDER_PATH, new_folder_name, f))]:
                    
                    logging.debug(f"Checking sub folder: {sub_folder}")
                    for weapon in god['weapons']:
                        logging.debug(f"Checking weapon: {weapon['id']}")
                        if sub_folder == str(weapon['id']):
                            new_sub_folder_name = weapon[f'name_{language}']
                            logging.info(f"Renaming sub folder {sub_folder} to {new_sub_folder_name}")
                            os.rename(os.path.join(RESULT_FOLDER_PATH, new_folder_name, sub_folder), os.path.join(RESULT_FOLDER_PATH, new_folder_name, new_sub_folder_name))
                            logging.info(f"Renamed sub folder {sub_folder} to {new_sub_folder_name}")
                        
def main(url='https://wavendb.com/spells', file_name="Waven_DB_Spells.json"):
    html_content = fetch_data_page(url)
    if html_content:
        data_page = extract_data_page(html_content)
        if data_page:
            output_file = os.path.join(THIS_FOLDER_PATH, file_name)
            
            # Write the result to the file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data_page, f, indent=4, ensure_ascii=False)
            
            logging.info(f"Data written to {output_file}")
            
            process_spells_data(file_name)
        else:
            logging.error("No data found to process.")
            
        if args.rename_folder:
            rename_folder(output_file)
    else:
        logging.error("No HTML content fetched from the URL.")
        
            
# Execute the main function
if __name__ == "__main__":
    
    args = parser.parse_args()
    
    available_languages = ['en', 'fr', 'es', 'de', 'pt']
    if args.language not in available_languages:
        logging.error(f"Language '{args.language}' is not available. Please choose from: {', '.join(available_languages)}")
        sys.exit()
        
    THIS_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
    RESULT_FOLDER_PATH = os.path.join(THIS_FOLDER_PATH, "Spells")
    
    if not os.path.exists(RESULT_FOLDER_PATH):
        os.makedirs(RESULT_FOLDER_PATH)
    
    # Supprime les logs précédent
    if os.path.exists(os.path.join(THIS_FOLDER_PATH, 'Waven_DB_Spell_Extractor.log')):
        os.remove(os.path.join(THIS_FOLDER_PATH, 'Waven_DB_Spell_Extractor.log'))
        
    # Configure logging to log to both file and console
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                        filename=os.path.join(THIS_FOLDER_PATH, 'Waven_DB_Spell_Extractor.log'),
                        filemode='a')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(console_handler)

    main()
