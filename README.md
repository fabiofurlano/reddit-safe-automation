# Reddit Safe Automation

⟤ Automated Reddit engagement for building karma and safe backlinks with built-in safety guardrails.

## 🌯 Features

- **Safety First**: Respects Reddit's rate limits and community guidelines
- **Value-First**: Educational, helpful comments before any promotional content
- **Smart Targeting**: Finds relevant threads in photo restoration communities
- **Supabase Logging**: Tracks all actions for analysis and compliance
- **Flexible Link Policy**: Control when/if your website link is included

## 🔒 Safety Guardrails

- ✅ **Rate Limiting**: Max 2-3 posts per week
- ✅ **Timing**: Minimum 4-6 hours between posts
- ✅ **90/10 Rule**: 90% community engagement, 10% promotional
- ✅ **Quality Check**: Value-first educational content
- ✅ **Subreddit Research**: Checks rules before posting

## ☺ Configuration

### GitHub Secrets (All Set! ✅)

```
REDDIT_CLIENT_ID         ✅ Set
REDDIT_CLIENT_SECRET     ✅ Set
REDDIT_USERNAME          ✅ Set
REDDIT_PASSWORD          ✅ Set
REDDIT_USER_AGENT        ✅ Set
SUPABASE_URL            ✅ Set
SUPABASE_SERVICE_KEY    ✅ Set
LINK_POLICY             ⏳ Setting now...
```

### Link Policies

- **`FOLLOW_UP_ONLY`** (Recommended): First comment is pure value, link only in follow-ups
- **`ALWAYS`**: Include link in every comment (use cautiously)
- **`NEVER`**: Never include links, karma building only

## 📅 Schedule

Runs automatically twice daily:
- **09:00 UTC** (Morning run)
- **21:00 UTC** (Evening run)

Can also be triggered manually from Actions tab.

## 🎯 Target Communities

- r/PhotoEditingRequests
- r/AskPhotography
- r/OldPhotos
- r/Colorization
- r/estoration
- r/PhotoRepair
- r/pics
- r/Photography

## 📊 Supabase Integration

All actions logged to `content_history` table:
- Comment posts with permalinks
- Rate limit checks
- Search activities
- Errors and safety stops

## 🚀 Usage

### Manual Run
1. Go to **Actions** tab
2. Select "Reddit Safe Automation"
3. Click "Run workflow"

### View Logs
- Check Actions runs for detailed output
- Query Supabase `content_history` table for historical data

## ⚠️ Important Notes

1. **Never spam**: Quality over quantity
2. **Follow subreddit rules**: Always check before posting
3. **Be genuinely helpful**: Real value builds karma
4. **Monitor closely**: Check logs and adjust as needed
5. **Respect the community**: Reddit bans accounts that abuse automation

## 🖧 Maintenance

- Review logs weekly
- Adjust targeting if needed
- Update comment templates for better engagement
- Monitor karma and account health

## 📈 Success Metrics

Track in Supabase:
- Comments posted vs. rate limits
- Subreddit coverage
- Safety checks passed
- Community responses

---

**Created**: October 2025  
**Status**: Production Ready  
**Safety Level**: Maximum
