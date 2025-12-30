
# Autonomous Train System Pakistan
An intelligent autonomous train simulation that shows how AI can optimize train routing across Pakistan’s railway network based on passenger priorities (cost, time, or distance).

# Autonomous Train System – Pakistan Railway Simulation

Interactive **railway control panel** for Pakistan’s network, with an AI-style routing engine that simulates up to three autonomous trains moving between major cities on a live map.[file:1][file:4] The system models utility-based routing (time, distance, cost), fire alarms, and automatic detours while exposing metrics like total distance, travel time, fuel cost, and an AI efficiency score.[file:1][file:4]

## Features

- **Web-based control panel UI** with modern dashboard styling, metrics cards, and configuration panels for trains, utilities, and risk mode.[file:1]  
- **Live Leaflet map** of Pakistan with city markers (KPK Station, Peer Swaha, Islamabad Station, Rawalpindi, Lahore, Gujranwala, Sindh) and animated train markers plus trails.[file:1][file:4]  
- **Up to 3 autonomous trains** with start/destination selection; setting `None` disables a train.[file:1][file:4]  
- **Utility modes**: Time / Distance / Cost, which change the effective speed and behavior of trains (time fastest, cost slowest).[file:1][file:4]  
- **Risk modes**: Safety / Comfort that influence an AI efficiency KPI representing routing quality.[file:1][file:4]  
- **Fire alarm system**: Raise/clear alarms at stations; trains automatically redirect to predefined safe stations or nearest safe station.[file:1][file:4]  
- **Operational metrics**:
  - Active trains count and total distance (km) across all trains.[file:1][file:4]
  - Per-train distance (km), travel time (minutes), and estimated fuel cost (PKR) based on diesel price and fuel per km.[file:1][file:4]
  - AI efficiency percentage (0–99%) dependent on risk/utility configuration.[file:4]  

## Tech stack

- **Backend**
  - Python 3
  - Flask (REST-style endpoints for `/`, `/start`, `/status`, `/reset`, `/trains`, `/firealarm`).[file:3]
  - Custom simulation engine in `railway_simulation.py` using:
    - Haversine distance for city-to-city distance in km.[file:4]
    - State machine tracking running flag, train list, total distance, AI efficiency, per-train stats, fire alarms, utility and risk modes.[file:4]
    - Time-stepped updates using `time.time()` and capped `dt` to keep simulation stable.[file:4]

- **Frontend**
  - HTML5/CSS3 single-page dashboard in `main.html`.[file:1]
  - Vanilla JavaScript for:
    - Calling backend endpoints via `fetch` (start, reset, fire alarm, status, trains).[file:1][file:3]
    - Polling status and trains at fixed intervals to update UI and map.[file:1]
  - Leaflet.js and OpenStreetMap tiles for map rendering and markers/trails.[file:1]

## Project structure

.
├── app.py # Flask application and API routes.
​
├── railway_simulation.py # Core simulation logic and state.
​
├── main.html # Frontend dashboard + JS + Leaflet map.
​
└── README.md # Project documentation.

text

### Backend overview (`app.py`)

- Serves the main UI at `/` using `render_template("main.html")`.[file:3]
- Provides JSON APIs:
  - `POST /start` – accepts a JSON config with up to 3 trains, risk mode, and utility mode, then initializes the simulation.[file:3][file:4]
  - `GET /status` – returns running state, active train count, total distance, AI efficiency, per-train distances, times, and costs, and active fire alarms.[file:3][file:4]
  - `POST /reset` – stops and clears the current simulation, resetting metrics.[file:3][file:4]
  - `GET /trains` – returns city coordinates, train states (position, color, path, completion), and fire alarm locations for map rendering.[file:3][file:4]
  - `POST /firealarm` – toggles a fire alarm at a given station (activate or clear).[file:3][file:4]

### Simulation engine (`railway_simulation.py`)

Core ideas inside the engine:

- **City graph**: Dictionary of key Pakistani stations with latitude/longitude stored as `CITIES`.[file:4]  
- **Alarm redirect mapping**: `ALARM_REDIRECT` defines where trains should reroute when a specific station is under alarm (e.g., Islamabad Station ↔ Rawalpindi, Lahore ↔ Gujranwala).[file:4]  
- **Nearest safe station fallback**: If a destination is invalid or under alarm and not explicitly mapped, the engine finds the nearest safe station not under alarm.[file:4]  
- **Utility-based speed**:
  - Time mode uses a higher base speed.
  - Distance mode uses medium speed.
  - Cost mode uses lowest speed to model fuel-saving behavior.
  - Random jitter added to speed to avoid perfectly uniform motion.[file:4]
- **Cost model**:
  - Uses diesel price per litre around Dec 2025 and litres per km to estimate PKR cost per km, multiplied by distance traveled.[file:4]
- **State updates**:
  - Each train has `startcity`, `destcity`, `latlng`, `progress`, `path`, `elapsedtime`, and `cost` fields.[file:4]
  - `stepifneeded` uses real time deltas to update positions, distances, times, and costs, and stops the simulation once all trains are completed.[file:4]

## Frontend UI (`main.html`)

- **Dashboard layout**:
  - Metrics cards for active trains, total distance, AI efficiency, and speed multiplier.[file:1]
  - Per-train KPI cards for distance, time, and cost for Train 1–3.[file:1]
  - Config panel for selecting train start/destination per train (KPK station, Peer Swaha, Islamabad Station, Rawalpindi, Lahore, Gujranwala, Sindh, or None).[file:1]
  - Toggles for Utility mode (Time, Distance, Cost) and Risk mode (Safety, Comfort).[file:1]
  - Fire alarm controls for choosing an alarm station and raising/clearing alarms.[file:1]
  - Start and Reset buttons controlling the simulation lifecycle.[file:1]
- **Map panel**:
  - Leaflet map centered roughly on Pakistan with OpenStreetMap tiles.[file:1]
  - City circle markers with tooltips.[file:1]
  - Train markers colored per train (e.g., red, green, blue) and polyline trails following the path.[file:1][file:4]
  - Alarm rings around stations with active fire alarms (red circle effect).[file:1]

- **Polling logic**:
  - `/status` polled at a fixed interval to update metrics and AI status label.[file:1][file:3]
  - `/trains` polled faster to keep map animation smooth.[file:1][file:3]

## How to run locally

### Prerequisites

- Python 3.9+ installed.
- `pip` available.
- Internet access for Leaflet and OpenStreetMap tiles (used via CDN).[file:1]

### Installation

1. Clone the repository
git clone https://github.com/<your-username>/pakistan-railway-ai-simulation.git
cd pakistan-railway-ai-simulation

2. (Optional) Create and activate a virtual environment
python -m venv venv

Windows:
venv\Scripts\activate

macOS / Linux:
source venv/bin/activate

3. Install dependencies
pip install flask

text

### Run the app

Run Flask server
python app.py

text

Then open your browser and go to:

- `http://127.0.0.1:5000/` or `http://localhost:5000/`  

You should see the control panel with metrics, controls, and the Pakistan railway map.[file:1][file:3]

### Basic usage

1. Choose start and destination cities for Train 1–3 (or leave `None` to disable a train).[file:1]  
2. Select utility mode (Time / Distance / Cost) and risk mode (Safety / Comfort).[file:1]  
3. Click **Start** to begin the simulation.[file:1]  
4. Watch the trains move on the map, while metrics update in real time.[file:1][file:4]  
5. Raise a **fire alarm** on a station and see trains automatically reroute to safe alternative stations.[file:1][file:4]  
6. Click **Reset** to stop and clear the simulation.[file:1][file:3]

## Possible extensions

- Add more stations and connections across Pakistan.[file:4]  
- Introduce passenger demand or freight volume and optimize routing based on revenue.[file:4]  
- Add historical or live traffic/delay data to adjust effective speeds.[file:4]  
- Integrate a real database for persisting scenarios and results.[file:4]

## Author

- Developed by `MUHAMMAD HAMMAD SHAKOOR` as an AI-driven railway simulation project focusing on Pakistan’s network and decision-making under risk and cost tradeoffs.
>>>>>>> ae9917d (Add detailed README)
