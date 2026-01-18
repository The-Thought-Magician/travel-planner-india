# RedBus API Analysis

**Date:** 2026-01-18
**Status:** API IS ACCESSIBLE - No authentication required!

---

## Discovery

The RedBus APIs are **accessible without any authentication**. The curl requests work by properly replicating the browser headers.

---

## API Endpoints

### 1. Autocomplete API (City/Location Search)

**Endpoint:** `https://www.redbus.in/seowapi/search-autocomplete`

**Method:** GET

**Parameters:**
| Parameter | Value | Description |
|-----------|-------|-------------|
| q | (letter) | Search query - city name prefix |
| cc | IND | Country code |
| lang | EN | Language |
| v | timestamp | Version timestamp |

**Response Structure:**
```json
{
  "response": {
    "numFound": 6,
    "docs": [
      {
        "ID": 123,
        "Name": "Chennai",
        "locationName": "Chennai (All Locations)",
        "locationType": "CITY",
        "parentLocation": 14,
        "region": "Tamil Nadu",
        "cc": "IND",
        "rank": 93988
      }
    ]
  }
}
```

**Key City IDs Discovered:**
- Chennai: 123
- NCR (Delhi): 733
- Coimbatore: 141
- Kolkata: 74820
- Vadodara (Central Bus Station): 203892
- Chatrapati Sambhajinagar: 309

### 2. Search Results API (Bus Routes)

**Endpoint:** `https://www.redbus.in/rpw/api/searchResults`

**Method:** POST

**Parameters:**
| Parameter | Example | Description |
|-----------|---------|-------------|
| fromCity | 74676 | Source city ID (Bhubaneswar) |
| toCity | 74820 | Destination city ID (Kolkata) |
| DOJ | 20-Jan-2026 | Date of Journey |
| limit | 10 | Results per page |
| offset | 0 | Pagination offset |
| meta | true | Include metadata |

**Request Body:**
```json
{
  "appliedFilterCount": 0,
  "onlyShow": [],
  "dt": [],
  "SeaterType": [],
  "AcType": [],
  "travelsList": [],
  "amtList": [],
  "bpList": [],
  "dpList": [],
  "CampaignFilter": [],
  "at": [],
  "persuasionList": [],
  "bpIdentifier": [],
  "dpIdentifier": [],
  "bcf": [],
  "opBusTypeFilterList": [],
  "priceRange": [],
  "RouteIds": [],
  "bpKeys": [],
  "dpKeys": [],
  "streaksFilter": [],
  "preRouteFilters": null
}
```

**Response Structure:**
```json
{
  "success": true,
  "data": {
    "metaData": {
      "totalCount": 36,
      "primoCount": 9
    },
    "busLogoBaseUrl": "https://origin-st.redbus.in/buslogos/country/",
    "rdBoostedInv": [
      {
        "operatorId": 34400,
        "travelsName": "OSRTC Buses",
        "routeId": 34081751,
        "busType": "A/C Seater/Sleeper (2+1)",
        "serviceName": "PURI - KOLKATA",
        "departureTime": "2026-01-20 20:50:00",
        "arrivalTime": "2026-01-21 06:00:00",
        "journeyDurationMin": 550,
        "fareList": [780, 840, 1040, 1330],
        "availableSeats": 40,
        "totalSeats": 56,
        "standardBpName": "Palasuni",
        "standardDpName": "Babughat",
        "totalRatings": 4.2,
        "numberOfReviews": "514",
        "amenities": [4, 5, 7, 10, 9, 26, 19],
        "cancellationPolicy": "0:12:100:0;12:24:50:0;24:-1:10:0",
        "isLiveTrackingAvailable": true,
        "isAc": true,
        "isSeater": true,
        "isSleeper": true
      }
    ]
  }
}
```

---

## Data Harvesting Strategy

### Phase 1: Get All City IDs

**Approach:** Iterate through all letters (a-z) and common combinations

```python
import requests
import string

headers = {
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36',
    'referer': 'https://www.redbus.in/bus-tickets'
}

cities = {}

# Try single letters
for letter in string.ascii_lowercase:
    params = {'q': letter, 'cc': 'IND', 'lang': 'EN'}
    response = requests.get('https://www.redbus.in/seowapi/search-autocomplete',
                           params=params, headers=headers)
    data = response.json()
    for doc in data['response']['docs']:
        if doc['locationType'] == 'CITY':
            cities[doc['ID']] = {
                'name': doc['Name'],
                'full_name': doc['locationName'],
                'region': doc['region']
            }

# Try common city name prefixes
common_prefixes = ['ban', 'che', 'mum', 'del', 'kol', 'hyd', 'pun', 'ahm']
for prefix in common_prefixes:
    params = {'q': prefix, 'cc': 'IND', 'lang': 'EN'}
    # ... same pattern

print(f"Found {len(cities)} unique cities")
```

### Phase 2: Get All Routes Between City Pairs

**Caution:** This could be millions of combinations. Need smart strategy:

1. **Start with top 50 cities** (MVP)
2. **Regional clustering** (North India routes first)
3. **Popular routes only** (based on search volume)
4. **Batch with delays** (respectful scraping)

```python
import time
from itertools import combinations

top_cities = list(cities.keys())[:50]
base_url = "https://www.redbus.in/rpw/api/searchResults"

headers = {
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36',
    'origin': 'https://www.redbus.in',
    'referer': 'https://www.redbus.in/bus-tickets',
    'content-type': 'application/json'
}

payload = {
    "appliedFilterCount": 0,
    "onlyShow": [], "dt": [], "SeaterType": [], "AcType": [],
    "travelsList": [], "amtList": [], "bpList": [], "dpList": [],
    # ... rest of empty filters
}

routes = []

for from_city, to_city in combinations(top_cities, 2):
    params = {
        'fromCity': from_city,
        'toCity': to_city,
        'DOJ': '25-Jan-2026',  # Future date
        'limit': 50,
        'offset': 0
    }

    response = requests.get(base_url, params=params, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            # Extract route information
            for bus in data['data'].get('rdBoostedInv', []):
                routes.append({
                    'from_city': from_city,
                    'to_city': to_city,
                    'operator': bus['travelsName'],
                    'departure': bus['departureTime'],
                    'arrival': bus['arrivalTime'],
                    'duration': bus['journeyDurationMin'],
                    'fares': bus['fareList'],
                    'bus_type': bus['busType']
                })

    # Respectful delay - 2-4 seconds between requests
    time.sleep(3)

    # Break after testing
    if len(routes) > 100:
        break

print(f"Collected {len(routes)} routes")
```

---

## Rate Limiting & Safety

**Observations:**
- API doesn't require authentication
- Uses browser fingerprinting (cookies in curl)
- Has rate limiting (observed after multiple requests)

**Safety Measures:**
1. **Add delays:** 2-5 seconds between requests
2. **Rotate user-agents:** Use different browser signatures
3. **Batch processing:** Weekly/monthly, not real-time
4. **Cache everything:** Store results, don't re-fetch

**Recommended Schedule:**
- **Initial harvest:** Spread over 1-2 weeks
- **Updates:** Once per month
- **Popular routes:** Once per week

---

## Feasibility: ⭐ HIGH

**Why this works:**
1. ✅ No API key required
2. ✅ Complete data returned (prices, times, availability)
3. ✅ Can discover all cities via autocomplete
4. ✅ Can query any route pair

**Caveats:**
1. ⚠️ Need to implement rate limiting
2. ⚠️ API may change (no official documentation)
3. ⚠️ Terms of Service may restrict scraping
4. ⚠️ Need to handle changes gracefully

**Recommendation:**
- **Use for MVP** to prove the concept
- **Store all data** in your database
- **Plan fallback** (official partnership, data.gov sources)
- **Be transparent** in your privacy policy

---

## Updated Feasibility Summary

| Data Type | Previous Assessment | New Assessment |
|-----------|---------------------|----------------|
| **Bus Routes** | ❌ Not feasible | ✅ **FEASIBLE** via RedBus API |
| **Bus Prices** | ❌ Not feasible | ✅ **FEASIBLE** - real-time fares returned |
| **Bus Schedules** | ❌ Not feasible | ✅ **FEASIBLE** - complete schedule data |

**This changes the MVP significantly!**

We can now provide:
- ✅ Train + Flight + Bus combinations
- ✅ Real-time pricing for all modes
- ✅ Complete journey planning

---

*Next: Create scripts to harvest this data safely.*
