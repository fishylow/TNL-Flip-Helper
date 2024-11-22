
import sys
import pyperclip
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from colorama import init, Fore, Style
import winsound
from normalize_file import merge_data
from history_checker import fetch_and_analyze_auction_data


# Initialize colorama for color support
init(autoreset=True)

# Define project folder

RARITY_COLORS = {
    2: (255, 255, 255),  # White
    3: (50, 255, 50),      # Green
    4: (0, 100, 255),      # Blue
    5: (255, 50, 255),    # Magenta
}

RARITY_COLORS_COLORAMA = {
    2: Fore.WHITE,  # White
    3: Fore.GREEN,  # Green
    4: Fore.BLUE,   # Blue
    5: Fore.MAGENTA # Magenta
}

# Define the interval in seconds
INTERVAL = 5
ITEM_DISPLAY_TIME = 30  # seconds to keep item on screen
global ITER_COUNT

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
        self.label.setFont(QFont('Arial', 14))
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        # Position in bottom right
        screen = QApplication.primaryScreen().geometry()
        self.move(700,0)
        
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
            winsound.Beep(400, 50)  # Frequency 400Hz, duration 50ms
        
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
        self.ITER_COUNT = 0

    def check_sales(self):
        self.overlay.check_and_reset()

        try:
            # Load merged data using normalize_file's merge_data function
            merged_data = merge_data()

            if not merged_data:
                return

            # Filter sales data for flagged items
            flagged_items = []
            for item in merged_data:
                sales = item.get("prices_list", [])
                # Ensure there are at least two sales entries to compare
                if len(sales) >= 2:
                    current_price = sales[0]
                    last_price = sales[1]
                    if current_price < 0.6 * last_price:
                        flagged_items.append(item)

            # Display flagged items
            for item in flagged_items:
                potential_profit = int((item['prices_list'][1] * 0.80) - item['prices_list'][0])
                if item['parent_num'] in self.previous_items or potential_profit <= 9:
                    continue
                
                
                rarity_color = RARITY_COLORS.get(item['parent_rarity'], (255, 255, 255))
                rarity_color_colorama = RARITY_COLORS_COLORAMA.get(item["parent_rarity"], Fore.WHITE)
                item_name_colored = f"{rarity_color_colorama}{item['parent_combined_name']}{Style.RESET_ALL}"
                if self.ITER_COUNT > 0:
                    if item['is_traited']:
                        history_data = fetch_and_analyze_auction_data(item['questlog_id'],item['trait_id'])
                        #print(f"Fetching traited: {item['parent_id']} | {item['trait_id']} | {item['parent_combined_name']}")
                    else:
                        history_data = fetch_and_analyze_auction_data(item['questlog_id'])                
                        #print(f"Fetching traited: {item['parent_id']} {item['parent_combined_name']}")
                display_text = f"({potential_profit}) {item['parent_combined_name']} | Current: {item['prices_list'][0]} | Last: {item['prices_list'][1]} Count: {item['quantity']}"
                display_text_colorama = f"({potential_profit}) {item_name_colored} | Current: {item['prices_list'][0]} | Last: {item['prices_list'][1]} Count: {item['quantity']}"
                
                if self.ITER_COUNT > 0 and history_data:
                    if history_data['count']: display_text += f" | 3DS: {history_data['count']}"
                    if history_data['median']: display_text += f" | 3DM: {history_data['median']}"
                                
                # Copy item name to clipboard
                pyperclip.copy(item['parent_name'])
                self.overlay.update_text(display_text, rarity_color)
                self.previous_items.add(item['parent_num'])
                print(f"{display_text_colorama}")

        except Exception as e:
            # Silent error handling - no sound, just text
            #self.overlay.update_text(f"Error: {str(e)}", play_sound=True)
            #pprint(item)
            #print(f"Silent error: {e}")
            #raise e
            pass
        self.ITER_COUNT += 1
        

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
