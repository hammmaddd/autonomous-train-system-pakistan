import time
import math
import random

# --------- Logical model, up to 3 trains on Pakistan map with fire alarms + utilities ----------

CITIES = {
    "KPK station": (34.015, 71.524),
    "Peer Swaha": (33.600, 72.900),
    "Islamabad Station": (33.738, 73.084),
    "Lahore": (31.514, 74.354),
    "Gujranwala": (32.187, 74.194),
    "Sindh": (24.860, 67.001),
}

_state = {
    "running": False,
    "last_update": time.time(),
    "trains": [],
    "total_distance": 0.0,
    "ai_efficiency": 0.0,
    "train_distances": {
        "Train 1": 0.0,
        "Train 2": 0.0,
        "Train 3": 0.0,
    },
    "train_times": {
        "Train 1": 0.0,
        "Train 2": 0.0,
        "Train 3": 0.0,
    },
    "train_costs": {
        "Train 1": 0.0,
        "Train 2": 0.0,
        "Train 3": 0.0,
    },
    "fire_alarms": set(),
    "utility_mode": "Time",   # Time | Distance | Cost
    "risk_mode": "Safety",    # Safety | Comfort
}


def _haversine_km(a, b):
    lat1, lon1 = a
    lat2, lon2 = b
    r = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    x = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(x))


def _nearest_safe_station(exclude_names):
    best_name = None
    best_dist = float("inf")
    for name, coords in CITIES.items():
        if name in exclude_names:
            continue
        if name in _state["fire_alarms"]:
            continue
        d = _haversine_km(coords, (30.65, 70.68))
        if d < best_dist:
            best_dist = d
            best_name = name
    return best_name


def _speed_for_utility():
    mode = _state["utility_mode"]
    if mode == "Time":
        base = 0.08
    elif mode == "Distance":
        base = 0.055
    else:
        base = 0.035
    jitter = random.uniform(-0.15, 0.15)
    return base * (1.0 + jitter)


def _build_train(name, start_name, dest_name, color):
    """Return one train or None. 'None' start or dest means disabled train."""
    if not start_name or start_name == "None" or start_name not in CITIES:
        return None
    if not dest_name or dest_name == "None":
        return None

    if dest_name not in CITIES or dest_name == start_name or dest_name in _state["fire_alarms"]:
        dest_name = _nearest_safe_station({start_name})

    if dest_name is None:
        return None

    sx, sy = CITIES[start_name]
    dx, dy = CITIES[dest_name]

    return {
        "name": name,
        "start_city": start_name,
        "dest_city": dest_name,
        "lat": sx,
        "lng": sy,
        "start_lat": sx,
        "start_lng": sy,
        "dest_lat": dx,
        "dest_lng": dy,
        "progress": 0.0,
        "speed": _speed_for_utility(),
        "color": color,
        "completed": False,
        "latlng": (sx, sy),
        "path": [(sx, sy)],
        "elapsed_time": 0.0,
        "cost": 0.0,
    }


def _init_trains_from_config(config: dict):
    trains = []
    colors = ["#ef4444", "#22c55e", "#3b82f6"]

    t1 = config.get("train1", {})
    t2 = config.get("train2", {})
    t3 = config.get("train3", {})

    spec = [
        ("Train 1", t1.get("start"), t1.get("dest"), colors[0]),
        ("Train 2", t2.get("start"), t2.get("dest"), colors[1]),
        ("Train 3", t3.get("start"), t3.get("dest"), colors[2]),
    ]

    for name, s_name, d_name, col in spec:
        t = _build_train(name, s_name, d_name, col)
        if t is not None:
            trains.append(t)

    return trains


def start_simulation_from_config(config: dict):
    global _state
    _state["utility_mode"] = config.get("utility_mode", "Time")
    _state["risk_mode"] = config.get("risk_mode", "Safety")

    _state["trains"] = _init_trains_from_config(config)
    _state["running"] = len(_state["trains"]) > 0
    _state["last_update"] = time.time()
    _state["total_distance"] = 0.0
    _state["train_distances"] = {k: 0.0 for k in _state["train_distances"]}
    _state["train_times"] = {k: 0.0 for k in _state["train_times"]}
    _state["train_costs"] = {k: 0.0 for k in _state["train_costs"]}

    base_eff = 0.8
    if _state["risk_mode"] == "Safety":
        base_eff += 0.1
    else:
        base_eff += 0.05
    if _state["utility_mode"] == "Time":
        base_eff += 0.03
    elif _state["utility_mode"] == "Cost":
        base_eff -= 0.02
    _state["ai_efficiency"] = max(0.0, min(base_eff, 0.99))


def reset_simulation():
    global _state
    _state["running"] = False
    _state["last_update"] = time.time()
    _state["trains"] = []
    _state["total_distance"] = 0.0
    _state["ai_efficiency"] = 0.0
    _state["train_distances"] = {k: 0.0 for k in _state["train_distances"]}
    _state["train_times"] = {k: 0.0 for k in _state["train_times"]}
    _state["train_costs"] = {k: 0.0 for k in _state["train_costs"]}


def set_fire_alarm(station_name: str, active: bool):
    if station_name not in CITIES:
        return
    if active:
        _state["fire_alarms"].add(station_name)
    else:
        _state["fire_alarms"].discard(station_name)


def _update_trains(dt: float):
    total_dist_increment = 0.0

    for t in _state["trains"]:
        if t["completed"]:
            continue

        t["progress"] += t["speed"] * dt
        if t["progress"] >= 1.0:
            t["progress"] = 1.0
            t["completed"] = True

        sx, sy = t["start_lat"], t["start_lng"]
        dx, dy = t["dest_lat"], t["dest_lng"]

        px = sx + (dx - sx) * t["progress"]
        py = sy + (dy - sy) * t["progress"]

        path_len = _haversine_km((sx, sy), (dx, dy))
        step_dist = path_len * (t["speed"] * dt)

        total_dist_increment += step_dist
        _state["train_distances"][t["name"]] += step_dist
        _state["train_times"][t["name"]] += dt
        _state["train_costs"][t["name"]] += step_dist * 0.2  # arbitrary cost per km

        t["lat"], t["lng"] = px, py
        t["latlng"] = (px, py)
        t["path"].append((px, py))
        if len(t["path"]) > 200:
            t["path"] = t["path"][-200:]

    _state["total_distance"] += total_dist_increment


def _step_if_needed():
    if not _state["running"]:
        return
    now = time.time()
    dt = now - _state["last_update"]
    _state["last_update"] = now
    dt = max(0.0, min(dt, 0.5))
    _update_trains(dt)
    if _state["trains"] and all(t.get("completed") for t in _state["trains"]):
        _state["running"] = False


def get_simulation_status():
    _step_if_needed()
    return {
        "running": _state["running"],
        "active_trains": sum(1 for t in _state["trains"] if not t["completed"]),
        "total_distance": _state["total_distance"],
        "ai_efficiency": _state["ai_efficiency"],
        "train_distances": _state["train_distances"],
        "train_times": _state["train_times"],
        "train_costs": _state["train_costs"],
        "fire_alarms": list(_state["fire_alarms"]),
        "utility_mode": _state["utility_mode"],
        "risk_mode": _state["risk_mode"],
    }


def get_trains_state():
    _step_if_needed()
    return {
        "cities": CITIES,
        "trains": _state["trains"],
        "fire_alarms": list(_state["fire_alarms"]),
    }
import time
import math
import random

# --------- Logical model, up to 3 trains on Pakistan map with fire alarms + utilities ----------

CITIES = {
    "KPK station": (34.015, 71.524),
    "Peer Swaha": (33.600, 72.900),
    "Islamabad Station": (33.738, 73.084),
    "Rawalpindi": (33.626057, 73.071442),  # nearby city for Islamabad detour [web:51]
    "Lahore": (31.514, 74.354),
    "Gujranwala": (32.187, 74.194),
    "Sindh": (24.860, 67.001),
}

# Mapping: when an alarm is raised at this station, trains targeting it should go here instead.
ALARM_REDIRECT = {
    "Islamabad Station": "Rawalpindi",
    "Rawalpindi": "Islamabad Station",
    "KPK station": "Peer Swaha",
    "Peer Swaha": "KPK station",
    "Lahore": "Gujranwala",
    "Gujranwala": "Lahore",
    "Sindh": "Gujranwala",
}

# Diesel price (PKR per litre) around Dec 2025. [web:42][web:43]
DIESEL_PRICE_PKR_PER_L = 10

# Assume train uses about 3 litres per km (rough heavy rail assumption). [web:23]
FUEL_L_PER_KM = 3.0

_state = {
    "running": False,
    "last_update": time.time(),
    "trains": [],
    "total_distance": 0.0,
    "ai_efficiency": 0.0,
    "train_distances": {
        "Train 1": 0.0,
        "Train 2": 0.0,
        "Train 3": 0.0,
    },
    "train_times": {
        "Train 1": 0.0,  # seconds
        "Train 2": 0.0,
        "Train 3": 0.0,
    },
    "train_costs": {
        "Train 1": 0.0,  # PKR
        "Train 2": 0.0,
        "Train 3": 0.0,
    },
    "fire_alarms": set(),
    "utility_mode": "Time",   # Time | Distance | Cost
    "risk_mode": "Safety",    # Safety | Comfort
}


def _haversine_km(a, b):
    lat1, lon1 = a
    lat2, lon2 = b
    r = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    x = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(x))


def _nearest_safe_station(exclude_names):
    """Fallback: nearest station not in exclude_names or alarm set."""
    best_name = None
    best_dist = float("inf")
    for name, coords in CITIES.items():
        if name in exclude_names:
            continue
        if name in _state["fire_alarms"]:
            continue
        d = _haversine_km(coords, (30.65, 70.68))
        if d < best_dist:
            best_dist = d
            best_name = name
    return best_name


def _redirect_for_alarm(station_name, start_name):
    """
    If there's an alarm at station_name, return the specific redirect station.
    If not defined, fall back to nearest safe station.
    """
    if station_name not in _state["fire_alarms"]:
        return station_name

    # specific mapping first
    target = ALARM_REDIRECT.get(station_name)
    if target and target in CITIES and target not in _state["fire_alarms"]:
        return target

    # else nearest safe station
    return _nearest_safe_station({start_name, station_name})


def _speed_for_utility():
    """Base speed fraction per second based on utility mode (Time fastest, Cost slowest)."""
    mode = _state["utility_mode"]
    if mode == "Time":
        base = 0.08
    elif mode == "Distance":
        base = 0.055
    else:  # Cost
        base = 0.035
    jitter = random.uniform(-0.15, 0.15)
    return base * (1.0 + jitter)


def _build_train(name, start_name, dest_name, color):
    """Return one train or None. 'None' start or dest means disabled train."""
    if not start_name or start_name == "None" or start_name not in CITIES:
        return None
    if not dest_name or dest_name == "None":
        return None

    # If destination has alarm (or invalid/same), redirect.
    if dest_name not in CITIES or dest_name == start_name or dest_name in _state["fire_alarms"]:
        dest_name = _redirect_for_alarm(dest_name, start_name)

    if dest_name is None or dest_name not in CITIES:
        return None

    sx, sy = CITIES[start_name]
    dx, dy = CITIES[dest_name]

    return {
        "name": name,
        "start_city": start_name,
        "dest_city": dest_name,
        "lat": sx,
        "lng": sy,
        "start_lat": sx,
        "start_lng": sy,
        "dest_lat": dx,
        "dest_lng": dy,
        "progress": 0.0,
        "speed": _speed_for_utility(),
        "color": color,
        "completed": False,
        "latlng": (sx, sy),
        "path": [(sx, sy)],
        "elapsed_time": 0.0,
        "cost": 0.0,
    }


def _init_trains_from_config(config: dict):
    trains = []
    colors = ["#ef4444", "#22c55e", "#3b82f6"]

    t1 = config.get("train1", {})
    t2 = config.get("train2", {})
    t3 = config.get("train3", {})

    spec = [
        ("Train 1", t1.get("start"), t1.get("dest"), colors[0]),
        ("Train 2", t2.get("start"), t2.get("dest"), colors[1]),
        ("Train 3", t3.get("start"), t3.get("dest"), colors[2]),
    ]

    for name, s_name, d_name, col in spec:
        t = _build_train(name, s_name, d_name, col)
        if t is not None:
            trains.append(t)

    return trains


def start_simulation_from_config(config: dict):
    global _state
    _state["utility_mode"] = config.get("utility_mode", "Time")
    _state["risk_mode"] = config.get("risk_mode", "Safety")

    _state["trains"] = _init_trains_from_config(config)
    _state["running"] = len(_state["trains"]) > 0
    _state["last_update"] = time.time()
    _state["total_distance"] = 0.0
    _state["train_distances"] = {k: 0.0 for k in _state["train_distances"]}
    _state["train_times"] = {k: 0.0 for k in _state["train_times"]}
    _state["train_costs"] = {k: 0.0 for k in _state["train_costs"]}

    base_eff = 0.8
    if _state["risk_mode"] == "Safety":
        base_eff += 0.1
    else:
        base_eff += 0.05
    if _state["utility_mode"] == "Time":
        base_eff += 0.03
    elif _state["utility_mode"] == "Cost":
        base_eff -= 0.02
    _state["ai_efficiency"] = max(0.0, min(base_eff, 0.99))


def reset_simulation():
    global _state
    _state["running"] = False
    _state["last_update"] = time.time()
    _state["trains"] = []
    _state["total_distance"] = 0.0
    _state["ai_efficiency"] = 0.0
    _state["train_distances"] = {k: 0.0 for k in _state["train_distances"]}
    _state["train_times"] = {k: 0.0 for k in _state["train_times"]}
    _state["train_costs"] = {k: 0.0 for k in _state["train_costs"]}


def set_fire_alarm(station_name: str, active: bool):
    if station_name not in CITIES:
        return
    if active:
        _state["fire_alarms"].add(station_name)
    else:
        _state["fire_alarms"].discard(station_name)


def _update_trains(dt: float):
    total_dist_increment = 0.0

    for t in _state["trains"]:
        if t["completed"]:
            continue

        t["progress"] += t["speed"] * dt
        if t["progress"] >= 1.0:
            t["progress"] = 1.0
            t["completed"] = True

        sx, sy = t["start_lat"], t["start_lng"]
        dx, dy = t["dest_lat"], t["dest_lng"]

        px = sx + (dx - sx) * t["progress"]
        py = sy + (dy - sy) * t["progress"]

        path_len = _haversine_km((sx, sy), (dx, dy))
        step_dist = path_len * (t["speed"] * dt)

        total_dist_increment += step_dist
        _state["train_distances"][t["name"]] += step_dist
        _state["train_times"][t["name"]] += dt
        # Cost = distance * fuel per km * diesel price
        _state["train_costs"][t["name"]] += step_dist * FUEL_L_PER_KM * DIESEL_PRICE_PKR_PER_L

        t["lat"], t["lng"] = px, py
        t["latlng"] = (px, py)
        t["path"].append((px, py))
        if len(t["path"]) > 200:
            t["path"] = t["path"][-200:]

    _state["total_distance"] += total_dist_increment


def _step_if_needed():
    if not _state["running"]:
        return
    now = time.time()
    dt = now - _state["last_update"]
    _state["last_update"] = now
    dt = max(0.0, min(dt, 0.5))
    _update_trains(dt)
    if _state["trains"] and all(t.get("completed") for t in _state["trains"]):
        _state["running"] = False


def get_simulation_status():
    _step_if_needed()
    return {
        "running": _state["running"],
        "active_trains": sum(1 for t in _state["trains"] if not t["completed"]),
        "total_distance": _state["total_distance"],
        "ai_efficiency": _state["ai_efficiency"],
        "train_distances": _state["train_distances"],
        "train_times": _state["train_times"],
        "train_costs": _state["train_costs"],
        "fire_alarms": list(_state["fire_alarms"]),
        "utility_mode": _state["utility_mode"],
        "risk_mode": _state["risk_mode"],
    }


def get_trains_state():
    _step_if_needed()
    return {
        "cities": CITIES,
        "trains": _state["trains"],
        "fire_alarms": list(_state["fire_alarms"]),
    }
