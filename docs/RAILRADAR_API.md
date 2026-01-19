# RailRadar API Integration

**Status:** ✅ CONFIRMED - Official API with generous free tier

---

## Overview

[RailRadar](https://railradar.in) is India's most comprehensive live train tracking platform:
- **13,334 trains tracked**
- **10,102 stations**
- **966K+ train schedules**
- **351K+ route crossings**

Created by: [@vishalkaleria](https://twitter.com/vishalkaleria)
Reddit: [Free Indian Railways data API](https://www.reddit.com/r/developersIndia/comments/1nbpbx1/)

---

## API Access

### Sign Up
1. Go to: https://railradar.in/signup
2. Create free account
3. Get API key from dashboard
4. **Each account gets its own API key**

### Free Tier
- **Generous rate limit** (~60 requests/minute per key)
- Perfect for hobbyist projects
- No credit card required

### With Multiple API Keys
If you have access to multiple API keys:
```
Rate Limit = Number of Keys × 60 requests/minute

Example with 100 keys:
100 × 60 = 6,000 requests/minute = 360,000 requests/hour
```

**This is enough for:**
- Daily polling of all 13,334 trains
- Real-time status for top trains
- Complete route discovery

---

## API Endpoints

| Endpoint | Description | Example |
|----------|-------------|---------|
| `/api/v1/live/{train_number}` | Live train status | `/api/v1/live/12301` |
| `/api/v1/train/{train_number}` | Train schedule | `/api/v1/train/12301` |
| `/api/v1/trains/{from}/{to}` | Trains between stations | `/api/v1/trains/NDLS/HWH` |
| `/api/v1/station/{code}` | Station info | `/api/v1/station/NDLS` |
| `/api/v1/trains` | All trains list | `/api/v1/trains` |
| `/api/v1/stations` | All stations list | `/api/v1/stations` |

### Authentication
```python
headers = {
    'X-API-Key': 'your_api_key_here',
    'Accept': 'application/json'
}
```

---

## Example Usage

### Live Train Status
```bash
curl 'https://railradar.in/api/v1/live/12301' \
  -H 'X-API-Key: your_api_key'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "train_number": "12301",
    "train_name": "RAJDHANI EXP",
    "current_position": {
      "lat": 23.4567,
      "lon": 77.8912,
      "station": "BPL",
      "delay_minutes": 15
    },
    "route": [...]
  }
}
```

### Trains Between Stations
```bash
curl 'https://railradar.in/api/v1/trains/NDLS/HWH' \
  -H 'X-API-Key: your_api_key'
```

---

## Multi-Key Harvester

Use the provided harvester script to leverage multiple API keys:

### Setup
```bash
# Create a file with your API keys (one per line)
echo "key1" > railradar_keys.txt
echo "key2" >> railradar_keys.txt
echo "key3" >> railradar_keys.txt
# ... add as many as you have
```

### Usage
```bash
# Discover all trains
python3 scripts/railradar_harvester.py --discover-trains --keys railradar_keys.txt

# Get live status for top trains (parallel)
python3 scripts/railradar_harvester.py --live-status --top-trains 100 --keys railradar_keys.txt

# Get live status for specific trains
python3 scripts/railradar_harvester.py --live-status --train-numbers 12301,12951,12953 --keys railradar_keys.txt

# Trains between two stations
python3 scripts/railradar_harvester.py --trains-between --from NDLS --to HWH --keys railradar_keys.txt
```

### Features
- ✅ **Automatic key rotation** - Distributes load across all keys
- ✅ **Rate limit handling** - Waits when keys are rate limited
- ✅ **Parallel requests** - Uses ThreadPoolExecutor
- ✅ **Statistics tracking** - Per-key usage monitoring
- ✅ **Error handling** - Retries with fallback keys

---

## Data Collection Strategy with Multiple Keys

### Daily Full Poll (13,334 trains)
```
13,334 trains ÷ (100 keys × 60 req/min) = ~2.2 minutes
```

With 100 API keys, you can poll **every train** in ~2 minutes!

### Hourly Top Trains
```
Top 500 trains ÷ (100 keys) = 5 seconds
```

### Real-Time Monitoring
For critical routes, poll every 5-10 minutes:
```
100 trains × 12 times/hour = 1,200 req/hour ≈ 20 req/min per key (with 100 keys)
```

---

## Integration with Travel Planner

### 1. Initial Setup (One-time)
```bash
# Discover all stations
python3 scripts/railradar_harvester.py --discover-stations --keys railradar_keys.txt

# Discover all trains
python3 scripts/railradar_harvester.py --discover-trains --keys railradar_keys.txt
```

### 2. Daily Delay Collection (Build Historical Data)
```bash
# Poll all trains daily
python3 scripts/railradar_harvester.py --live-status --top-trains 13334 --keys railradar_keys.txt
```

### 3. Real-Time API Endpoint
```python
# In your FastAPI app
from railradar_harvester import RailRadarHarvester

harvester = RailRadarHarvester(api_keys=YOUR_KEYS)

@app.get("/api/v1/train/{train_number}/live")
async def get_live_status(train_number: str):
    status = harvester.get_live_status(train_number)
    return status
```

---

## Building Your Own Delay Database

RailRadar gives you live data. **Collect it over time** to build:

### Delay History Table
| train_number | date | scheduled_arrival | actual_arrival | delay_minutes |
|--------------|------|-------------------|----------------|---------------|
| 12301 | 2026-01-18 | 18:30 | 18:47 | 17 |
| 12301 | 2026-01-17 | 18:30 | 18:35 | 5 |
| 12301 | 2026-01-16 | 18:30 | 18:25 | -5 |

### Reliability Metrics
```sql
SELECT
    train_number,
    AVG(delay_minutes) as avg_delay,
    COUNT(*) as total_observations,
    SUM(CASE WHEN delay_minutes > 30 THEN 1 ELSE 0 END) as delayed_over_30m,
    SUM(CASE WHEN delay_minutes < 0 THEN 1 ELSE 0 END) as early_arrivals
FROM delay_history
WHERE date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY train_number;
```

This becomes your **competitive advantage** - no one else has this data!

---

## Comparison: RailRadar vs Alternatives

| Feature | RailRadar | indianrailapi | NTES (official) |
|---------|-----------|---------------|-----------------|
| **API Access** | ✅ Free signup | ❌ Paid only | ❌ No public API |
| **Rate Limit** | ~60/min/key | Varies | N/A |
| **Live Status** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Historical** | ❓ Collect yourself | ❌ No | ❌ No |
| **Multi-key** | ✅ Supported | ❓ Unknown | N/A |

**Verdict:** RailRadar is the **best option** for live train data!

---

## Cost Estimate

### With Free API Keys
- **Cost:** ₹0 (free tier)
- **Capacity:** 6,000 req/min with 100 keys
- **Sufficient for:** All 13,334 trains polled every 2-3 minutes

### If Need More
Contact RailRadar for enterprise access - pricing not publicly listed but likely reasonable for Indian market.

---

## Notes

1. **Respect rate limits** - Don't exceed 60 req/min per key
2. **Cache responses** - Store data locally
3. **Share attribution** - Credit RailRadar where appropriate
4. **Provide feedback** - Help improve the API

---

*For the harvester script, see: `scripts/railradar_harvester.py`*
*For API documentation, see: https://railradar.in/docs*
