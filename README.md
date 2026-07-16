# FirstResponderHub

Free specialized AI tools for U.S. first responders and volunteers. Live at <https://firstresponder.freshskyai.com>.

The umbrella site that:
- Tells the volunteer-firefighter-applicant pitch
- Links to current administrative drafting tools
- Labels the separate NFIRS demonstration as legacy because USFA moved 2026 reporting to NERIS
- Is the canonical URL to send to a chief

Current source mappings use NFPA 1010 (2024), NFPA 1020 (2025), NFPA 1550 (2024), NFPA 1660 (2024), OSHA 29 CFR 1910.134, and NFPA 1006 with the edition formally adopted by the state/AHJ. NFPA's availability of a 2027 NFPA 1006 edition does not make it universally controlling. Source URLs, editions, and retrieval dates appear beside affected tools. Outputs are administrative drafts only and must never direct active-incident decisions.

Flask app using the shared privacy-restricted U.S. provider chain. Public access is free; there is no paid plan, contract, or user API key.

## Deploy

Push to `main` triggers GH Actions → `gcloud run deploy firstresponder` via Workload Identity Federation. Standard pattern from the rest of the Fresh Sky AI portfolio.
