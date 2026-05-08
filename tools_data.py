"""
First-responder tool definitions for /tools/<slug> routes.

Each tool is a single LLM-driven worksheet — one form, one prompt,
one result page. Stateless (no database). Free for fire / EMS.

To add a new tool, append an entry to TOOLS. The route handler in
app.py reads from this dict.
"""
from __future__ import annotations

TOOLS: dict[str, dict] = {

    'training-tracker': {
        'title':       'Training Tracker',
        'tagline':     'Build a year-of-training plan for your department or your own NFPA 1001 / 1002 / 1006 progress.',
        'icon':        '📋',
        'fields': [
            ('role',     'Your role (probie / FF / officer / chief / training officer)', 'textarea'),
            ('current',  'Certifications already held (FF I, FF II, EVOC, EMT, etc.)',  'textarea'),
            ('target',   'Goal for the next 6–12 months',                                'textarea'),
            ('hours',    'Approximate training hours available per month',               'input'),
        ],
        'system_prompt': (
            "You are a fire-service training planner. Build a realistic, NFPA-aligned 6–12 month "
            "training plan for the user. Output: (1) PRIORITY PATH — the top 3 certifications or "
            "skills that unlock the most for them given their role, with NFPA standard references "
            "(1001/1002/1006/1041 etc.). (2) MONTHLY BREAKDOWN — month-by-month hours allocated "
            "to (a) live drills, (b) classroom / online (FEMA EMI IS courses, NFA Online, state "
            "academy), (c) physical fitness and skill maintenance. (3) FREE RESOURCES — list "
            "specific free courses by name and platform (FEMA EMI IS-100/200/700/800, NFA Online, "
            "Vector Solutions trial, etc.) — only ones that are actually free. (4) MILESTONES — "
            "what they should be able to demonstrate at month 3, 6, 12. (5) DISCLAIMER — this is "
            "a planning aid; actual cert pathways are set by the AHJ (authority having "
            "jurisdiction) and NFPA. Verify with your training officer before committing."
        ),
    },

    'pre-incident': {
        'title':       'Pre-Incident Plan',
        'tagline':     'Draft a pre-incident plan (PIP) for a target hazard in your district. NFPA 1620 aligned.',
        'icon':        '🏢',
        'fields': [
            ('building',     'Building / occupancy (address optional, type required: e.g. "3-story garden apartment, 24 units")', 'textarea'),
            ('construction', 'Construction class if known (Type I–V, year built, sprinklered y/n)',                                'textarea'),
            ('hazards',      'Known hazards (LP gas, oxygen storage, hoarding, fire-protection deficiencies, access issues)',     'textarea'),
            ('size',         'Approximate footprint (sq ft) and number of stories',                                                'input'),
        ],
        'system_prompt': (
            "You are a pre-incident planning assistant for fire / EMS. Produce a structured "
            "draft pre-incident plan in the format used by NFPA 1620: (1) BUILDING DESCRIPTION — "
            "construction type, age, footprint, height, occupancy classification (NFPA 5000 / "
            "ICC). (2) BUILT-IN FIRE PROTECTION — sprinklers, standpipes, fire alarm, smoke "
            "control if any. Note absence too. (3) UTILITIES — electric, gas, water shutoffs "
            "with assumed locations (operator must verify). (4) ACCESS — apparatus access, "
            "FDC connection, hydrant locations within 300 ft, key-box / Knox-box if known. "
            "(5) HAZARDS — list each user-provided hazard with the specific tactical "
            "consideration. (6) STRATEGIC PRIORITIES — defensive vs offensive triggers, "
            "rescue profile, water supply needs. (7) RECOMMENDED RESPONSE — initial alarm "
            "assignment for this occupancy. (8) NOTES TO COMPANY OFFICERS — what to walk-"
            "through on the next pre-incident visit. (9) DISCLAIMER — this is a draft for "
            "the operator to verify on-site, not an authoritative PIP. Final PIP must be "
            "approved per AHJ / department SOP."
        ),
    },

    'sog-search': {
        'title':       'SOG / SOP Search',
        'tagline':     'Paste an SOG / SOP excerpt or describe a scenario; get plain-language guidance and citations.',
        'icon':        '📑',
        'fields': [
            ('sog',      'Paste relevant SOG / SOP text (or describe what your dept policy generally says about this topic)', 'textarea'),
            ('scenario', "What's actually happening on-scene right now (or the question you have)",                            'textarea'),
        ],
        'system_prompt': (
            "You are a fire-service SOG / SOP interpreter. The user pastes their department's "
            "policy text (or describes it) and a scenario; you produce: (1) WHAT THE POLICY "
            "SAYS — quote or paraphrase the relevant sections, in order of relevance to the "
            "scenario. (2) THE PLAIN-ENGLISH ANSWER — what the policy means for this specific "
            "scenario. (3) GREY AREAS — anything the policy doesn't directly address; flag "
            "them as 'consult IC or duty chief.' (4) RELEVANT NFPA / OSHA STANDARDS — only "
            "well-known ones with their numbers (e.g. NFPA 1500 for member health and safety, "
            "1561 for incident command, OSHA 1910.134 for SCBA). (5) DISCLAIMER — your "
            "department's SOG is authoritative; this is interpretation help only. When in "
            "doubt on-scene, fall back to the chain of command."
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
            "operator can paste into a doc and print."
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
            "specific channels for their locale: high schools, community colleges, local "
            "Facebook groups, NextDoor, military transition programs (Transition Assistance "
            "Program), workforce-development boards, small-business community boards. (3) "
            "WHAT TO SAY — recruitment-message angles that work for volunteer FD: pension / "
            "LOSAP credit (state-dependent), tuition reimbursement (PA / NJ / others), "
            "skill-building (EMT / driver-operator), structured camaraderie. Avoid 'hero' "
            "imagery alone — it draws the wrong applicants and misses the people whose "
            "primary motivation is community + skill-building. (4) INTERVIEW STRUCTURE — "
            "30-min applicant interview script (motivation / availability / fitness self-"
            "assessment / family support). (5) MID-FUNNEL — buddy / mentor program for the "
            "first 90 days. Drop-out reasons usually concentrate at: physical-fitness "
            "surprise, family resistance, schedule misfit. Address each. (6) RETENTION — "
            "what keeps members past their first cert: clear next-cert path, leadership "
            "opportunities by year 2, public recognition (department social, family events). "
            "(7) METRICS TO TRACK — applicants / month, % completing FF I, % active at 1 "
            "year, % active at 3 years. (8) FREE TOOLS — NVFC's recruitment toolkit, IFSI / "
            "NFFF resources, FEMA's Volunteer Leadership Section. (9) DISCLAIMER — every "
            "department's culture is unique; treat this as a starting framework, not a "
            "prescription."
        ),
    },
}


def get_tool(slug: str) -> dict | None:
    return TOOLS.get(slug)


def all_slugs() -> list[str]:
    return list(TOOLS.keys())
