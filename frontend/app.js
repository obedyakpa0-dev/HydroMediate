/**
 * HydroMediate Frontend Application Logic
 */

function getApiBase() {
    if (window.HYDRO_API_URL) return window.HYDRO_API_URL;
    
    const loc = window.location;
    if (loc && loc.protocol && loc.protocol.startsWith("http")) {
        if (loc.hostname.includes("github.io")) {
            return "https://hydromediate-backend.onrender.com";
        }
        return loc.origin;
    }
    return "http://127.0.0.1:55210";
}

const API_BASE = getApiBase();
let sessionId = "default_session";
let currentState = null;

// DOM Elements
const btnStart = document.getElementById("btnStart");
const btnNextTurn = document.getElementById("btnNextTurn");
const btnProbeReport = document.getElementById("btnProbeReport");
const btnTriggerShock = document.getElementById("btnTriggerShock");
const btnViewAccord = document.getElementById("btnViewAccord");
const btnSend = document.getElementById("btnSend");
const userInput = document.getElementById("userInput");

const chatMessages = document.getElementById("chatMessages");
const turnCounter = document.getElementById("turnCounter");
const capacityLabel = document.getElementById("capacityLabel");
const shockStatusBadge = document.getElementById("shockStatusBadge");
const aiStatusBadge = document.getElementById("aiStatusBadge");
const aiLabel = document.getElementById("aiLabel");

const supplyRatioText = document.getElementById("supplyRatioText");
const progressHouseholds = document.getElementById("progressHouseholds");
const progressSchool = document.getElementById("progressSchool");
const progressSubsistence = document.getElementById("progressSubsistence");
const progressCashcrop = document.getElementById("progressCashcrop");
const progressGovt = document.getElementById("progressGovt");

const tabLedgerBtn = document.getElementById("tabLedgerBtn");
const tabAccordBtn = document.getElementById("tabAccordBtn");
const tabLedgerContent = document.getElementById("tabLedgerContent");
const tabAccordContent = document.getElementById("tabAccordContent");
const claimsList = document.getElementById("claimsList");
const accordViewer = document.getElementById("accordViewer");

// Event Listeners
document.addEventListener("DOMContentLoaded", () => {
    initSession();

    btnStart.addEventListener("click", initSession);
    btnNextTurn.addEventListener("click", () => advanceStep());
    btnProbeReport.addEventListener("click", () => probeReport());
    btnTriggerShock.addEventListener("click", () => triggerShock());
    btnViewAccord.addEventListener("click", () => showAccordTab());
    btnSend.addEventListener("click", () => sendUserMessage());

    userInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendUserMessage();
    });

    tabLedgerBtn.addEventListener("click", () => {
        tabLedgerBtn.classList.add("active");
        tabAccordBtn.classList.remove("active");
        tabLedgerContent.classList.remove("hidden");
        tabAccordContent.classList.add("hidden");
    });

    tabAccordBtn.addEventListener("click", () => {
        showAccordTab();
    });
});

async function checkApiHealth() {
    try {
        const res = await fetch(`${API_BASE}/api/health`);
        const data = await res.json();
        if (data.gemini_active) {
            aiLabel.textContent = "Gemini 3.6 Flash Active";
            aiStatusBadge.classList.add("ai-badge");
        } else {
            aiLabel.textContent = "Engine Rules Mode";
            aiStatusBadge.classList.remove("ai-badge");
        }
    } catch (err) {
        console.warn("API health check failed:", err);
    }
}

async function initSession() {
    try {
        await checkApiHealth();
        const res = await fetch(`${API_BASE}/api/negotiation/start`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: sessionId })
        });
        const data = await res.json();
        currentState = data.state;
        renderUI();
    } catch (err) {
        alert("Failed to initialize session. Make sure backend server is running at " + API_BASE);
    }
}

async function advanceStep(message = null) {
    try {
        const res = await fetch(`${API_BASE}/api/negotiation/step`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: sessionId, user_message: message })
        });
        const data = await res.json();
        currentState = data.state;
        renderUI();
    } catch (err) {
        console.error("Step failed:", err);
    }
}

async function probeReport() {
    try {
        const res = await fetch(`${API_BASE}/api/negotiation/probe_report`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: sessionId })
        });
        const data = await res.json();
        currentState = data.state;
        renderUI();
    } catch (err) {
        console.error("Probe failed:", err);
    }
}

async function triggerShock() {
    try {
        const res = await fetch(`${API_BASE}/api/negotiation/trigger_shock`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: sessionId })
        });
        const data = await res.json();
        currentState = data.state;
        renderUI();
    } catch (err) {
        console.error("Shock failed:", err);
    }
}

function sendUserMessage() {
    const text = userInput.value.trim();
    if (!text) return;
    advanceStep(text);
    userInput.value = "";
}

async function showAccordTab() {
    tabAccordBtn.classList.add("active");
    tabLedgerBtn.classList.remove("active");
    tabAccordContent.classList.remove("hidden");
    tabLedgerContent.classList.add("hidden");

    try {
        const res = await fetch(`${API_BASE}/api/negotiation/accord?session_id=${sessionId}`);
        const data = await res.json();
        renderAccord(data.accord);
    } catch (err) {
        accordViewer.innerHTML = `<p style="color: var(--danger);">Failed to load accord document.</p>`;
    }
}

function renderUI() {
    if (!currentState) return;

    // 1. Turn & Capacity
    turnCounter.textContent = `TURN: ${currentState.current_turn}`;
    const cap = currentState.borehole_capacity;
    capacityLabel.textContent = `CAPACITY: ${cap.toLocaleString()} L/DAY`;

    if (currentState.is_shocked) {
        shockStatusBadge.classList.add("shocked");
        capacityLabel.textContent = `CRITICAL: 30,000 L/DAY (-40%)`;
    } else {
        shockStatusBadge.classList.remove("shocked");
    }

    // 2. Chat Messages
    chatMessages.innerHTML = "";
    currentState.messages.forEach(msg => {
        const div = document.createElement("div");
        div.className = `chat-bubble role-${msg.role || 'mediator'}`;
        
        let speakerIcon = '<i class="fa-solid fa-scale-balanced"></i>';
        const spk = (msg.speaker || "").toLowerCase();
        if (spk.includes("mediator")) speakerIcon = '<i class="fa-solid fa-brain"></i>';
        else if (spk.includes("system") || spk.includes("shock")) speakerIcon = '<i class="fa-solid fa-triangle-exclamation"></i>';
        else if (spk.includes("house") || spk.includes("village")) speakerIcon = '<i class="fa-solid fa-house"></i>';
        else if (spk.includes("school") || spk.includes("st. jude")) speakerIcon = '<i class="fa-solid fa-school"></i>';
        else if (spk.includes("cash")) speakerIcon = '<i class="fa-solid fa-money-bill-trend-up"></i>';
        else if (spk.includes("subsist") || spk.includes("farmer")) speakerIcon = '<i class="fa-solid fa-seedling"></i>';
        else if (spk.includes("govt") || spk.includes("official")) speakerIcon = '<i class="fa-solid fa-building-columns"></i>';
        else if (msg.role === 'user') speakerIcon = '<i class="fa-solid fa-user-gear"></i>';

        div.innerHTML = `
            <div class="chat-meta">
                <span class="speaker-tag">${speakerIcon} ${msg.speaker || 'Mediator'}</span>
                <span>Turn ${msg.turn}</span>
            </div>
            <div class="chat-text">${formatMarkdown(msg.text)}</div>
        `;
        chatMessages.appendChild(div);
    });
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // 3. Gauges & Allocations
    let totalAlloc = 0;
    const st = currentState.stakeholders || {};
    const allocs = {
        hh: st.households ? st.households.allocated_liters || 10000 : 10000,
        sch: st.school ? st.school.allocated_liters || 5000 : 5000,
        sub: st.farmers_subsistence ? st.farmers_subsistence.allocated_liters || 8000 : 8000,
        cash: st.farmers_cashcrop ? st.farmers_cashcrop.allocated_liters || 5000 : 5000,
        gov: st.govt_official ? st.govt_official.allocated_liters || 2000 : 2000
    };

    totalAlloc = allocs.hh + allocs.sch + allocs.sub + allocs.cash + allocs.gov;
    supplyRatioText.textContent = `${totalAlloc.toLocaleString()} / ${cap.toLocaleString()} L allocated`;

    progressHouseholds.style.width = `${(allocs.hh / cap) * 100}%`;
    progressSchool.style.width = `${(allocs.sch / cap) * 100}%`;
    progressSubsistence.style.width = `${(allocs.sub / cap) * 100}%`;
    progressCashcrop.style.width = `${(allocs.cash / cap) * 100}%`;
    progressGovt.style.width = `${(allocs.gov / cap) * 100}%`;

    // 4. Claims List
    renderClaimsList(currentState.claims || []);
}

function renderClaimsList(claims) {
    claimsList.innerHTML = "";
    claims.forEach(c => {
        const card = document.createElement("div");
        card.className = `claim-card ${c.contradiction_found ? 'contradiction' : ''}`;
        
        let badge = `<span class="claim-badge badge-verified"><i class="fa-solid fa-circle-check"></i> Verified</span>`;
        if (c.contradiction_found) {
            badge = `<span class="claim-badge badge-contradiction"><i class="fa-solid fa-bug"></i> PROBED CONTRADICTION</span>`;
        }

        card.innerHTML = `
            <div class="claim-header">
                <span class="claim-speaker">${c.speaker} (Turn ${c.turn})</span>
                ${badge}
            </div>
            <div class="claim-text">"${c.claim_text}"</div>
            <div class="claim-details">${c.details}</div>
        `;
        claimsList.appendChild(card);
    });
}

function renderAccord(accord) {
    if (!accord) return;

    let allocRows = accord.stakeholder_allocations.map(a => `
        <tr>
            <td><strong>${a.name}</strong></td>
            <td><strong>${a.allocated_liters_day.toLocaleString()} L/day</strong> (${a.pct_of_capacity}%)</td>
            <td><code>${a.time_window}</code></td>
            <td><code>${a.meter_id}</code></td>
        </tr>
    `).join("");

    let infraItems = accord.technical_monitoring_infrastructure.map(i => `<li>${i}</li>`).join("");

    accordViewer.innerHTML = `
        <div class="accord-title">
            <i class="fa-solid fa-certificate"></i> ${accord.title}
        </div>

        <div class="accord-section">
            <p><strong>Status:</strong> <span style="color: var(--success); font-weight: 700;">${accord.status}</span> | <strong>Borehole Sustainable Yield:</strong> ${accord.borehole_capacity_lday.toLocaleString()} L/day</p>
        </div>

        <div class="accord-section">
            <h4><i class="fa-solid fa-chart-pie"></i> Specific Volumetric Allocations & Pumping Windows</h4>
            <table class="accord-table">
                <thead>
                    <tr>
                        <th>Stakeholder</th>
                        <th>Daily Allocation</th>
                        <th>Pumping Time Slot</th>
                        <th>Smart Meter ID</th>
                    </tr>
                </thead>
                <tbody>
                    ${allocRows}
                </tbody>
            </table>
        </div>

        <div class="accord-section">
            <h4><i class="fa-solid fa-microchip"></i> Technical Monitoring Infrastructure</h4>
            <ul style="margin-left: 1.25rem; font-size: 0.88rem; color: #cbd5e1;">
                ${infraItems}
            </ul>
        </div>

        <div class="accord-section">
            <h4><i class="fa-solid fa-gavel"></i> Accountability & Graduated Penalty Protocol</h4>
            
            <div class="penalty-box">
                <div class="penalty-title">Tier 1 Penalty (Minor Overage: 1% to 15%)</div>
                <div><strong>Trigger:</strong> ${accord.accountability_and_penalty_protocol.tier_1_minor_overage.trigger}</div>
                <div><strong>Enforcement:</strong> ${accord.accountability_and_penalty_protocol.tier_1_minor_overage.penalty}</div>
            </div>

            <div class="penalty-box">
                <div class="penalty-title">Tier 2 Penalty (Moderate Overage >15% or Tampering)</div>
                <div><strong>Trigger:</strong> ${accord.accountability_and_penalty_protocol.tier_2_moderate_overage_or_tampering.trigger}</div>
                <div><strong>Enforcement:</strong> ${accord.accountability_and_penalty_protocol.tier_2_moderate_overage_or_tampering.penalty}</div>
            </div>

            <div class="penalty-box">
                <div class="penalty-title">Tier 3 Penalty (Severe Violation / Bypass)</div>
                <div><strong>Trigger:</strong> ${accord.accountability_and_penalty_protocol.tier_3_severe_violation_or_unauthorized_bypass.trigger}</div>
                <div><strong>Enforcement:</strong> ${accord.accountability_and_penalty_protocol.tier_3_severe_violation_or_unauthorized_bypass.penalty}</div>
            </div>
        </div>
    `;
}

function formatMarkdown(text) {
    if (!text) return "";
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>');
}
