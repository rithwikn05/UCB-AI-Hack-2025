import requests
import json
import time
from typing import List, Dict, Any

def test_hazard_recognition_accuracy_multi_agent_robust():
    """
    Test the climate hazard recognition accuracy of the intelligent multi-API agent system.
    This script interacts with the FastAPI endpoint, which orchestrates the uAgents network.
    It expects the 'Intelligent Multi-API Landscape Evolution System' to be running.
    Uses the /get-results/{request_id} polling endpoint for robust status checks.
    """
    
    base_url = "http://localhost:8080"
    analyze_location_url = f"{base_url}/analyze-location"
    get_results_url_template = f"{base_url}/get-results/" # Will append request_id

    # Define concise test cases with expected hazard keywords and button keywords.
    # IMPORTANT: Adjust these expected keywords based on what your LLMs
    # (both coordinator's and specialists') are likely to generate
    # given the API data they can access and synthesize.
    test_cases = [
        {
            "name": "San Francisco (Seismic/Wildfire)",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "priority": "urgent",
            "expected_analysis_keywords": ["earthquake", "seismic", "wildfire", "fault", "urban", "coastal"],
            "expected_button_keywords": ["earthquake", "wildfire", "seismic", "rupture", "coastal erosion", "urban impact"]
        },
        {
            "name": "Miami (Hurricane/Flood)",
            "latitude": 25.7617,
            "longitude": -80.1918,
            "priority": "urgent",
            "expected_analysis_keywords": ["hurricane", "flood", "coastal", "tropical", "storm surge"],
            "expected_button_keywords": ["hurricane", "storm surge", "flood", "coastal erosion", "tropical impact"]
        },
        {
            "name": "Phoenix (Drought/Heat)",
            "latitude": 33.4484,
            "longitude": -112.0740,
            "priority": "comprehensive",
            "expected_analysis_keywords": ["drought", "heatwave", "arid", "desert"],
            "expected_button_keywords": ["drought", "heatwave", "desertification", "water scarcity"]
        },
        {
            "name": "Mount Fuji, Japan (Volcano/Earthquake)",
            "latitude": 35.3606, # Near Mount Fuji
            "longitude": 138.7278,
            "priority": "urgent",
            "expected_analysis_keywords": ["volcano", "earthquake", "seismic", "eruption", "mountain", "ashfall"],
            "expected_button_keywords": ["volcanic eruption", "earthquake", "lava flow", "ashfall", "seismic activity"]
        },
        {
            "name": "Bangladesh Delta (Flood/Sea Level)",
            "latitude": 22.3475,
            "longitude": 91.8123,
            "priority": "comprehensive",
            "expected_analysis_keywords": ["flood", "sea level rise", "storm surge", "cyclone", "delta", "coastal", "tropical"],
            "expected_button_keywords": ["flood", "sea level rise", "cyclone impact", "delta erosion", "storm surge"]
        },
        {
            "name": "Fairbanks, Alaska (Arctic/Permafrost)",
            "latitude": 64.2008,
            "longitude": -149.4937,
            "priority": "comprehensive",
            "expected_analysis_keywords": ["arctic", "permafrost", "cold", "thaw", "winter storm"],
            "expected_button_keywords": ["permafrost thaw", "arctic warming", "ice melt", "extreme cold"]
        }
    ]
    
    print("🧠 Testing Climate Hazard Recognition Accuracy (Robust Polling Mode)...")
    print("======================================================================")
    
    # Pre-check: Ensure the API server is running
    try:
        health_response = requests.get(f"{base_url}/health")
        if health_response.status_code == 200:
            print("✅ API server is healthy. Starting tests.")
            health_data = health_response.json()
            print(f"  System: {health_data.get('system')}")
            print(f"  Total APIs: {health_data.get('total_apis')}")
            print(f"  Agent Count: {len(health_data.get('agents', {}))}")
            print(f"  Coordinator Address: {health_data.get('agents', {}).get('intelligent_climate_coordinator', 'N/A')}")
            print()
        else:
            print(f"❌ API server health check failed: {health_response.status_code}")
            print("Please ensure your 'Intelligent Multi-API Landscape Evolution System' is running.")
            return
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Could not connect to API server at {base_url}. Is it running?")
        print(f"Error: {e}")
        print("Remember to start your main agent system file in a separate terminal FIRST.")
        return
    
    total_tests = len(test_cases)
    passed_tests = 0

    # Polling parameters
    polling_interval = 2 # seconds between polls
    max_polling_attempts = 25 # Total wait time = polling_interval * max_polling_attempts (e.g., 2s * 25 = 50s)

    for i, test_case in enumerate(test_cases):
        name = test_case['name']
        latitude = test_case['latitude']
        longitude = test_case['longitude']
        priority = test_case['priority']
        expected_analysis_keywords = [k.lower() for k in test_case['expected_analysis_keywords']]
        expected_button_keywords = [k.lower() for k in test_case['expected_button_keywords']]

        print(f"\n--- Test Case {i+1}/{total_tests}: {name} ({priority.upper()}) ---")
        print(f"Location: ({latitude}, {longitude})")
        print(f"Expected Analysis Keywords: {', '.join(expected_analysis_keywords)}")
        print(f"Expected Button Keywords: {', '.join(expected_button_keywords)}")
        
        request_id = None
        final_report_data = None
        
        try:
            start_test_case_time = time.time()
            
            # Step 1: Send the initial request to trigger agent processing
            post_response = requests.post(
                analyze_location_url,
                json={
                    "latitude": latitude,
                    "longitude": longitude,
                    "priority": priority, 
                    "reasoning_context": "Landscape evolution simulation for game engine"
                },
                timeout=30 # Increased timeout for initial POST as it includes some processing and agent dispatch
            )
            
            post_data = post_response.json()
            request_id = post_data.get('request_id')

            if not request_id:
                print(f"❌ Initial POST failed to return request_id. Response: {post_data}")
                print(f"  Test Result: ❌ FAILED (No request_id)")
                time.sleep(1) # Short pause before next test
                continue

            print(f"  Request ID: {request_id}. Initial status: {post_data.get('status', 'Unknown')}")

            # Step 2: Poll the /get-results endpoint until completion or timeout
            for attempt in range(max_polling_attempts):
                time.sleep(polling_interval) # Wait before polling
                
                get_response = requests.get(f"{get_results_url_template}{request_id}")
                get_data = get_response.json()
                
                if get_data.get('status') == 'completed':
                    final_report_data = get_data.get('report')
                    print(f"✅ Polling successful. Status: Completed after {attempt+1} attempts.")
                    break
                elif get_data.get('status') == 'processing':
                    print(f"  Still processing (Attempt {attempt+1}/{max_polling_attempts})...")
                else:
                    print(f"  Polling failed with unexpected status: {get_data.get('status')}. Data: {get_data}")
                    break
            
            if not final_report_data:
                print(f"❌ Timed out waiting for results for request_id: {request_id} after {max_polling_attempts * polling_interval} seconds.")
                print(f"  Test Result: ❌ FAILED (Timeout)")
                time.sleep(1) # Short pause before next test
                continue

            # --- Process the final report data ---
            total_processing_time = final_report_data.get('processing_time', time.time() - start_test_case_time)
            print(f"✅ Analysis complete in {total_processing_time:.2f}s")
            
            # Extract detected hazards from various parts of the report
            coordinator_reasoning = final_report_data.get('coordinator_reasoning', '').lower()
            detected_analysis_text = coordinator_reasoning

            specialist_contributions = final_report_data.get('specialist_contributions', [])
            for contrib in specialist_contributions:
                detected_analysis_text += " " + contrib.lower()
            
            # Final Simulation Buttons
            detected_buttons = [btn.lower() for btn in final_report_data.get('simulation_buttons', [])]
            
            print(f"  Aggregated Analysis Text (snippet): {detected_analysis_text[:150]}...") # Show a snippet
            print(f"  Generated Simulation Buttons: {', '.join(detected_buttons)}")
            
            # Assess analysis text keyword match
            analysis_match = 0
            for expected_k in expected_analysis_keywords:
                if expected_k in detected_analysis_text:
                    analysis_match += 1
            analysis_accuracy = (analysis_match / len(expected_analysis_keywords)) * 100 if expected_analysis_keywords else 100
            
            # Assess button keyword match
            button_match = 0
            for expected_k in expected_button_keywords:
                if any(expected_k in btn for btn in detected_buttons):
                    button_match += 1
            button_accuracy = (button_match / len(expected_button_keywords)) * 100 if expected_button_keywords else 100
            
            print(f"  Analysis Keyword Match: {analysis_accuracy:.1f}%")
            print(f"  Button Keyword Match: {button_accuracy:.1f}%")

            # Decide if test passed (adjust these thresholds based on desired accuracy)
            if analysis_accuracy >= 60 and button_accuracy >= 60: # Example thresholds
                print("  Test Result: ✅ PASSED (Hazard recognition acceptable)")
                passed_tests += 1
            else:
                print("  Test Result: ❌ FAILED (Hazard recognition not as expected)")
                
        except requests.exceptions.RequestException as req_err:
            print(f"  Test Result: ❌ FAILED (Network/Request Error: {req_err})")
        except json.JSONDecodeError:
            print(f"  Test Result: ❌ FAILED (Invalid JSON response from server)")
            # Try to print raw response if possible
            if 'post_response' in locals():
                print(f"  Raw POST Response: {post_response.text}")
            if 'get_response' in locals():
                print(f"  Raw GET Response: {get_response.text}")
        except Exception as e:
            print(f"  Test Result: ❌ FAILED (An unexpected error occurred: {e})")

        time.sleep(2) # Short pause between test cases to prevent flooding the server

    print("\n===================================================")
    print(f"Final Report: {passed_tests}/{total_tests} tests passed.")
    print("===================================================")

if __name__ == "__main__":
    # IMPORTANT: Ensure your main agent system file (e.g., climate_research_agent.py)
    # is running in a separate terminal window BEFORE you execute this test script.
    
    test_hazard_recognition_accuracy_multi_agent_robust()