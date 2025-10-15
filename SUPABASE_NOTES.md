# 📊 Supabase Integration Notes

**Updated**: October 15, 2025  
**Status**: ✅ Production Ready  
**Database**: `content_history` (PostgreSQL)

---

## 🗂️ Database Schema

### Table: `content_history`

Holds **all actions** from Reddit automation:
- Comment generations
- Posts
- Errors
- Safety check triggers
- Rate limit skips

Fields: `id`, `platform`, `action`, `details` (JSONB), `performed_at`

---

## 📝 Log Entry Types

### 1: AI Comment Generated
{"action": "ai_comment_generated", "platform": "reddit", "details": {"model": "gml-4.6", "subreddit": "PhotoEditingRequests", "length": 187, "tokens_used": 234}}

### 2: Reddit Comment Posted
{"action": "reddit_comment", "platform": "reddit", "details": {"subreddit": "PhotoEditingRequests", "comment_url": "https://reddit.com/r/PhotoEditingRequests/comments/xxx/_/yyy"}}

### 3: Safety Check Triggered (90/10)
{"action": "ninety_ten_skip", "platform": "reddit", "details": {"reason": "safety_rule_triggered", "promotional_ratio": 0.15}}

### 4: Rate Limit Exceeded
{"action": "rate_limit_skip", "platform": "reddit", "details": {"reason": "safety_rule_triggered"}}

### 5: API Errors
{"action": "ai_comment_error", "platform": "reddit", "details": {"error": "Request failed: 429"}}

---

## 📍 Useful Queries for Monitoring

### Get Recent Activity (Last 24 Hours)

```sql
SELECT action, details, performed_at
FROM content_history
WHERE platform = 'reddit' AND performed_at > NOW() - INTERVAL '24 hours'
ORDER BY performed_at DES; 
```

### Count Comments Posted This Week

```sql
SELECT COUNT(*) as comments_posted
FROM content_history
WHERE action = 'reddit_comment' AND performed_at > NOW() - INTERVAL '7 days';
```

### Track Promotional Ratio

```sql
SELECT performed_at, details
FROM content_history
WHERE action = 'ninety_ten_skip' AND platform = 'reddit'
ORDER BY performed_at DESC LIMIT 20;
```

### Error Analysis

```sql
SELECT details, COUNT()) as error_count
FROM content_history
WHERE action LIKE '%error%' AND platform = 'reddit'
GROUP BY bYdetails
ORDER BY error_count DESC;

```

---

## 📊 Analytics Dashboard Ideas

### Daily Activity Summary

```sql
SELECT DATE(performed_at) as date, COUNT(*) as actions,
  SUM(CASE WHEN action = 'reddit_comment' THEN 1 ELSE 0 END) as comments
FROM content_history
WHERE platform = 'reddit'
GROUP BY DATE
created_at) ORDER BY date DESC;

```

### Success Rate

```sql
SELECT ROUND(100.0 * COUNT(CASE WHEN action = 'reddit_comment' THEN 1 END) / 
 NULLIF(COUNT(CASE WHEN action = 'ai_comment_generated' THEN 1 END), 0), 2)
 as success_rate_percent
FROM content_history
WHERE platform = 'reddit' AND performed_at > NOW() - INTERVAL '7 days';

```

---

## 🔐 Cross-Platform Support

∥ This database will hold data for:
- Reddit (Current)
- Facebook (Planned)
- LinkedIn (Planned)
- X/Twitter (Planned)
 - Other platforms
_