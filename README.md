# Reddit Safe Automation (Karma + Backlinks)
Runs twice per day (09:00 & 21:00 UTC). Guardrails:
- Rotate r/Colorization, r/AskPhotography, r/OldPhotos, r/PhotoEditingRequests
- Skip locked/archived/old (>14d); randomize tips; max 2 actions/run
- LINK_POLICY: NEVER_IN_FIRST_COMMENT | MOD_ALLOWED | FOLLOW_UP_ONLY

Secrets: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD, REDDIT_USER_AGENT, SUPABASE_URL, SUPABASE_SERVICE_KEY, LINK_POLICY