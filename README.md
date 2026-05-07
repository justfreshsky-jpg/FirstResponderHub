# FirstResponderHub

Static landing page for Fresh Sky AI's free first-responder tools. Live at <https://firstresponder.freshskyai.com>.

The umbrella site that:
- Tells the volunteer-firefighter-applicant pitch
- Links to live tools (currently NFIRS Assistant)
- Lists the roadmap for departments that want to weigh in
- Is the canonical URL to send to a chief

Standalone Flask app, no `freshsky_common` dependency. The whole thing is one route serving an HTML template.

## Deploy

Push to `main` triggers GH Actions → `gcloud run deploy firstresponder` via Workload Identity Federation. Standard pattern from the rest of the Fresh Sky AI portfolio.
