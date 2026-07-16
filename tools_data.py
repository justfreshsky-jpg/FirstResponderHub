"""
First-responder tool definitions for /tools/<slug> routes.

Each tool is a single LLM-driven worksheet — one form, one prompt,
one result page. Stateless (no database). Free for fire / EMS.

To add a new tool, append an entry to TOOLS. The route handler in
app.py reads from this dict.
"""
from __future__ import annotations

SOURCE_RETRIEVED = '2026-07-16'
NFPA_1010_URL = 'https://link.nfpa.org/all-publications/1010/2024'
NFPA_1020_URL = 'https://link.nfpa.org/all-publications/1020/2025'
NFPA_1006_URL = 'https://link.nfpa.org/all-publications/1006/2027'
NFPA_1550_URL = 'https://link.nfpa.org/all-publications/1550/2024'
NFPA_1660_URL = 'https://link.nfpa.org/all-publications/1660/2024'
OSHA_RESPIRATORY_URL = (
    'https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.134'
)

TOOLS: dict[str, dict] = {

    'training-tracker': {
        'title':       'Training Tracker',
        'tagline':     'Build a year-of-training plan using current NFPA publication families and the editions adopted by your AHJ.',
        'icon':        '📋',
        'fields': [
            ('role',     'Your role (probie / FF / officer / chief / training officer)', 'textarea'),
            ('current',  'Certifications already held (FF I, FF II, EVOC, EMT, etc.)',  'textarea'),
            ('target',   'Goal for the next 6–12 months',                                'textarea'),
            ('hours',    'Approximate training hours available per month',               'input'),
        ],
        'authorities': [
            {
                'title': 'NFPA 1010 — Professional Qualifications for Firefighters',
                'version': '2024 edition; consolidates the former NFPA 1001/1002 pathways',
                'url': NFPA_1010_URL,
                'retrieved': SOURCE_RETRIEVED,
            },
            {
                'title': 'NFPA 1020 — Instructor, Fire Officer, and EMS Officer Professional Qualifications',
                'version': '2025 edition; replaces separate NFPA 1021/1041 references',
                'url': NFPA_1020_URL,
                'retrieved': SOURCE_RETRIEVED,
            },
            {
                'title': 'NFPA 1006 — Technical Rescue Personnel Professional Qualifications',
                'version': (
                    'NFPA LiNK lists 2021 and 2027 editions; neither edition is universally '
                    'in force—use only the edition formally adopted by the state/AHJ'
                ),
                'url': NFPA_1006_URL,
                'retrieved': SOURCE_RETRIEVED,
            },
        ],
        'system_prompt': (
            "You are a fire-service training planner. Build a realistic, NFPA-aligned 6–12 month "
            "training plan for the user. Output: (1) PRIORITY PATH — the top 3 certifications or "
            "skills that may fit their role. Use the current publication families: NFPA 1010 "
            "(2024) for firefighter/driver-operator professional qualifications; NFPA 1020 "
            "(2025) for instructor/fire officer/EMS officer qualifications; and NFPA 1006 for "
            "technical-rescue personnel. Do not treat the 2027 edition as in force unless the "
            "user's state/AHJ has formally adopted it; if adoption is unknown, omit the edition "
            "and label it unconfirmed. Do not cite the "
            "superseded standalone NFPA 1001, 1002, 1021, or 1041 as current. Never claim that an "
            "NFPA standard itself awards certification or that a named course satisfies local "
            "certification. (2) MONTHLY BREAKDOWN — month-by-month hours allocated "
            "to (a) live drills, (b) classroom / online (FEMA EMI IS courses, NFA Online, state "
            "academy), (c) physical fitness and skill maintenance. (3) RESOURCES — list a course "
            "only when it is clearly identified as free on an official FEMA, USFA/NFA, state, or "
            "AHJ page; otherwise give the official catalog as a search lead and label cost/credit "
            "unconfirmed. (4) MILESTONES — "
            "what they should be able to demonstrate at month 3, 6, 12. (5) DISCLAIMER — this is "
            "a planning aid; actual cert pathways are set by the AHJ (authority having "
            "jurisdiction), state credentialing body, and adopted standards. Verify the exact "
            "edition, prerequisites, and credit with the training officer before committing."
        ),
    },

    'pre-incident': {
        'title':       'Pre-Incident Plan',
        'tagline':     'Draft a site-verification worksheet using the NFPA 1660 (2024) pre-incident planning framework.',
        'icon':        '🏢',
        'fields': [
            ('building',     'Building / occupancy (address optional, type required: e.g. "3-story garden apartment, 24 units")', 'textarea'),
            ('construction', 'Construction class if known (Type I–V, year built, sprinklered y/n)',                                'textarea'),
            ('hazards',      'Known hazards (LP gas, oxygen storage, hoarding, fire-protection deficiencies, access issues)',     'textarea'),
            ('size',         'Approximate footprint (sq ft) and number of stories',                                                'input'),
        ],
        'authorities': [
            {
                'title': 'NFPA 1660 — Emergency, Continuity, and Crisis Management',
                'version': '2024 edition; Chapters 17–23 incorporate former NFPA 1620 content',
                'url': NFPA_1660_URL,
                'retrieved': SOURCE_RETRIEVED,
            },
        ],
        'system_prompt': (
            "You are a pre-incident planning worksheet assistant for fire/EMS. NFPA 1620 is "
            "not the current standalone reference; its material is incorporated in NFPA 1660 "
            "(2024), Chapters 17–23. Produce a conservative information-gathering draft, not "
            "an operational plan: (1) USER-SUPPLIED FACTS — repeat only facts given and mark "
            "every other field UNKNOWN / VERIFY ON SITE. Never infer construction type, code "
            "classification, occupant load, fire-flow need, or system capability. (2) SITE AND "
            "OCCUPANCY CHECKS — prompts for physical/site factors, occupancy, water supply and "
            "fire-protection systems, and special hazards. (3) UTILITIES AND ACCESS — fields to "
            "record verified shutoffs, FDCs, hydrants, key boxes, access constraints, and contacts; "
            "never assume a location or fixed distance. (4) INCIDENT-OPERATIONS INFORMATION — "
            "questions the AHJ must answer under its adopted SOGs. Do not recommend alarm "
            "assignments, offensive/defensive triggers, staffing, tactics, or water supply. "
            "(5) VALIDATION AND MAINTENANCE — on-site walkthrough, responsible reviewer, approval, "
            "last-verified date, and review/update cadence set by the AHJ. (6) DISCLAIMER — this "
            "unverified worksheet must not be used for dispatch or scene decisions until the AHJ "
            "has validated and approved it."
        ),
    },

    'sog-search': {
        'title':       'SOG / SOP Search',
        'tagline':     'Review pasted SOG/SOP text for training or after-action use; never for an active incident.',
        'icon':        '📑',
        'fields': [
            ('sog',      'Paste relevant SOG / SOP text (required for interpretation; otherwise provide only the topic)',    'textarea'),
            ('scenario', 'Training or after-action scenario (not an active incident)',                                         'textarea'),
        ],
        'authorities': [
            {
                'title': 'NFPA 1550 — Emergency Responder Health and Safety',
                'version': '2024 edition; combines former NFPA 1500, 1521, and 1561',
                'url': NFPA_1550_URL,
                'retrieved': SOURCE_RETRIEVED,
            },
            {
                'title': 'OSHA 29 CFR 1910.134 — Respiratory Protection',
                'version': 'Current OSHA standard page',
                'url': OSHA_RESPIRATORY_URL,
                'retrieved': SOURCE_RETRIEVED,
            },
        ],
        'system_prompt': (
            "You are a fire-service SOG / SOP interpreter. The user pastes their department's "
            "policy text and a scenario. If no actual policy text is supplied, say you cannot "
            "interpret or quote the department policy and provide only questions for the IC/duty "
            "chief. Otherwise produce: (1) WHAT THE POLICY "
            "SAYS — quote or paraphrase the relevant sections, in order of relevance to the "
            "scenario. (2) THE PLAIN-ENGLISH ANSWER — what the policy means for this specific "
            "scenario. (3) GREY AREAS — anything the policy doesn't directly address; flag "
            "them as 'consult IC or duty chief.' (4) RELEVANT NFPA / OSHA STANDARDS — only "
            "use the verified source map: NFPA 1550 (2024) combines former NFPA 1500, 1521, "
            "and 1561; OSHA 29 CFR 1910.134 covers respiratory protection. Do not invent a "
            "section number or claim a standard applies to the user's public employer without "
            "confirming federal/state-plan jurisdiction and local adoption. (5) DISCLAIMER — "
            "your department's adopted SOG, applicable law, and chain of command are controlling. "
            "Never treat this output as real-time scene direction."
        ),
    },

    'apparatus-check': {
        'title':       'Apparatus Check Log',
        'tagline':     'Generate a daily / weekly apparatus check sheet for engine, ladder, ambulance, or special unit.',
        'icon':        '🚒',
        'fields': [
            ('apparatus', 'Apparatus type (engine, ladder/quint, ambulance, brush truck, tanker, rescue, etc.)', 'input'),
            ('frequency', 'Frequency (start-of-shift, daily, weekly, monthly)',                                  'input'),
            ('extras',    'Any equipment unique to your rig (ALS supplies, specific extrication tools, foam, hazmat kit)', 'textarea'),
        ],
        'system_prompt': (
            "You are a fire-apparatus check-sheet generator. Produce a printable check list for "
            "the apparatus + frequency the user specified. Sections in order: (1) EXTERIOR & "
            "CHASSIS — fluids (oil / coolant / power steering / DEF), tires & lugs, lights, "
            "mirrors, body damage. (2) ENGINE / DRIVELINE — start, idle, gauges, no warning "
            "lamps, air-pressure brakes (if applicable), parking-brake test. (3) PUMP & WATER "
            "(engines/tankers) — primer, suction, tank-to-pump, discharge gauges, hoselines "
            "loaded correctly. (4) AERIAL / GROUND LADDERS — bedded, secured, unsecured-tip "
            "tools accounted for, hydraulic levels (if aerial). (5) SCBA / PPE — bottle "
            "pressures, mask seals, spare cylinders, PASS device function. (6) MEDICAL / "
            "RESCUE EQUIPMENT — defib pads in date, O2 cylinder pressures, AED self-test "
            "passed, suction works, splints / C-collars, stretcher straps. (7) USER EXTRAS — "
            "everything they listed in the 'extras' field, each with a yes/no checkbox and a "
            "'note' field. (8) SIGNATURE BLOCK — operator name, date, shift, deficiencies "
            "found / remedied. Output should be plainly formatted text with [ ] checkboxes — "
            "operator can paste into a doc and print. Never invent numeric pass/fail limits, "
            "maintenance intervals, torque/pressure criteria, or an out-of-service decision. "
            "Label each criterion 'verify against department policy and manufacturer instructions'; "
            "a generated checklist cannot replace inspection, maintenance, or qualified review."
        ),
    },

    'recruitment': {
        'title':       'Recruitment Funnel',
        'tagline':     'A 90-day recruiter playbook for volunteer / part-paid departments — outreach, interviews, retention.',
        'icon':        '🤝',
        'fields': [
            ('dept',       'Department (volunteer, combination, paid-on-call) and rough roster size', 'textarea'),
            ('locale',     'Locale type (rural, suburban, urban) and any nearby competing departments / job markets', 'textarea'),
            ('challenges', "What's been hard about recruiting lately (no applicants, applicants drop out before training, retention after FF I, etc.)", 'textarea'),
        ],
        'system_prompt': (
            "You are a volunteer / part-paid fire-service recruitment consultant. Produce a "
            "90-day playbook for the department: (1) DIAGNOSE — identify the most likely "
            "bottleneck given their challenges (top of funnel = no applicants; mid funnel = "
            "drop during training; bottom funnel = post-cert retention). (2) OUTREACH — "
            "testable channels for their locale: high schools, community colleges, local "
            "Facebook groups, NextDoor, military transition programs (Transition Assistance "
            "Program), workforce-development boards, small-business community boards. (3) "
            "WHAT TO SAY — recruitment-message hypotheses to test for this department: pension / "
            "LOSAP credit (state-dependent), tuition reimbursement (PA / NJ / others), "
            "skill-building (EMT / driver-operator), and structured camaraderie. Do not claim "
            "that an angle works universally or label applicants as 'right' or 'wrong.' (4) INTERVIEW STRUCTURE — "
            "30-min applicant interview script (motivation / availability / fitness self-"
            "assessment / family support). (5) MID-FUNNEL — buddy / mentor program for the "
            "first 90 days. Ask whether possible friction includes physical-fitness expectations, "
            "family support, scheduling, training access, or administrative load; do not state an "
            "unsupported universal cause. Address only causes supported by the user's input. (6) RETENTION — "
            "hypotheses to test locally, such as a clear next-cert path, leadership "
            "opportunities, recognition, and family-inclusive events; do not claim a proven "
            "retention effect without department data. "
            "(7) METRICS TO TRACK — applicants / month, % completing FF I, % active at 1 "
            "year, % active at 3 years. (8) RESOURCE LEADS — point to official NVFC, USFA/NFA, "
            "state fire-service, or department resources only when the current title/URL is "
            "known; otherwise label the lead unverified. (9) DISCLAIMER — every "
            "department's culture is unique; treat this as a starting framework, not a "
            "prescription."
        ),
    },
}


def get_tool(slug: str) -> dict | None:
    return TOOLS.get(slug)


def all_slugs() -> list[str]:
    return list(TOOLS.keys())
