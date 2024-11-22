import requests
import json

def fetch_data():
    url = "https://questlog.gg/throne-and-liberty/api/trpc/actionHouse.getAuctionHouse?input=%7B%22language%22%3A%22en%22%2C%22regionId%22%3A%22eu-e%22%7D"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Assuming the actual data is within the 'data' key
    else:
        raise Exception(f"Failed to fetch data. Status code: {response.status_code}")

def extract_data(data):
    result = {}
    if isinstance(data, list):
        for item in data:  # Assuming the data is a list of items
            if isinstance(item, dict):
                name = item.get('name')
                item_id = item.get('id')
                if name and item_id:
                    result[name] = item_id
    return result

def export_to_json(data, filename="questlog_db.json"):
    if data:
        with open(filename, "w") as json_file:
            json.dump(data, json_file, indent=4)
    else:
        print("No data to export.")

def main():
    try:
        data = fetch_data()
        extracted_data = extract_data(data["result"]["data"])
        export_to_json(extracted_data)
        print(f"Data successfully exported to questlog_db.json")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()