# HydroMediate - Community Borehole AI Mediator System

HydroMediate is an AI-powered multi-stakeholder negotiation mediator built to resolve high-stakes resource allocation conflicts for a shrinking community borehole.

Rather than acting as an arbitrary judge or leading an ungrounded chat, HydroMediate acts as an active, evidence-driven **Mediator**. It facilitates consensus, challenges authority tactics, exposes fabricated usage reports, tracks claim contradictions across turns, dynamically adjusts to a sudden 40% water yield drop, and produces an **Enforceable Water Accord** complete with measurable terms and graduated accountability mechanisms.

---

## Scenario Context

- **Resource**: Community Borehole (Baseline capacity: 50,000 L/day -> Depleted by 40% mid-negotiation to 30,000 L/day).
- **Stakeholders**:
  1. **Households**: Basic human rights, drinking, cooking, and sanitation.
  2. **Newly Built School**: 400 pupils needing drinking & hygiene water. Zero historical precedent, but protected against age/precedent discrimination.
  3. **Subsistence Farmers**: Smallholders growing staple food crops (high food security priority).
  4. **Cash-Crop Farmers**: Commercial avocado/macadamia growers (high economic value, internal rift with subsistence growers).
  5. **Local Government Official**: Demands water diversion for a vague "Future Commercial & Industrial Park", presenting rank and a fabricated usage report.

---

## Key Technical Features

1. **Non-Deference to Institutional Rank**: Firmly enforces procedural equality, rejecting decrees and vague authority claims.
2. **Fabricated Usage Report Prober**: Performs hydro-dynamic and economic cross-examinations, exposing pipe flow capacity limits and fake historical claims.
3. **Claim & Contradiction Audit Ledger**: Logs turn-by-turn assertions and highlights conflicting claims across time.
4. **Intra-Farmer Rift Resolution**: Separates baseline food-security crops from commercial cash-crop surplus allocations.
5. **Dynamic 40% Yield Reduction Shock**: Simulates mid-negotiation aquifer drop and recalculates allocations equitably.
6. **Enforceable Water Sharing Accord**: Generates specific L/day volumetric limits, hourly pumping schedules, IoT smart sub-metering mandates, and a 3-tier graduated non-compliance penalty protocol.

---

## Getting Started

### Backend Setup (FastAPI + Python)

1. Navigate to `backend`:
   ```powershell
   cd backend
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Option: Configure `.env` with your `GEMINI_API_KEY`:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
   *(Note: If no API key is provided, the system seamlessly runs in full deterministic heuristic simulation mode!)*

5. Start the server:
   ```powershell
   python -m uvicorn main:app --reload --port 8000
   ```

### Frontend Setup

In a second terminal window:
1. Navigate to `frontend`:
   ```powershell
   cd frontend
   ```
2. Start a simple web server:
   ```powershell
   python -m http.server 3000
   ```
3. Open `http://127.0.0.1:3000` in your web browser.

---

## API Endpoints

- `GET /` - Health check & server status.
- `POST /api/negotiation/start` - Initialize a new mediation session.
- `POST /api/negotiation/step` - Advance to the next negotiation turn.
- `POST /api/negotiation/probe_report` - Trigger cross-examination of the official's fake report.
- `POST /api/negotiation/trigger_shock` - Execute the -40% borehole yield shock event.
- `GET /api/negotiation/ledger` - Fetch the real-time claim contradiction ledger.
- `GET /api/negotiation/accord` - Generate and download the binding Enforceable Agreement.
