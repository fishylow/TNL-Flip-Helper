# Throne And Liberty Flip helper

A price monitoring tool for Throne And Liberty's auction house that helps identify potentially underpriced items for market flipping opportunities.

## Features

-  Automatic data refresh from TLDB.info API
-  Real-time price monitoring and analysis
-  Alerts for items priced below 50% of their normal market value
-  Region-specific filtering
-  On screen UI with notification sound

## Prerequisites

- Node.js (for data fetching)
- Python 3.x
- Required Python packages:
  ```
  colorama
  ```
- Required Node.js packages:
  ```
  devalue
  compress-json
  ```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/fishylow/Throne-And-Liberty-Flipbot.git
   cd throne-and-liberty-flipbot
   ```

2. Install Python dependencies:
   ```bash
   pip install colorama
   ```

3. Install Node.js dependencies:
   ```bash
   npm install devalue compress-json
   ```

4. Configure the project path in `check_prices.py`:
   ```python
   PROJECT_FOLDER = r"path/to/project/folder"
   ```

5. Set your desired region in `script.js`:
   ```javascript
   const GROUP = "30001"; // EU Early Access by default
   ```

## Usage

1. Start the data fetcher:
   ```bash
   node script.js
   ```

2. In a separate terminal, start the price monitor:
   ```bash
   python check_prices.py
   ```

The bot will:
- Fetch auction house data every 30 seconds
- Monitor for items priced below 50% of their next lowest listing
- Display alerts with item names, traits, and price comparisons
- Highlight new alerts in red

## Configuration

### Refresh Interval
- In `script.js`: Modify `INTERVAL` (default: 30000ms)
- In `check_prices.py`: Modify `INTERVAL` (default: 30 seconds)

### Region Selection
Modify the `GROUP` constant in `script.js` to match your server region code.

## Disclaimer

This tool is for educational purposes only. Please use responsibly and in accordance with Throne And Liberty's terms of service.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
