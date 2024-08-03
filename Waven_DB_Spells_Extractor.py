import json
import configparser
import os
import requests
from PIL import Image
import logging
from requests.exceptions import RequestException
from PIL import UnidentifiedImageError


THIS_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
json_filename = "Waven_DB_Spells.json"

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

def process_spells_data():
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
        with open(os.path.join(THIS_FOLDER_PATH, json_filename)) as file:
            data = json.load(file)
        
        # Process each spell in the data
        for spell in data['props']['spells']:
            try:
                # Extract spell information
                name_fr = spell['name_fr']
                name_en = spell['name_en']
                cost = spell['cost']
                element = spell['element']
                gauge_element = spell['gauge1Element']
                gauge_nb = spell['gauge1Value']
                gauge2_element = spell['gauge2Element']
                gauge2_nb = spell['gauge2Value']
                weapon = spell['specific_to_weapon']
                familie = spell['families']
                img_id = spell['img']

                logging.info(f"Processing spell: {name_en}")

                # Create configuration for the spell
                config = create_spell_config(name_fr, name_en, cost, element, gauge_element, gauge_nb,
                                             gauge2_element, gauge2_nb, weapon, familie)

                # Create directory structure and save configuration
                cwd = create_directory_structure(familie, weapon)
                save_spell_config(config, cwd, name_fr)

                # Download and process spell image
                download_and_process_image(img_id, cwd, name_fr)
            except KeyError as e:
                logging.error(f"Missing key in spell data: {e}")
            except Exception as e:
                logging.error(f"Error processing spell {name_en if 'name_en' in locals() else 'unknown'}: {e}")
    except FileNotFoundError:
        logging.error(f"JSON file not found: {json_filename}")
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in file: {json_filename}")
    except Exception as e:
        logging.error(f"Unexpected error in process_spells_data: {e}")

def create_spell_config(name_fr, name_en, cost, element, gauge_element, gauge_nb,
                        gauge2_element, gauge2_nb, weapon, familie):
    """
    Create a configuration object for a spell.

    Args:
        name_fr : French name of the spell.
        name_en : English name of the spell.
        cost : Cost of the spell.
        element : Element of the spell.
        gauge_element : First gauge element.
        gauge_nb : First gauge value.
        gauge2_element : Second gauge element.
        gauge2_nb : Second gauge value.
        weapon : Weapon associated with the spell.
        familie : Family of the spell.

    Returns:
        dict: Configuration object for the spell in .json format.
    """
    config = {
        'name_fr': name_fr,
        'name_en': name_en,
        'cost': cost,
        'element': element,
        'gauge_element': gauge_element,
        'gauge_nb': gauge_nb,
        'gauge2_element': gauge2_element,
        'gauge2_nb': gauge2_nb,
        'weapon': weapon,
        'familie': familie
    }
    return config

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
        cwd = os.path.join(THIS_FOLDER_PATH, str(familie))  # Convert to str
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

def save_spell_config(config, cwd, name_fr):
    """
    Save the spell configuration to a .json file.

    Args:
        config (configparser.ConfigParser): Configuration object for the spell.
        cwd (str): Directory path where the file will be saved.
        name_fr (str): French name of the spell (used for the filename).
    """
    try:
        with open(os.path.join(cwd, f"{name_fr}.json"), 'w') as configfile:
            json.dump(config, configfile)
        logging.info(f"Saved configuration for spell: {name_fr}")
    except IOError as e:
        logging.error(f"Error saving configuration for spell {name_fr}: {e}")

def download_and_process_image(img_id, cwd, name_fr):
    """
    Download, convert, and save the spell image.

    Args:
        img_id (str): ID of the image to download.
        cwd (str): Directory path where the image will be saved.
        name_fr (str): French name of the spell (used for the filename).
    """
    url = f"https://wavendb.com/img/spells/{img_id}.png.webp"
    webp_path = os.path.join(cwd, f'{name_fr}.png.webp')
    png_path = os.path.join(cwd, f'{name_fr}.png')

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
        
        logging.info(f"Successfully processed image for spell: {name_fr}")
    except RequestException as e:
        logging.error(f"Error downloading image for spell {name_fr}: {e}")
    except UnidentifiedImageError as e:
        logging.error(f"Error processing image for spell {name_fr}: {e}")
    except OSError as e:
        logging.error(f"Error saving or deleting image for spell {name_fr}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error processing image for spell {name_fr}: {e}")

# Execute the main function
if __name__ == "__main__":
    process_spells_data()