import json
import requests
from datetime import datetime, timedelta, timezone
import statistics
from pprint import pprint

def fetch_and_analyze_auction_data(item_id, trait_id=None):
    url = "https://questlog.gg/throne-and-liberty/api/trpc/actionHouse.getAuctionItem"
    item_id = item_id
    if trait_id:
        params = {
            "input": json.dumps({
                "language": "en",
                "regionId": "eu-e",
                "itemId": item_id,
                "traitId": trait_id,
                "timespan": 360
            })
        }
    else:
        params = {
            "input": json.dumps({
                "language": "en",
                "regionId": "eu-e",
                "itemId": item_id,
                "timespan": 360
            })
        }
    response = requests.get(url, params=params)
    #pprint(response.json())
    #pprint(item_id)

    if response.status_code == 200:
        data = response.json()
        history = data.get("result", {}).get("data", {}).get("history", [])
        count = 0
        prices = []
        three_days_ago = datetime.now(timezone.utc) - timedelta(days=3)

        previous_stock = None
        for record in history:
            if record.get("traitId") == trait_id:
                time_bucket = record.get("timeBucket")
                if time_bucket:
                    record_date = datetime.fromisoformat(time_bucket.replace("Z", "+00:00"))
                    if record_date >= three_days_ago:
                        current_stock = record.get("inStock")
                        if previous_stock is not None and current_stock < previous_stock:
                            sold_quantity = previous_stock - current_stock
                            count += sold_quantity
                            prices.extend([record.get("minPrice")] * sold_quantity)
                        previous_stock = current_stock

        if count > 0:
            median_price = statistics.median(prices)
            #print(f"{item_id} Sold {count} with median {median_price}")
            return {"count":count, "median":median_price}
        else:
            #print("No items sold in the past 3 days.")
            return None
    else:
        print(f"Failed to fetch data. Status code: {response.json()}")
        print(f"Failed to fetch data. Status code: {response.status_code}")

if __name__ == "__main__":
    item_id = "bracelet_aa_t1_nomal_001"
    trait_id = 1670377921
    fetch_and_analyze_auction_data(item_id, trait_id)
