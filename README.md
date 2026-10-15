# FirstResponderHub

Specialized paid administrative tools for U.S. first responders and volunteers. Live at <https://firstresponder.freshskyai.com>.

The umbrella site that:
- Tells the volunteer-firefighter-applicant pitch
- Links to current administrative drafting tools
- Links to a separate, bounded NERIS preparation aid that does not file reports or assign official codes
- Is the canonical URL to send to a chief

Current source mappings use NFPA 1010 (2024), NFPA 1020 (2025), NFPA 1550 (2024), NFPA 1660 (2024), OSHA 29 CFR 1910.134, and NFPA 1006 with the edition formally adopted by the state/AHJ. NFPA's availability of a 2027 NFPA 1006 edition does not make it universally controlling. Source URLs, editions, and retrieval dates appear beside affected tools. Outputs are administrative drafts only and must never direct active-incident decisions.

Flask app using the shared privacy-restricted U.S. provider chain. Access includes three previews, then Civic costs $14.99/month with no automatic overage charges; no user API key is required.

## Deploy

Deployment is started manually through the GitHub Actions `Deploy` workflow
(`workflow_dispatch`); pushing or merging source does not run it. It prepares a
zero-traffic candidate using Workload Identity Federation. Production promotion
remains a separate manual workflow.

The deployment gate reads `cloud-run-budget-lock` explicitly from the FreshSky
project `neon-glyph-491500-e2`. A failed or missing read blocks deployment. Only
`open:<timezone-aware ISO timestamp>` is accepted, with an age of at most 30 hours
and at most 2 minutes of future clock skew. Empty, literal `open`, malformed,
stale, `locked`, and `throttled` values fail closed. These are the existing
FreshSky production bounds, taken from
[`budget_runtime.py`](https://github.com/justfreshsky-jpg/freshskyai/blob/b682121fc5f02b4b2b74ff1ec508f4116c9dbff9/budget_runtime.py)
and its deployment checker at that reviewed source commit.

Offline checks: `python -m pytest tests/ -q` and
`node --test tests/review_pack_model.test.mjs`. Budget-gate tests execute the
workflow's actual shell block with a local mocked `gcloud`; they make no Cloud
calls or deployments.
