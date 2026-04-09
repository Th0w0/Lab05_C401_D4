from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY", "")

# =========================================================
# Data Models
# =========================================================

@dataclass
class Stop:
    name: str
    desired_arrival_time: Optional[str] = None


@dataclass
class Vehicle:
    model: str
    usable_battery_kwh: float
    efficiency_kwh_per_km: float  # average energy consumption


@dataclass
class BatteryState:
    start_soc_percent: float
    min_arrival_soc_percent: float = 10.0
    min_charge_target_soc_percent: float = 20.0
    max_charge_target_soc_percent: float = 80.0


@dataclass
class Charger:
    station_id: str
    station_name: str
    power_kw: float
    price_per_kwh_vnd: float
    efficiency: float = 0.9
    address: str = ""
    city: str = ""
    province: str = ""
    country: str = "Vietnam"
    lat: Optional[float] = None
    lon: Optional[float] = None


@dataclass
class RouteInfo:
    origin: str
    destination: str
    distance_km: float
    drive_time_min: float


@dataclass
class DriveStep:
    type: str = "drive"
    origin: str = ""
    destination: str = ""
    distance_km: float = 0.0
    drive_time_min: float = 0.0
    start_soc_percent: float = 0.0
    end_soc_percent: float = 0.0
    energy_used_kwh: float = 0.0


@dataclass
class ChargeStep:
    type: str = "charge"
    station_id: str = ""
    station_name: str = ""
    arrival_soc_percent: float = 0.0
    target_soc_percent: float = 0.0
    energy_added_kwh: float = 0.0
    charging_time_min: float = 0.0
    charging_cost_vnd: float = 0.0


@dataclass
class PlannerSummary:
    trip_feasible: bool
    total_distance_km: float
    total_drive_time_min: float
    total_charging_time_min: float
    total_charging_cost_vnd: float
    final_soc_percent: float
    total_stops: int


@dataclass
class PlannerResult:
    status: str
    summary: PlannerSummary
    itinerary: List[Dict[str, Any]]
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class PlannerPolicy:
    mode: str = "balanced"  # min_time | min_cost | min_stops | balanced
    max_corridor_km: float = 15.0
    min_charger_power_kw: float = 0.0
    preferred_min_arrival_soc_percent: float = 10.0

    weight_drive_time: float = 1.0
    weight_charge_time: float = 1.0
    weight_charge_cost: float = 0.001
    weight_num_stops: float = 25.0
    weight_low_soc_risk: float = 3.0


# =========================================================
# Tool 1: Travel Time Tool
# =========================================================

import requests
from typing import Dict, Any, Optional


class TravelTimeTool:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.base_url = "https://api.geoapify.com/v1/routing"
        self.geocode_url = "https://api.geoapify.com/v1/geocode/search"
        self._coord_cache = {}

    def geocode(self, location_name: str) -> tuple[float, float]:
        if location_name in self._coord_cache:
            res = self._coord_cache[location_name]
            if isinstance(res, tuple):
                return res

        import urllib.parse
        encoded_name = urllib.parse.quote(location_name)
        url = f"{self.geocode_url}?text={encoded_name}&filter=countrycode:vn&apiKey={self.api_key}"
        
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Geocoding API error: {response.status_code}")
        
        data = response.json()
        if not data.get("features"):
            raise ValueError(f"Location not found: {location_name}")
        
        coords = data["features"][0]["geometry"]["coordinates"] # [lon, lat]
        lat, lon = float(coords[1]), float(coords[0])
        
        self._coord_cache[location_name] = (lat, lon)
        return (lat, lon)

    def _build_url(self, origin: Any, destination: Any) -> str:
        def get_lat_lon(loc):
            if isinstance(loc, (tuple, list)) and len(loc) == 2:
                return loc[0], loc[1]
            return self.geocode(str(loc))

        try:
            lat1, lon1 = get_lat_lon(origin)
            lat2, lon2 = get_lat_lon(destination)
        except Exception as e:
            raise ValueError(f"Error resolving coordinates in build_url: {str(e)}")
            
        return (
            f"{self.base_url}"
            f"?waypoints={lat1},{lon1}|{lat2},{lon2}"
            f"&mode=drive"
            f"&apiKey={self.api_key}"
        )

    def get_route_summary(self, origin: str, destination: str) -> Dict[str, float]:
        url = self._build_url(origin, destination)
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Geoapify API error: {response.text}")
        data = response.json()
        try:
            route = data["features"][0]["properties"]
            return {
                "distance_km": route["distance"] / 1000.0,
                "drive_time_min": route["time"] / 60.0,
            }
        except Exception:
            raise ValueError("Invalid response from Geoapify")

    def get_route_detail(
        self,
        origin: str,
        destination: str,
    ) -> Dict[str, Any]:
        url = self._build_url(origin, destination)
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Geoapify API error: {response.text}")
        data = response.json()
        try:
            feature = data["features"][0]
            properties = feature["properties"]
            geometry = feature["geometry"]["coordinates"]
            return {
                "distance_km": properties["distance"] / 1000.0,
                "drive_time_min": properties["time"] / 60.0,
                "geometry": geometry,
                "legs": properties.get("legs", []),
            }
        except Exception:
            raise ValueError("Invalid detailed route from Geoapify")

# =========================================================
# Tool 2: Energy Consumption Tool
# =========================================================
class EnergyConsumptionTool:
    @staticmethod
    def estimate(distance_km: float, vehicle: Vehicle) -> Dict[str, float]:
        energy_used_kwh = distance_km * vehicle.efficiency_kwh_per_km
        soc_used_percent = (energy_used_kwh / vehicle.usable_battery_kwh) * 100.0
        return {
            "energy_used_kwh": energy_used_kwh,
            "soc_used_percent": soc_used_percent,
        }

# =========================================================
# Tool 3: Charging Time Tool
# =========================================================
class ChargingTimeTool:
    @staticmethod
    def estimate(
        usable_battery_kwh: float,
        start_soc_percent: float,
        target_soc_percent: float,
        charger: Charger,
    ) -> Dict[str, float]:
        if target_soc_percent <= start_soc_percent:
            return {"energy_added_kwh": 0.0, "charging_time_min": 0.0}
        soc_delta = target_soc_percent - start_soc_percent
        energy_added_kwh = usable_battery_kwh * soc_delta / 100.0
        effective_power_kw = charger.power_kw * charger.efficiency
        if effective_power_kw <= 0:
            raise ValueError("Invalid charger effective power.")
        charging_time_hours = energy_added_kwh / effective_power_kw
        charging_time_min = charging_time_hours * 60.0
        return {
            "energy_added_kwh": energy_added_kwh,
            "charging_time_min": charging_time_min,
        }

# =========================================================
# Tool 4: Charging Cost Tool
# =========================================================
class ChargingCostTool:
    @staticmethod
    def estimate(energy_kwh: float, charger: Charger) -> Dict[str, float]:
        return {"charging_cost_vnd": energy_kwh * charger.price_per_kwh_vnd}

# =========================================================
# Tool 5: Charging Station Selector
# =========================================================
class ChargingStationSelector:
    def __init__(self, chargers_by_location: Optional[Dict[str, List[Charger]]] = None) -> None:
        self.chargers_by_location = chargers_by_location or {}

    def select_best_charger(
        self,
        current_location: str,
        required_min_power_kw: float = 0.0,
    ) -> Charger:
        key = _normalize_text(current_location)
        candidates = self.chargers_by_location.get(key, [])
        if not candidates:
            for charger_list in self.chargers_by_location.values():
                for c in charger_list:
                    blob = _normalize_text(f"{c.address} {c.city} {c.province}")
                    if key in blob:
                        candidates = charger_list
                        break
                if candidates: break
        filtered = [c for c in candidates if c.power_kw >= required_min_power_kw]
        if not filtered:
            raise ValueError(f"No charger found near {current_location}")
        filtered.sort(key=lambda c: c.power_kw, reverse=True)
        return filtered[0]

    def find_chargers_near_route(
        self,
        route_polyline: Any,
        threshold_km: float = 10.0
    ) -> List[Charger]:
        flat_points = []
        if isinstance(route_polyline, list) and len(route_polyline) > 0:
            if isinstance(route_polyline[0][0], list):
                for segment in route_polyline:
                    flat_points.extend(segment)
            else:
                flat_points = route_polyline

        all_chargers = []
        seen_ids = set()
        for charger_list in self.chargers_by_location.values():
            for c in charger_list:
                if c.station_id not in seen_ids and c.lat is not None and c.lon is not None:
                    is_near = False
                    for i in range(0, len(flat_points), 5):
                        pt = flat_points[i]
                        if len(pt) < 2: continue
                        p_lon, p_lat = pt[0], pt[1]
                        d = haversine(c.lat, c.lon, p_lat, p_lon)
                        if d <= threshold_km:
                            is_near = True
                            break
                    if is_near:
                        all_chargers.append(c)
                        seen_ids.add(c.station_id)
        return all_chargers

# =========================================================
# Main Planner (Graph-Based Dijkstra)
# =========================================================
class EVTripPlanner:
    def __init__(
        self,
        travel_time_tool: TravelTimeTool,
        energy_tool: EnergyConsumptionTool,
        charging_time_tool: ChargingTimeTool,
        charging_cost_tool: ChargingCostTool,
        station_selector: ChargingStationSelector,
    ) -> None:
        self.travel_time_tool = travel_time_tool
        self.energy_tool = energy_tool
        self.charging_time_tool = charging_time_tool
        self.charging_cost_tool = charging_cost_tool
        self.station_selector = station_selector

    def plan_trip(
        self,
        start_location: str,
        stops: List[Stop],
        vehicle: Vehicle,
        battery: BatteryState,
        policy: Optional[PlannerPolicy] = None,
    ) -> PlannerResult:
        if policy is None:
            policy = PlannerPolicy()
        warnings = []
        destination = stops[-1].name
        
        # 1. Get detailed route with polyline
        try:
            route_detail = self.travel_time_tool.get_route_detail(start_location, destination)
            polyline = route_detail["geometry"]
            print(f"🌍 TRIP FOUND: {start_location} -> {destination} ({route_detail['distance_km']:.1f} km)")
        except Exception as e:
            return self._fail(str(e), battery)

        # 2. Find chargers along route corridor
        near_chargers = self.station_selector.find_chargers_near_route(polyline, threshold_km=policy.max_corridor_km)
        print(f"📍 FOUND {len(near_chargers)} CHARGERS NEAR ROUTE CORRIDOR.")

        # 3. Geocode start and destination
        try:
            start_lat, start_lon = self.travel_time_tool.geocode(start_location)
            dest_lat, dest_lon = self.travel_time_tool.geocode(destination)
        except Exception as e:
            return self._fail(f"Geocoding failed: {str(e)}", battery)

        # 4. Graph Construction (Dijkstra)
        import heapq
        nodes = [{"name": start_location, "type": "origin", "lat": start_lat, "lon": start_lon}]
        for c in near_chargers:
            if c.power_kw >= policy.min_charger_power_kw:
                nodes.append({"name": c.station_name, "type": "charger", "lat": c.lat, "lon": c.lon, "charger": c})
        nodes.append({"name": destination, "type": "destination", "lat": dest_lat, "lon": dest_lon})
        
        n_count = len(nodes)
        best_metrics = [float("inf")] * n_count
        parents = [-1] * n_count
        soc_at_node = [0.0] * n_count
        edge_details = [None] * n_count
        
        queue = [(0.0, 0, battery.start_soc_percent)] 
        best_metrics[0] = 0.0
        soc_at_node[0] = battery.start_soc_percent
        
        while queue:
            curr_metric, u_idx, u_soc = heapq.heappop(queue)
            if curr_metric > best_metrics[u_idx]: continue
            u = nodes[u_idx]
            d_u_dest = haversine(u["lat"], u["lon"], dest_lat, dest_lon)
            
            for v_idx in range(n_count):
                if u_idx == v_idx: continue
                v = nodes[v_idx]
                d_v_dest = haversine(v["lat"], v["lon"], dest_lat, dest_lon)
                if d_v_dest >= d_u_dest and u["type"] != "origin": continue
                
                departure_soc = u_soc
                if u["type"] == "charger": departure_soc = min(100.0, battery.max_charge_target_soc_percent)
                
                max_range = (departure_soc - battery.min_arrival_soc_percent) * (vehicle.usable_battery_kwh / 100.0) / vehicle.efficiency_kwh_per_km
                if haversine(u["lat"], u["lon"], v["lat"], v["lon"]) > max_range * 1.5: continue
                
                try:
                    summary = self.travel_time_tool.get_route_summary((u["lat"], u["lon"]), (v["lat"], v["lon"]))
                    road_dist = summary["distance_km"]
                    drive_time = summary["drive_time_min"]
                except: continue
                
                energy_est = self.energy_tool.estimate(road_dist, vehicle)
                soc_needed = energy_est["soc_used_percent"] + battery.min_arrival_soc_percent
                actual_u_soc = u_soc
                charge_info = None
                charge_time = 0.0
                
                if actual_u_soc < soc_needed:
                    ch_u = u["charger"] if u["type"] == "charger" else None
                    if u["type"] == "origin":
                        try: ch_u = self.station_selector.select_best_charger(u["name"])
                        except: pass
                    if ch_u:
                        target_soc = min(100.0, battery.max_charge_target_soc_percent)
                        if target_soc >= soc_needed:
                            c_est = self.charging_time_tool.estimate(vehicle.usable_battery_kwh, actual_u_soc, target_soc, ch_u)
                            c_cost = self.charging_cost_tool.estimate(c_est["energy_added_kwh"], ch_u)
                            charge_info = {
                                "type": "charge", "station_id": ch_u.station_id, "station_name": ch_u.station_name,
                                "arrival_soc_percent": actual_u_soc, "target_soc_percent": target_soc,
                                "energy_added_kwh": c_est["energy_added_kwh"], "charging_time_min": c_est["charging_time_min"],
                                "charging_cost_vnd": c_cost["charging_cost_vnd"]
                            }
                            charge_time = c_est["charging_time_min"]
                            actual_u_soc = target_soc
                        else: continue
                    else: continue
                
                v_arrival_soc = actual_u_soc - energy_est["soc_used_percent"]
                charge_cost = charge_info["charging_cost_vnd"] if charge_info else 0.0
                num_stops = 1.0 if charge_info else 0.0
                low_soc_risk = max(0.0, policy.preferred_min_arrival_soc_percent - v_arrival_soc)
                
                if policy.mode == "min_time":
                    step_metric = drive_time + charge_time
                elif policy.mode == "min_cost":
                    step_metric = charge_cost
                elif policy.mode == "min_stops":
                    step_metric = num_stops
                else:
                    step_metric = (
                        drive_time * policy.weight_drive_time +
                        charge_time * policy.weight_charge_time +
                        charge_cost * policy.weight_charge_cost +
                        num_stops * policy.weight_num_stops +
                        low_soc_risk * policy.weight_low_soc_risk
                    )
                
                new_total_metric = curr_metric + step_metric
                
                if new_total_metric < best_metrics[v_idx]:
                    best_metrics[v_idx] = new_total_metric
                    parents[v_idx] = u_idx
                    soc_at_node[v_idx] = v_arrival_soc
                    edge_details[v_idx] = {
                        "drive": {
                            "type": "drive", "origin": u["name"], "destination": v["name"],
                            "distance_km": road_dist, "drive_time_min": drive_time,
                            "start_soc_percent": actual_u_soc, "end_soc_percent": v_arrival_soc,
                            "energy_used_kwh": energy_est["energy_used_kwh"]
                        },
                        "charge": charge_info
                    }
                    heapq.heappush(queue, (new_total_metric, v_idx, v_arrival_soc))

        dest_idx = n_count - 1
        if best_metrics[dest_idx] == float("inf"):
            return self._fail("Không tìm thấy lộ trình khả thi.", battery)
            
        final_itinerary = []
        curr = dest_idx
        while curr != 0:
            details = edge_details[curr]
            final_itinerary.append(details["drive"])
            if details["charge"]: final_itinerary.append(details["charge"])
            curr = parents[curr]
        final_itinerary.reverse()
        
        tot_dist = sum(x["distance_km"] for x in final_itinerary if x["type"] == "drive")
        tot_drive_time = sum(x["drive_time_min"] for x in final_itinerary if x["type"] == "drive")
        tot_charge_time = sum(x["charging_time_min"] for x in final_itinerary if x["type"] == "charge")
        tot_charge_cost = sum(x["charging_cost_vnd"] for x in final_itinerary if x["type"] == "charge")
        
        return PlannerResult(
            status="success",
            summary=PlannerSummary(
                trip_feasible=True, total_distance_km=round(tot_dist, 2),
                total_drive_time_min=round(tot_drive_time, 2), total_charging_time_min=round(tot_charge_time, 2),
                total_charging_cost_vnd=round(tot_charge_cost, 2), final_soc_percent=round(soc_at_node[dest_idx], 2),
                total_stops=len([x for x in final_itinerary if x["type"] == "charge"]),
            ),
            itinerary=final_itinerary, warnings=warnings, errors=[],
        )

    def _fail(self, message: str, battery: BatteryState) -> PlannerResult:
        return PlannerResult(
            status="failed",
            summary=PlannerSummary(
                trip_feasible=False, total_distance_km=0.0, total_drive_time_min=0.0,
                total_charging_time_min=0.0, total_charging_cost_vnd=0.0,
                final_soc_percent=battery.start_soc_percent, total_stops=0,
            ),
            itinerary=[], warnings=[], errors=[message],
        )

# =========================================================
# Demo Scenarios
# =========================================================
import unicodedata

def _normalize_text(text: str) -> str:
    text = text.strip().lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.replace("tp.", "thanh pho ").replace("tp ", "thanh pho ").replace(",", " ")
    return " ".join(text.split())

def haversine(lat1, lon1, lat2, lon2):
    import math
    R = 6371.0
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def build_mock_chargers() -> Dict[str, List[Charger]]:
    chargers = {
        "Ha Noi": [Charger("HN_DC_01", "VinFast Ha Noi Fast", 60, 3000, address="Số 1 Thanh Huệ Trại, Đa Phúc, Hà Nội, Vietnam", city="Hà Nội", province="Hà Nội", lat=21.23182, lon=105.86744)],
        "Thanh Hoa": [
            Charger("TH_DC_01", "VinFast Bim Son", 60, 3100, address="134 Ngõ 430 Trần Phú, phường Lam Sơn, thị xã Bỉm Sơn, Thanh Hóa, Vietnam", city="Bỉm Sơn", province="Thanh Hóa", lat=20.07097, lon=105.88590),
            Charger("TH_DC_02", "VinFast TP Thanh Hoa", 60, 3100, address="Tân Hạnh, Đông Tân, Thành phố Thanh Hóa, Thanh Hóa, Vietnam", city="Thành phố Thanh Hóa", province="Thanh Hóa", lat=19.72846, lon=105.83582),
        ],
        "Vinh": [Charger("VI_DC_01", "VinFast Vinh", 60, 3200, address="Khối 3, Phường Vinh Lộc, Nghệ An, Vietnam", city="Vinh Lộc", province="Nghệ An", lat=18.73988, lon=105.70926)],
        "Ha Tinh": [Charger("HT_DC_01", "VinFast Ha Tinh", 60, 3200, address="Số 25 Ngõ 247 Quang Trung, Trần Phú, Hà Tĩnh, Vietnam", city="Hà Tĩnh", province="Hà Tĩnh", lat=18.36854, lon=105.89462)],
        "Quang Binh": [
            Charger("QB_DC_01", "VinFast Quang Binh 1", 60, 3200, address="Thôn Vân Tiền, xã Quảng Lưu, huyện Quảng Trạch, Quảng Bình, Vietnam", city="Quảng Trạch", province="Quảng Bình", lat=17.81705, lon=106.37773),
            Charger("QB_DC_02", "VinFast Quang Binh 2", 60, 3200, address="Chòm 6, thôn Trung Minh, xã Quảng Châu, huyện Quảng Trạch, Quảng Bình, Vietnam", city="Quảng Trạch", province="Quảng Bình", lat=17.88025, lon=106.41266),
        ],
        "Hue": [
            Charger("HU_DC_01", "VinFast Hue 1", 120, 3200, address="16 Kiệt 85 Trưng Nữ Vương, Phường Phú Bài, Huế, Vietnam", city="Huế", province="Huế", lat=16.40783, lon=107.66756),
            Charger("HU_DC_02", "VinFast Hue 2", 120, 3200, address="32/72 Dương Thiệu Tước, Phường Thanh Thủy, Huế, Vietnam", city="Huế", province="Huế", lat=16.44187, lon=107.61362),
        ],
        "Da Nang": [Charger("DN_DC_01", "VinFast Da Nang", 20, 3200, address="569 H7/2 Trần Cao Vân, phường Xuân Hà, quận Thanh Khê, Đà Nẵng, Vietnam", city="Đà Nẵng", province="Đà Nẵng", lat=16.07044, lon=108.18820)],
    }
    alias_map = {"ha noi": "Ha Noi", "thanh hoa": "Thanh Hoa", "vinh": "Vinh", "ha tinh": "Ha Tinh", "quang binh": "Quang Binh", "hue": "Hue", "da nang": "Da Nang"}
    expanded = dict(chargers)
    for alias, canonical in alias_map.items():
        if canonical in chargers: expanded[alias] = chargers[canonical]
    return expanded

def create_planner() -> EVTripPlanner:
    return EVTripPlanner(
        travel_time_tool=TravelTimeTool(api_key=GEOAPIFY_API_KEY),
        energy_tool=EnergyConsumptionTool(),
        charging_time_tool=ChargingTimeTool(),
        charging_cost_tool=ChargingCostTool(),
        station_selector=ChargingStationSelector(chargers_by_location=build_mock_chargers()),
    )

def run_scenario(title: str, planner: EVTripPlanner, start_location: str, stops: List[Stop], vehicle: Vehicle, battery: BatteryState, policy: Optional[PlannerPolicy] = None) -> None:
    if policy is None:
        policy = PlannerPolicy(mode="balanced")
    print(f"\n{'='*80}\n{title} (Policy: {policy.mode})\n{'='*80}")
    result = planner.plan_trip(start_location=start_location, stops=stops, vehicle=vehicle, battery=battery, policy=policy)
    from pprint import pprint
    pprint(asdict(result))

def main() -> None:
    planner = create_planner()
    vehicle = Vehicle(model="VF 8", usable_battery_kwh=78.0, efficiency_kwh_per_km=0.19)

    run_scenario("CASE 1 - Direct trip, no charging", planner, "Ha Noi", [Stop(name="Hai Phong")], vehicle, BatteryState(start_soc_percent=90.0))
    run_scenario("CASE 2 - Need 1 charging stop", planner, "Ha Noi", [Stop(name="Thanh pho Vinh")], vehicle, BatteryState(start_soc_percent=80.0))
    run_scenario("CASE 3 - Multiple stations (Hue)", planner, "Ha Noi", [Stop(name="Huế")], vehicle, BatteryState(start_soc_percent=80.0))
    run_scenario("CASE 4 - Long distance (Da Nang)", planner, "Ha Noi", [Stop(name="Da Nang")], vehicle, BatteryState(start_soc_percent=80.0))
    run_scenario("CASE 5 - Policy: min_cost", planner, "Ha Noi", [Stop(name="Da Nang")], vehicle, BatteryState(start_soc_percent=80.0), policy=PlannerPolicy(mode="min_cost"))
    run_scenario("CASE 6 - Policy: min_stops", planner, "Ha Noi", [Stop(name="Da Nang")], vehicle, BatteryState(start_soc_percent=80.0), policy=PlannerPolicy(mode="min_stops"))
    run_scenario("CASE 7 - Policy: balanced", planner, "Ha Noi", [Stop(name="Da Nang")], vehicle, BatteryState(start_soc_percent=80.0), policy=PlannerPolicy(mode="balanced"))

if __name__ == "__main__":
    main()