# Waven DB Spell Extractor

## Description

The Waven DB Spell Extractor is a Python script designed to automate the extraction, organization, and processing of spell data from a JSON file. This script performs the following tasks:

1. **Download Json Data** from https://wavendb.com/spells
2. **Loads spell data** from a JSON file.
3. **Creates configuration files** for each spell in `.json` format.
4. **Organizes spells** into folders based on their family and weapon.
5. **Downloads and converts spell images** from WebP to PNG format.

## Requirements

- Python 3.x
- `requests` library
- `Pillow` library
- `beautifulsoup4` library

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/waven-db-spell-extractor.git
    cd waven-db-spell-extractor
    ```

2. **Install the required libraries**:
    ```sh
    pip install requests Pillow beautifulsoup4
    ```
    OR
   ```sh
    pip install -r Requirements.txt
    ```

## Usage
1. **Run the script**:
    ```sh
    python waven_db_spell_extractor.py
    ```
## Arguments
`-mv` Rename folders into gods and weapons names (exemple : Folder `1` will be rename as `Iop`).
`-l` Set the language preference, default is `en`. Available language : en, fr, es, de, pt.

##Exemple
1. **Download data in spanish and rename folder"
    ```sh
    python waven_db_spell_extractor.py -mv -l es
    ```

## Script Details

### Functions

- **`process_spells_data`**: Main function that processes the spell data, creates configuration files, organizes directories, and handles image downloads and conversions.
- **`create_spell_config`**: Generates a configuration object for a spell.
- **`create_directory_structure`**: Creates a nested directory structure for storing spell data based on family and weapon.
- **`save_spell_config`**: Saves the spell configuration to a `.json` file.
- **`download_and_process_image`**: Downloads the spell image, converts it from WebP to PNG, and saves it in the appropriate directory.
- - **`fetch_data_page`**: Fetches the HTML content from the given URL.
- **`extract_data_page`**: Extracts the `data-page` attribute from the HTML content and parses it into a dictionary.
- **`rename_folder`**: Rename folders into gods and weapons names.

### Error Handling

The script includes comprehensive error handling to log issues related to:
- Missing keys in the JSON data.
- File operations (reading, writing, creating directories).
- Image processing (downloading, converting).
- Network requests.

This ensures that the script continues running even if it encounters problems with individual spells.

## Example

Here is an example of how the directory structure and configuration files will be organized:

```
Waven_DB_Spells/
├── Spells/
│  ├── 11/
│     ├── weapon1/
│     │   ├── spell1.json
│     │   ├── spell1.png
│     │   ├── spell2.json
│     │   ├── spell2.png
│     ├── weapon2/
│     │   ├── spell3.json
│     │   ├── spell3.png
│     └── weapon3/
│         ├── spell4.json
│         ├── spell4.png
...
```

Each `.json` file contains the configuration details for a spell, and each `.png` file is the downloaded and converted image for that spell.

## Contributing

If you would like to contribute to this project, please fork the repository and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the GNUv3.0 License. See the [LICENSE](LICENSE) file for details.

## Contact

If you have any questions or need further assistance, please open an issue in this repository.

## Disclaimer
This project is intended solely for educational purposes and to provide a practical example of data extraction, processing, and organization techniques. There is no intention to harm, infringe on copyrights, or misuse the information and resources provided. Users are encouraged to use this script responsibly and ensure that they have the proper permissions when handling data and resources from external sources.

Please note that I cannot be held responsible for any misuse, damage, or legal issues that may arise from the use of this script. Users are fully responsible for their actions and must ensure compliance with all applicable laws and regulations.

---

Thank you for using the Waven DB Spell Extractor!
