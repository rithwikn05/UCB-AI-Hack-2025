#!/usr/bin/env python3
"""
EXPANDED 30-CITY GLOBAL DISASTER DETECTION TEST SCRIPT
Tests 30 diverse cities worldwide to comprehensively validate natural disaster detection accuracy
Provides fresh perspective on system intelligence and geographic coverage
"""

import requests
import json
import time
from typing import List, Dict, Tuple
import random

# =============================================================================
# EXPANDED 30-CITY GLOBAL TEST DATABASE
# =============================================================================

EXPANDED_GLOBAL_TEST_CITIES = [
    # NORTH AMERICA - Diverse Regions
    {
        "name": "Vancouver, Canada",
        "latitude": 49.2827, "longitude": -123.1207,
        "country": "Canada",
        "expected_disasters": ["earthquake", "landslide", "flood"],
        "primary_risk": "seismic",
        "climate": "temperate_oceanic",
        "terrain": "coastal_mountains"
    },
    {
        "name": "Mexico City, Mexico",
        "latitude": 19.4326, "longitude": -99.1332,
        "country": "Mexico",
        "expected_disasters": ["earthquake", "volcano", "air_pollution"],
        "primary_risk": "seismic",
        "climate": "subtropical_highland",
        "terrain": "mountain_basin"
    },
    {
        "name": "Denver, Colorado",
        "latitude": 39.7392, "longitude": -104.9903,
        "country": "USA",
        "expected_disasters": ["tornado", "blizzard", "hail"],
        "primary_risk": "severe_weather",
        "climate": "continental",
        "terrain": "high_plains"
    },
    {
        "name": "Honolulu, Hawaii",
        "latitude": 21.3099, "longitude": -157.8581,
        "country": "USA",
        "expected_disasters": ["hurricane", "tsunami", "volcano"],
        "primary_risk": "volcanic",
        "climate": "tropical",
        "terrain": "volcanic_island"
    },
    {
        "name": "Charleston, South Carolina",
        "latitude": 32.7767, "longitude": -79.9311,
        "country": "USA",
        "expected_disasters": ["hurricane", "earthquake", "flood"],
        "primary_risk": "hurricane",
        "climate": "humid_subtropical",
        "terrain": "coastal_lowland"
    },
    
    # SOUTH AMERICA - Diverse Geography
    {
        "name": "Santiago, Chile",
        "latitude": -33.4489, "longitude": -70.6693,
        "country": "Chile",
        "expected_disasters": ["earthquake", "landslide", "drought"],
        "primary_risk": "seismic",
        "climate": "mediterranean",
        "terrain": "mountain_valley"
    },
    {
        "name": "Bogotá, Colombia",
        "latitude": 4.7110, "longitude": -74.0721,
        "country": "Colombia",
        "expected_disasters": ["earthquake", "landslide", "flood"],
        "primary_risk": "seismic",
        "climate": "tropical_highland",
        "terrain": "mountain_plateau"
    },
    {
        "name": "Manaus, Brazil",
        "latitude": -3.1190, "longitude": -60.0217,
        "country": "Brazil",
        "expected_disasters": ["flood", "drought", "wildfire"],
        "primary_risk": "flooding",
        "climate": "tropical_rainforest",
        "terrain": "amazon_basin"
    },
    {
        "name": "Buenos Aires, Argentina",
        "latitude": -34.6118, "longitude": -58.3960,
        "country": "Argentina",
        "expected_disasters": ["flood", "storm", "drought"],
        "primary_risk": "flooding",
        "climate": "humid_subtropical",
        "terrain": "river_delta"
    },
    
    # EUROPE - Varied Climate Zones
    {
        "name": "Reykjavik, Iceland",
        "latitude": 64.1466, "longitude": -21.9426,
        "country": "Iceland",
        "expected_disasters": ["volcano", "earthquake", "blizzard"],
        "primary_risk": "volcanic",
        "climate": "subarctic",
        "terrain": "volcanic_island"
    },
    {
        "name": "Lisbon, Portugal",
        "latitude": 38.7223, "longitude": -9.1393,
        "country": "Portugal",
        "expected_disasters": ["earthquake", "wildfire", "tsunami"],
        "primary_risk": "seismic",
        "climate": "mediterranean",
        "terrain": "coastal_hills"
    },
    {
        "name": "Amsterdam, Netherlands",
        "latitude": 52.3676, "longitude": 4.9041,
        "country": "Netherlands",
        "expected_disasters": ["flood", "storm", "sea_level_rise"],
        "primary_risk": "flooding",
        "climate": "temperate_oceanic",
        "terrain": "river_delta"
    },
    {
        "name": "Athens, Greece",
        "latitude": 37.9838, "longitude": 23.7275,
        "country": "Greece",
        "expected_disasters": ["earthquake", "wildfire", "drought"],
        "primary_risk": "seismic",
        "climate": "mediterranean",
        "terrain": "coastal_mountains"
    },
    {
        "name": "Stockholm, Sweden",
        "latitude": 59.3293, "longitude": 18.0686,
        "country": "Sweden",
        "expected_disasters": ["blizzard", "flood", "storm"],
        "primary_risk": "cold_weather",
        "climate": "continental",
        "terrain": "archipelago"
    },
    
    # AFRICA - Continental Diversity
    {
        "name": "Lagos, Nigeria",
        "latitude": 6.5244, "longitude": 3.3792,
        "country": "Nigeria",
        "expected_disasters": ["flood", "coastal_erosion", "storm"],
        "primary_risk": "flooding",
        "climate": "tropical_savanna",
        "terrain": "coastal_lagoon"
    },
    {
        "name": "Cairo, Egypt",
        "latitude": 30.0444, "longitude": 31.2357,
        "country": "Egypt",
        "expected_disasters": ["drought", "dust_storm", "flash_flood"],
        "primary_risk": "drought",
        "climate": "hot_desert",
        "terrain": "river_valley"
    },
    {
        "name": "Nairobi, Kenya",
        "latitude": -1.2921, "longitude": 36.8219,
        "country": "Kenya",
        "expected_disasters": ["drought", "flood", "landslide"],
        "primary_risk": "drought",
        "climate": "tropical_highland",
        "terrain": "highland_plateau"
    },
    {
        "name": "Casablanca, Morocco",
        "latitude": 33.5731, "longitude": -7.5898,
        "country": "Morocco",
        "expected_disasters": ["earthquake", "drought", "flood"],
        "primary_risk": "seismic",
        "climate": "mediterranean",
        "terrain": "coastal_plain"
    },
    
    # ASIA - Monsoon & Seismic Zones
    {
        "name": "Seoul, South Korea",
        "latitude": 37.5665, "longitude": 126.9780,
        "country": "South Korea",
        "expected_disasters": ["earthquake", "typhoon", "flood"],
        "primary_risk": "seismic",
        "climate": "continental",
        "terrain": "mountainous"
    },
    {
        "name": "Jakarta, Indonesia",
        "latitude": -6.2088, "longitude": 106.8456,
        "country": "Indonesia",
        "expected_disasters": ["earthquake", "tsunami", "volcano"],
        "primary_risk": "seismic",
        "climate": "tropical_monsoon",
        "terrain": "coastal_delta"
    },
    {
        "name": "Bangkok, Thailand",
        "latitude": 13.7563, "longitude": 100.5018,
        "country": "Thailand",
        "expected_disasters": ["flood", "drought", "typhoon"],
        "primary_risk": "flooding",
        "climate": "tropical_monsoon",
        "terrain": "river_delta"
    },
    {
        "name": "Kathmandu, Nepal",
        "latitude": 27.7172, "longitude": 85.3240,
        "country": "Nepal",
        "expected_disasters": ["earthquake", "landslide", "flood"],
        "primary_risk": "seismic",
        "climate": "subtropical_highland",
        "terrain": "mountain_valley"
    },
    {
        "name": "Karachi, Pakistan",
        "latitude": 24.8607, "longitude": 67.0011,
        "country": "Pakistan",
        "expected_disasters": ["cyclone", "heat_wave", "flood"],
        "primary_risk": "extreme_heat",
        "climate": "hot_desert",
        "terrain": "coastal_desert"
    },
    {
        "name": "Ho Chi Minh City, Vietnam",
        "latitude": 10.8231, "longitude": 106.6297,
        "country": "Vietnam",
        "expected_disasters": ["typhoon", "flood", "drought"],
        "primary_risk": "typhoon",
        "climate": "tropical_monsoon",
        "terrain": "mekong_delta"
    },
    
    # OCEANIA & PACIFIC
    {
        "name": "Auckland, New Zealand",
        "latitude": -36.8485, "longitude": 174.7633,
        "country": "New Zealand",
        "expected_disasters": ["earthquake", "volcano", "cyclone"],
        "primary_risk": "seismic",
        "climate": "temperate_oceanic",
        "terrain": "volcanic_peninsula"
    },
    {
        "name": "Sydney, Australia",
        "latitude": -33.8688, "longitude": 151.2093,
        "country": "Australia",
        "expected_disasters": ["wildfire", "drought", "cyclone"],
        "primary_risk": "wildfire",
        "climate": "humid_subtropical",
        "terrain": "coastal_basin"
    },
    {
        "name": "Suva, Fiji",
        "latitude": -18.1248, "longitude": 178.4501,
        "country": "Fiji",
        "expected_disasters": ["cyclone", "tsunami", "flood"],
        "primary_risk": "cyclone",
        "climate": "tropical",
        "terrain": "volcanic_island"
    },
    
    # MIDDLE EAST
    {
        "name": "Tehran, Iran",
        "latitude": 35.6892, "longitude": 51.3890,
        "country": "Iran",
        "expected_disasters": ["earthquake", "drought", "dust_storm"],
        "primary_risk": "seismic",
        "climate": "semi_arid",
        "terrain": "mountain_basin"
    },
    {
        "name": "Tel Aviv, Israel",
        "latitude": 32.0853, "longitude": 34.7818,
        "country": "Israel",
        "expected_disasters": ["earthquake", "drought", "flash_flood"],
        "primary_risk": "seismic",
        "climate": "mediterranean",
        "terrain": "coastal_plain"
    },
    
    # ARCTIC & EXTREME
    {
        "name": "Murmansk, Russia",
        "latitude": 68.9585, "longitude": 33.0827,
        "country": "Russia",
        "expected_disasters": ["blizzard", "ice_storm", "polar_night"],
        "primary_risk": "extreme_cold",
        "climate": "subarctic",
        "terrain": "arctic_coast"
    }
]

# =============================================================================
# ENHANCED ACCURACY SCORING SYSTEM
# =============================================================================

def score_disaster_accuracy_enhanced(city: Dict, generated_buttons: List[str]) -> Dict:
    """Enhanced accuracy scoring with detailed analysis"""
    
    expected_disasters = city["expected_disasters"]
    primary_risk = city["primary_risk"]
    
    # Convert buttons to lowercase for matching
    button_text = " ".join(generated_buttons).lower()
    
    # Enhanced scoring
    detected_disasters = []
    missed_disasters = []
    false_positives = []
    accuracy_score = 0
    
    # Check each expected disaster
    for disaster in expected_disasters:
        disaster_keywords = get_disaster_keywords_enhanced(disaster)
        
        # Check if any keyword is found in buttons
        found = any(keyword in button_text for keyword in disaster_keywords)
        
        if found:
            detected_disasters.append(disaster)
            # Primary risk gets double points
            accuracy_score += 3 if disaster == primary_risk else 1
        else:
            missed_disasters.append(disaster)
    
    # Check for unexpected disasters (false positives)
    all_disaster_types = [
        "earthquake", "volcano", "hurricane", "typhoon", "cyclone", "tornado", 
        "wildfire", "flood", "drought", "tsunami", "landslide", "blizzard",
        "heatwave", "ice_storm", "dust_storm"
    ]
    
    for disaster_type in all_disaster_types:
        if disaster_type not in expected_disasters:
            keywords = get_disaster_keywords_enhanced(disaster_type)
            if any(keyword in button_text for keyword in keywords):
                false_positives.append(disaster_type)
    
    # Calculate enhanced accuracy
    total_possible = len(expected_disasters) * 2  # Allow for bonus points
    if primary_risk in expected_disasters:
        total_possible += 1  # Extra point for primary risk
    
    accuracy_percentage = min((accuracy_score / max(total_possible, 1)) * 100, 100)
    
    # Geographic relevance bonus
    climate_appropriate = validate_climate_detection_enhanced(city, button_text)
    terrain_appropriate = validate_terrain_detection_enhanced(city, button_text)
    
    if climate_appropriate:
        accuracy_percentage += 5
    if terrain_appropriate:
        accuracy_percentage += 5
    
    accuracy_percentage = min(accuracy_percentage, 100)
    
    return {
        "detected_disasters": detected_disasters,
        "missed_disasters": missed_disasters,
        "false_positives": false_positives,
        "accuracy_score": accuracy_score,
        "accuracy_percentage": accuracy_percentage,
        "primary_risk_detected": primary_risk in [d.lower() for d in detected_disasters],
        "total_expected": len(expected_disasters),
        "climate_appropriate": climate_appropriate,
        "terrain_appropriate": terrain_appropriate,
        "geographic_bonus": climate_appropriate or terrain_appropriate
    }

def get_disaster_keywords_enhanced(disaster_type: str) -> List[str]:
    """Enhanced keyword mapping for disaster detection"""
    
    keyword_map = {
        "earthquake": ["earthquake", "seismic", "quake", "tremor", "fault", "ground shaking", "rupture"],
        "volcano": ["volcano", "volcanic", "eruption", "lava", "ash", "pyroclastic", "lahar"],
        "hurricane": ["hurricane", "storm", "surge", "tropical storm", "cyclone", "typhoon"],
        "typhoon": ["typhoon", "storm", "surge", "tropical storm", "cyclone", "hurricane"],
        "cyclone": ["cyclone", "storm", "surge", "tropical storm", "hurricane", "typhoon"],
        "tornado": ["tornado", "twister", "storm", "funnel", "severe thunderstorm"],
        "wildfire": ["wildfire", "fire", "burn", "blaze", "bushfire", "forest fire"],
        "flood": ["flood", "flooding", "deluge", "inundation", "overflow", "surge"],
        "drought": ["drought", "dry", "arid", "water shortage", "desertification"],
        "tsunami": ["tsunami", "tidal wave", "surge", "seismic wave"],
        "landslide": ["landslide", "slide", "slope failure", "debris flow", "mudslide"],
        "blizzard": ["blizzard", "snow", "ice storm", "winter storm", "snowstorm"],
        "heatwave": ["heat", "temperature", "hot", "thermal", "extreme heat"],
        "heat_wave": ["heat", "temperature", "hot", "thermal", "extreme heat"],
        "ice_storm": ["ice", "storm", "winter", "freeze", "freezing"],
        "dust_storm": ["dust", "sand", "storm", "sandstorm", "haboob"],
        "flash_flood": ["flash flood", "flood", "rapid flooding", "sudden flood"],
        "sea_level_rise": ["sea level", "coastal", "rise", "erosion", "submersion"],
        "air_pollution": ["pollution", "smog", "air quality", "toxic"],
        "coastal_erosion": ["erosion", "coastal", "cliff", "beach"],
        "extreme_heat": ["heat", "temperature", "hot", "thermal"],
        "extreme_cold": ["cold", "freeze", "frost", "ice", "polar"],
        "polar_night": ["polar", "darkness", "winter", "extreme cold"]
    }
    
    return keyword_map.get(disaster_type.lower(), [disaster_type.lower()])

def validate_climate_detection_enhanced(city: Dict, button_text: str) -> bool:
    """Enhanced climate validation"""
    
    climate = city['climate']
    
    climate_indicators = {
        'tropical': ['hurricane', 'typhoon', 'monsoon', 'heat', 'storm', 'cyclone'],
        'tropical_rainforest': ['flood', 'rain', 'storm', 'humidity'],
        'tropical_monsoon': ['monsoon', 'flood', 'rain', 'cyclone', 'typhoon'],
        'tropical_highland': ['landslide', 'rain', 'temperature'],
        'mediterranean': ['wildfire', 'drought', 'heat', 'dry'],
        'temperate_oceanic': ['storm', 'rain', 'wind', 'flood'],
        'humid_subtropical': ['hurricane', 'storm', 'flood', 'heat'],
        'continental': ['tornado', 'blizzard', 'temperature', 'storm'],
        'subarctic': ['blizzard', 'ice', 'cold', 'freeze', 'snow'],
        'hot_desert': ['drought', 'heat', 'dust', 'flash flood'],
        'semi_arid': ['drought', 'dust', 'heat', 'flash flood']
    }
    
    expected_indicators = climate_indicators.get(climate, [])
    return any(indicator in button_text for indicator in expected_indicators)

def validate_terrain_detection_enhanced(city: Dict, button_text: str) -> bool:
    """Enhanced terrain validation"""
    
    terrain = city['terrain']
    
    terrain_indicators = {
        'coastal': ['storm surge', 'hurricane', 'tsunami', 'coastal', 'erosion', 'flood'],
        'mountain': ['landslide', 'avalanche', 'slide', 'slope', 'earthquake'],
        'volcanic': ['volcano', 'eruption', 'lava', 'ash', 'earthquake'],
        'desert': ['drought', 'heat', 'dust', 'flash flood'],
        'delta': ['flood', 'surge', 'overflow', 'monsoon'],
        'island': ['storm', 'surge', 'hurricane', 'typhoon', 'tsunami'],
        'arctic': ['blizzard', 'ice', 'cold', 'freeze'],
        'plains': ['tornado', 'storm', 'wind', 'drought']
    }
    
    # Check for any terrain keyword in the terrain description
    for terrain_type, indicators in terrain_indicators.items():
        if terrain_type in terrain:
            return any(indicator in button_text for indicator in indicators)
    
    return True  # Default to true if terrain not specifically categorized

# =============================================================================
# COMPREHENSIVE TEST RUNNER
# =============================================================================

def test_30_city_disaster_detection():
    """Comprehensive test of 30 diverse cities for disaster detection accuracy"""
    
    print("🌍 COMPREHENSIVE 30-CITY GLOBAL DISASTER DETECTION TEST")
    print("🎯 Testing 30 diverse cities across all continents")
    print("📊 Fresh perspective on natural disaster detection intelligence")
    print("🔄 Randomized testing order for unbiased results")
    print("=" * 80)
    
    base_url = "http://localhost:8080"
    
    # Test system health first
    try:
        health_response = requests.get(f"{base_url}/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ System health check failed")
            return
        
        health_data = health_response.json()
        print("✅ System is healthy and ready for testing")
        print(f"🎮 System: {health_data.get('system', 'Unknown')}")
        print(f"⚡ Target time: {health_data.get('target_time', 'Unknown')}")
        print(f"🌍 Earthquake intelligence: {health_data.get('earthquake_intelligence', 'Unknown')}")
        print()
    except Exception as e:
        print(f"❌ Cannot connect to system: {e}")
        print("💡 Make sure to run the enhanced button generation server first")
        return
    
    # Randomize test order for fresh perspective
    test_cities = EXPANDED_GLOBAL_TEST_CITIES.copy()
    random.shuffle(test_cities)
    
    # Test results tracking
    results = []
    total_accuracy = 0
    perfect_scores = 0
    primary_risk_detected = 0
    continent_stats = {}
    disaster_stats = {}
    processing_times = []
    
    # Test each city
    for i, city in enumerate(test_cities, 1):
        print(f"🌍 Test {i}/30: {city['name']}")
        print(f"📍 Coordinates: {city['latitude']}, {city['longitude']}")
        print(f"🏳️  Country: {city['country']}")
        print(f"🌡️  Climate: {city['climate']}")
        print(f"🏔️  Terrain: {city['terrain']}")
        print(f"🎯 Expected disasters: {', '.join(city['expected_disasters'])}")
        print(f"⚠️  Primary risk: {city['primary_risk']}")
        
        try:
            # Make request with timeout
            start_time = time.time()
            response = requests.post(f"{base_url}/analyze-location",
                                   json={
                                       "latitude": city["latitude"],
                                       "longitude": city["longitude"],
                                       "research_priority": "comprehensive"
                                   },
                                   timeout=20)  # Extended timeout for comprehensive testing
            
            elapsed_time = time.time() - start_time
            processing_times.append(elapsed_time)
            
            print(f"⏱️  Response time: {elapsed_time:.1f}s", end="")
            
            if elapsed_time < 10.0:
                print(" ✅ Under 10 seconds!")
            else:
                print(" ⚠️  Over 10 seconds")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for simulation buttons
                buttons = data.get('simulation_buttons', [])
                
                if buttons:
                    print(f"🎮 Generated {len(buttons)} buttons:")
                    
                    for j, button in enumerate(buttons, 1):
                        print(f"   {j}. 🔴 {button}")
                    
                    # Enhanced accuracy scoring
                    accuracy = score_disaster_accuracy_enhanced(city, buttons)
                    results.append({
                        "city": city,
                        "buttons": buttons,
                        "accuracy": accuracy,
                        "response_time": elapsed_time,
                        "system_data": data
                    })
                    
                    print(f"\n📊 ENHANCED ACCURACY ANALYSIS:")
                    print(f"   ✅ Detected: {', '.join(accuracy['detected_disasters']) if accuracy['detected_disasters'] else 'None'}")
                    if accuracy['missed_disasters']:
                        print(f"   ❌ Missed: {', '.join(accuracy['missed_disasters'])}")
                    if accuracy['false_positives']:
                        print(f"   ⚠️  Unexpected: {', '.join(accuracy['false_positives'])}")
                    print(f"   🎯 Primary risk detected: {'✅ YES' if accuracy['primary_risk_detected'] else '❌ NO'}")
                    print(f"   📈 Accuracy score: {accuracy['accuracy_score']} ({accuracy['accuracy_percentage']:.1f}%)")
                    
                    # Geographic context validation
                    if accuracy['climate_appropriate']:
                        print(f"   🌡️  Climate context: ✅ Appropriate")
                    if accuracy['terrain_appropriate']:
                        print(f"   🏔️  Terrain context: ✅ Appropriate")
                    if accuracy['geographic_bonus']:
                        print(f"   🎁 Geographic bonus: +5-10%")
                    
                    # Update statistics
                    total_accuracy += accuracy['accuracy_percentage']
                    if accuracy['accuracy_percentage'] >= 90:
                        perfect_scores += 1
                    if accuracy['primary_risk_detected']:
                        primary_risk_detected += 1
                    
                    # Track by continent
                    continent = get_continent(city['country'])
                    if continent not in continent_stats:
                        continent_stats[continent] = {'total': 0, 'accuracy_sum': 0}
                    continent_stats[continent]['total'] += 1
                    continent_stats[continent]['accuracy_sum'] += accuracy['accuracy_percentage']
                    
                    # Track disaster detection rates
                    for disaster in city['expected_disasters']:
                        if disaster not in disaster_stats:
                            disaster_stats[disaster] = {'detected': 0, 'total': 0}
                        disaster_stats[disaster]['total'] += 1
                        if disaster in accuracy['detected_disasters']:
                            disaster_stats[disaster]['detected'] += 1
                    
                    # Show earthquake intelligence if available
                    earthquake_intel = data.get('earthquake_intelligence', {})
                    if earthquake_intel and earthquake_intel.get('success'):
                        seismic_risk = earthquake_intel.get('seismic_risk', 'unknown')
                        data_source = earthquake_intel.get('data_source', 'unknown')
                        print(f"   🌍 Earthquake intel: {seismic_risk} risk ({data_source})")
                
                else:
                    print("❌ No buttons generated")
                    print(f"   Error: {data.get('error', 'Unknown error')}")
                    
            else:
                print(f"❌ HTTP Error {response.status_code}")
                print(f"   Response: {response.text[:150]}...")
                
        except requests.exceptions.Timeout:
            print("❌ Request timed out (>20 seconds)")
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        print("\n" + "─" * 70 + "\n")
        
        # Brief pause to avoid rate limiting
        if i % 5 == 0:
            print("⏸️  Brief pause to avoid rate limiting...")
            time.sleep(3)
        else:
            time.sleep(0.5)
    
    # Generate comprehensive report
    generate_comprehensive_30_city_report(
        results, total_accuracy, perfect_scores, primary_risk_detected,
        continent_stats, disaster_stats, processing_times
    )

def get_continent(country: str) -> str:
    """Get continent for a country"""
    continent_map = {
        'USA': 'North America', 'Canada': 'North America', 'Mexico': 'North America',
        'Chile': 'South America', 'Colombia': 'South America', 'Brazil': 'South America', 'Argentina': 'South America',
        'Iceland': 'Europe', 'Portugal': 'Europe', 'Netherlands': 'Europe', 'Greece': 'Europe', 'Sweden': 'Europe',
        'Nigeria': 'Africa', 'Egypt': 'Africa', 'Kenya': 'Africa', 'Morocco': 'Africa', 'South Africa': 'Africa',
        'South Korea': 'Asia', 'Indonesia': 'Asia', 'Thailand': 'Asia', 'Nepal': 'Asia', 'Pakistan': 'Asia', 
        'Vietnam': 'Asia', 'Iran': 'Asia', 'Israel': 'Asia', 'Russia': 'Asia',
        'New Zealand': 'Oceania', 'Australia': 'Oceania', 'Fiji': 'Oceania'
    }
    return continent_map.get(country, 'Other')

def generate_comprehensive_30_city_report(
    results: List[Dict], total_accuracy: float, perfect_scores: int, 
    primary_risk_detected: int, continent_stats: Dict, disaster_stats: Dict,
    processing_times: List[float]
):
    """Generate comprehensive analysis report for 30-city test"""
    
    print("🌍 COMPREHENSIVE 30-CITY DISASTER DETECTION REPORT")
    print("=" * 70)
    
    total_tests = len(results)
    avg_accuracy = total_accuracy / max(total_tests, 1)
    avg_processing_time = sum(processing_times) / max(len(processing_times), 1)
    
    print(f"📊 OVERALL STATISTICS:")
    print(f"   🌍 Cities tested: {total_tests}/30")
    print(f"   📈 Average accuracy: {avg_accuracy:.1f}%")
    print(f"   ⏱️  Average processing time: {avg_processing_time:.1f}s")
    print(f"   🏆 Perfect scores (≥90%): {perfect_scores}/{total_tests} ({perfect_scores/max(total_tests,1)*100:.1f}%)")
    print(f"   🎯 Primary risks detected: {primary_risk_detected}/{total_tests} ({primary_risk_detected/max(total_tests,1)*100:.1f}%)")
    print(f"   ⚡ Under 10s responses: {sum(1 for t in processing_times if t < 10)}/{len(processing_times)}")
    
    # Performance assessment
    print(f"\n🎯 SYSTEM PERFORMANCE ASSESSMENT:")
    if avg_accuracy >= 85:
        print("🏆 EXCELLENT: Outstanding disaster detection capabilities")
    elif avg_accuracy >= 75:
        print("✅ VERY GOOD: Strong disaster detection performance")
    elif avg_accuracy >= 65:
        print("✅ GOOD: Solid disaster detection capabilities")
    else:
        print("⚠️  NEEDS IMPROVEMENT: System requires optimization")
    
    # Speed assessment
    if avg_processing_time <= 5:
        print("⚡ SPEED: Excellent - very fast response times")
    elif avg_processing_time <= 10:
        print("⚡ SPEED: Good - meeting target response times")
    else:
        print("⚠️  SPEED: Slower than target - consider optimization")
    
    # Disaster type detection rates
    print(f"\n📋 DISASTER TYPE DETECTION RATES:")
    for disaster, stats in sorted(disaster_stats.items()):
        rate = stats['detected'] / max(stats['total'], 1) * 100
        status = "🟢" if rate >= 80 else "🟡" if rate >= 60 else "🔴"
        print(f"   {status} {disaster.replace('_', ' ').title()}: {stats['detected']}/{stats['total']} ({rate:.1f}%)")
    
    # Continental performance analysis
    print(f"\n🗺️  CONTINENTAL PERFORMANCE ANALYSIS:")
    for continent, stats in sorted(continent_stats.items()):
        if stats['total'] > 0:
            continent_avg = stats['accuracy_sum'] / stats['total']
            print(f"   🌍 {continent}: {continent_avg:.1f}% average ({stats['total']} cities)")
    
    # Top and bottom performers
    sorted_results = sorted(results, key=lambda r: r['accuracy']['accuracy_percentage'], reverse=True)
    
    print(f"\n🏆 TOP 5 PERFORMERS:")
    for i, result in enumerate(sorted_results[:5], 1):
        city = result['city']
        acc = result['accuracy']['accuracy_percentage']
        time_taken = result['response_time']
        print(f"   {i}. {city['name']}, {city['country']}: {acc:.1f}% ({time_taken:.1f}s)")
    
    print(f"\n⚠️  BOTTOM 5 PERFORMERS (Need Attention):")
    for i, result in enumerate(sorted_results[-5:], 1):
        city = result['city']
        acc = result['accuracy']['accuracy_percentage']
        missed = result['accuracy']['missed_disasters']
        print(f"   {i}. {city['name']}, {city['country']}: {acc:.1f}% (missed: {', '.join(missed)})")
    
    # Earthquake intelligence analysis
    earthquake_cities = [r for r in results if any('earthquake' in disaster for disaster in r['city']['expected_disasters'])]
    earthquake_detected = len([r for r in earthquake_cities if 'earthquake' in r['accuracy']['detected_disasters']])
    
    if earthquake_cities:
        earthquake_rate = earthquake_detected / len(earthquake_cities) * 100
        print(f"\n🌍 EARTHQUAKE INTELLIGENCE ANALYSIS:")
        print(f"   📊 Earthquake zones tested: {len(earthquake_cities)}")
        print(f"   ✅ Earthquakes detected: {earthquake_detected}/{len(earthquake_cities)} ({earthquake_rate:.1f}%)")
        
        # Show earthquake intelligence sources
        earthquake_intel_sources = {}
        for result in earthquake_cities:
            earthquake_data = result['system_data'].get('earthquake_intelligence', {})
            source = earthquake_data.get('data_source', 'none')
            if source not in earthquake_intel_sources:
                earthquake_intel_sources[source] = 0
            earthquake_intel_sources[source] += 1
        
        print(f"   📡 Intelligence sources:")
        for source, count in earthquake_intel_sources.items():
            print(f"      • {source}: {count} cities")
    
    # Climate and terrain analysis
    climate_appropriate = len([r for r in results if r['accuracy']['climate_appropriate']])
    terrain_appropriate = len([r for r in results if r['accuracy']['terrain_appropriate']])
    
    print(f"\n🌡️  GEOGRAPHIC INTELLIGENCE ANALYSIS:")
    print(f"   🌡️  Climate-appropriate responses: {climate_appropriate}/{total_tests} ({climate_appropriate/max(total_tests,1)*100:.1f}%)")
    print(f"   🏔️  Terrain-appropriate responses: {terrain_appropriate}/{total_tests} ({terrain_appropriate/max(total_tests,1)*100:.1f}%)")
    
    # Speed distribution analysis
    speed_categories = {
        'Very Fast (≤3s)': len([t for t in processing_times if t <= 3]),
        'Fast (3-5s)': len([t for t in processing_times if 3 < t <= 5]),
        'Good (5-8s)': len([t for t in processing_times if 5 < t <= 8]),
        'Acceptable (8-10s)': len([t for t in processing_times if 8 < t <= 10]),
        'Slow (>10s)': len([t for t in processing_times if t > 10])
    }
    
    print(f"\n⚡ SPEED DISTRIBUTION ANALYSIS:")
    for category, count in speed_categories.items():
        percentage = count / max(len(processing_times), 1) * 100
        print(f"   {category}: {count} responses ({percentage:.1f}%)")
    
    # Error analysis
    failed_tests = 30 - total_tests
    if failed_tests > 0:
        print(f"\n❌ ERROR ANALYSIS:")
        print(f"   Failed requests: {failed_tests}/30 ({failed_tests/30*100:.1f}%)")
        print(f"   Most likely causes: API timeouts, rate limiting, network issues")
    
    # Recommendations based on results
    print(f"\n💡 SYSTEM OPTIMIZATION RECOMMENDATIONS:")
    
    if avg_accuracy < 75:
        print("   🔧 Accuracy: Improve geographic analysis and disaster keyword detection")
    
    if avg_processing_time > 8:
        print("   ⚡ Speed: Consider reducing API timeout or optimizing parallel processing")
    
    if earthquake_rate < 80:
        print("   🌍 Earthquake: Enhance seismic zone coverage or API fallback mechanisms")
    
    low_detection_disasters = [d for d, s in disaster_stats.items() 
                              if (s['detected']/max(s['total'],1)) < 0.6 and s['total'] >= 2]
    if low_detection_disasters:
        print(f"   📋 Disaster Types: Improve detection for: {', '.join(low_detection_disasters)}")
    
    # Final assessment and readiness
    print(f"\n🎮 GAME ENGINE INTEGRATION READINESS:")
    
    readiness_score = 0
    total_criteria = 5
    
    if avg_accuracy >= 70:
        print("   ✅ Accuracy: System provides reliable disaster scenarios")
        readiness_score += 1
    else:
        print("   ❌ Accuracy: Below acceptable threshold for game use")
    
    if avg_processing_time <= 10:
        print("   ✅ Speed: Meets real-time requirements for game integration")
        readiness_score += 1
    else:
        print("   ❌ Speed: Too slow for real-time game integration")
    
    if earthquake_rate >= 70:
        print("   ✅ Earthquake Intelligence: Adequate seismic scenario generation")
        readiness_score += 1
    else:
        print("   ❌ Earthquake Intelligence: Needs improvement for geological realism")
    
    if climate_appropriate/max(total_tests,1) >= 0.7:
        print("   ✅ Geographic Intelligence: Good climate-terrain awareness")
        readiness_score += 1
    else:
        print("   ❌ Geographic Intelligence: Insufficient climate-terrain matching")
    
    if failed_tests <= 3:
        print("   ✅ Reliability: System demonstrates good stability")
        readiness_score += 1
    else:
        print("   ❌ Reliability: Too many failed requests for production use")
    
    readiness_percentage = (readiness_score / total_criteria) * 100
    
    print(f"\n🎯 OVERALL READINESS SCORE: {readiness_score}/{total_criteria} ({readiness_percentage:.0f}%)")
    
    if readiness_percentage >= 80:
        print("🏆 EXCELLENT: System is ready for game engine integration!")
        print("🎮 Recommend: Proceed with landscape simulation game development")
    elif readiness_percentage >= 60:
        print("✅ GOOD: System is mostly ready with minor improvements needed")
        print("🔧 Recommend: Address specific weaknesses before full deployment")
    else:
        print("⚠️  NEEDS WORK: System requires significant improvements")
        print("🛠️  Recommend: Focus on major issues before game integration")
    
    # Summary statistics for quick reference
    print(f"\n📋 QUICK REFERENCE SUMMARY:")
    print(f"   • Total cities tested: {total_tests}/30")
    print(f"   • Average accuracy: {avg_accuracy:.1f}%")
    print(f"   • Average response time: {avg_processing_time:.1f}s")
    print(f"   • Earthquake detection rate: {earthquake_rate:.1f}% ({earthquake_detected}/{len(earthquake_cities)})")
    print(f"   • Perfect scores: {perfect_scores}/{total_tests}")
    print(f"   • System readiness: {readiness_percentage:.0f}%")

if __name__ == "__main__":
    print("🌍 COMPREHENSIVE 30-CITY DISASTER DETECTION TESTER")
    print("🎯 Fresh perspective on natural disaster detection accuracy")
    print("📊 Testing system intelligence across maximum geographic diversity")
    print("🔄 Randomized testing order for unbiased evaluation")
    print("⚡ Real-world performance assessment for game engine integration")
    print()
    
    # Show test cities for transparency
    print(f"📍 TESTING {len(EXPANDED_GLOBAL_TEST_CITIES)} DIVERSE GLOBAL CITIES:")
    continents = {}
    for city in EXPANDED_GLOBAL_TEST_CITIES:
        continent = get_continent(city['country'])
        if continent not in continents:
            continents[continent] = []
        continents[continent].append(city['name'])
    
    for continent, cities in continents.items():
        print(f"   🌍 {continent}: {len(cities)} cities")
        print(f"      {', '.join(cities[:3])}{'...' if len(cities) > 3 else ''}")
    
    print()
    
    # Run comprehensive test
    test_30_city_disaster_detection()
    
    print("\n🎯 COMPREHENSIVE TEST COMPLETE!")
    print("🌍 Fresh accuracy assessment across maximum geographic diversity")
    print("🎮 System evaluation complete for landscape simulation integration")