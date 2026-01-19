# ixigo Flight API Analysis

**Date:** 2026-01-18
**Status:** ✅ API ACCESSIBLE - Simple Authentication!

---

## Discovery

The ixigo flight outlook API is **accessible without complex authentication**.

---

## API Endpoint

### Flight Price Range API

**Endpoint:** `https://www.ixigo.com/outlook/v1/onward/ranged`

**Method:** GET

**Authentication:**
- `apikey: ixiweb$2$` (simple pattern, no signup needed!)
- `clientid: ixiweb`
- `deviceid: any random string`
- `uuid: any random string`

**Parameters:**
| Parameter | Example | Description |
|-----------|---------|-------------|
| origin | JAI | Origin airport IATA code |
| destination | IDR | Destination airport IATA code |
| departureDate | 20012026 | Departure date (DDMMYYYY) |
| fareClass | e | Economy (e) or Business (b) |
| paxCombinationType | 100 | Passenger combination (100 = 1 adult) |
| refundTypes | REFUNDABLE,NON_REFUNDABLE,PARTIALLY_REFUNDABLE | Filter by refund type |

**Response Structure:**
```json
{
  "data": {
    "going": {
      "origin": "JAI",
      "destination": "IDR",
      "startDate": "05-01-2026",
      "endDate": "04-02-2026",
      "results": [
        {
          "airline": "IndiGo",
          "airlineCode": "6E",
          "flightNumber": "6E7148",
          "date": "19-01-2026",
          "fare": 6120.0,
          "providerId": "1058",
          "searchId": "18012026231613000$1058"
        }
      ],
      "ranges": {
        "R": [6493, 8850],
        "G": [0, 4939],
        "Y": [4940, 6492]
      }
    },
    "showOutlook": true
  }
}
```

**What you get:**
- ✅ Flight prices across a 30-day date range
- ✅ Airline name and code
- ✅ Flight numbers
- ✅ Price range categories (R=Peak, Y=Medium, G=Low)
- ✅ Multiple airlines per route

---

## Key Advantages vs AviationStack

| Feature | ixigo | AviationStack |
|---------|-------|---------------|
| **Auth Required** | Simple pattern ($2$) | API Key signup |
| **Free Tier** | No limit visible | 100 req/month |
| **Price Data** | ✅ Yes | ⚠️ Limited |
| **Date Range** | 30 days in one call | Per date |
| **Rate Limiting** | None observed | Strict |

**Verdict:** ixigo is **better** for price discovery and MVP!

---

## Indian Airport IATA Codes

### Major Airports

| Code | City | Airport Name |
|------|------|--------------|
| DEL | Delhi | Indira Gandhi International |
| BOM | Mumbai | Chhatrapati Shivaji Maharaj |
| BLR | Bangalore | Kempegowda International |
| MAA | Chennai | Chennai International |
| CCU | Kolkata | Netaji Subhash Chandra Bose |
| HYD | Hyderabad | Rajiv Gandhi International |
| COK | Kochi | Cochin International |

### Other Important Airports

| Code | City | Code | City |
|------|------|------|------|
| JAI | Jaipur | JLR | Jabalpur |
| AMD | Ahmedabad | GAY | Gaya |
| PNQ | Pune | PAT | Patna |
| GOI | Goa | IXR | Ranchi |
| CJB | Coimbatore | VNS | Varanasi |
| TRV | Thiruvananthapuram | IXU | Aurangabad |
| GAU | Guwahati | NAG | Nagpur |
| LKO | Lucknow | VTZ | Visakhapatnam |
| DED | Dehradun | BBI | Bhubaneswar |
| SXR | Srinagar | JDH | Jodhpur |
| IXB | Bagdogra | UDR | Udaipur |
| IDR | Indore | JGA | Jamnagar |

---

## Harvesting Strategy

```python
import requests
from datetime import datetime, timedelta

def get_flight_prices(origin: str, destination: str):
    """Get flight prices for a route over next 30 days."""

    # Get date 7 days from now
    journey_date = (datetime.now() + timedelta(days=7)).strftime("%d%m%Y")

    url = "https://www.ixigo.com/outlook/v1/onward/ranged"

    params = {
        "origin": origin,
        "destination": destination,
        "departureDate": journey_date,
        "fareClass": "e",
        "paxCombinationType": "100",
        "refundTypes": "REFUNDABLE,NON_REFUNDABLE,PARTIALLY_REFUNDABLE"
    }

    headers = {
        "accept": "*/*",
        "apikey": "ixiweb$2$",
        "appversion": "2",
        "clientid": "ixiweb",
        "content-type": "application/json; charset=UTF-8",
        "deviceid": "travel-planner-device",
        "ixisrc": "ixiweb",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36",
        "uuid": "travel-planner-uuid"
    }

    response = requests.get(url, params=params, headers=headers)
    return response.json()


# Example usage
data = get_flight_prices("DEL", "BOM")

for flight in data["data"]["going"]["results"]:
    print(f"{flight['airline']} {flight['flightNumber']}: "
          f"₹{flight['fare']} on {flight['date']}")
```

---

## Usage for Travel Planner

1. **Price Discovery:** Get fare ranges for any route
2. **Date Flexibility:** Show prices across 30 days
3. **Airline Options:** All carriers on the route
4. **Budget Planning:** Price range categories (G/Y/R)

**Integration Strategy:**
- Use ixigo for price trends and discovery
- Use AviationStack (if needed) for detailed flight info
- Store price data for historical analysis

---

## Feasibility: ⭐ EXCELLENT

**Why this is great:**
1. ✅ No API signup required
2. ✅ Returns 30 days of prices in ONE call
3. ✅ Shows multiple airlines
4. ✅ No rate limiting observed
5. ✅ Simple IATA code based

**This is actually BETTER than AviationStack for price discovery!**

---

*Note: Use respectfully. Don't flood the API. Implement delays between requests.*
