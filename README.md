# FirstResponderHub

Free specialized AI tools for U.S. first responders and volunteers. Live at <https://firstresponder.freshskyai.com>.

The umbrella site that:
- Tells the volunteer-firefighter-applicant pitch
- Links to live tools (currently NFIRS Assistant)
- Lists the roadmap for departments that want to weigh in
- Is the canonical URL to send to a chief

Flask app using the shared privacy-restricted U.S. provider chain. Public access is free; there is no paid plan, contract, or user API key.

## Deploy

Push to `main` triggers GH Actions → `gcloud run deploy firstresponder` via Workload Identity Federation. Standard pattern from the rest of the Fresh Sky AI portfolio.
