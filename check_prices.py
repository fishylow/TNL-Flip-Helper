import json
import time
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama for color support
init(autoreset=True)

# Define file paths
LIST_FILE_PATH = rf"C:\Users\neder\OneDrive\Dokumentumok\MarketSniper\Attempt2\list.json"
ITEMS_FILE_PATH = rf"C:\Users\neder\OneDrive\Dokumentumok\MarketSniper\Attempt2\items.json"
TRAITS_FILE_PATH = rf"C:\Users\neder\OneDrive\Dokumentumok\MarketSniper\Attempt2\traits.json"

# Define the interval in seconds
INTERVAL = 30

# To track previously printed items
previous_items = set()

def load_json(file_path):
    # Load JSON data from a file.
    if not Path(file_path).is_file():
        print(f"File '{file_path}' not found.")
        return {}
    with open(file_path, "r") as file:
        return json.load(file)

def match_ids_with_names_and_traits(flagged_ids, items_data, traits_data, sales_data):
    # Match flagged IDs with their names and traits.
    id_to_name = {str(item["num"]): item["name"] for item in items_data}
    results = []
    
    for item_id in flagged_ids:
        name = id_to_name.get(item_id, "Unknown Item")
        first_trait = sales_data[item_id]["sales"][0].get("t")
        trait_name = traits_data.get(str(first_trait), {}).get("name", "Unknown Trait")
        results.append((item_id, name, first_trait, trait_name))
    
    return results

def check_sales():
    global previous_items
    try:
        # Load data from files
        list_data = load_json(LIST_FILE_PATH)
        items_data = load_json(ITEMS_FILE_PATH)
        traits_data = load_json(TRAITS_FILE_PATH)

        if not list_data or not items_data or not traits_data:
            print("Data not available. Skipping this iteration...")
            return

        # Filter sales data for flagged IDs
        flagged_ids = []
        prices = {}
        for item_id, item_data in list_data.items():
            sales = item_data.get("sales", [])
            # Ensure there are at least two sales entries to compare
            if len(sales) >= 2:
                first_price = sales[0].get("p")
                second_price = sales[1].get("p")
                if first_price is not None and second_price is not None:
                    # Check if the first price is less than 50% of the second
                    if first_price < 0.5 * second_price:
                        flagged_ids.append(item_id)
                        prices[item_id] = (first_price, second_price)

        # Match flagged IDs with names and traits
        matched_items = match_ids_with_names_and_traits(flagged_ids, items_data, traits_data, list_data)

        # Prepare new items for highlighting
        current_items = set(flagged_ids)
        new_items = current_items - previous_items
        previous_items = current_items

        # Print the results
        if matched_items:
            print(r"-------------------Flagged items with unusally low price (<50% of normal):-------------------")
            for item_id, name, trait_id, trait_name in matched_items:
                first_price, second_price = prices[item_id]
                highlight = Fore.RED if item_id in new_items else ""
                print(f"{highlight}Lowest: {first_price} | Next: {second_price} | Item: {name} | Trait: {trait_name}")
        else:
            print("No items found with unusually low prices")

    except Exception as e:
        print(f"An error occurred: {e}")

def start_monitoring():
    print(f"Starting monitoring for files:")
    print(f"- List file: {LIST_FILE_PATH}")
    print(f"- Items file: {ITEMS_FILE_PATH}")
    print(f"- Traits file: {TRAITS_FILE_PATH}")
    while True:
        check_sales()
        time.sleep(INTERVAL)

if __name__ == "__main__":
    start_monitoring()
