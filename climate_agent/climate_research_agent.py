from uagents import Agent, Context, Protocol, Bureau
from uagents.setup import fund_agent_if_low
import asyncio
import aiohttp
import json
from typing import Dict, List, Optional
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic import ValidationError # Import for robust JSON parsing
import uvicorn
import threading
from groq import Groq
from dataclasses import dataclass
import ssl
import certifi # For SSL context

# Configuration - ADD YOUR LLM API KEY
GROQ_API_KEY = "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" # REPLACE WITH YOUR GROQ KEY!

# Groq client setup
groq_client = Groq(api_key=GROQ_API_KEY)

# Pre-create SSL context for aiohttp for minor speedup and reliability
ssl_context = ssl.create_default_context(cafile=certifi.where())

# =============================================================================
# FREE API REGISTRY - 15+ FREE APIs with intelligent selection
# =============================================================================

@dataclass
class APIInfo:
    name: str
    url: str
    specialty: str
    geographic_relevance: List[str]
    data_type: str
    reliability: float # 0.0 to 1.0
    latency: str # 'fast', 'medium', 'slow'
    description: str

FREE_API_REGISTRY = {
    # WEATHER & CLIMATE (FREE)
    "openweather_current": APIInfo(
        name="OpenWeather Current",
        url="https://api.openweathermap.org/data/2.5/weather",
        specialty="current_weather",
        geographic_relevance=["global"],
        data_type="real_time",
        reliability=0.85,
        latency="fast",
        description="Current weather conditions worldwide"
    ),
    
    "openweather_forecast": APIInfo(
        name="OpenWeather 5-Day Forecast", 
        url="https://api.openweathermap.org/data/2.5/forecast",
        specialty="weather_prediction",
        geographic_relevance=["global"],
        data_type="predictive", 
        reliability=0.80,
        latency="fast",
        description="5-day weather forecast"
    ),
    
    "open_meteo": APIInfo(
        name="Open-Meteo Weather",
        url="https://api.open-meteo.com/v1/forecast",
        specialty="detailed_weather",
        geographic_relevance=["global"],
        data_type="real_time",
        reliability=0.88,
        latency="fast",
        description="Free weather API with detailed meteorological data"
    ),
    
    # GEOLOGICAL (FREE)
    "usgs_earthquake": APIInfo(
        name="USGS Earthquake",
        url="https://earthquake.usgs.gov/fdsnws/event/1/query",
        specialty="seismic_activity",
        geographic_relevance=["global", "seismic_zones"],
        data_type="real_time",
        reliability=0.98,
        latency="fast",
        description="Real-time earthquake data from USGS"
    ),
    
    "volcano_discovery": APIInfo(
        name="Volcano Discovery",
        url="https://api.volcanodiscovery.com/v1/", # NOTE: This is a placeholder/mock in call_volcano_discovery_api
        specialty="volcanic_activity",
        geographic_relevance=["volcanic_zones", "ring_of_fire"],
        data_type="real_time", 
        reliability=0.85,
        latency="medium",
        description="Volcanic activity and eruption data"
    ),
    
    "elevation_api": APIInfo(
        name="Open Elevation API",
        url="https://api.open-elevation.com/api/v1/lookup",
        specialty="elevation_data",
        geographic_relevance=["global"],
        data_type="static",
        reliability=0.90,
        latency="fast",
        description="Free elevation data for any coordinates"
    ),
    
    # ENVIRONMENTAL (FREE)
    "nasa_firms": APIInfo(
        name="NASA FIRMS Fire",
        url="https://firms.modaps.eosdis.nasa.gov/api/area/csv/", # NOTE: Needs API key and specific region query structure for real use
        specialty="fire_detection",
        geographic_relevance=["global", "fire_prone"],
        data_type="real_time",
        reliability=0.88,
        latency="fast",
        description="NASA fire detection from satellites"
    ),
    
    "usgs_water": APIInfo(
        name="USGS Water Services",
        url="https://waterservices.usgs.gov/nwis/iv/",
        specialty="water_monitoring",
        geographic_relevance=["north_america"],
        data_type="real_time",
        reliability=0.91,
        latency="fast",
        description="Real-time water data for US"
    ),
    
    "air_quality_waqi": APIInfo(
        name="World Air Quality Index",
        url="https://api.waqi.info/feed/", # NOTE: Requires token, using "demo"
        specialty="air_quality",
        geographic_relevance=["global", "urban"],
        data_type="real_time",
        reliability=0.83,
        latency="fast",
        description="Global air quality monitoring"
    ),
    
    # OCEAN & MARINE (FREE)
    "noaa_tides": APIInfo(
        name="NOAA Tides & Currents",
        url="https://api.tidesandcurrents.noaa.gov/api/prod/", # NOTE: Simplified/mocked, requires station lookup
        specialty="ocean_conditions",
        geographic_relevance=["coastal", "north_america"],
        data_type="real_time",
        reliability=0.92,
        latency="fast",
        description="Tide, water level, and meteorological data"
    ),
    
    "marine_weather": APIInfo(
        name="Marine Weather API",
        url="https://marine-api.open-meteo.com/v1/marine",
        specialty="marine_conditions",
        geographic_relevance=["coastal", "ocean"],
        data_type="real_time",
        reliability=0.84,
        latency="fast",
        description="Ocean wave height, temperature, currents"
    ),
    
    # SATELLITE & IMAGERY (FREE)
    "landsat_api": APIInfo(
        name="USGS Landsat",
        url="https://landsatlook.usgs.gov/sat-api/", # NOTE: Mocked
        specialty="satellite_imagery",
        geographic_relevance=["global"],
        data_type="historical",
        reliability=0.93,
        latency="medium",
        description="Free Landsat satellite imagery"
    ),
    
    "sentinel_hub": APIInfo(
        name="Sentinel Hub (Free Tier)",
        url="https://services.sentinel-hub.com/api/v1/", # NOTE: Mocked, complex authentication
        specialty="satellite_monitoring",
        geographic_relevance=["global"],
        data_type="real_time",
        reliability=0.89,
        latency="medium", 
        description="European satellite data (Sentinel missions)"
    ),
    
    # WEATHER EXTREMES (FREE)
    "severe_weather": APIInfo(
        name="Severe Weather API",
        url="https://api.weather.gov/", # NOTE: US only
        specialty="extreme_weather",
        geographic_relevance=["north_america"],
        data_type="real_time",
        reliability=0.94,
        latency="fast",
        description="NWS severe weather alerts and warnings"
    ),
    
    "global_disaster": APIInfo(
        name="Global Disaster Alert",
        url="https://www.gdacs.org/xml/rss.xml", # NOTE: Mocked, RSS parsing
        specialty="natural_disasters",
        geographic_relevance=["global"],
        data_type="real_time",
        reliability=0.87,
        latency="fast",
        description="Global disaster and emergency information"
    )
}

# =============================================================================
# INTELLIGENT API SELECTOR (Optimized for speed)
# =============================================================================

class IntelligentAPISelector:
    """LLM-powered API selection based on location and requirements"""
    
    @staticmethod
    async def select_optimal_apis(
        latitude: float, 
        longitude: float,
        agent_specialty: str,
        priority: str,
        simulation_context: Dict,
        full_geographic_context: Dict # Added: Pre-computed geographic context
    ) -> Dict:
        """Main API selection function - returns optimal APIs for this request"""
        
        # Step 1: Geographic analysis is now done by coordinator and passed here.
        geo_context = full_geographic_context
        
        # Step 2: Filter relevant APIs based on agent specialty and geographic context
        relevant_apis = IntelligentAPISelector._filter_relevant_apis(
            agent_specialty, geo_context
        )
        
        # Step 3: LLM intelligent selection from relevant options
        llm_selection = await IntelligentAPISelector._llm_select_apis(
            latitude, longitude, agent_specialty, priority,
            relevant_apis, geo_context, simulation_context
        )
        
        return {
            'selected_apis': llm_selection['selected_apis'],
            'reasoning': llm_selection['reasoning'],
            'geographic_context': geo_context, # Ensure geo_context is returned
            'confidence': llm_selection.get('confidence', 0.8),
            'backup_apis': relevant_apis[len(llm_selection['selected_apis']):]
        }
    
    @staticmethod
    def _filter_relevant_apis(agent_specialty: str, geo_context: Dict) -> List[str]:
        """Filter APIs based on agent specialty and geographic relevance"""
        
        relevant_apis = []
        
        # Extract hazards and region types from the *pre-computed* geo_context
        geo_hazard_risks = [h.lower() for h in geo_context.get('hazard_risks', [])]
        geo_region_types = [r.lower() for r in geo_context.get('region_types', [])]
        
        for api_name, api_info in FREE_API_REGISTRY.items():
            # Check specialty relevance (case-insensitive for better matching)
            specialty_match = (
                agent_specialty.lower() in api_info.specialty.lower() or
                api_info.specialty.lower() in agent_specialty.lower() or
                any(word.lower() in api_info.specialty.lower() for word in agent_specialty.split('_'))
            )
            
            # Check geographic relevance
            geographic_match = (
                "global" in api_info.geographic_relevance or
                any(region.lower() in api_info.geographic_relevance 
                    for region in geo_region_types) or
                any(hazard.lower() in api_info.specialty.lower() 
                    for hazard in geo_hazard_risks)
            )
            
            # Include if relevant
            if specialty_match or geographic_match:
                relevant_apis.append(api_name)
        
        # Sort by reliability AND prioritize 'fast' APIs (higher reliability first, then 'fast' latency)
        relevant_apis.sort(
            key=lambda x: (FREE_API_REGISTRY[x].reliability, 1 if FREE_API_REGISTRY[x].latency == 'fast' else 0),
            reverse=True 
        )
        
        return relevant_apis
    
    @staticmethod
    async def _llm_select_apis(
        latitude: float, longitude: float, agent_specialty: str,
        priority: str, relevant_apis: List[str], 
        geo_context: Dict, simulation_context: Dict
    ) -> Dict:
        """LLM makes final API selection from relevant options"""
        
        # Prepare API details for LLM (limit to top 8 for conciseness for LLM)
        api_details = {}
        for api_name in relevant_apis[:8]: # Reduced from 10 to send less data to LLM, faster inference
            api_info = FREE_API_REGISTRY[api_name]
            api_details[api_name] = {
                'specialty': api_info.specialty,
                'description': api_info.description,
                'reliability': api_info.reliability,
                'latency': api_info.latency,
                'data_type': api_info.data_type
            }
        
        # Concise prompt to save tokens and inference time
        prompt = f"""
        You are a {agent_specialty} agent selecting optimal APIs for landscape simulation.
        Location: {latitude}°, {longitude}° | Priority: {priority}
        Geographic Context: {json.dumps(geo_context, separators=(',', ':'))}
        Simulation Needs: {json.dumps(simulation_context, separators=(',', ':'))}
        
        Available APIs (top relevant based on pre-filtering):
        {json.dumps(api_details, indent=2)}
        
        Select the 3-5 BEST APIs for this specific location and simulation needs.
        
        **Prioritize:**
        - High geographic relevance.
        - Direct impact on main hazards/simulation type.
        - 'fast' latency, especially for '{priority}' priority.
        - Data complementarity (avoid redundant data, get diverse insights).
        
        Respond ONLY with a JSON object:
        {{
            "selected_apis": ["api1", "api2", "api3"],
            "reasoning": "Concise explanation for selection.",
            "confidence": 0.85
        }}
        """
        
        try:
            response = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-70b-8192",
                temperature=0.4,
                max_tokens=250 # Reduced max_tokens for concise JSON output
            )
            
            content = response.choices[0].message.content.strip()
            return json.loads(content)
        except Exception as e:
            print(f"LLM API selection failed: {e}")
            # Fallback selection: just take the top 3 from pre-filtered list
            return {
                "selected_apis": relevant_apis[:3],
                "reasoning": "Fallback selection due to LLM error or invalid JSON.",
                "confidence": 0.6
            }

# =============================================================================
# MESSAGE MODELS
# =============================================================================

class LocationAnalysisRequest(BaseModel):
    request_id: str
    latitude: float
    longitude: float
    priority: str
    reasoning_context: str

class EnhancedSpecialistTaskRequest(BaseModel):
    request_id: str
    specialist_type: str
    latitude: float
    longitude: float
    priority: str
    simulation_context: Dict
    coordinator_analysis: str
    full_geographic_context: Dict # New: Pass pre-computed geographic context

class EnhancedSpecialistResult(BaseModel):
    request_id: str
    specialist_type: str
    selected_apis: List[str]
    api_results: Dict
    agent_analysis: str
    confidence: float
    simulation_buttons: List[str] # Ensure this is always present and a list
    visual_effects: List[str]

class FinalReport(BaseModel):
    request_id: str
    location: str
    scenarios: List[Dict]
    coordinator_reasoning: str
    specialist_contributions: List[str]
    simulation_buttons: List[str] # Ensure this is always present and a list
    total_processing_time: float

# Global coordination storage
active_research = {}
completed_research = {}

# =============================================================================
# ENHANCED COORDINATOR AGENT
# =============================================================================

# Coordinator Agent's port and endpoint - MUST match FastAPI's target
COORDINATOR_AGENT_PORT = 8000
COORDINATOR_AGENT_ENDPOINT = f"http://127.0.0.1:{COORDINATOR_AGENT_PORT}/submit"

coordinator = Agent(
    name="intelligent_climate_coordinator",
    seed="intelligent_coord_12345",
    port=COORDINATOR_AGENT_PORT, # Explicitly assign port
    endpoint=[COORDINATOR_AGENT_ENDPOINT] # Explicitly assign endpoint
)
fund_agent_if_low(coordinator.wallet.address())

coordinator_protocol = Protocol("IntelligentClimateCoordination")

@coordinator.on_event("startup")
async def coordinator_startup(ctx: Context):
    ctx.logger.info("🧠 Intelligent Multi-API Climate Coordinator ONLINE")
    # Use ctx.agent.address for reliable info as endpoint might be managed by Bureau
    ctx.logger.info(f"🤖 Address: {ctx.agent.address}") 
    ctx.logger.info(f"📡 Managing {len(FREE_API_REGISTRY)} FREE APIs")

@coordinator_protocol.on_message(model=LocationAnalysisRequest)
async def intelligent_coordinate_research(ctx: Context, sender: str, msg: LocationAnalysisRequest):
    """Enhanced coordination with intelligent API selection"""
    
    ctx.logger.info(f"🧠 COORDINATOR: Received request {msg.request_id} from {sender} for {msg.latitude}, {msg.longitude}")
    
    # Store request
    active_research[msg.request_id] = {
        'start_time': time.time(),
        'location': f"{msg.latitude},{msg.longitude}",
        'specialist_results': {},
        'expected_specialists': []
    }
    
    # --- OPTIMIZATION: Combine initial LLM calls ---
    # Coordinator now does the detailed geographic analysis for everyone
    full_geographic_context = await analyze_detailed_geography(msg.latitude, msg.longitude)
    
    # LLM determines simulation context using the detailed geographic context
    simulation_context = await analyze_simulation_requirements(
        msg.latitude, msg.longitude, msg.priority, full_geographic_context
    )
    
    # Store contexts
    active_research[msg.request_id]['simulation_context'] = simulation_context
    active_research[msg.request_id]['full_geographic_context'] = full_geographic_context # Store for report
    active_research[msg.request_id]['expected_specialists'] = simulation_context['specialists_needed']
    
    ctx.logger.info(f"🎯 SIMULATION TYPE: {simulation_context['simulation_type']}")
    ctx.logger.info(f"🤖 DEPLOYING: {simulation_context['specialists_needed']}")
    
    # Deploy specialist agents with intelligent API selection
    for specialist_type in simulation_context['specialists_needed']:
        enhanced_task = EnhancedSpecialistTaskRequest(
            request_id=msg.request_id,
            specialist_type=specialist_type,
            latitude=msg.latitude,
            longitude=msg.longitude,
            priority=msg.priority,
            simulation_context=simulation_context,
            coordinator_analysis=simulation_context['analysis'],
            full_geographic_context=full_geographic_context # Pass the pre-computed context
        )
        
        # Send to intelligent specialist agents (they will select APIs)
        try:
            # Use fixed names for resolution - these are the agent names
            # It's vital that these names match the 'name' given to the Agent instances below
            specialist_address = await ctx.resolve(f"intelligent_{specialist_type}")

            if specialist_address:
                await ctx.send(specialist_address, enhanced_task)
                ctx.logger.info(f"📤 COORDINATOR: Dispatched {specialist_type} to {specialist_address}")
            else:
                ctx.logger.error(f"Could not resolve address for {specialist_type}. Is agent running and configured correctly?")
        except Exception as e:
            ctx.logger.error(f"❌ Failed to dispatch {specialist_type}: {e}")

@coordinator_protocol.on_message(model=EnhancedSpecialistResult)
async def collect_enhanced_results(ctx: Context, sender: str, msg: EnhancedSpecialistResult):
    """Collect results from intelligent specialists"""
    
    ctx.logger.info(f"📥 COORDINATOR: Received {msg.specialist_type} results for {msg.request_id}")
    
    if msg.request_id in active_research:
        # Store enhanced result
        active_research[msg.request_id]['specialist_results'][msg.specialist_type] = {
            'selected_apis': msg.selected_apis,
            'api_results': msg.api_results, 
            'analysis': msg.agent_analysis,
            'confidence': msg.confidence,
            'simulation_buttons': msg.simulation_buttons, # Ensure this is always a list
            'visual_effects': msg.visual_effects
        }
        
        # Check completion
        expected = set(active_research[msg.request_id]['expected_specialists'])
        received = set(active_research[msg.request_id]['specialist_results'].keys())
        
        if received == expected: # All expected specialists have reported
            ctx.logger.info(f"✅ COORDINATOR: All intelligent specialists completed for request {msg.request_id}")
            
            final_report = await generate_enhanced_report(msg.request_id)
            completed_research[msg.request_id] = final_report
            del active_research[msg.request_id]
        elif received.issuperset(expected): # Received more than expected (e.g. retries) or all expected are there
             ctx.logger.warning(f"⚠️ COORDINATOR: Received more results than expected or duplicates for {msg.request_id}. Expected: {expected}, Received: {received}")
             # Still generate report if all expected are there. This might happen with retries or issues.
             final_report = await generate_enhanced_report(msg.request_id)
             completed_research[msg.request_id] = final_report
             del active_research[msg.request_id]
        else:
            ctx.logger.info(f"⏳ COORDINATOR: Still awaiting results for {msg.request_id}. Expected: {expected - received}")


coordinator.include(coordinator_protocol)

# =============================================================================
# INTELLIGENT SPECIALIST AGENTS (Receive full geographic context)
# =============================================================================

# CLIMATE SPECIALIST
climate_agent = Agent(
    name="intelligent_climate_specialist",
    seed="intelligent_climate_67890",
    # Explicitly define ports for local Bureau to ensure ctx.resolve works.
    port=8021, 
    endpoint=["http://127.0.0.1:8021/submit"]
)
fund_agent_if_low(climate_agent.wallet.address())

climate_protocol = Protocol("IntelligentClimateAnalysis")

@climate_agent.on_event("startup")
async def climate_startup(ctx: Context):
    ctx.logger.info("🌤️ Intelligent Climate Specialist ONLINE - Can select from 15+ APIs")

@climate_protocol.on_message(model=EnhancedSpecialistTaskRequest)
async def intelligent_climate_analysis(ctx: Context, sender: str, msg: EnhancedSpecialistTaskRequest):
    """Climate agent with intelligent API selection"""
    
    ctx.logger.info(f"🌡️ CLIMATE AGENT: Intelligent analysis for {msg.latitude}, {msg.longitude}")
    
    try:
        # STEP 1: Intelligent API selection (now uses full_geographic_context from coordinator)
        api_selection = await IntelligentAPISelector.select_optimal_apis(
            latitude=msg.latitude,
            longitude=msg.longitude,
            agent_specialty="climate_weather_atmospheric",
            priority=msg.priority,
            simulation_context=msg.simulation_context,
            full_geographic_context=msg.full_geographic_context # Pass pre-computed context
        )
        
        selected_apis = api_selection['selected_apis']
        ctx.logger.info(f"🧠 CLIMATE: Selected APIs: {selected_apis}")
        ctx.logger.info(f"🎯 REASONING: {api_selection['reasoning']}")
        
        # STEP 2: Call selected APIs
        # Added a max_timeout for the entire API call block for this specialist
        api_results = await call_multiple_apis(selected_apis, msg.latitude, msg.longitude, overall_timeout=20.0)
        
        # STEP 3: LLM synthesis
        synthesis = await synthesize_climate_data(
            api_results, msg.latitude, msg.longitude, msg.simulation_context
        )
        
        # STEP 4: Send results back to coordinator
        result = EnhancedSpecialistResult(
            request_id=msg.request_id,
            specialist_type="climate_specialist",
            selected_apis=selected_apis,
            api_results=api_results,
            agent_analysis=synthesis['analysis'],
            confidence=synthesis['confidence'],
            simulation_buttons=synthesis['simulation_buttons'], # Ensure list is always returned
            visual_effects=synthesis['visual_effects']
        )
        
        # Using coordinator.address directly as it's globally defined by Bureau
        await ctx.send(coordinator.address, result)
        
        ctx.logger.info(f"✅ CLIMATE: Analysis complete with {len(selected_apis)} APIs")
        
    except Exception as e:
        ctx.logger.error(f"❌ CLIMATE AGENT ERROR: {e}")
        # Send a failure result back to coordinator for robustness
        await ctx.send(coordinator.address, EnhancedSpecialistResult(
            request_id=msg.request_id,
            specialist_type="climate_specialist",
            selected_apis=[], api_results={}, agent_analysis=f"Error in processing: {e}",
            confidence=0.0, simulation_buttons=["Error: Climate Data Missing"], visual_effects=[]
        ))

climate_agent.include(climate_protocol)

# GEOLOGICAL SPECIALIST  
geological_agent = Agent(
    name="intelligent_geological_specialist",
    seed="intelligent_geological_54321",
    # Explicitly define ports for local Bureau to ensure ctx.resolve works.
    port=8022, 
    endpoint=["http://127.0.0.1:8022/submit"]
)
fund_agent_if_low(geological_agent.wallet.address())

geological_protocol = Protocol("IntelligentGeologicalAnalysis")

@geological_agent.on_event("startup")
async def geological_startup(ctx: Context):
    ctx.logger.info("🏔️ Intelligent Geological Specialist ONLINE - Earthquake/Volcano/Elevation APIs")

@geological_protocol.on_message(model=EnhancedSpecialistTaskRequest)
async def intelligent_geological_analysis(ctx: Context, sender: str, msg: EnhancedSpecialistTaskRequest):
    """Geological agent with intelligent API selection"""
    
    ctx.logger.info(f"🌍 GEOLOGICAL: Intelligent analysis for {msg.latitude}, {msg.longitude}")
    
    try:
        # Intelligent API selection for geological data (now uses full_geographic_context)
        api_selection = await IntelligentAPISelector.select_optimal_apis(
            latitude=msg.latitude,
            longitude=msg.longitude,
            agent_specialty="geological_seismic_volcanic_elevation",
            priority=msg.priority,
            simulation_context=msg.simulation_context,
            full_geographic_context=msg.full_geographic_context # Pass pre-computed context
        )
        
        selected_apis = api_selection['selected_apis']
        ctx.logger.info(f"🧠 GEOLOGICAL: Selected APIs: {selected_apis}")
        
        # Call geological APIs
        api_results = await call_multiple_apis(selected_apis, msg.latitude, msg.longitude, overall_timeout=20.0)
        
        # Synthesize geological data
        synthesis = await synthesize_geological_data(
            api_results, msg.latitude, msg.longitude, msg.simulation_context
        )
        
        result = EnhancedSpecialistResult(
            request_id=msg.request_id,
            specialist_type="geological_specialist",
            selected_apis=selected_apis,
            api_results=api_results,
            agent_analysis=synthesis['analysis'],
            confidence=synthesis['confidence'],
            simulation_buttons=synthesis['simulation_buttons'], # Ensure list is always returned
            visual_effects=synthesis['visual_effects']
        )
        
        await ctx.send(coordinator.address, result)
        
        ctx.logger.info(f"✅ GEOLOGICAL: Analysis complete")
        
    except Exception as e:
        ctx.logger.error(f"❌ GEOLOGICAL AGENT ERROR: {e}")
        # Send a failure result back to coordinator for robustness
        await ctx.send(coordinator.address, EnhancedSpecialistResult(
            request_id=msg.request_id,
            specialist_type="geological_specialist",
            selected_apis=[], api_results={}, agent_analysis=f"Error in processing: {e}",
            confidence=0.0, simulation_buttons=["Error: Geological Data Missing"], visual_effects=[]
        ))

geological_agent.include(geological_protocol)

# ENVIRONMENTAL SPECIALIST
environmental_agent = Agent(
    name="intelligent_environmental_specialist", 
    seed="intelligent_environmental_98765",
    # Explicitly define ports for local Bureau to ensure ctx.resolve works.
    port=8023, 
    endpoint=["http://127.0.0.1:8023/submit"]
)
fund_agent_if_low(environmental_agent.wallet.address())

environmental_protocol = Protocol("IntelligentEnvironmentalAnalysis")

@environmental_agent.on_event("startup")
async def environmental_startup(ctx: Context):
    ctx.logger.info("🌿 Intelligent Environmental Specialist ONLINE - Fire/Water/Air/Ocean APIs")

@environmental_protocol.on_message(model=EnhancedSpecialistTaskRequest)
async def intelligent_environmental_analysis(ctx: Context, sender: str, msg: EnhancedSpecialistTaskRequest):
    """Environmental agent with intelligent API selection"""
    
    ctx.logger.info(f"🌊 ENVIRONMENTAL: Intelligent analysis for {msg.latitude}, {msg.longitude}")
    
    try:
        # Intelligent API selection for environmental data (now uses full_geographic_context)
        api_selection = await IntelligentAPISelector.select_optimal_apis(
            latitude=msg.latitude,
            longitude=msg.longitude, 
            agent_specialty="environmental_fire_water_air_ocean",
            priority=msg.priority,
            simulation_context=msg.simulation_context,
            full_geographic_context=msg.full_geographic_context # Pass pre-computed context
        )
        
        selected_apis = api_selection['selected_apis']
        ctx.logger.info(f"🧠 ENVIRONMENTAL: Selected APIs: {selected_apis}")
        
        # Call environmental APIs
        api_results = await call_multiple_apis(selected_apis, msg.latitude, msg.longitude, overall_timeout=20.0)
        
        # Synthesize environmental data
        synthesis = await synthesize_environmental_data(
            api_results, msg.latitude, msg.longitude, msg.simulation_context
        )
        
        result = EnhancedSpecialistResult(
            request_id=msg.request_id,
            specialist_type="environmental_specialist",
            selected_apis=selected_apis,
            api_results=api_results,
            agent_analysis=synthesis['analysis'],
            confidence=synthesis['confidence'],
            simulation_buttons=synthesis['simulation_buttons'], # Ensure list is always returned
            visual_effects=synthesis['visual_effects']
        )
        
        await ctx.send(coordinator.address, result)
        
        ctx.logger.info(f"✅ ENVIRONMENTAL: Analysis complete")
        
    except Exception as e:
        ctx.logger.error(f"❌ ENVIRONMENTAL AGENT ERROR: {e}")
        # Send a failure result back to coordinator for robustness
        await ctx.send(coordinator.address, EnhancedSpecialistResult(
            request_id=msg.request_id,
            specialist_type="environmental_specialist",
            selected_apis=[], api_results={}, agent_analysis=f"Error in processing: {e}",
            confidence=0.0, simulation_buttons=["Error: Environmental Data Missing"], visual_effects=[]
        ))

environmental_agent.include(environmental_protocol)

# =============================================================================
# MULTI-API CALLING FUNCTIONS (Optimized timeouts)
# =============================================================================

async def call_multiple_apis(selected_apis: List[str], latitude: float, longitude: float, overall_timeout: float = 20.0) -> Dict:
    """Call multiple APIs in parallel and return results, with an overall timeout."""
    
    results = {}
    
    async def call_single_api(api_name: str):
        try:
            data = None # Initialize data to None
            # IMPORTANT: All API call functions from FREE_API_REGISTRY should be handled here.
            # Make sure to implement actual API calls for all 15+ if not already.
            if api_name == "openweather_current":
                data = await call_openweather_api(latitude, longitude)
            elif api_name == "openweather_forecast":
                data = await call_openweather_forecast_api(latitude, longitude)
            elif api_name == "open_meteo":
                data = await call_open_meteo_api(latitude, longitude)
            elif api_name == "usgs_earthquake":
                data = await call_earthquake_api(latitude, longitude)
            elif api_name == "volcano_discovery":
                data = await call_volcano_discovery_api(latitude, longitude)
            elif api_name == "elevation_api":
                data = await call_elevation_api(latitude, longitude)
            elif api_name == "nasa_firms":
                data = await call_fire_api(latitude, longitude)
            elif api_name == "usgs_water":
                data = await call_water_api(latitude, longitude)
            elif api_name == "air_quality_waqi":
                data = await call_air_quality_api(latitude, longitude)
            elif api_name == "noaa_tides":
                data = await call_tides_api(latitude, longitude)
            elif api_name == "marine_weather":
                data = await call_marine_weather_api(latitude, longitude)
            elif api_name == "landsat_api":
                data = await call_landsat_api(latitude, longitude)
            elif api_name == "sentinel_hub":
                data = await call_sentinel_hub_api(latitude, longitude)
            elif api_name == "severe_weather":
                data = await call_severe_weather_api(latitude, longitude)
            elif api_name == "global_disaster":
                data = await call_global_disaster_api(latitude, longitude)
            else:
                # Fallback for any API not explicitly handled above (e.g., if new ones are added)
                print(f"⚠️ MOCK: Unimplemented API '{api_name}' called. Returning mock data.")
                data = {"success": True, "api_name": api_name, "mock_data": f"Mock data for {api_name}"}
            
            if data is not None: # Only add if data was successfully assigned
                results[api_name] = data
            
        except Exception as e:
            results[api_name] = {"success": False, "error": str(e), "api_name": api_name}
    
    # Call APIs in parallel with an overall timeout for the entire block
    tasks = [call_single_api(api_name) for api_name in selected_apis]
    try:
        await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=overall_timeout)
    except asyncio.TimeoutError:
        print(f"⚠️ API calls for specialist timed out after {overall_timeout} seconds. Partial results may be available.")
        # Ensure any partial results are still captured in the `results` dict.
    
    return results

# =============================================================================
# FREE API IMPLEMENTATIONS (Optimized timeouts & SSL context)
# IMPORTANT: Many of these are placeholders/mocks. You need to implement
# their actual API calls if you want real data from all 15+.
# =============================================================================

# --- Individual API call functions with updated timeouts and SSL context ---
async def call_openweather_api(latitude: float, longitude: float):
    # This key is only a demo, replace it with your actual OpenWeather API key
    # You need to get a free API key from openweathermap.org
    OPENWEATHER_API_KEY = "0453464a2222d955db9b8a5f6043c371" 
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            async with session.get(url, timeout=7) as response: # Tighter timeout
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True, "api_name": "openweather_current", "temperature": data["main"]["temp"],
                        "humidity": data["main"]["humidity"], "description": data["weather"][0]["description"],
                        "wind_speed": data["wind"]["speed"], "pressure": data["main"]["pressure"], "location": data["name"]
                    }
    except Exception as e: print(f"OpenWeather API error: {e}")
    return {"success": False, "api_name": "openweather_current"}

async def call_openweather_forecast_api(latitude: float, longitude: float):
    OPENWEATHER_API_KEY = "0453464a2222d955db9b8a5f6043c371" # Replace with your key
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            async with session.get(url, timeout=10) as response: # Tighter timeout
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True, "api_name": "openweather_forecast", "city_name": data["city"]["name"],
                        "forecast_list": [{"dt": item["dt"], "temp": item["main"]["temp"], "description": item["weather"][0]["description"]} for item in data["list"][:5]] # Get first 5 forecasts
                    }
    except Exception as e: print(f"OpenWeather Forecast API error: {e}")
    return {"success": False, "api_name": "openweather_forecast"}

async def call_open_meteo_api(latitude: float, longitude: float):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&hourly=temperature_2m,precipitation,windspeed_10m"
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            async with session.get(url, timeout=7) as response: # Tighter timeout
                if response.status == 200:
                    data = await response.json()
                    current = data["current_weather"]
                    return {
                        "success": True, "api_name": "open_meteo", "temperature": current["temperature"],
                        "wind_speed": current["windspeed"], "wind_direction": current["winddirection"],
                        "weather_code": current["weathercode"], "hourly_forecast": data["hourly"]
                    }
    except Exception as e: print(f"Open-Meteo API error: {e}")
    return {"success": False, "api_name": "open_meteo"}

async def call_earthquake_api(latitude: float, longitude: float):
    min_lat, max_lat = latitude - 1, latitude + 1
    min_lon, max_lon = longitude - 1, longitude + 1
    url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2024-01-01&minlatitude={min_lat}&maxlatitude={max_lat}&minlongitude={min_lon}&maxlongitude={max_lon}"
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            async with session.get(url, timeout=10) as response: # Tighter timeout
                if response.status == 200:
                    data = await response.json()
                    earthquakes = data.get("features", [])
                    earthquake_count = len(earthquakes)
                    max_magnitude = max([eq["properties"]["mag"] for eq in earthquakes if eq["properties"]["mag"]], default=0)
                    return {
                        "success": True, "api_name": "usgs_earthquake", "earthquake_count": earthquake_count,
                        "max_magnitude": max_magnitude, "seismic_risk": "high" if max_magnitude > 4.0 else "moderate" if max_magnitude > 2.0 else "low",
                        "recent_activity": earthquake_count > 0
                    }
    except Exception as e: print(f"Earthquake API error: {e}")
    return {"success": False, "api_name": "usgs_earthquake"}

async def call_volcano_discovery_api(latitude: float, longitude: float):
    # --- MOCK / PLACEHOLDER ---
    print(f"🌋 MOCK: Calling Volcano Discovery API for {latitude}, {longitude}")
    await asyncio.sleep(0.5) # Simulate network delay
    return {
        "success": True,
        "api_name": "volcano_discovery",
        "volcano_activity": "low",
        "nearby_volcanoes": 0,
        "eruption_risk": "very_low"
    }

async def call_elevation_api(latitude: float, longitude: float):
    url = f"https://api.open-elevation.com/api/v1/lookup?locations={latitude},{longitude}"
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            async with session.get(url, timeout=7) as response: # Tighter timeout
                if response.status == 200:
                    data = await response.json()
                    elevation = data["results"][0]["elevation"]
                    return {
                        "success": True, "api_name": "elevation_api", "elevation_meters": elevation,
                        "elevation_category": "high" if elevation > 1000 else "moderate" if elevation > 100 else "low",
                        "terrain_type": "mountain" if elevation > 1500 else "hill" if elevation > 300 else "flat"
                    }
    except Exception as e: print(f"Elevation API error: {e}")
    return {"success": False, "api_name": "elevation_api"}

async def call_fire_api(latitude: float, longitude: float):
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/c6f747e9d6b9e64f8d9c3e7e5b8c3b5a/VIIRS_SNPP_NRT/{longitude-0.5},{latitude-0.5},{longitude+0.5},{latitude+0.5}/7"
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            async with session.get(url, timeout=10) as response: # Tighter timeout
                if response.status == 200:
                    csv_data = await response.text()
                    fire_count = len(csv_data.strip().split('\n')) - 1 if csv_data.strip() else 0
                    fire_risk = min(fire_count / 2.0 + 2.0, 5.0) if fire_count > 0 else 1.0
                    return {
                        "success": True, "api_name": "nasa_firms", "fire_count": fire_count,
                        "fire_risk": fire_risk, "fire_season": "high" if fire_risk > 3.0 else "moderate" if fire_risk > 2.0 else "low"
                    }
    except Exception as e: print(f"Fire API error: {e}")
    return {"success": False, "api_name": "nasa_firms"}

async def call_water_api(latitude: float, longitude: float):
    bbox = f"{longitude-0.5},{latitude-0.5},{longitude+0.5},{latitude+0.5}"
    url = f"https://waterservices.usgs.gov/nwis/iv/?format=json&bbox={bbox}&parameterCd=00060&siteStatus=active"
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            async with session.get(url, timeout=10) as response: # Tighter timeout
                if response.status == 200:
                    data = await response.json()
                    site_count = len(data.get('value', {}).get('timeSeries', []))
                    flood_risk = 3.5 if site_count > 5 else (2.5 if site_count > 0 else 1.5)
                    return {
                        "success": True, "api_name": "usgs_water", "monitoring_sites": site_count,
                        "flood_risk": flood_risk, "water_availability": "monitored" if site_count > 0 else "unmonitored"
                    }
    except Exception as e: print(f"Water API error: {e}")
    return {"success": False, "api_name": "usgs_water"}

async def call_tides_api(latitude: float, longitude: float):
    # --- MOCK / PLACEHOLDER ---
    url = f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?date=latest&station=8454000&product=water_level&datum=MLLW&units=metric&time_zone=gmt&format=json" # Mock station
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            async with session.get(url, timeout=7) as response: # Tighter timeout
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True, "api_name": "noaa_tides", "coastal_access": True,
                        "tide_data_available": len(data.get('data', [])) > 0, "sea_level_concern": "monitor" if abs(latitude) < 45 else "low"
                    }
    except Exception as e: print(f"Tides API error: {e}")
    return {"success": False, "api_name": "noaa_tides"}

async def call_air_quality_api(latitude: float, longitude: float):
    token = "demo" 
    url = f"https://api.waqi.info/feed/geo:{latitude};{longitude}/?token={token}"
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            async with session.get(url, timeout=7) as response: # Tighter timeout
                if response.status == 200:
                    data = await response.json()
                    if data["status"] == "ok":
                        aqi = data["data"]["aqi"]
                        return {
                            "success": True, "api_name": "air_quality_waqi", "aqi": aqi,
                            "air_quality": "good" if aqi < 50 else "moderate" if aqi < 100 else "unhealthy",
                            "pollution_level": aqi / 100.0
                        }
    except Exception as e: print(f"Air Quality API error: {e}")
    return {"success": False, "api_name": "air_quality_waqi"}

async def call_severe_weather_api(latitude: float, longitude: float):
    url = f"https://api.weather.gov/alerts/active?point={latitude},{longitude}"
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            async with session.get(url, timeout=7) as response: # Tighter timeout
                if response.status == 200:
                    data = await response.json()
                    alerts = data.get("features", [])
                    return {
                        "success": True, "api_name": "severe_weather", "active_alerts": len(alerts),
                        "has_warnings": len(alerts) > 0, "alert_types": [alert["properties"]["event"] for alert in alerts[:3]]
                    }
    except Exception as e: print(f"Severe Weather API error: {e}")
    return {"success": False, "api_name": "severe_weather"}

async def call_global_disaster_api(latitude: float, longitude: float):
    # --- MOCK / PLACEHOLDER ---
    print(f"🌍 MOCK: Calling Global Disaster API for {latitude}, {longitude}")
    await asyncio.sleep(0.5)
    return {"success": True, "api_name": "global_disaster", "disasters_nearby": 0}

async def call_marine_weather_api(latitude: float, longitude: float):
    url = f"https://marine-api.open-meteo.com/v1/marine?latitude={latitude}&longitude={longitude}&hourly=wave_height,wave_direction,wave_period"
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            async with session.get(url, timeout=7) as response: # Tighter timeout
                if response.status == 200:
                    data = await response.json()
                    hourly = data.get('hourly', {})
                    return {
                        "success": True, "api_name": "marine_weather", "wave_height": hourly.get('wave_height', [0])[0],
                        "wave_direction": hourly.get('wave_direction', [0])[0], "wave_period": hourly.get('wave_period', [0])[0]
                    }
    except Exception as e: print(f"Marine Weather API error: {e}")
    return {"success": False, "api_name": "marine_weather"}

async def call_landsat_api(latitude: float, longitude: float):
    # --- MOCK / PLACEHOLDER ---
    print(f"🛰️ MOCK: Calling Landsat API for {latitude}, {longitude}")
    await asyncio.sleep(0.5)
    return {"success": True, "api_name": "landsat_api", "imagery_available": True, "last_updated_days_ago": 30}

async def call_sentinel_hub_api(latitude: float, longitude: float):
    # --- MOCK / PLACEHOLDER ---
    print(f"🛰️ MOCK: Calling Sentinel Hub API for {latitude}, {longitude}")
    await asyncio.sleep(0.5)
    return {"success": True, "api_name": "sentinel_hub", "satellite_data_count": 5, "cloud_coverage_percent": 10}


# =============================================================================
# LLM SYNTHESIS FUNCTIONS (Optimized prompts)
# =============================================================================

async def analyze_detailed_geography(latitude: float, longitude: float) -> Dict:
    """LLM analyzes detailed geographic characteristics of coordinates (now done by coordinator)"""
    prompt = f"""
    Analyze the geographic characteristics for coordinates {latitude}°, {longitude}°:
    
    Determine concisely:
    1. Region type (e.g., coastal, mountain, desert, urban, arctic, tropical).
    2. Climate zone (e.g., temperate, arid, polar, subtropical).
    3. Natural hazard risks (e.g., earthquake, volcano, hurricane, flood, wildfire, drought). Be specific if common.
    4. Ecosystem type (e.g., rainforest, savanna, tundra, wetland, grassland, urbanized).
    5. Proximity to water bodies (e.g., oceanfront, lakeside, riverine, inland).
    6. Elevation category (e.g., sea_level, lowlands, hills, mountains, plateau).
    7. Special geographic features or zones (e.g., seismic_zone, volcanic_arc, major river delta, wildfire_prone_area).
    
    Respond ONLY with a JSON object:
    {{
        "region_types": ["coastal", "temperate"],
        "climate_zone": "temperate_oceanic", 
        "hazard_risks": ["earthquake", "wildfire", "flooding"],
        "ecosystem": "temperate_forest",
        "water_proximity": "coastal",
        "elevation_category": "hills",
        "special_features": ["bay_area", "seismic_zone"]
    }}
    """
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
            temperature=0.3,
            max_tokens=250 # Reduced max_tokens for quicker output
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Detailed geography analysis failed: {e}")
        return {
            "region_types": ["general"], "climate_zone": "temperate", "hazard_risks": ["general_weather"],
            "ecosystem": "mixed", "water_proximity": "inland", "elevation_category": "unknown", "special_features": []
        }


async def analyze_simulation_requirements(latitude: float, longitude: float, priority: str, full_geographic_context: Dict) -> Dict:
    """LLM determines simulation requirements for this location"""
    # Now takes full_geographic_context, reducing redundant geographic analysis
    prompt = f"""
    Analyze location {latitude}°, {longitude}° for landscape evolution simulation requirements.
    Priority: {priority}
    Full Geographic Context: {json.dumps(full_geographic_context, separators=(',', ':'))}
    
    Determine:
    1. Primary simulation type (e.g., coastal_erosion, mountain_weathering, forest_dynamics, urban_expansion, etc.).
    2. Key environmental factors that drive landscape change here.
    3. Which specialist agents are most relevant (choose from: climate_specialist, geological_specialist, environmental_specialist).
    4. Timeline of expected changes (e.g., immediate, seasonal, long-term).
    
    Respond ONLY with a JSON object:
    {{
        "simulation_type": "primary_landscape_change_type",
        "analysis": "Concise geographic analysis and reasoning.",
        "environmental_factors": ["factor1", "factor2"],
        "specialists_needed": ["climate_specialist", "geological_specialist"],
        "timeline": "change_timeline",
        "key_risks": ["risk1", "risk2"]
    }}
    """
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
            temperature=0.4,
            max_tokens=300 # Reduced max_tokens
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Simulation analysis failed: {e}")
        return {
            "simulation_type": "general_landscape_change", "analysis": "General landscape evolution analysis",
            "environmental_factors": ["weather", "geology"], "specialists_needed": ["climate_specialist", "environmental_specialist"],
            "timeline": "seasonal", "key_risks": ["climate_variability"]
        }


async def synthesize_climate_data(api_results: Dict, latitude: float, longitude: float, context: Dict) -> Dict:
    """LLM synthesizes climate data from multiple APIs"""
    # Prompt optimized for conciseness and directness
    prompt = f"""
    You are a climate specialist. Synthesize climate API data for {latitude}°, {longitude}° landscape simulation.
    Simulation Context: {json.dumps(context, separators=(',', ':'))}
    API Results: {json.dumps(api_results, indent=2, default=str, separators=(',', ':'))}
    
    Provide:
    1. Overall climate analysis for landscape evolution.
    2. Key visual effects for simulation.
    3. 3-5 UI buttons for climate scenarios.
    4. Confidence (0.0-1.0).
    
    Respond ONLY with a JSON object:
    {{
        "analysis": "Combined climate analysis.",
        "visual_effects": ["effect1", "effect2"],
        "simulation_buttons": ["Button1", "Button2"],
        "confidence": 0.85
    }}
    """
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
            temperature=0.5,
            max_tokens=200 # Reduced max_tokens
        )
        result = json.loads(response.choices[0].message.content)
        # Ensure simulation_buttons is a list, even if LLM fails
        if not isinstance(result.get("simulation_buttons"), list):
            result["simulation_buttons"] = []
        if not isinstance(result.get("visual_effects"), list):
            result["visual_effects"] = []
        return result
    except Exception as e:
        print(f"Climate synthesis failed: {e}")
        return {
            "analysis": "Climate analysis from multiple APIs failed.", "visual_effects": ["weather_change", "temperature_shift"],
            "simulation_buttons": ["Weather Change", "Climate Shift"], "confidence": 0.5
        }

async def synthesize_geological_data(api_results: Dict, latitude: float, longitude: float, context: Dict) -> Dict:
    """LLM synthesizes geological data from multiple APIs"""
    # Prompt optimized for conciseness and directness
    prompt = f"""
    You are a geological specialist. Synthesize earthquake, volcano, elevation API data for {latitude}°, {longitude}° landscape simulation.
    Simulation Context: {json.dumps(context, separators=(',', ':'))}
    API Results: {json.dumps(api_results, indent=2, default=str, separators=(',', ':'))}
    
    Provide:
    1. Geological hazard assessment for landscape evolution.
    2. Key terrain-based visual effects for simulation.
    3. 3-5 UI buttons for geological scenarios.
    4. Confidence (0.0-1.0).
    
    Respond ONLY with a JSON object:
    {{
        "analysis": "Geological analysis.",
        "visual_effects": ["effect1", "effect2"],
        "simulation_buttons": ["Button1", "Button2"],
        "confidence": 0.85
    }}
    """
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
            temperature=0.5,
            max_tokens=200 # Reduced max_tokens
        )
        result = json.loads(response.choices[0].message.content)
        # Ensure simulation_buttons is a list, even if LLM fails
        if not isinstance(result.get("simulation_buttons"), list):
            result["simulation_buttons"] = []
        if not isinstance(result.get("visual_effects"), list):
            result["visual_effects"] = []
        return result
    except Exception as e:
        print(f"Geological synthesis failed: {e}")
        return {
            "analysis": "Geological analysis from multiple APIs failed.", "visual_effects": ["terrain_shift", "elevation_change"],
            "simulation_buttons": ["Earthquake", "Erosion"], "confidence": 0.5
        }

async def synthesize_environmental_data(api_results: Dict, latitude: float, longitude: float, context: Dict) -> Dict:
    """LLM synthesizes environmental data from multiple APIs"""
    # Prompt optimized for conciseness and directness
    prompt = f"""
    You are an environmental specialist. Synthesize fire, water, air quality, ocean API data for {latitude}°, {longitude}° landscape simulation.
    Simulation Context: {json.dumps(context, separators=(',', ':'))}
    API Results: {json.dumps(api_results, indent=2, default=str, separators=(',', ':'))}
    
    Provide:
    1. Environmental impact assessment for landscape evolution.
    2. Key ecosystem-based visual effects for simulation.
    3. 3-5 UI buttons for environmental scenarios.
    4. Confidence (0.0-1.0).
    
    Respond ONLY with a JSON object:
    {{
        "analysis": "Environmental analysis.",
        "visual_effects": ["effect1", "effect2"],
        "simulation_buttons": ["Button1", "Button2"],
        "confidence": 0.85
    }}
    """
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
            temperature=0.5,
            max_tokens=200 # Reduced max_tokens
        )
        result = json.loads(response.choices[0].message.content)
        # Ensure simulation_buttons is a list, even if LLM fails
        if not isinstance(result.get("simulation_buttons"), list):
            result["simulation_buttons"] = []
        if not isinstance(result.get("visual_effects"), list):
            result["visual_effects"] = []
        return result
    except Exception as e:
        print(f"Environmental synthesis failed: {e}")
        return {
            "analysis": "Environmental analysis from multiple APIs failed.", "visual_effects": ["ecosystem_change", "pollution_impact"],
            "simulation_buttons": ["Wildfire", "Flooding"], "confidence": 0.5
        }

async def generate_enhanced_report(request_id: str) -> FinalReport:
    """Generate final enhanced report with multi-API results"""
    
    research_data = active_research[request_id]
    processing_time = time.time() - research_data['start_time']
    
    scenarios = []
    contributions = []
    all_buttons = []
    
    for specialist_type, result in research_data['specialist_results'].items():
        # Create enhanced scenarios
        scenario = {
            "label": f"Multi-API {specialist_type.replace('_', ' ').title()}",
            "type": "multi_api_analysis",
            "description": result['analysis'][:200] + "...",
            "confidence": result['confidence'],
            "source": f"Intelligent {specialist_type}",
            "selected_apis": result['selected_apis'],
            "api_count": len(result['selected_apis']),
            "visual_effects": result['visual_effects'],
            "autonomous": True
        }
        scenarios.append(scenario)
        contributions.append(f"{specialist_type}: {result['analysis'][:100]}...")
        # FIX: Ensure simulation_buttons is always a list when extending
        if isinstance(result.get('simulation_buttons'), list):
            all_buttons.extend(result['simulation_buttons'])
        else:
            print(f"⚠️ Warning: {specialist_type} did not return a list for simulation_buttons. Skipping.")

    # FIX: Ensure final_report always has a list for simulation_buttons
    final_buttons = list(set(all_buttons)) if all_buttons else ["Default Button 1", "Default Button 2"] # Provide minimum fallback
    
    return FinalReport(
        request_id=request_id,
        location=research_data['location'],
        scenarios=scenarios,
        coordinator_reasoning=research_data['simulation_context']['analysis'],
        specialist_contributions=contributions,
        simulation_buttons=final_buttons,  # Removed duplicates via set() already
        total_processing_time=processing_time
    )

# =============================================================================
# FASTAPI INTEGRATION
# =============================================================================

app = FastAPI(title="Intelligent Multi-API Landscape Evolution System")

@app.post("/analyze-location")
async def intelligent_multi_api_research(query: dict):
    """
    Intelligent multi-API landscape evolution research.
    This endpoint acts as a gateway, forwarding the request to the Coordinator Agent.
    """
    try:
        latitude = query['latitude']
        longitude = query['longitude']
        priority = query.get('research_priority', 'comprehensive')
        
        request_id = f"intelligent_req_{int(time.time())}_{latitude}_{longitude}"
        
        print(f"🚀 FastAPI: Received request {request_id} for {latitude}, {longitude}")
        
        # Create the message for the Coordinator Agent
        analysis_request = LocationAnalysisRequest(
            request_id=request_id,
            latitude=latitude,
            longitude=longitude,
            priority=priority,
            reasoning_context="Intelligent landscape evolution simulation"
        )
        
        # --- FIX: Send request to the Coordinator Agent's HTTP endpoint ---
        # FastAPI now acts as an HTTP client to its own agent network.
        # Coordinator Agent's endpoint is hardcoded based on its definition.
        # This requires the coordinator to have a defined port/endpoint.
        coordinator_endpoint_url = COORDINATOR_AGENT_ENDPOINT # Use the globally defined endpoint
        
        # We need an aiohttp session specifically for sending this request
        # using secure SSL context.
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            try:
                async with session.post(
                    coordinator_endpoint_url,
                    json=analysis_request.dict(), # Convert Pydantic model to dict for JSON payload
                    timeout=5 # Short timeout for sending the message to the agent
                ) as response:
                    response_text = await response.text()
                    if response.status != 200:
                        print(f"❌ FastAPI: Failed to send request to Coordinator. Status: {response.status}, Response: {response_text}")
                        # Raise HTTPException with the error details from the agent if possible
                        raise HTTPException(status_code=500, detail=f"Failed to dispatch to coordinator agent: {response_text}")
            except aiohttp.ClientConnectorError as ce:
                print(f"❌ FastAPI: Connection error to Coordinator Agent endpoint ({coordinator_endpoint_url}): {ce}")
                raise HTTPException(status_code=500, detail=f"Could not connect to coordinator agent. Is it running on {coordinator_endpoint_url}? Error: {ce}")
            except asyncio.TimeoutError:
                print(f"❌ FastAPI: Timeout sending request to Coordinator Agent endpoint ({coordinator_endpoint_url})")
                raise HTTPException(status_code=500, detail=f"Timeout dispatching to coordinator agent.")
            except Exception as e:
                print(f"❌ FastAPI: Unexpected error sending request to Coordinator: {e}")
                raise HTTPException(status_code=500, detail=f"Error dispatching to coordinator agent: {e}")
        
        print(f"✅ FastAPI: Dispatched request {request_id} to Coordinator Agent. Awaiting results...")

        # Give agents a reasonable time to process.
        # For actual client-facing applications, implement polling via /get-results/{request_id}.
        await asyncio.sleep(20) # Reduced from 25, can be fine-tuned.

        # Check for results in the global completed_research storage
        if request_id in completed_research:
            report = completed_research[request_id]
            return {
                "request_id": report.request_id,
                "location": report.location,
                "scenarios": report.scenarios,
                "coordinator_reasoning": report.coordinator_reasoning,
                "specialist_contributions": report.specialist_contributions,
                "simulation_buttons": report.simulation_buttons,
                "processing_time": report.total_processing_time,
                "system_type": "Intelligent Multi-API Agent Network",
                "api_count": sum(s.get('api_count', 0) for s in report.scenarios if isinstance(s, dict)),
                "intelligence": "LLM-powered API selection + Multi-source synthesis",
                "autonomy_level": "High - Agents intelligently select optimal APIs"
            }
        else:
            # If not completed in time, return a processing status
            return {
                "request_id": request_id, 
                "status": "Intelligent agents processing (may need more time)",
                "message": "Agents are intelligently selecting and calling multiple APIs. Please use /get-results/{request_id} to check for completion.",
                "system_type": "Intelligent Multi-API Agent Network"
            }
        
    except Exception as e:
        print(f"❌ FastAPI: General error in /analyze-location route: {e}")
        raise HTTPException(status_code=500, detail=f"Intelligent Agent network error: {str(e)}")

# Polling endpoint to retrieve results once agents complete processing.
@app.get("/get-results/{request_id}")
async def get_results(request_id: str):
    """Poll endpoint to retrieve results once agents complete processing."""
    if request_id in completed_research:
        report = completed_research[request_id]
        return {
            "status": "completed",
            "report": {
                "request_id": report.request_id,
                "location": report.location,
                "scenarios": report.scenarios,
                "coordinator_reasoning": report.coordinator_reasoning,
                "specialist_contributions": report.specialist_contributions,
                "simulation_buttons": report.simulation_buttons,
                "processing_time": report.total_processing_time,
                "system_type": "Intelligent Multi-API Agent Network",
                "api_count": sum(s.get('api_count', 0) for s in report.scenarios if isinstance(s, dict)),
                "intelligence": "LLM-powered API selection + Multi-source synthesis",
                "autonomy_level": "High - Agents intelligently select optimal APIs"
            }
        }
    elif request_id in active_research:
        return {
            "status": "processing",
            "message": "Agents are still working on your request."
        }
    else:
        raise HTTPException(status_code=404, detail="Request ID not found or expired.")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "system": "Intelligent Multi-API Landscape Evolution Network",
        "agents": {
            "intelligent_climate_coordinator": str(coordinator.address),
            "intelligent_climate_specialist": str(climate_agent.address),
            "intelligent_geological_specialist": str(geological_agent.address),
            "intelligent_environmental_specialist": str(environmental_agent.address)
        },
        "total_apis": len(FREE_API_REGISTRY),
        "api_types": list(set(api.specialty for api in FREE_API_REGISTRY.values())),
        "intelligence": "LLM-powered API selection per location",
        "all_apis_free": True,
        "geographic_optimization": "Location-specific API selection",
        "ssl_context_used": True # Indicate SSL context is used
    }

@app.get("/available-apis")
async def list_available_apis():
    """List all available free APIs"""
    return {
        "total_apis": len(FREE_API_REGISTRY),
        "apis": {
            name: {
                "specialty": api.specialty,
                "description": api.description,
                "reliability": api.reliability,
                "geographic_relevance": api.geographic_relevance,
                "cost": "FREE"
            }
            for name, api in FREE_API_REGISTRY.items()
        }
    }

# =============================================================================
# AGENT RUNNER
# =============================================================================

def run_intelligent_agent_network():
    """Run intelligent multi-API agent network"""
    # Create new event loop for this thread, crucial for asyncio operations in a separate thread
    asyncio.set_event_loop(asyncio.new_event_loop())
    
    from uagents import Bureau
    bureau = Bureau()
    
    # Add agents to the Bureau
    bureau.add(coordinator)
    bureau.add(climate_agent)
    bureau.add(geological_agent)
    bureau.add(environmental_agent)
    
    print(f"🤖 Starting Intelligent Multi-API Agent Network... at {time.ctime()}")
    print(f"🧠 Coordinator: {coordinator.address}") # Removed endpoint print here
    print(f"🌤️ Climate Specialist: {climate_agent.address}") # Removed endpoint print here
    print(f"🏔️ Geological Specialist: {geological_agent.address}") # Removed endpoint print here
    print(f"🌿 Environmental Specialist: {environmental_agent.address}") # Removed endpoint print here
    print(f"📡 Managing {len(FREE_API_REGISTRY)} FREE APIs with intelligent selection")
    
    # Run the Bureau, which starts the agents' event loops
    bureau.run()

if __name__ == "__main__":
    print(f"🚀 INTELLIGENT MULTI-API LANDSCAPE EVOLUTION SYSTEM - Startup at {time.ctime()}")
    print("🧠 LLM-Powered API Selection + Multi-Source Data Synthesis")
    print("📡 15+ FREE APIs with Geographic Optimization")
    print("🤖 Truly Intelligent Agent Network (Keeping the Agenticness!)")
    print("🎮 Advanced Landscape Simulation Intelligence")
    
    if GROQ_API_KEY == "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": # Check against your actual placeholder
        print("⚠️  WARNING: Add your FREE Groq API key for LLM functionality")
        print("🔗 Get your FREE key at: https://console.groq.com/")
    
    # Start intelligent agent network in background thread
    agent_thread = threading.Thread(target=run_intelligent_agent_network, daemon=True)
    agent_thread.start()
    
    # Give agents a slightly shorter time to initialize, they should be fast enough.
    print("⏳ Intelligent agents initializing... (giving 3 seconds)")
    time.sleep(3) 
    
    print("\n🌐 Starting API server on port 8080...")
    # FIX: Use the actual coordinator's endpoint URL for client communication clarity
    print(f"FastAPI will dispatch requests to Coordinator Agent's endpoint: {COORDINATOR_AGENT_ENDPOINT}")
    print("💡 For better client experience, consider polling /get-results/{request_id} after initial POST to FastAPI.")
    print("🧪 Test with POST to http://localhost:8080/analyze-location (with JSON body)")
    print("🧪 Example test POST body: {\"latitude\": 37.7749, \"longitude\": -122.4194, \"priority\": \"urgent\"}")
    print("🗺️  View available APIs: http://localhost:8080/available-apis")
    
    uvicorn.run(app, host="0.0.0.0", port=8080)