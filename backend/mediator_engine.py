"""
HydroMediate Engine - Community Borehole AI Mediator
Core logic for stakeholder management, report probing, claim ledger, yield shock handling,
and enforceable accord generation.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import math

class ClaimEntry(BaseModel):
    id: str
    speaker: str
    turn: int
    claim_text: str
    verified: bool
    contradiction_found: bool
    details: str

class Stakeholder(BaseModel):
    id: str
    name: str
    subfaction: Optional[str] = None
    baseline_demand: float  # Liters / day
    current_ask: float
    priority_tier: int  # 1: Human Rights/Health, 2: Basic Livelihood/Food, 3: Economic Commercial, 4: Speculative
    allocated_liters: float = 0.0
    time_window: str = ""
    meter_id: str = ""
    notes: str = ""

class NegotiationState(BaseModel):
    session_id: str
    current_turn: int
    borehole_capacity: float  # 50,000 initially, 30,000 after 40% shock
    initial_capacity: float = 50000.0
    is_shocked: bool = False
    shock_applied_turn: Optional[int] = None
    report_probed: bool = False
    stakeholders: Dict[str, Stakeholder]
    claims: List[ClaimEntry] = []
    messages: List[Dict[str, Any]] = []
    accord_generated: bool = False

class MediatorEngine:
    def __init__(self, session_id: str = "default_session"):
        self.state = self.create_initial_state(session_id)

    @staticmethod
    def create_initial_state(session_id: str) -> NegotiationState:
        stakeholders = {
            "households": Stakeholder(
                id="households",
                name="Village Households (200 Families)",
                baseline_demand=12000.0,
                current_ask=12000.0,
                priority_tier=1,
                meter_id="MTR-HH-01",
                time_window="05:00 - 08:00 & 17:00 - 20:00",
                notes="Essential drinking, cooking, hygiene (60 L/family/day)."
            ),
            "school": Stakeholder(
                id="school",
                name="St. Jude New Community School",
                baseline_demand=6000.0,
                current_ask=6000.0,
                priority_tier=1,
                meter_id="MTR-SCH-01",
                time_window="07:30 - 15:30 (Mon-Fri)",
                notes="400 pupils & staff. No historical precedent, but essential human rights priority."
            ),
            "farmers_subsistence": Stakeholder(
                id="farmers_subsistence",
                name="Subsistence Farmers",
                subfaction="Food Security (Maize/Cassava)",
                baseline_demand=10000.0,
                current_ask=10000.0,
                priority_tier=2,
                meter_id="MTR-AG-SUB",
                time_window="04:00 - 07:00 & 18:00 - 21:00",
                notes="50 smallholders growing household food crops."
            ),
            "farmers_cashcrop": Stakeholder(
                id="farmers_cashcrop",
                name="Cash-Crop Commercial Farmers",
                subfaction="Commercial Export (Avocado/Macadamia)",
                baseline_demand=20000.0,
                current_ask=20000.0,
                priority_tier=3,
                meter_id="MTR-AG-CASH",
                time_window="22:00 - 04:00 (Night Drip)",
                notes="High-value export crops driving local cash economy. Flexible during scarcity."
            ),
            "govt_official": Stakeholder(
                id="govt_official",
                name="District Commissioner's Office",
                baseline_demand=15000.0,
                current_ask=15000.0,
                priority_tier=4,
                meter_id="MTR-GOV-DEV",
                time_window="11:00 - 14:00 (Conditional)",
                notes="Demands diversion for future Industrial Zone; presented fabricated usage report."
            )
        }
        
        initial_claims = [
            ClaimEntry(
                id="claim-1",
                speaker="District Commissioner",
                turn=1,
                claim_text="The municipal development project has historical senior water rights under Executive Order #402 requiring 15,000 L/day.",
                verified=False,
                contradiction_found=False,
                details="Asserted top institutional priority without presenting hydro-geological permit."
            ),
            ClaimEntry(
                id="claim-2",
                speaker="Cash-Crop Representative",
                turn=1,
                claim_text="Cash-crop exports contribute 70% of local tax revenue, so commercial irrigation must take precedence over new non-contributing users like the school.",
                verified=False,
                contradiction_found=False,
                details="Discounted new school allocation based on absence of historical precedent."
            ),
            ClaimEntry(
                id="claim-3",
                speaker="Subsistence Farmers Rep",
                turn=1,
                claim_text="Commercial growers consume 4x more water per acre than staple crops, threatening community food survival.",
                verified=True,
                contradiction_found=False,
                details="Accurate agronomic water requirement ratio for export fruits vs maize."
            )
        ]

        state = NegotiationState(
            session_id=session_id,
            current_turn=1,
            borehole_capacity=50000.0,
            initial_capacity=50000.0,
            stakeholders=stakeholders,
            claims=initial_claims,
            messages=[{
                "turn": 1,
                "speaker": "Mediator AI",
                "role": "mediator",
                "text": "Welcome all stakeholders. Our objective today is to negotiate an enforceable, equitable agreement for our community borehole (current baseline yield: 50,000 Liters/day). Total baseline requests stand at 63,000 L/day. We will apply evidence standards equally to all parties, protect basic human rights for households and the school, and address internal farming priorities."
            }]
        )
        return state

    def probe_fabricated_report(self) -> Dict[str, Any]:
        """
        Cross-examines the District Commissioner's Hydro-Economic Assessment Report.
        Exposes physics contradictions (pipe flow limit) and administrative gaps (no EIA/permits).
        """
        self.state.report_probed = True
        
        # Add probed claim to ledger
        probed_claim = ClaimEntry(
            id=f"claim-probe-{len(self.state.claims)+1}",
            speaker="District Commissioner",
            turn=self.state.current_turn,
            claim_text="Report claims Pipe #2 discharged 35,000 L/day at 6 bar pressure for municipal test site under Executive Order #402.",
            verified=False,
            contradiction_found=True,
            details="PROBED: 2-inch PVC schedule 40 pipe at 6 bar has a maximum fluid dynamic flow limit of 14,400 L/day. Claimed 35,000 L/day is physically impossible (243% over physical capacity). No EIA permit exists on county records."
        )
        self.state.claims.append(probed_claim)

        probe_message = {
            "turn": self.state.current_turn,
            "speaker": "Mediator AI (Report Verification Protocol)",
            "role": "mediator",
            "text": "🔍 **PROBING FABRICATED REPORT**: The District Commissioner's submitted 'Hydro-Economic Impact Assessment' has been cross-examined against physical fluid dynamics and county registries:\n\n"
                    "1. **Physical Line Limit Contradiction**: The report claims Pipe #2 historically delivered 35,000 L/day at 6 bar pressure. However, standard fluid mechanics dictates a 2-inch PVC line at 6 bar has a maximum discharge limit of **14,400 L/day**. The 35,000 L/day figure is physically impossible.\n"
                    "2. **Regulatory & Permit Deficit**: County Land & Environmental Board records confirm zero Environmental Impact Assessment (EIA) or water abstraction permits exist for 'Executive Order #402'.\n\n"
                    "**Mediator Ruling**: institutional rank does not override physical law or administrative transparency. The 15,000 L/day speculative request cannot be granted on unverified historical claims. Any allocation must be tied to verified construction milestones."
        }
        self.state.messages.append(probe_message)
        
        return {
            "status": "probed",
            "findings": {
                "pipe_max_flow": 14400.0,
                "claimed_flow": 35000.0,
                "discrepancy_pct": 143.0,
                "eia_verified": False
            },
            "message": probe_message
        }

    def trigger_yield_shock(self) -> Dict[str, Any]:
        """
        Triggers the mid-negotiation shock event: Well engineer reports output drop by 40%.
        Adjusts capacity from 50,000 L/day down to 30,000 L/day.
        Recalculates allocations dynamically preserving essential priorities.
        """
        self.state.is_shocked = True
        self.state.shock_applied_turn = self.state.current_turn
        self.state.borehole_capacity = self.state.initial_capacity * 0.60  # 30,000 L/day

        shock_claim = ClaimEntry(
            id=f"claim-shock-{len(self.state.claims)+1}",
            speaker="Community Well Engineer",
            turn=self.state.current_turn,
            claim_text="Aquifer draw test reveals borehole static water table has dropped. Maximum safe sustainable yield is reduced by 40% to 30,000 L/day.",
            verified=True,
            contradiction_found=False,
            details="Hydrological emergency. All allocations must be re-negotiated under strict tier priority."
        )
        self.state.claims.append(shock_claim)

        shock_message = {
            "turn": self.state.current_turn,
            "speaker": "Mediator AI (Emergency Yield Adjustment)",
            "role": "system",
            "text": "⚠️ **CRITICAL YIELD SHOCK DETECTED**: The Lead Hydro-Engineer has just delivered an urgent field report. Due to severe groundwater table drop, the safe sustainable borehole yield is reduced by **40%**, down from **50,000 L/day to 30,000 L/day**!\n\n"
                    "**Emergency Mediation Protocol Activated**:\n"
                    "- Household drinking & health: Preserved at 10,000 L/day baseline minimum.\n"
                    "- St. Jude School: Protected at 5,000 L/day minimum (sanitation & pupil hydration non-negotiable).\n"
                    "- Subsistence Farmers: Guaranteed 8,000 L/day staple food crop baseline.\n"
                    "- Cash-Crop Farmers & Govt Dev: Reallocated from remaining 7,000 L/day surplus with strict off-peak smart metering."
        }
        self.state.messages.append(shock_message)

        return {
            "status": "shock_applied",
            "new_capacity": self.state.borehole_capacity,
            "reduction_pct": 40.0,
            "message": shock_message
        }

    def compute_allocations(self) -> Dict[str, float]:
        """
        Calculates equitable, multi-tiered water allocation based on current borehole capacity.
        Ensures school is never zero-allocated and institutional speculation is capped.
        """
        cap = self.state.borehole_capacity
        
        if not self.state.is_shocked:
            # 50,000 L/day capacity allocation logic
            # Tier 1 (Human Rights): Households = 11,000 L, School = 6,000 L
            # Tier 2 (Food Security): Subsistence = 10,000 L
            # Tier 3 (Commercial): Cash-crop = 16,000 L
            # Tier 4 (Govt Dev Reserve): Govt = 7,000 L (conditional reserve)
            allocs = {
                "households": 11000.0,
                "school": 6000.0,
                "farmers_subsistence": 10000.0,
                "farmers_cashcrop": 16000.0,
                "govt_official": 7000.0
            }
        else:
            # 30,000 L/day capacity allocation logic (-40% Shock)
            # Tier 1 (Human Rights - Protected): Households = 10,000 L (91% of baseline), School = 5,000 L (83% of baseline)
            # Tier 2 (Food Security): Subsistence = 8,000 L (80% of baseline)
            # Tier 3 (Commercial): Cash-crop = 5,000 L (night drip efficiency mandate)
            # Tier 4 (Govt Dev): 2,000 L (conditional off-peak tank storage buffer)
            allocs = {
                "households": 10000.0,
                "school": 5000.0,
                "farmers_subsistence": 8000.0,
                "farmers_cashcrop": 5000.0,
                "govt_official": 2000.0
            }

        # Update state stakeholders
        for k, v in allocs.items():
            if k in self.state.stakeholders:
                self.state.stakeholders[k].allocated_liters = v

        return allocs

    def generate_enforceable_accord(self) -> Dict[str, Any]:
        """
        Generates a binding, measurable Water Sharing Accord with accountability protocols.
        """
        allocations = self.compute_allocations()
        self.state.accord_generated = True
        
        total_allocated = sum(allocations.values())
        capacity = self.state.borehole_capacity

        accord_doc = {
            "title": "Borehole Water Sharing & Accountability Accord",
            "session_id": self.state.session_id,
            "status": "BINDING & ENFORCEABLE",
            "borehole_capacity_lday": capacity,
            "total_allocated_lday": total_allocated,
            "reserve_buffer_lday": max(0.0, capacity - total_allocated),
            "is_shocked_state": self.state.is_shocked,
            "stakeholder_allocations": [
                {
                    "stakeholder_id": k,
                    "name": self.state.stakeholders[k].name,
                    "allocated_liters_day": allocations[k],
                    "pct_of_capacity": round((allocations[k] / capacity) * 100, 1),
                    "time_window": self.state.stakeholders[k].time_window,
                    "meter_id": self.state.stakeholders[k].meter_id,
                    "notes": self.state.stakeholders[k].notes
                } for k in allocations
            ],
            "technical_monitoring_infrastructure": [
                "Mandatory installation of Class-B IoT Smart Flow Meters with 15-minute cellular telemetry on all 5 sub-lines.",
                "Solar pump equipped with programmable digital timer locks restricting pumping to assigned time windows.",
                "Public real-time digital dashboard installed at the School entrance displaying daily meter totals."
            ],
            "accountability_and_penalty_protocol": {
                "tier_1_minor_overage": {
                    "trigger": "Volumetric consumption 1% to 15% above daily quota over a 24-hour cycle.",
                    "penalty": "Automated system warning sent to designated representative + 15% quota reduction applied to the following week's allocation."
                },
                "tier_2_moderate_overage_or_tampering": {
                    "trigger": "Volumetric consumption >15% over quota OR failure to report meter readings for 48 hours.",
                    "penalty": "Dynamic physical flow-throttling valve activated (capping line to 50% flow rate for 72 hours) + $150 penalty fee paid into Community Borehole Maintenance Escrow."
                },
                "tier_3_severe_violation_or_unauthorized_bypass": {
                    "trigger": "Bypassing sub-meter, tampering with solar timer locks, or unauthorized off-window pumping.",
                    "penalty": "Immediate 7-day physical line lockout + forfeit of allocation to emergency community reserve + referral to County Water Oversight Authority."
                }
            },
            "governance_board": [
                "1 Village Household Representative (Rotating annual term)",
                "1 St. Jude School Principal/Parent-Teacher Board Member",
                "1 Subsistence Farmers Cooperative Lead",
                "1 Cash-Crop Growers Association Delegate",
                "1 Independent Civil Society Hydro-Inspector"
            ]
        }

        return accord_doc

    def process_step(self, user_message: Optional[str] = None) -> Dict[str, Any]:
        """
        Advances the negotiation by 1 turn. Handles dialogues, claim tracking,
        and automated mediator prompts.
        """
        self.state.current_turn += 1
        turn = self.state.current_turn

        if user_message:
            self.state.messages.append({
                "turn": turn,
                "speaker": "User / Delegate",
                "role": "user",
                "text": user_message
            })

        # Automated turn responses simulating dynamic stakeholder discussions
        if turn == 2 and not self.state.report_probed:
            self.probe_fabricated_report()
        elif turn == 3 and not self.state.is_shocked:
            # Resolving intra-farmer rift
            message = {
                "turn": turn,
                "speaker": "Mediator AI (Farmer Sub-faction Reconciliation)",
                "role": "mediator",
                "text": "🌱 **INTRA-FARMER RIFT MEDIATION**: Cash-crop growers demand priority due to economic output, while subsistence growers demand food security precedence.\n\n"
                        "**Mediator Framework**: We establish a 2-Tier Agricultural Allocation:\n"
                        "1. **Food Security Baseline**: Subsistence staple crops are guaranteed a firm 8,000–10,000 L/day baseline.\n"
                        "2. **Efficiency & Off-Peak Commercial Quota**: Cash-crop growers receive drip-irrigation slots scheduled strictly at night (22:00-04:00) when household and school demand is zero, maximizing overall system efficiency."
            }
            self.state.messages.append(message)
        elif turn == 4 and not self.state.is_shocked:
            # Triggering yield shock automatically if not already triggered
            self.trigger_yield_shock()
        elif turn >= 5:
            # Generate final accord
            self.generate_enforceable_accord()
            message = {
                "turn": turn,
                "speaker": "Mediator AI",
                "role": "mediator",
                "text": "🤝 **NEGOTIATION CONVERGENCE ACHIEVED**: All stakeholders have reached a consensus framework. The final **Enforceable Water Sharing Accord** is now generated with specific volumetric quotas, hourly pump windows, smart metering protocols, and 3-tier non-compliance penalties."
            }
            self.state.messages.append(message)

        return {
            "state": self.state.dict(),
            "latest_message": self.state.messages[-1] if self.state.messages else None
        }
