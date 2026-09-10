"""
Automated unit tests for HydroMediate engine and backend logic.
"""

import sys
import os

# Ensure backend folder is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mediator_engine import MediatorEngine

def test_initialization():
    engine = MediatorEngine("test_session")
    assert engine.state.borehole_capacity == 50000.0
    assert len(engine.state.stakeholders) == 5
    assert "school" in engine.state.stakeholders
    assert engine.state.stakeholders["school"].baseline_demand == 6000.0
    print("[OK] Initialization Test Passed!")

def test_fabricated_report_probing():
    engine = MediatorEngine("test_session")
    res = engine.probe_fabricated_report()
    assert res["status"] == "probed"
    assert engine.state.report_probed is True
    # Check claim ledger updated with probed claim
    contradiction_claims = [c for c in engine.state.claims if c.contradiction_found]
    assert len(contradiction_claims) > 0
    print("[OK] Fabricated Report Probing Test Passed!")

def test_yield_shock_and_reallocation():
    engine = MediatorEngine("test_session")
    shock_res = engine.trigger_yield_shock()
    assert shock_res["status"] == "shock_applied"
    assert engine.state.borehole_capacity == 30000.0  # -40%
    
    allocs = engine.compute_allocations()
    assert sum(allocs.values()) <= 30000.0
    assert allocs["school"] > 0  # School never dismissed or zeroed!
    assert allocs["households"] >= 10000.0  # Essential drinking rights preserved
    print("[OK] 40% Yield Reduction Shock & Reallocation Test Passed!")

def test_enforceable_accord_generation():
    engine = MediatorEngine("test_session")
    engine.trigger_yield_shock()
    accord = engine.generate_enforceable_accord()
    assert accord["status"] == "BINDING & ENFORCEABLE"
    assert len(accord["stakeholder_allocations"]) == 5
    assert "accountability_and_penalty_protocol" in accord
    assert "tier_1_minor_overage" in accord["accountability_and_penalty_protocol"]
    assert "tier_2_moderate_overage_or_tampering" in accord["accountability_and_penalty_protocol"]
    assert "tier_3_severe_violation_or_unauthorized_bypass" in accord["accountability_and_penalty_protocol"]
    print("[OK] Enforceable Accord Generation Test Passed!")

if __name__ == "__main__":
    test_initialization()
    test_fabricated_report_probing()
    test_yield_shock_and_reallocation()
    test_enforceable_accord_generation()
    print("\n--- ALL BACKEND TESTS PASSED SUCCESSFULLY! ---")
