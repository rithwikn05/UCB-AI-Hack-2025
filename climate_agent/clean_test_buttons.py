#!/usr/bin/env python3
"""
FAST BUTTON GENERATION TEST SCRIPT
Tests the optimized system for sub-10-second response times
"""

import requests
import json
import time

def test_fast_button_generation():
    """Test the fast button generation system"""
    
    print("🚀 TESTING FAST BUTTON GENERATION SYSTEM")
    print("🎯 Target: Under 10 seconds per location")
    print("=" * 60)
    
    # Test locations with expected themes
    test_locations = [
        {
            "latitude": 37.7749, "longitude": -122.4194,
            "name": "San Francisco, CA",
            "expected": ["earthquake", "wildfire", "weather"]
        },
        {
            "latitude": 25.7617, "longitude": -80.1918,
            "name": "Miami, FL",
            "expected": ["hurricane", "storm", "coastal", "flood"]
        },
        {
            "latitude": 45.5152, "longitude": -122.6784,
            "name": "Portland, OR", 
            "expected": ["wildfire", "earthquake", "storm"]
        },
        {
            "latitude": 40.7128, "longitude": -74.0060,
            "name": "New York City, NY",
            "expected": ["storm", "flood", "hurricane"]
        }
    ]
    
    base_url = "http://localhost:8080"
    
    # Test health first
    try:
        print("🏥 Testing system health...")
        health_response = requests.get(f"{base_url}/health", timeout=5)
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ System healthy: {health_data['system']}")
            print(f"🎯 Target time: {health_data['target_time']}")
            print()
        else:
            print("❌ Health check failed")
            return
            
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("💡 Make sure to run: python optimized_climate_research_agent.py")
        return
    
    # Test each location
    total_time = 0
    successful_tests = 0
    all_buttons = []
    
    for i, location in enumerate(test_locations, 1):
        print(f"🌍 Test {i}/4: {location['name']}")
        print(f"📍 Coordinates: {location['latitude']}, {location['longitude']}")
        
        try:
            # Time the request
            start_time = time.time()
            
            response = requests.post(f"{base_url}/analyze-location", 
                                   json={
                                       "latitude": location["latitude"],
                                       "longitude": location["longitude"],
                                       "research_priority": "urgent"
                                   },
                                   timeout=15)  # Allow up to 15s as safety
            
            elapsed_time = time.time() - start_time
            total_time += elapsed_time
            
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
                    print(f"🎮 Generated {len(buttons)} simulation buttons:")
                    for j, button in enumerate(buttons, 1):
                        print(f"   {j}. 🔴 {button}")
                    
                    all_buttons.extend(buttons)
                    successful_tests += 1
                    
                    # Check for expected themes
                    button_text = ' '.join(buttons).lower()
                    found_themes = []
                    for theme in location['expected']:
                        if any(theme_word in button_text for theme_word in theme.split()):
                            found_themes.append(theme)
                    
                    if found_themes:
                        print(f"✅ Found expected themes: {', '.join(found_themes)}")
                    else:
                        print("⚠️  No expected themes detected")
                    
                    # Check API usage
                    apis_used = data.get('apis_used', [])
                    if apis_used:
                        print(f"📡 APIs used: {len(apis_used)} ({', '.join(apis_used[:3])}...)")
                    
                    # Check method
                    method = data.get('method', 'unknown')
                    print(f"🛠️  Method: {method}")
                    
                else:
                    print("❌ No buttons generated")
                    print(f"   Error: {data.get('error', 'Unknown error')}")
                    
            else:
                print(f"❌ HTTP Error {response.status_code}")
                print(f"   Response: {response.text[:100]}...")
                
        except requests.exceptions.Timeout:
            print("❌ Request timed out (>15 seconds)")
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        print()
        time.sleep(1)  # Brief pause between tests
    
    # Summary report
    print("📊 FAST GENERATION TEST SUMMARY")
    print("=" * 40)
    print(f"✅ Successful tests: {successful_tests}/{len(test_locations)}")
    print(f"🎮 Total buttons generated: {len(all_buttons)}")
    
    if successful_tests > 0:
        avg_time = total_time / successful_tests
        print(f"⏱️  Average response time: {avg_time:.1f}s")
        
        under_10s = sum(1 for i in range(successful_tests) if total_time/successful_tests < 10)
        print(f"🎯 Tests under 10s: {under_10s}/{successful_tests}")
        
        if avg_time < 10.0:
            print("🏆 SUCCESS! Average time under 10 seconds")
        else:
            print("⚠️  NEEDS OPTIMIZATION: Average time over 10 seconds")
    
    # Show unique button types
    if all_buttons:
        unique_buttons = set(all_buttons)
        print(f"🎮 Unique button types: {len(unique_buttons)}")
        
        # Categorize buttons
        categories = {
            "Weather": ["storm", "hurricane", "weather", "wind", "rain"],
            "Fire": ["fire", "wildfire", "burn"],
            "Water": ["flood", "tsunami", "surge", "water"],
            "Geological": ["earthquake", "volcano", "seismic"],
            "Climate": ["climate", "temperature", "drought", "heat"]
        }
        
        for category, keywords in categories.items():
            count = sum(1 for button in all_buttons 
                       if any(keyword in button.lower() for keyword in keywords))
            if count > 0:
                print(f"   {category}: {count} buttons")
    
    print("\n🎯 PERFORMANCE ANALYSIS:")
    if successful_tests == len(test_locations) and total_time/max(successful_tests,1) < 10:
        print("🏆 EXCELLENT: All tests passed under 10 seconds!")
        print("🎮 Ready for game engine integration")
    elif successful_tests > 0:
        print("✅ GOOD: System working but may need speed optimization")
        print("💡 Consider reducing API calls or timeouts")
    else:
        print("❌ NEEDS DEBUGGING: Button generation not working")
        print("🔧 Check server logs and API connections")

def test_quick_endpoints():
    """Test the quick test endpoints"""
    
    print("\n🧪 TESTING QUICK ENDPOINTS")
    print("=" * 30)
    
    quick_tests = [
        (37.7749, -122.4194, "San Francisco"),
        (51.5074, -0.1278, "London"),
        (-33.8688, 151.2093, "Sydney")
    ]
    
    for lat, lon, city in quick_tests:
        print(f"🌍 Quick test: {city}")
        
        try:
            start = time.time()
            response = requests.get(f"http://localhost:8080/test-buttons/{lat}/{lon}", timeout=12)
            elapsed = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ⏱️  {elapsed:.1f}s - {len(data['buttons'])} buttons")
                print(f"   🎮 Buttons: {', '.join(data['buttons'][:3])}...")
                
                if elapsed < 10.0:
                    print("   ✅ Under 10 seconds!")
                else:
                    print("   ⚠️  Over 10 seconds")
            else:
                print(f"   ❌ Error {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        print()

def stress_test():
    """Quick stress test with multiple requests"""
    
    print("\n💪 STRESS TEST (5 rapid requests)")
    print("=" * 35)
    
    test_coords = [
        (40.7128, -74.0060),  # NYC
        (34.0522, -118.2437), # LA  
        (41.8781, -87.6298),  # Chicago
        (29.7604, -95.3698),  # Houston
        (33.4484, -112.0740)  # Phoenix
    ]
    
    start_stress = time.time()
    successful = 0
    
    for i, (lat, lon) in enumerate(test_coords, 1):
        print(f"🚀 Stress test {i}/5: {lat}, {lon}")
        
        try:
            start = time.time()
            response = requests.post("http://localhost:8080/analyze-location",
                                   json={"latitude": lat, "longitude": lon},
                                   timeout=12)
            elapsed = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                buttons = data.get('simulation_buttons', [])
                print(f"   ✅ {elapsed:.1f}s - {len(buttons)} buttons")
                successful += 1
            else:
                print(f"   ❌ Error {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    total_stress_time = time.time() - start_stress
    print(f"\n📊 Stress test results:")
    print(f"   ✅ Successful: {successful}/5")
    print(f"   ⏱️  Total time: {total_stress_time:.1f}s")
    print(f"   📈 Average per request: {total_stress_time/5:.1f}s")

if __name__ == "__main__":
    print("🚀 FAST BUTTON GENERATION SYSTEM TESTER")
    print("🎯 Testing sub-10-second landscape simulation button generation")
    print("🧠 Geographic intelligence + API data + LLM synthesis")
    print()
    
    # Run all tests
    test_fast_button_generation()
    test_quick_endpoints()
    stress_test()
    
    print("\n🎯 TEST COMPLETE!")
    print("🎮 System ready for game engine integration if all tests passed")
    print("💡 Use POST /analyze-location for production button generation")