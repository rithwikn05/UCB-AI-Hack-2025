import requests
import json
import time

def test_llm_agent_network():
    """Test the TRUE LLM-powered agent network"""
    url = "http://localhost:8080/analyze-location"
    
    # Test locations for LLM analysis
    test_locations = [
        {"latitude": -12, "longitude": -55, "name": "Amazon Rainforest", "research_priority": "comprehensive"},
        {"latitude": 37.7749, "longitude": -122.4194, "name": "San Francisco Bay Area", "research_priority": "urgent"},  
        {"latitude": 25.7617, "longitude": -80.1918, "name": "Miami (Hurricane Zone)", "research_priority": "comprehensive"},
        {"latitude": 34.0522, "longitude": -118.2437, "name": "Los Angeles (Fire Zone)", "research_priority": "urgent"}
    ]
    
    print("🧠 Testing TRUE LLM-Powered Agent Network...\n")
    print("🤖 This system uses Groq LLM for intelligent decision making")
    print("📡 Real agent-to-agent communication via uAgent protocols")
    print("=" * 70)
    
    # Test health first
    try:
        health_response = requests.get("http://localhost:8080/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print("✅ LLM Agent Network is healthy!")
            print(f"🧠 LLM Integration: {health_data.get('llm_integration', 'Unknown')}")
            print(f"📡 Communication: {health_data.get('communication', 'Unknown')}")
            print(f"🤖 Agents: {len(health_data.get('agents', {}))}")
            print()
            
            # Display agent addresses
            agents = health_data.get('agents', {})
            for role, address in agents.items():
                print(f"   {role}: {address[:20]}...")
            print()
        else:
            print("❌ LLM agent network health check failed")
            return
    except Exception as e:
        print(f"❌ Cannot connect to LLM agent network: {e}")
        print("Make sure you're running climate_research_agent.py with your Groq API key!")
        return
    
    # Test LLM-powered research
    for i, location in enumerate(test_locations, 1):
        print(f"🧠 Test {i}: LLM Analysis for {location['name']}")
        print(f"📍 Coordinates: {location['latitude']}, {location['longitude']}")
        print(f"⚡ Priority: {location['research_priority']}")
        
        try:
            start_time = time.time()
            
            response = requests.post(url, json={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "research_priority": location["research_priority"]
            })
            
            request_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if LLM processing is complete
                if data.get('status') == 'LLM agents processing':
                    print(f"🔄 LLM Agents are thinking... (waited {request_time:.1f}s)")
                    print(f"   Status: {data.get('message', 'Processing')}")
                    print(f"   Request ID: {data.get('request_id', 'Unknown')}")
                else:
                    # Full LLM results available
                    print(f"✅ LLM Analysis Complete! ({request_time:.1f}s)")
                    
                    # Display LLM coordinator reasoning
                    llm_reasoning = data.get('llm_coordinator_reasoning', '')
                    if llm_reasoning:
                        print(f"🧠 LLM Coordinator Reasoning:")
                        print(f"   {llm_reasoning[:150]}...")
                    
                    # Display specialist contributions
                    contributions = data.get('specialist_contributions', [])
                    if contributions:
                        print(f"🤖 Specialist Agent Contributions:")
                        for contrib in contributions:
                            print(f"   - {contrib}")
                    
                    # Display scenarios
                    scenarios = data.get('scenarios', [])
                    print(f"📊 Generated {len(scenarios)} LLM-Enhanced Scenarios:")
                    
                    for j, scenario in enumerate(scenarios, 1):
                        print(f"   {j}. {scenario.get('label', 'Unknown Scenario')}")
                        print(f"      Source: {scenario.get('source', 'Unknown')}")
                        print(f"      Confidence: {scenario.get('confidence', 0)}")
                        
                        # Show LLM reasoning
                        agent_reasoning = scenario.get('agent_reasoning', '')
                        if agent_reasoning:
                            print(f"      🧠 LLM Reasoning: {agent_reasoning[:100]}...")
                        
                        # Show API calls made
                        api_calls = scenario.get('api_calls', [])
                        if api_calls:
                            print(f"      📡 APIs Called: {', '.join(api_calls)}")
                
                print()
                
            else:
                print(f"❌ Error {response.status_code} for {location['name']}")
                print(f"   Response: {response.text[:100]}...")
                print()
                
        except Exception as e:
            print(f"❌ Request failed for {location['name']}: {e}")
            print()
        
        # Brief pause between tests
        time.sleep(1)

def test_llm_decision_variability():
    """Test that LLM makes different decisions for different locations"""
    url = "http://localhost:8080/analyze-location"
    
    print("🧪 Testing LLM Decision Variability...")
    print("🧠 Different locations should trigger different LLM reasoning")
    print("=" * 70)
    
    # Very different locations to test LLM intelligence
    contrasting_locations = [
        {"latitude": 90, "longitude": 0, "name": "North Pole (Arctic)", "priority": "comprehensive"},
        {"latitude": -90, "longitude": 0, "name": "South Pole (Antarctica)", "priority": "comprehensive"},
        {"latitude": 0, "longitude": 0, "name": "Equatorial Atlantic", "priority": "comprehensive"},
        {"latitude": 19.5951, "longitude": 155.4094, "name": "Hawaii (Volcanic)", "priority": "comprehensive"}
    ]
    
    for location in contrasting_locations:
        print(f"🌍 Testing: {location['name']}")
        
        try:
            response = requests.post(url, json={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "research_priority": location["priority"]
            })
            
            if response.status_code == 200:
                data = response.json()
                
                if 'llm_coordinator_reasoning' in data:
                    reasoning = data['llm_coordinator_reasoning']
                    print(f"🧠 LLM Reasoning: {reasoning[:120]}...")
                    
                    # Check for location-specific insights
                    location_keywords = ['arctic', 'tropical', 'volcanic', 'polar', 'equatorial', 'coastal']
                    found_keywords = [kw for kw in location_keywords if kw.lower() in reasoning.lower()]
                    if found_keywords:
                        print(f"✅ LLM detected location characteristics: {', '.join(found_keywords)}")
                    else:
                        print("📝 LLM provided general analysis")
                else:
                    print("🔄 LLM still processing...")
                
                print()
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            print()

def test_priority_differences():
    """Test that LLM responds differently to urgent vs comprehensive priority"""
    url = "http://localhost:8080/analyze-location"
    
    print("⚡ Testing LLM Priority Response Differences...")
    print("🧠 LLM should adapt strategy based on urgent vs comprehensive priority")
    print("=" * 70)
    
    test_location = {"latitude": 37.7749, "longitude": -122.4194, "name": "San Francisco"}
    
    for priority in ["urgent", "comprehensive"]:
        print(f"🎯 Testing {priority.upper()} priority:")
        
        try:
            response = requests.post(url, json={
                "latitude": test_location["latitude"],
                "longitude": test_location["longitude"],
                "research_priority": priority
            })
            
            if response.status_code == 200:
                data = response.json()
                
                if 'llm_coordinator_reasoning' in data:
                    reasoning = data['llm_coordinator_reasoning']
                    print(f"🧠 LLM Strategy: {reasoning[:150]}...")
                    
                    # Look for priority-specific language
                    if priority == "urgent":
                        urgent_keywords = ['fast', 'quick', 'immediate', 'urgent', 'priority']
                        found = [kw for kw in urgent_keywords if kw.lower() in reasoning.lower()]
                        if found:
                            print(f"✅ LLM adapted for urgency: {', '.join(found)}")
                    else:
                        comprehensive_keywords = ['thorough', 'comprehensive', 'detailed', 'complete']
                        found = [kw for kw in comprehensive_keywords if kw.lower() in reasoning.lower()]
                        if found:
                            print(f"✅ LLM adapted for thoroughness: {', '.join(found)}")
                
                print()
                
        except Exception as e:
            print(f"❌ Priority test failed: {e}")
            print()

if __name__ == "__main__":
    print("🚀 TESTING TRUE LLM-POWERED AGENTIC CLIMATE RESEARCH")
    print("🧠 Groq Llama3-70B Intelligence + Real uAgent Communication")
    print("🤖 Dynamic Decision Making + Agent-to-Agent Messaging")
    print("=" * 70)
    print()
    
    test_llm_agent_network()
    print("=" * 70)
    test_llm_decision_variability()
    print("=" * 70)
    test_priority_differences()