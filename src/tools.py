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


# =========================================================
# Tool 1: Travel Time Tool
# =========================================================

import requests
from typing import Dict, Any, Optional


class TravelTimeTool:
    def __init__(self, api_key: Optional[str] = None, route_db: Optional[Dict[tuple, Any]] = None) -> None:
        self.api_key = api_key
        self.route_db = route_db or {}
        self.base_url = "https://api.geoapify.com/v1/routing"

    def _build_url(self, origin: str, destination: str) -> str:
        return (
            f"{self.base_url}"
            f"?waypoints={origin}|{destination}"
            f"&mode=drive"
            f"&apiKey={self.api_key}"
        )

    def get_route_summary(self, origin: str, destination: str) -> Dict[str, float]:
        """
        Phase 1: Fast route summary (NO heavy geometry parsing)
        """
        if (origin, destination) in self.route_db:
            route = self.route_db[(origin, destination)]
            return {
                "distance_km": route.distance_km,
                "drive_time_min": route.drive_time_min,
            }

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
        """
        Phase 2: Detailed route (ONLY call when needed)
        Includes geometry for segmentation
        """
        if (origin, destination) in self.route_db:
            route = self.route_db[(origin, destination)]
            return {
                "distance_km": route.distance_km,
                "drive_time_min": route.drive_time_min,
                "geometry": [],
                "legs": [],
            }

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
                "geometry": geometry,  # raw polyline (list of [lon, lat])
                "legs": properties.get("legs", []),  # useful for step-level segmentation
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

    @staticmethod
    def can_reach(
        distance_km: float,
        vehicle: Vehicle,
        battery: BatteryState,
    ) -> bool:
        """
        Fast feasibility check (Phase 1)
        """
        est = EnergyConsumptionTool.estimate(distance_km, vehicle)
        required_soc = est["soc_used_percent"] + battery.min_arrival_soc_percent

        return battery.start_soc_percent >= required_soc

    @staticmethod
    def estimate_max_range_km(
        vehicle: Vehicle,
        battery: BatteryState,
    ) -> float:
        """
        Estimate usable driving range based on SOC window
        """
        usable_soc = (
            battery.max_charge_target_soc_percent
            - battery.min_arrival_soc_percent
        )

        usable_energy = vehicle.usable_battery_kwh * (usable_soc / 100.0)

        return usable_energy / vehicle.efficiency_kwh_per_km

    @staticmethod
    def estimate_num_charges(
        distance_km: float,
        vehicle: Vehicle,
        battery: BatteryState,
    ) -> int:
        """
        Heuristic: estimate number of charging stops
        """
        max_range = EnergyConsumptionTool.estimate_max_range_km(vehicle, battery)

        if max_range <= 0:
            raise ValueError("Invalid max range")

        import math

        num_segments = math.ceil(distance_km / max_range)

        # number of charges = segments - 1
        return max(0, num_segments - 1)


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
            return {
                "energy_added_kwh": 0.0,
                "charging_time_min": 0.0,
            }

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
        return {
            "charging_cost_vnd": energy_kwh * charger.price_per_kwh_vnd
        }


# =========================================================
# Optional Tool 5: Charging Station Selector
# =========================================================

class ChargingStationSelector:
    def __init__(self, chargers_by_location: Optional[Dict[str, List[Charger]]] = None) -> None:
        self.chargers_by_location = chargers_by_location or {}

    def select_best_charger(
        self,
        current_location: str,
        required_min_power_kw: float = 0.0,
    ) -> Charger:
        candidates = self.chargers_by_location.get(current_location, [])
        filtered = [c for c in candidates if c.power_kw >= required_min_power_kw]

        if not filtered:
            raise ValueError(f"No charger found near {current_location}")

        filtered.sort(key=lambda c: c.power_kw, reverse=True)
        return filtered[0]


# =========================================================
# Main Planner
# =========================================================
from dataclasses import asdict
from typing import List, Dict, Any


class EVTripPlanner:
    def __init__(
        self,
        travel_time_tool,
        energy_tool,
        charging_time_tool,
        charging_cost_tool,
        station_selector,
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
    ) -> PlannerResult:

        errors: List[str] = []
        warnings: List[str] = []
        itinerary: List[Dict[str, Any]] = []

        destination = stops[-1].name
        current_soc = battery.start_soc_percent

        # =========================================================
        # STEP 1 — Route Summary (FAST)
        # =========================================================
        try:
            summary = self.travel_time_tool.get_route_summary(
                start_location,
                destination,
            )
        except Exception as e:
            return self._fail(str(e), battery)

        total_distance = summary["distance_km"]
        total_drive_time = summary["drive_time_min"]

        # =========================================================
        # STEP 2 — Check if direct trip possible
        # =========================================================
        if self.energy_tool.can_reach(total_distance, vehicle, battery):

            energy_est = self.energy_tool.estimate(total_distance, vehicle)

            drive_step = DriveStep(
                origin=start_location,
                destination=destination,
                distance_km=total_distance,
                drive_time_min=total_drive_time,
                start_soc_percent=current_soc,
                end_soc_percent=current_soc - energy_est["soc_used_percent"],
                energy_used_kwh=energy_est["energy_used_kwh"],
            )

            itinerary.append(asdict(drive_step))

            return PlannerResult(
                status="success",
                summary=PlannerSummary(
                    trip_feasible=True,
                    total_distance_km=total_distance,
                    total_drive_time_min=total_drive_time,
                    total_charging_time_min=0.0,
                    total_charging_cost_vnd=0.0,
                    final_soc_percent=drive_step.end_soc_percent,
                    total_stops=0,
                ),
                itinerary=itinerary,
                warnings=warnings,
                errors=errors,
            )

        # =========================================================
        # STEP 3 — Estimate number of charges
        # =========================================================
        num_charges = self.energy_tool.estimate_num_charges(
            total_distance,
            vehicle,
            battery,
        )

        # =========================================================
        # STEP 4 — Get detailed route (ONLY NOW)
        # =========================================================
        try:
            route_detail = self.travel_time_tool.get_route_detail(
                start_location,
                destination,
            )
        except Exception as e:
            return self._fail(str(e), battery)

        # =========================================================
        # STEP 5 — Split into zones (based on num_charges)
        # =========================================================
        zones = self._build_zones(
            route_detail["distance_km"],
            num_charges,
        )

        # =========================================================
        # STEP 6 — Find chargers per zone
        # =========================================================
        zone_chargers = []

        for zone in zones:
            try:
                charger = self.station_selector.select_best_charger(
                    zone["approx_location"]
                )
                zone_chargers.append(charger)
            except Exception:
                warnings.append(f"No charger found for zone {zone}")
                zone_chargers.append(None)

        # =========================================================
        # STEP 7 — Build candidate path (simple linear)
        # =========================================================
        path = [start_location]

        for charger in zone_chargers:
            if charger:
                path.append(charger.station_name)

        path.append(destination)

        # =========================================================
        # STEP 8 — Validate path (SOC simulation)
        # =========================================================
        current_location = start_location
        current_soc = battery.start_soc_percent

        total_distance_km = 0.0
        total_drive_time_min = 0.0
        total_charging_time_min = 0.0
        total_charging_cost_vnd = 0.0

        for next_location in path[1:]:

            try:
                route = self.travel_time_tool.get_route_summary(
                    current_location,
                    next_location,
                )
            except Exception as e:
                errors.append(str(e))
                break

            energy_est = self.energy_tool.estimate(route["distance_km"], vehicle)

            required_soc = energy_est["soc_used_percent"] + battery.min_arrival_soc_percent

            # Charge if needed
            if current_soc < required_soc:
                try:
                    charger = self.station_selector.select_best_charger(current_location)
                except Exception as e:
                    errors.append(str(e))
                    break

                target_soc = battery.max_charge_target_soc_percent

                charge_time = self.charging_time_tool.estimate(
                    vehicle.usable_battery_kwh,
                    current_soc,
                    target_soc,
                    charger,
                )

                charge_cost = self.charging_cost_tool.estimate(
                    charge_time["energy_added_kwh"],
                    charger,
                )

                itinerary.append(asdict(ChargeStep(
                    station_id=charger.station_id,
                    station_name=charger.station_name,
                    arrival_soc_percent=current_soc,
                    target_soc_percent=target_soc,
                    energy_added_kwh=charge_time["energy_added_kwh"],
                    charging_time_min=charge_time["charging_time_min"],
                    charging_cost_vnd=charge_cost["charging_cost_vnd"],
                )))

                total_charging_time_min += charge_time["charging_time_min"]
                total_charging_cost_vnd += charge_cost["charging_cost_vnd"]

                current_soc = target_soc

            # Drive
            drive_end_soc = current_soc - energy_est["soc_used_percent"]

            itinerary.append(asdict(DriveStep(
                origin=current_location,
                destination=next_location,
                distance_km=route["distance_km"],
                drive_time_min=route["drive_time_min"],
                start_soc_percent=current_soc,
                end_soc_percent=drive_end_soc,
                energy_used_kwh=energy_est["energy_used_kwh"],
            )))

            total_distance_km += route["distance_km"]
            total_drive_time_min += route["drive_time_min"]

            current_soc = drive_end_soc
            current_location = next_location

        # =========================================================
        # FINAL RESULT
        # =========================================================
        return PlannerResult(
            status="success" if not errors else "failed",
            summary=PlannerSummary(
                trip_feasible=len(errors) == 0,
                total_distance_km=round(total_distance_km, 2),
                total_drive_time_min=round(total_drive_time_min, 2),
                total_charging_time_min=round(total_charging_time_min, 2),
                total_charging_cost_vnd=round(total_charging_cost_vnd, 2),
                final_soc_percent=round(current_soc, 2),
                total_stops=num_charges,
            ),
            itinerary=itinerary,
            warnings=warnings,
            errors=errors,
        )

    # =========================================================
    # Helpers
    # =========================================================

    def _build_zones(self, total_distance_km: float, num_charges: int):
        """
        Simple equal split zones (MVP)
        """
        zones = []
        if num_charges == 0:
            return zones

        segment_length = total_distance_km / (num_charges + 1)

        for i in range(num_charges):
            zones.append({
                "start_km": i * segment_length,
                "end_km": (i + 1) * segment_length,
                "approx_location": f"zone_{i}",  # placeholder
            })

        return zones

    def _fail(self, msg: str, battery: BatteryState):
        return PlannerResult(
            status="failed",
            summary=PlannerSummary(
                trip_feasible=False,
                total_distance_km=0.0,
                total_drive_time_min=0.0,
                total_charging_time_min=0.0,
                total_charging_cost_vnd=0.0,
                final_soc_percent=battery.start_soc_percent,
                total_stops=0,
            ),
            itinerary=[],
            errors=[msg],
        )
# =========================================================
# Demo Scenarios
# =========================================================

def build_mock_route_db() -> Dict[tuple, RouteInfo]:
    return {
        ("Ha Noi", "Hai Phong"): RouteInfo("Ha Noi", "Hai Phong", 120, 110),
        ("Ha Noi", "Thanh Hoa"): RouteInfo("Ha Noi", "Thanh Hoa", 150, 180),
        ("Thanh Hoa", "Vinh"): RouteInfo("Thanh Hoa", "Vinh", 140, 170),
        ("Ha Noi", "Vinh"): RouteInfo("Ha Noi", "Vinh", 290, 350),  # NEW
        ("Ha Noi", "Da Nang"): RouteInfo("Ha Noi", "Da Nang", 780, 900),  # NEW (long)
    }
def build_mock_chargers() -> Dict[str, List[Charger]]:
    return {
        "Ha Noi": [
            Charger("HN_DC_01", "Ha Noi Fast Charger", 60, 3000),
        ],
        "Thanh Hoa": [
            Charger("TH_DC_01", "Thanh Hoa Fast Charger", 60, 3100),
        ],
        "Nghe An": [
            Charger("NA_DC_01", "Nghe An Fast Charger", 60, 3200),
        ],
        # cố tình KHÔNG có charger ở Da Nang để test fail
    }

def create_planner() -> EVTripPlanner:
    return EVTripPlanner(
        travel_time_tool=TravelTimeTool(api_key=GEOAPIFY_API_KEY, route_db=build_mock_route_db()),
        energy_tool=EnergyConsumptionTool(),
        charging_time_tool=ChargingTimeTool(),
        charging_cost_tool=ChargingCostTool(),
        station_selector=ChargingStationSelector(chargers_by_location=build_mock_chargers()),
    )


def run_scenario(
    title: str,
    planner: EVTripPlanner,
    start_location: str,
    stops: List[Stop],
    vehicle: Vehicle,
    battery: BatteryState,
) -> None:
    print("=" * 80)
    print(title)
    print("=" * 80)

    result = planner.plan_trip(
        start_location=start_location,
        stops=stops,
        vehicle=vehicle,
        battery=battery,
    )

    print(asdict(result))
    print()

def main() -> None:
    planner = create_planner()

    vehicle = Vehicle(
        model="VF 8",
        usable_battery_kwh=78.0,
        efficiency_kwh_per_km=0.19,
    )

    # =========================================================
    # CASE 1 — Đi thẳng A → B (KHÔNG SẠC)
    # =========================================================
    battery_1 = BatteryState(start_soc_percent=90.0)

    run_scenario(
        title="CASE 1 - Direct trip, no charging",
        planner=planner,
        start_location="Ha Noi",
        stops=[Stop(name="Hai Phong")],
        vehicle=vehicle,
        battery=battery_1,
    )

    # =========================================================
    # CASE 2 — A → B cần 1 lần sạc
    # =========================================================
    battery_2 = BatteryState(start_soc_percent=35.0)

    run_scenario(
        title="CASE 2 - Need 1 charging stop",
        planner=planner,
        start_location="Ha Noi",
        stops=[Stop(name="Vinh")],
        vehicle=vehicle,
        battery=battery_2,
    )

    # =========================================================
    # CASE 3 — A → B KHÔNG có trạm sạc → FAIL
    # =========================================================
    battery_3 = BatteryState(start_soc_percent=20.0)

    run_scenario(
        title="CASE 3 - No charger available → should fail",
        planner=planner,
        start_location="Ha Noi",
        stops=[Stop(name="Da Nang")],
        vehicle=vehicle,
        battery=battery_3,
    )

    # =========================================================
    # CASE 4 — A → B cần 2 lần sạc
    # =========================================================
    battery_4 = BatteryState(start_soc_percent=25.0)

    run_scenario(
        title="CASE 4 - Need 2 charging stops",
        planner=planner,
        start_location="Ha Noi",
        stops=[Stop(name="Da Nang")],
        vehicle=vehicle,
        battery=battery_4,
    )

if __name__ == "__main__":
    main()