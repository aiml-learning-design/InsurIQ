import requests
from typing import Optional, Dict, Tuple
import snowflake.connector
from pydantic import BaseModel
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskType(str, Enum):
    FIRE = "fire"
    FLOOD = "flood"
    WINDSTORM = "windstorm"
    EARTHQUAKE = "earthquake"
    CONSTRUCTION = "construction"
    CLAIMS = "claims"

class RiskAssessmentResult(BaseModel):
    score: float  # Risk score between 0-5
    confidence: float  # Confidence score between 0-1
    factors: Dict[str, float]  # Contributing factors to the score
    raw_data: Dict  # Raw API response data

class RiskAPIs:
    """Central class for all external risk assessment API integrations"""

    def __init__(self, snowflake_config: Dict):
        """Initialize with Snowflake connection for claims data"""
        self.sf_conn = snowflake.connector.connect(**snowflake_config)
        self.api_config = {
            "hazardhub": {"url": "https://api.hazardhub.com/v1/risks"},
            "fema": {"url": "https://api.nationalflooddata.com/dataservice/v3/flood"},
            "attom": {"url": "https://api.attomdata.com/propertyapi/v1.0.0/property/detail"},
            "usgs": {"url": "https://earthquake.usgs.gov/ws/designmaps/asce7-16.json"},
            "overpass": {"url": "https://overpass-api.de/api/interpreter"}
        }

    def get_fire_risk(self, lat: float, lon: float, construction_type: str) -> Optional[RiskAssessmentResult]:
        """
        Calculate fire risk score (0-5) considering:
        - Proximity to fire stations
        - Wildfire risk from vegetation and housing density
        - Construction type vulnerability
        """
        try:
            # Get fire station proximity
            fire_stations = self._get_fire_stations(lat, lon)
            distance = self._calculate_closest_distance(lat, lon, fire_stations) if fire_stations else 10.0

            # Get wildfire risk factors
            wildfire_data = self._get_hazard_data(lat, lon).get('wildfire', {})

            # Calculate component scores
            distance_score = min(distance / 10, 1) * 5  # Normalize to 0-5
            wildfire_score = wildfire_data.get('score', 0) / 20  # Convert 0-100 to 0-5
            construction_factor = self._get_construction_factor(construction_type)

            # Composite score with weights
            composite_score = (distance_score * 0.4 + wildfire_score * 0.4) * construction_factor

            return RiskAssessmentResult(
                score=min(composite_score, 5),
                confidence=0.9 if fire_stations else 0.7,
                factors={
                    "fire_station_distance_km": distance,
                    "wildfire_score": wildfire_score,
                    "construction_factor": construction_factor
                },
                raw_data={"stations": fire_stations, "wildfire": wildfire_data}
            )

        except Exception as e:
            logger.error(f"Fire risk assessment failed: {e}")
            return None

    def get_flood_risk(self, lat: float, lon: float, has_basement: bool) -> Optional[RiskAssessmentResult]:
        """Calculate flood risk based on FEMA zones and basement presence"""
        try:
            flood_data = requests.get(
                self.api_config["fema"]["url"],
                headers={"X-API-KEY": "YOUR_FEMA_KEY"},
                params={"lat": lat, "lon": lon}
            ).json()

            zone_score = {
                "VE": 5, "AE": 4, "A": 3, "X": 1, "D": 2
            }.get(flood_data.get("FLD_ZONE"), 1)

            basement_penalty = 1.5 if has_basement else 1.0

            return RiskAssessmentResult(
                score=min(zone_score * basement_penalty, 5),
                confidence=0.85,
                factors={
                    "flood_zone": flood_data.get("FLD_ZONE"),
                    "basement_penalty": basement_penalty
                },
                raw_data=flood_data
            )

        except Exception as e:
            logger.error(f"Flood risk assessment failed: {e}")
            return None

    def get_windstorm_risk(self, lat: float, lon: float) -> Optional[RiskAssessmentResult]:
        """Assess hurricane, tornado, and hail risks"""
        try:
            wind_data = self._get_hazard_data(lat, lon).get('wind', {})

            return RiskAssessmentResult(
                score=max(
                    wind_data.get('hurricaneScore',0)/20,
                    wind_data.get('tornadoScore',0)/20,
                    wind_data.get('hailScore',0)/20
                ),
                confidence=0.8,
                factors={
                    "hurricane": wind_data.get('hurricaneScore',0)/20,
                    "tornado": wind_data.get('tornadoScore',0)/20,
                    "hail": wind_data.get('hailScore',0)/20
                },
                raw_data=wind_data
            )

        except Exception as e:
            logger.error(f"Windstorm risk assessment failed: {e}")
            return None

    def get_earthquake_risk(self, lat: float, lon: float) -> Optional[RiskAssessmentResult]:
        """Calculate seismic risk using USGS data"""
        try:
            quake_data = requests.get(
                self.api_config["usgs"]["url"],
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "riskCategory": "II",
                    "siteClass": "D"
                }
            ).json()

            return RiskAssessmentResult(
                score=min(quake_data.get('pga',0)*5, 5),
                confidence=0.75,
                factors={"pga": quake_data.get('pga',0)},
                raw_data=quake_data
            )

        except Exception as e:
            logger.error(f"Earthquake risk assessment failed: {e}")
            return None

    def get_construction_risk(self, address: str) -> Optional[RiskAssessmentResult]:
        """Assess property construction risk using ATTOM data"""
        try:
            prop_data = requests.get(
                self.api_config["attom"]["url"],
                params={"address": address},
                headers={"apikey": "YOUR_ATTOM_KEY"}
            ).json().get('property', {})

            building = prop_data.get('building', {})
            roof_score = {"Good": 1, "Fair": 3, "Poor": 5}.get(building.get('condition'), 3)

            return RiskAssessmentResult(
                score=roof_score,
                confidence=0.7,
                factors={
                    "roof_condition": building.get('condition'),
                    "year_built": building.get('yearBuilt')
                },
                raw_data=prop_data
            )

        except Exception as e:
            logger.error(f"Construction risk assessment failed: {e}")
            return None

    def get_claims_risk(self, lat: float, lon: float) -> Optional[RiskAssessmentResult]:
        """Check historical claims in the area"""
        try:
            cur = self.sf_conn.cursor()
            cur.execute(f"""
                SELECT COUNT(*) 
                FROM claims_history 
                WHERE ST_DISTANCE(
                    ST_MAKEPOINT({lon}, {lat}),
                    ST_MAKEPOINT(longitude, latitude)
                ) <= 5000
                AND claim_date > DATEADD(year, -5, CURRENT_DATE())
            """)
            claim_count = cur.fetchone()[0]

            return RiskAssessmentResult(
                score=min(claim_count, 5),
                confidence=0.9,
                factors={"nearby_claims": claim_count},
                raw_data={"claim_count": claim_count}
            )

        except Exception as e:
            logger.error(f"Claims risk assessment failed: {e}")
            return None

    # Helper methods
    def _get_fire_stations(self, lat: float, lon: float) -> Optional[list]:
        """Get nearby fire stations from OpenStreetMap"""
        try:
            query = f"""[out:json];node["amenity"="fire_station"](around:10000,{lat},{lon});out;"""
            response = requests.get(
                self.api_config["overpass"]["url"],
                params={"data": query}
            )
            return response.json().get('elements', [])
        except Exception as e:
            logger.warning(f"Failed to get fire stations: {e}")
            return None

    def _get_hazard_data(self, lat: float, lon: float) -> Dict:
        """Get hazard data from HazardHub API"""
        try:
            response = requests.get(
                self.api_config["hazardhub"]["url"],
                headers={"Authorization": "Bearer YOUR_HAZARDHUB_TOKEN"},
                params={"lat": lat, "lng": lon}
            )
            return response.json()
        except Exception as e:
            logger.warning(f"Failed to get hazard data: {e}")
            return {}

    def _calculate_closest_distance(self, lat: float, lon: float, stations: list) -> float:
        """Calculate distance to closest fire station in km"""
        closest = min(stations, key=lambda s: (s['lat']-lat)**2 + (s['lon']-lon)**2)
        return ((closest['lat']-lat)**2 + (closest['lon']-lon)**2)**0.5 * 111  # Convert to km

    def _get_construction_factor(self, construction_type: str) -> float:
        """Get risk multiplier based on construction type"""
        return {
            "wood": 1.2, "concrete": 0.8, "steel": 0.7,
            "masonry": 1.0, "unknown": 1.1
        }.get(construction_type.lower(), 1.0)