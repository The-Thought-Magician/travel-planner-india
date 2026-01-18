#!/usr/bin/env python3
"""
Test bus data sources for India.

Major challenge: No free public API exists.
Options:
1. Check government state transport portals
2. Test RedBus/AbhiBus scraping (carefully)
3. Check if any state RTC has open data
"""

import requests
import json
import time
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()


def test_gov_bus_data():
    """Test government bus data sources."""

    print("=" * 60)
    print("Testing Bus Data Sources")
    print("=" * 60)

    # State transport portals that might have data
    sources = [
        {
            "name": "APSRTC (Andhra)",
            "url": "https://www.apsrtc.ap.gov.in/",
            "has_api": False
        },
        {
            "name": "KSRTC (Kerala)",
            "url": "https://online.keralartc.com/",
            "has_api": False
        },
        {
            "name": "TNSTC (Tamil Nadu)",
            "url": "https://www.tnstc.in/",
            "has_api": False
        },
        {
            "name": "GSRTC (Gujarat)",
            "url": "https://gsrtc.in/site/",
            "has_api": False
        },
        {
            "name": "MSRTC (Maharashtra)",
            "url": "https://msrtc.maharashtra.gov.in/",
            "has_api": False
        },
        {
            "name": "RSRTC (Rajasthan)",
            "url": "https://rsrtc.rajasthan.gov.in/",
            "has_api": False
        },
        {
            "name": "OSRTC (Odisha)",
            "url": "https://www.osrtc.com/",
            "has_api": False
        },
        {
            "name": "HRTC (Himachal)",
            "url": "https://hrtchp.com/",
            "has_api": False
        },
    ]

    print(f"\n🔍 Test 1: Checking state transport portals")
    print("-" * 60)

    accessible = []
    for source in sources:
        try:
            response = requests.get(source["url"], timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (compatible; TravelPlanner-Bot/1.0)"
            })
            if response.status_code == 200:
                print(f"✅ {source['name']}: Accessible")
                accessible.append(source["name"])

                # Check if there's any API link mentioned
                if "api" in response.text.lower():
                    print(f"   🔍 Possible API mentioned in page")
        except Exception as e:
            print(f"❌ {source['name']}: Failed")

    print(f"\n✅ Accessible portals: {len(accessible)}/{len(sources)}")

    return accessible


def test_redbus_scraping():
    """
    Test if RedBus can be scraped for route information.
    NOTE: This is for research only. Heavy scraping may violate ToS.
    """

    print(f"\n🚌 Test 2: RedBus accessibility check (research only)")
    print("-" * 60)

    # Sample route search
    url = "https://www.redbus.in/search?fromCityId=122&toCityId=380&onward=2026-01-20"

    try:
        response = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html')

            # Check for common indicators
            if "bus" in response.text.lower() and "route" in response.text.lower():
                print(f"⚠️  RedBus returns data for route queries")
                print(f"   ⚠️  Scraping possible but may violate ToS")
                print(f"   ⚠️  Official API partnership recommended")

            # Check for rate limiting
            if "captcha" in response.text.lower() or "blocked" in response.text.lower():
                print(f"❌ RedBus has anti-scraping measures")

        return True

    except Exception as e:
        print(f"❌ RedBus check failed: {str(e)[:50]}")
        return False


def test_abhibus_scraping():
    """Test if AbhiBus can be accessed."""

    print(f"\n🚌 Test 3: AbhiBus accessibility check")
    print("-" * 60)

    url = "https://www.abhibus.com/"

    try:
        response = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

        if response.status_code == 200:
            print(f"✅ AbhiBus is accessible")
            print(f"   ⚠️  No public API available")
            print(f"   ⚠️  Partnership required for official access")

        return True

    except Exception as e:
        print(f"❌ AbhiBus check failed: {str(e)[:50]}")
        return False


def check_data_gov_buses():
    """Check data.gov.in for bus datasets."""

    print(f"\n📊 Test 4: data.gov.in bus datasets")
    print("-" * 60)

    # Known bus datasets on data.gov.in
    datasets = [
        ("https://data.gov.in/catalog/bus-routes-thane", "Thane Bus Routes"),
    ]

    found = []
    for url, name in datasets:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: Available")
                found.append(name)
            else:
                print(f"❌ {name}: Error {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Failed")

    if found:
        print(f"\n✅ Found {len(found)} government bus datasets")
        print(f"   ⚠️  Limited to specific cities")
        print(f"   ⚠️  May not be updated regularly")

    return found


def main():
    """Run all bus data tests."""

    accessible_portals = test_gov_bus_data()
    test_redbus_scraping()
    test_abhibus_scraping()
    gov_datasets = check_data_gov_buses()

    print("\n" + "=" * 60)
    print("✅ Bus data testing completed")
    print("=" * 60)

    print("\n📝 Summary - Bus Data Feasibility:")
    print("  " + "-" * 56)
    print("  ❌ No free public API exists (RedBus, AbhiBus)")
    print("  ⚠️  State RTC portals: Accessible but no unified API")
    print("  ⚠️  Scraping: Possible but legal/technical risks")
    print("  ⚠️  Government data: Limited, city-specific")
    print()
    print("  💡 RECOMMENDATION:")
    print("     1. Start with trains + flights only (MVP)")
    print("     2. Approach state RTCs for API partnership")
    print("     3. Consider crowdsourced bus stop data")
    print("     4. Bus routes can be added in Phase 2")


if __name__ == "__main__":
    main()
