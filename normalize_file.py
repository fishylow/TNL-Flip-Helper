import json
import subprocess
from pathlib import Path

# Initialize colorama for color support

# Define project folder
PROJECT_FOLDER = Path(__file__).parent

LIST_FILE_PATH = PROJECT_FOLDER / "list.json"
ITEMS_FILE_PATH = PROJECT_FOLDER / "items.json"
TRAITS_FILE_PATH = PROJECT_FOLDER / "traits.json"
QUESTLOG_DB_FILE_PATH = PROJECT_FOLDER / "questlog_db.json"

DEBUG = False


def load_json(file_path):
    # Load JSON data from a file.
    if not Path(file_path).is_file():
        print(f"File '{file_path}' not found.")
        return {}
    with open(file_path, "r") as file:
        return json.load(file)


def merge_data():
    process = subprocess.Popen(['node', 'script.js'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        # Wait for the process to complete (optional timeout)
        stdout, stderr = process.communicate(timeout=10)  # Optional: use a timeout to avoid hanging
        print("Node.js output:", stdout)
    except subprocess.TimeoutExpired:
        # Terminate the process if it takes too long
        process.kill()
        print("Node.js script took too long and was terminated.")
    
    NORMALIZED_LIST = []
    price_data = load_json(LIST_FILE_PATH)
    items_data = load_json(ITEMS_FILE_PATH)
    traits_data = load_json(TRAITS_FILE_PATH)
    questlog_data = load_json(QUESTLOG_DB_FILE_PATH)
    
    def fetch_prices(parent_id):
        record = price_data.get(str(parent_id),{})
        sales = record.get("sales",[])
        return sales
        
    
    for item in items_data:
        item_sales_data = fetch_prices(item["num"])
        base_item = {
            "parent_id": item["id"],
            "parent_num": item["num"],
            "parent_name": item["name"],
            "parent_rarity": item["rarity"],
            "parent_icon": item["icon"],
            "rarity": item["rarity"],
            "is_traited": False,
            "questlog_id": questlog_data.get(item["name"])
        }
        
        if item["traits"]:
            for trait in item["traits"]:
                traited_item = base_item.copy()
                traited_sales_data = [sale['p'] for sale in item_sales_data if sale.get('t') == trait]
                
                traited_item["is_traited"] = True
                traited_item["trait_id"] = trait
                traited_item["trait_name"] = traits_data[str(trait)]["name"]
                traited_item["parent_combined_name"] = f"{item['name']} - {traits_data[str(trait)]['name']}"
                traited_item["prices_list"] = traited_sales_data
                traited_item["quantity"] = len(traited_sales_data)
                NORMALIZED_LIST.append(traited_item)
        else:
            parent_item_sales = [sale['p'] for sale in item_sales_data]
            base_item["parent_combined_name"] = item["name"]
            base_item["prices_list"] = parent_item_sales
            base_item["quantity"] = len(parent_item_sales)
            NORMALIZED_LIST.append(base_item)
    
    if DEBUG: 
        with open("normalized_list.json", "w") as json_file:
            json.dump(NORMALIZED_LIST, json_file, indent=4)
            print("ok")
            
    #print("Total Generated List Length:", len(NORMALIZED_LIST))
    return NORMALIZED_LIST