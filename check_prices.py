import json
import time
import os
import sys
import pyperclip
from pathlib import Path
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from colorama import init
import winsound

# Initialize colorama for color support
init(autoreset=True)

# Define project folder
PROJECT_FOLDER = r"C:\Users\neder\OneDrive\Dokumentumok\MarketSniper\Attempt2"

LIST_FILE_PATH = os.path.join(PROJECT_FOLDER, "list.json")
ITEMS_FILE_PATH = os.path.join(PROJECT_FOLDER, "items.json")
TRAITS_FILE_PATH = os.path.join(PROJECT_FOLDER, "traits.json")

RARITY_COLORS = {
    2: (255, 255, 255),  # White
    3: (0, 255, 0),      # Green
    4: (0, 0, 255),      # Blue
    5: (255, 0, 255),    # Magenta
}

# Define the interval in seconds
INTERVAL = 5
ITEM_DISPLAY_TIME = 30  # seconds to keep item on screen

class OverlayWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Make the window frameless and transparent
        self.setWindowFlags(Qt.FramelessWindowHint | 
                            Qt.WindowStaysOnTopHint | 
                            Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set up layout
        layout = QVBoxLayout()
        self.label = QLabel("Monitoring...")
        self.label.setFont(QFont('Arial', 10))
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        # Position in bottom right
        screen = QApplication.primaryScreen().geometry()
        self.move(900,0)
        
        # Timer for clearing display
        self.clear_timer = QTimer(self)
        self.clear_timer.setSingleShot(True)
        self.clear_timer.timeout.connect(self.reset_text)
        
        # Track last update time
        self.last_update_time = None

    def update_text(self, text, color=None, play_sound=True):
        if color:
            self.label.setStyleSheet(f"color: rgb{color}; background-color: rgba(0,0,0,100);")
        self.label.setText(text)
        
        # Optionally play sound
        if play_sound:
            winsound.Beep(100, 50)  # Frequency 1000Hz, duration 100ms
        
        # Record update time and start timer
        self.last_update_time = datetime.now()
        self.clear_timer.start(ITEM_DISPLAY_TIME * 1000)

    def check_and_reset(self):
        # If no recent update, do nothing
        if not self.last_update_time:
            return
        
        # Check if display time has elapsed
        time_since_update = (datetime.now() - self.last_update_time).total_seconds()
        if time_since_update >= ITEM_DISPLAY_TIME:
            self.reset_text()

    def reset_text(self):
        self.label.setText("Monitoring...")
        self.label.setStyleSheet("")
        self.last_update_time = None

class FlipBot:
    def __init__(self, overlay):
        self.overlay = overlay
        self.previous_items = set()

    def check_sales(self):
        # Check if previous item should be cleared
        self.overlay.check_and_reset()

        try:
            # Load data from files
            list_data = load_json(LIST_FILE_PATH)
            items_data = load_json(ITEMS_FILE_PATH)
            traits_data = load_json(TRAITS_FILE_PATH)

            if not list_data or not items_data or not traits_data:
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
            new_items = current_items - self.previous_items
            self.previous_items.update(new_items)

            # Update overlay
            if new_items:
                for item_id, name, rarity, trait_name in matched_items:
                    if item_id in new_items:
                        first_price, second_price = prices[item_id]
                        rarity_color = RARITY_COLORS.get(rarity, (255, 255, 255))
                        display_text = f"{name} | Lowest: {first_price}"
                        
                        # Copy item name to clipboard
                        pyperclip.copy(name)
                        
                        self.overlay.update_text(display_text, rarity_color)
                        print(f"New flagged item: {display_text}")

        except Exception as e:
            # Silent error handling - no sound, just text
            self.overlay.update_text(f"Error: {str(e)}", play_sound=False)
            print(f"Silent error: {e}")

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

def start_monitoring():
    app = QApplication(sys.argv)
    overlay = OverlayWidget()
    overlay.show()

    # Create FlipBot instance
    flipbot = FlipBot(overlay)

    # Set up timer for periodic checks
    timer = QTimer()
    timer.timeout.connect(flipbot.check_sales)
    timer.start(INTERVAL * 1000)  # Convert to milliseconds

    print("Monitoring started. Overlay is active.")
    sys.exit(app.exec_())

if __name__ == "__main__":
    start_monitoring()