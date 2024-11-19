import json
import time
import os
from pathlib import Path
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama for color support
init(autoreset=True)

# Define project folder
PROJECT_FOLDER = r"C:\Users\neder\OneDrive\Dokumentumok\MarketSniper\Attempt2"

LIST_FILE_PATH = os.path.join(PROJECT_FOLDER, "list.json")
ITEMS_FILE_PATH = os.path.join(PROJECT_FOLDER, "items.json")
TRAITS_FILE_PATH = os.path.join(PROJECT_FOLDER, "traits.json")

RARITY_COLORS = {
    2: Style.BRIGHT + Fore.WHITE,
    3: Style.BRIGHT + Fore.GREEN,
    4: Style.BRIGHT + Fore.BLUE,
    5: Style.BRIGHT + Fore.MAGENTA, 
}

# Define the interval in seconds
INTERVAL = 5

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
    """Match flagged IDs with their names, traits, and rarity."""
    id_to_item = {str(item["num"]): item for item in items_data}
    results = []
    
    for item_id in flagged_ids:
        item_data = id_to_item.get(item_id, {})
        name = item_data.get("name", "Unknown Item")
        rarity = item_data.get("rarity", 2)  # Default to 2 if no rarity is specified
        first_trait = sales_data[item_id]["sales"][0].get("t")
        trait_name = traits_data.get(str(first_trait), {}).get("name", "Unknown Trait")
        results.append((item_id, name, rarity, trait_name))
    
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

        # Match flagged IDs with names, rarity, and traits
        matched_items = match_ids_with_names_and_traits(flagged_ids, items_data, traits_data, list_data)

        # Prepare new items for display
        current_items = set(flagged_ids)
        new_items = current_items - previous_items
        previous_items.update(new_items)

        # Print new items
        if new_items:
            print(f"New flagged items at {datetime.now().strftime('%H:%M')}:")
            for item_id, name, rarity, trait_name in matched_items:
                if item_id in new_items:
                    first_price, second_price = prices[item_id]
                    rarity_color = RARITY_COLORS.get(rarity, Style.BRIGHT + Fore.WHITE)
                    print(
                        f"{rarity_color}{name}{Style.RESET_ALL} | Lowest: {first_price} | Next: {second_price} | Trait: {trait_name}"
                    )
        else:
            print(f"No new items at {datetime.now().strftime('%H:%M')}.")

    except Exception as e:
        print(f"An error occurred: {e}")

def start_monitoring():
    print(f"Starting monitoring for files:")
    print(f"- List file: {LIST_FILE_PATH}")
    print(f"- Items file: {ITEMS_FILE_PATH}")
    print(f"- Traits file: {TRAITS_FILE_PATH}")
    while True:
        check_sales()
        time.sleep(INTERVAL)  # Check every 30 seconds

if __name__ == "__main__":
    start_monitoring()
