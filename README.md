# Reddit Safe Automation

🚀 **AI-Powered Reddit Engagement** for building karma and safe backlinks with built-in safety guardrails.

## ✨ Features

- **🤖 AI-Generated Comments**: Powered by z.ai GML-4.6 for unique, contextual, genuinely helpful responses
- **🛡️ Safety First**: Respects Reddit's rate limits and community guidelines
- **📝 Value-First**: Educational, helpful comments before any promotional content
- **🎯 Smart Targeting**: Finds relevant threads in photo restoration communities
- **📊 Supabase Logging**: Tracks all actions for analysis and compliance monitoring
- **🔗 Flexible Link Policy**: Control when/if your website link is included
- **⏰ Scheduled Automation**: Runs twice daily (09:00 & 21:00 UTC)

## 🛡️ Safety Guardrails

- ✅ **Rate Limiting**: Max 3 posts per week (configurable)
- ✅ **Timing**: Minimum 4-6 hours between posts
- ✅ **90/10 Rule**: 90% community engagement, 10% promotional content (Reddit safety rule)
- ✅ **Quality Check**: Value-first educational content
- ✅ **Subreddit Research**: Checks rules before posting
- ✅ **Error Handling**: Fails safely, never posts if limits exceeded

## 🤖 AI Integration (z.ai GML-4.6)

Every comment is **dynamically generated** by z.ai GML-4.6:

```python
# Example AI Generation
Thread Title: "How to restore my grandfather's old photo?"
Thread Body: "The photo is very faded and has water damage..."

AI Prompt: Generate a helpful, expert comment that demonstrates knowledge
Result: Unique comment tailored to the specific thread context
```

**Why AI over hardcoded templates?**
- ✅ Unique comments prevent ban for repetitive behavior
- ✅ Context-aware responses feel genuine
- ✅ Better community engagement = more karma
- ✅ Adapts to different subreddit styles
- ✅ Learns from what works

## ⚙️ Configuration

### GitHub Secrets (All Set ✅)

```
REDDIT_CLIENT_ID          ✅ Set
REDDIT_CLIENT_SECRET      ✅ Set
REDDIT_USERNAME           ✅ Set
REDDIT_PASSWORD           ✅ Set
REDDIT_USER_AGENT         ✅ Set
ZAI_API_KEY               ✅ Set (z.ai GML-4.6 access)
SUPABASE_URL              ✅ Set
SUPABASE_SERVICE_KEY      ✅ Set
LINK_POLICY               ✅ Setting: FOLLOW_UP_ONLY
```

### Link Policies

- **`FOLLOW_UP_ONLY`** (Recommended): First comment is pure value, link only in follow-ups
- **`ALWAYS`**: Include link in every comment (use cautiously)
- **`NEVER`**: Never include links, karma building only

## 📊 Supabase Integration

### Table: `content_history`

Logs **every action** for compliance & analytics:

```
{
  "platform": "reddit",
  "action": "ai_comment_generated",
  "subreddit": "PhotoEditingRequests",
  "thread_title": "How to restore...",
  "comment_url": "https://reddit.com/r/...",
  "model": "gml-4.6",
  "length": 187,
  "tokens_used": 125,
  "performed_at": "2025-10-15T22:25:30Z"
}
```

**Tracked Actions:**
- `ai_comment_generated` - AI created a comment
- `reddit_comment` - Comment posted to Reddit
- `ninety_ten_skip` - Skipped due to 90/10 rule violation
- `rate_limit_skip` - Skipped due to rate limiting
- `automation_run_complete` - Run finished successfully
- `automation_error` - Error occurred
- `ai_comment_error` - AI API call failed

**Query Example:**
```sql
SELECT 
  platform,
  action,
  COUNT(*) as count,
  date(performed_at) as date
FROM content_history
WHERE platform = 'reddit'
GROUP BY date, action
ORDER BY date DESC;
```

## ⏰ Schedule

Runs automatically twice daily:
- **09:00 UTC** (3 AM EST / Midnight PST)
- **21:00 UTC** (4 PM EST / 1 PM PST)

Can also be triggered manually from Actions tab.

## 🎯 Target Communities

- r/PhotoEditingRequests
- r/AskPhotography
- r/OldPhotos
- r/Colorization
- r/restoration
- r/PhotoRepair
- r/pics
- r/Photography

## 🚀 Usage

### Manual Run
1. Go to **Actions** tab
2. Select **"Reddit Safe Automation"** workflow
3. Click **"Run workflow"** button

### View Logs
- **Real-time**: GitHub Actions UI shows live output
- **Historical**: Query Supabase `content_history` table
- **Analytics**: Check karma growth and thread performance

## 📋 Project Status

### ✅ Completed Features
- [x] Reddit API integration (PRAW)
- [x] z.ai GML-4.6 AI comment generation
- [x] 90/10 safety rule enforcement
- [x] Rate limiting (3 posts/week)
- [x] Supabase logging
- [x] GitHub Actions scheduling
- [x] Error handling & failsafes
- [x] Link policy control

### 🔧 Recent Updates

**October 15, 2025:**
- ✅ Fixed GitHub Actions workflow syntax error (REDDIT_PASSWORD)
- ✅ Integrated z.ai GML-4.6 for AI comment generation
- ✅ Added 90/10 rule enforcement
- ✅ Implemented Supabase logging
- ✅ Added comprehensive safety checks
- ✅ Created automated scheduling
- ✅ Updated README with Handover Notes for Agents

## 📚 Handover Notes for Other Agents

### Repository Structure
```
reddit-safe-automation/
├── README.md                         # Documentation (THIS FILE)
├── reddit_automation-with-ai.py       # Main script with AI integration ⭐
├── reddit_automation.py               # Legacy version (deprecated)
└── .github/workflows/
    └── reddit-automation.yml          # GitHub Actions workflow
```

### Key Files

**`reddit_automation-with-ai.py`** (ACTIVE - Use this!)
- Main automation script
- Uses z.ai GML-4.6 for AI comment generation
- Enforces 90/10 rule
- Logs to Supabase
- Rate limiting & error handling

**`.github/workflows/reddit-automation.yml`** (Latest fix applied)
- Scheduled to run 09:00 & 21:00 UTC
- Triggers workflow_dispatch for manual runs
- Sets all environment variables from GitHub Secrets
- Recently fixed: Removed syntax error from REDDIT_PASSWORD

### Critical Configuration

**z.ai API Integration:**
```python
ZAI_API_ENDPOINT = "https://api.z.ai/v1/chat/completions"
ZAI_MODEL = "gml-4.6"
ZAI_API_KEY = secrets.ZAI_API_KEY  # From GitHub Secrets
```

**Reddit Rate Limits:**
```python
RATE_LIMIT_MAX_POSTS_PER_WEEK = 3
MIN_HOURS_BETWEEN_POSTS = 4
```

**90/10 Rule Settings:**
```python
NINETY_TEN_RULE_MAX_PROMOTIONAL_RATIO = 0.10  # 10% max
NINETY_TEN_MIN_ACTIVITY = 10  # Need 10+ posts/comments to check
```

### Supabase Connection Details

**Database:** Same Supabase project integrated with Reddit automation

**Table:** `content_history`
- Logs all actions automatically
- Use for analytics, compliance, and troubleshooting
- Query by action type, date, platform

**Environment Variables (GitHub Secrets):**
- `SUPABASE_URL` - API endpoint
- `SUPABASE_SERVICE_KEY` - Authentication

### Troubleshooting Checklist

| Issue | Solution |
|-------|----------|
| Workflow not running | Check GitHub Actions → Recent runs for errors |
| AI comments not generating | Verify ZAI_API_KEY in Secrets, check Supabase logs |
| Rate limit errors | Check `ninety_ten_skip` events in Supabase |
| Missing logs | Ensure SUPABASE_SERVICE_KEY has write access |
| Reddit auth fails | Verify REDDIT_* secrets are correct |

### Next Steps for Agents

1. **Monitor Performance:** Check Supabase `content_history` weekly
2. **Adjust Targeting:** Update `TARGET_SUBREDDITS` if results drop
3. **Refine Prompts:** Modify AI prompt in `generate_ai_comment()` based on engagement
4. **Track Karma:** Monitor @Big_Plastic_6393 Reddit profile
5. **Security:** Rotate API keys quarterly

### Important Links

- 🐙 GitHub Repo: https://github.com/fabiofurlano/reddit-safe-automation
- 📊 Supabase Dashboard: [Your Supabase project URL]
- 🤖 z.ai Documentation: https://docs.z.ai/devpack/overview
- 🔗 Reddit PRAW Docs: https://praw.readthedocs.io/
- ⚙️ GitHub Actions: https://github.com/fabiofurlano/reddit-safe-automation/actions

### Notes

- **Never hardcode secrets** - Always use GitHub Secrets
- **Test before deploying** - Manual run first
- **Monitor closely** - Check logs after each run
- **Respect Reddit** - Follow all community guidelines
- **Quality over quantity** - Better to post less than to get banned

---

**Created:** October 2025  
**Status:** Production Ready  
**AI Model:** z.ai GML-4.6  
**Safety Level:** Maximum  
**Last Updated:** October 15, 2025 (Fixed workflow, added AI integration)
