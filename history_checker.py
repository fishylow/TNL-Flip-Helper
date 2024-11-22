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

    if response.status_code == 200:
        data = response.json()
        history = data.get("result", {}).get("data", {}).get("history", [])
        #pprint(history)
        
        count_7_days = 0
        prices_7_days = []
        count_3_days = 0
        prices_3_days = []
        count_1_day = 0
        prices_1_day = []

        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        three_days_ago = datetime.now(timezone.utc) - timedelta(days=3)
        one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)

        previous_stock = None
        for record in history:
            if record.get("traitId") == trait_id:
                time_bucket = record.get("timeBucket")
                if time_bucket:
                    record_date = datetime.fromisoformat(time_bucket.replace("Z", "+00:00"))
                    current_stock = record.get("inStock")
                    if previous_stock is not None and current_stock < previous_stock:
                        sold_quantity = previous_stock - current_stock
                        min_price = record.get("minPrice")

                        if record_date >= seven_days_ago:
                            count_7_days += sold_quantity
                            prices_7_days.extend([min_price] * sold_quantity)

                        if record_date >= three_days_ago:
                            count_3_days += sold_quantity
                            prices_3_days.extend([min_price] * sold_quantity)

                        if record_date >= one_day_ago:
                            count_1_day += sold_quantity
                            prices_1_day.extend([min_price] * sold_quantity)

                    previous_stock = current_stock

        result = {}
        if count_1_day > 0:
            median_price_1_day = statistics.median(prices_1_day)
            result["1D"] = {"count": count_1_day, "median": median_price_1_day}
        if count_3_days > 0:
            median_price_3_days = statistics.median(prices_3_days)
            result["3D"] = {"count": count_3_days, "median": median_price_3_days}
        if count_7_days > 0:
            median_price_7_days = statistics.median(prices_7_days)
            result["7D"] = {"count": count_7_days, "median": median_price_7_days}



        if result:
            return result
        else:
            return None
    else:
        print(f"Failed to fetch data. Status code: {response.json()}")
        print(f"Failed to fetch data. Status code: {response.status_code}")

if __name__ == "__main__":
    item_id = "sword_aa_t3_plant_004"
    trait_id = 1670377858
    result = fetch_and_analyze_auction_data(item_id, trait_id)
    if result:
        pprint(result)
    else:
        print("No items sold in the specified timeframes.")
