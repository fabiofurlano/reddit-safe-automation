
#!/usr/bin/env python3
"""
Reddit Safe Automation with AI-Generated Comments
Powered by z.ai GML-4.6 + PRAW + Supabase
Production-Ready for Real Karma Building
"""

import os
import sys
import time
import praw
from datetime import datetime, timezone
import requests
import json

# ============ CONFIGURATION ============

# Reddit Credentials (from GitHub Secrets)
REDDIT_CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET')
REDDIT_USERNAME = os.environ.get('REDDIT_USERNAME')
REDDIT_PASSWORD = os.environ.get('REDDIT_PASSWORD')
REDDIT_USER_AGENT = os.environ.get('REDDIT_USER_AGENT')

# z.ai GML-4.6 Configuration
ZAI_API_KEY = os.environ.get('ZAI_API_KEY')
ZAI_API_ENDPOINT = "https://api.z.ai/v1/chat/completions"  # Standard z.ai endpoint
ZAI_MODEL = "gml-4.6"

# Supabase Configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')

# Link Policy
LINK_POLICY = os.environ.get('LINK_POLICY', 'FOLLOW_UP_ONLY')

# Website URL
WEBSITE_URL = "https://ai-old-image-restore.site/"

# 🛡️ SAFETY GUARDRAILS
RATE_LIMIT_MAX_POSTS_PER_WEEK = 3
MIN_HOURS_BETWEEN_POSTS = 4
NINETY_TEN_RULE_MAX_PROMOTIONAL_RATIO = 0.10  # 10% max
NINETY_TEN_MIN_ACTIVITY = 10  # Need 10+ posts/comments to check

# Target subreddits (photo restoration niche)
TARGET_SUBREDDITS = [
    'PhotoEditingRequests',
    'AskPhotography',
    'OldPhotos',
    'Colorization',
    'restoration',
    'PhotoRepair',
    'pics',
    'Photography'
]

# Search queries for finding relevant threads
SEARCH_QUERIES = [
    'restore old photo',
    'photo restoration help',
    'AI photo repair',
    'colorize old photo',
    'fix damaged photo',
    'enhance old picture'
]

# ============ LOGGING TO SUPABASE ============

def log_to_supabase(action, platform, details):
    """Log action to Supabase for tracking and analytics"""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print(f"⏭️  Supabase not configured, skipping log: {action}")
        return
    
    try:
        headers = {
            'apikey': SUPABASE_SERVICE_KEY,
            'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'platform': platform,
            'action': action,
            'details': details,
            'performed_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = requests.post(
            f'{SUPABASE_URL}/rest/v1/content_history',
            headers=headers,
            json=payload
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Logged to Supabase: {action}")
        else:
            print(f"⚠️  Failed to log to Supabase: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️  Error logging to Supabase: {str(e)}")

# ============ 🛡️ SAFETY CHECKS ============

def check_ninety_ten_rule(reddit):
    """
    CRITICAL: Enforce 90% engagement / 10% promotion rule
    Reddit bans accounts that post too much promotional content
    """
    try:
        user = reddit.redditor(REDDIT_USERNAME)
        
        # Get recent activity (last 50 posts/comments)
        recent_comments = list(user.comments.new(limit=50))
        recent_submissions = list(user.submissions.new(limit=50))
        
        total_activity = len(recent_comments) + len(recent_submissions)
        
        # Need minimum activity to properly check
        if total_activity < NINETY_TEN_MIN_ACTIVITY:
            print(f"⚠️  NOT ENOUGH HISTORY YET ({total_activity}/{NINETY_TEN_MIN_ACTIVITY}). Allowing early activity.")
            return True
        
        # Count promotional items (those with website link)
        promo_count = 0
        for comment in recent_comments:
            if WEBSITE_URL in comment.body:
                promo_count += 1
        
        for submission in recent_submissions:
            if WEBSITE_URL in submission.selftext:
                promo_count += 1
        
        # Calculate ratio
        promo_ratio = promo_count / total_activity
        
        if promo_ratio > NINETY_TEN_RULE_MAX_PROMOTIONAL_RATIO:
            print(f"\n❌ STOP: 90/10 RULE VIOLATED!")
            print(f"    Promotional ratio: {promo_ratio*100:.1f}% (max: 10%)")
            print(f"    Promotional items: {promo_count}/{total_activity}")
            print(f"    📝 Tip: Help the community with non-promotional posts first!")
            return False
        
        print(f"✅ 90/10 Rule OK: {promo_ratio*100:.1f}% promotional")
        return True
        
    except Exception as e:
        print(f"⚠️  Error checking 90/10 rule: {str(e)}")
        return False  # Fail safely

def check_rate_limits(reddit):
    """Check if we're within safe rate limits"""
    try:
        user = reddit.redditor(REDDIT_USERNAME)
        recent_submissions = list(user.submissions.new(limit=50))
        
        # Count posts in last 7 days
        now = datetime.now(timezone.utc)
        week_ago = now.timestamp() - (7 * 24 * 60 * 60)
        recent_posts = [s for s in recent_submissions if s.created_utc > week_ago]
        
        if len(recent_posts) >= RATE_LIMIT_MAX_POSTS_PER_WEEK:
            print(f"⏱️  RATE LIMIT: Already posted {len(recent_posts)} times this week (max: {RATE_LIMIT_MAX_POSTS_PER_WEEK})")
            return False
        
        # Check time since last post
        if recent_submissions:
            last_post_time = recent_submissions[0].created_utc
            hours_since_last = (now.timestamp() - last_post_time) / 3600
            
            if hours_since_last < MIN_HOURS_BETWEEN_POSTS:
                print(f"⏱️  RATE LIMIT: Last post was {hours_since_last:.1f} hours ago (min: {MIN_HOURS_BETWEEN_POSTS})")
                return False
        
        print(f"✅ Rate limits OK: {len(recent_posts)}/{RATE_LIMIT_MAX_POSTS_PER_WEEK} posts this week")
        return True
        
    except Exception as e:
        print(f"⚠️  Error checking rate limits: {str(e)}")
        return False

# ============ 🤖 AI COMMENT GENERATION ============

def generate_ai_comment(thread_context):
    """
    🤖 Use z.ai GML-4.6 to generate contextual, valuable comments
    This is the CORE of your karma-building strategy
    """
    try:
        thread_title = thread_context.get('title', '')
        thread_body = thread_context.get('body', '')[:500]  # Context limit
        subreddit = thread_context.get('subreddit', '')
        
        # Build prompt for GML-4.6
        prompt = f"""You are a helpful photo restoration expert on Reddit (u/Big_Plastic_6393).

Community: r/{subreddit}
Thread Title: {thread_title}
Thread Content: {thread_body}

Generate a BRIEF, HELPFUL comment (100-200 words max) that:
1. ✅ Answers their question or provides genuine value
2. ✅ Demonstrates real expertise and experience
3. ✅ Does NOT mention my service/website unless they ask "how"
4. ✅ Is natural and conversational (not robotic)
5. ✅ Builds genuine community trust
6. ✅ Follows Reddit community guidelines

CRITICAL RULES:
- Be genuinely helpful FIRST, promotional NEVER
- Only mention the website if they specifically ask how to get help
- Share techniques and knowledge freely
- Be engaging and real

Generate the comment now (just the comment text, no preamble):"""

        # Call z.ai GML-4.6
        headers = {
            'Authorization': f'Bearer {ZAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': ZAI_MODEL,
            'messages': [
                {'role': 'system', 'content': 'You are a helpful Reddit photo restoration expert. Provide valuable, genuine advice.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.7,  # Some creativity but not random
            'max_tokens': 250
        }
        
        print(f"🤖 Calling z.ai GML-4.6 to generate AI comment...")
        response = requests.post(
            ZAI_API_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_comment = result['choices'][0]['message']['content'].strip()
            
            print(f"✅ AI Generated ({len(ai_comment)} chars):\n{ai_comment[:150]}...\n")
            
            # Log to Supabase for analysis
            log_to_supabase(
                action='ai_comment_generated',
                platform='reddit',
                details={
                    'model': ZAI_MODEL,
                    'subreddit': subreddit,
                    'length': len(ai_comment),
                    'tokens_used': result.get('usage', {}).get('total_tokens', 0)
                }
            )
            
            return ai_comment
        else:
            print(f"❌ z.ai API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error generating AI comment: {str(e)}")
        log_to_supabase(
            action='ai_comment_error',
            platform='reddit',
            details={'error': str(e)}
        )
        return None

# ============ THREAD SEARCH ============

def search_relevant_threads(reddit):
    """Search for relevant threads to comment on"""
    print("\n🔍 Searching for relevant threads...")
    relevant_threads = []
    
    try:
        for query in SEARCH_QUERIES[:2]:  # Limit to 2 queries per run
            print(f"   Searching: '{query}'")
            
            for subreddit_name in TARGET_SUBREDDITS[:5]:  # Check first 5 subreddits
                try:
                    subreddit = reddit.subreddit(subreddit_name)
                    
                    # Search recent posts (last 7 days)
                    for submission in subreddit.search(query, time_filter='week', limit=3):
                        # Skip if already commented
                        if any(comment.author == REDDIT_USERNAME for comment in submission.comments.list()[:20]):
                            continue
                        
                        relevant_threads.append({
                            'submission': submission,
                            'subreddit': subreddit_name,
                            'title': submission.title,
                            'body': submission.selftext,
                            'url': submission.url,
                            'score': submission.score
                        })
                        
                        if len(relevant_threads) >= 5:
                            break
                            
                except Exception as e:
                    print(f"   ⚠️  Error searching r/{subreddit_name}: {str(e)}")
                    continue
                
                if len(relevant_threads) >= 5:
                    break
            
            time.sleep(2)  # Rate limiting between searches
        
        print(f"✅ Found {len(relevant_threads)} relevant threads")
        return relevant_threads[:5]  # Return top 5
        
    except Exception as e:
        print(f"❌ Error searching threads: {str(e)}")
        return []

# ============ POSTING COMMENTS ============

def post_helpful_comments(reddit, threads):
    """Post AI-generated, helpful comments on relevant threads"""
    if not threads:
        print("No threads to comment on")
        return 0
    
    comments_posted = 0
    print(f"\n💬 Posting helpful comments...")
    
    for thread in threads[:2]:  # Max 2 comments per run (safety)
        try:
            submission = thread['submission']
            
            print(f"\n   📌 Thread: r/{thread['subreddit']} - '{thread['title'][:60]}...'")
            
            # Generate AI comment
            ai_comment = generate_ai_comment({
                'title': thread['title'],
                'body': thread['body'],
                'subreddit': thread['subreddit']
            })
            
            if not ai_comment:
                print(f"   ⚠️  Failed to generate comment, skipping")
                continue
            
            # Post comment
            comment = submission.reply(ai_comment)
            comments_posted += 1
            
            print(f"   ✅ Comment posted: {comment.permalink}")
            
            # Log to Supabase
            log_to_supabase(
                action='reddit_comment',
                platform='reddit',
                details={
                    'subreddit': thread['subreddit'],
                    'thread_title': thread['title'],
                    'comment_url': f"https://reddit.com{comment.permalink}",
                    'policy': LINK_POLICY,
                    'value_first': True
                }
            )
            
            # Rate limiting between comments
            time.sleep(60)  # 1 minute between comments
            
        except Exception as e:
            print(f"   ❌ Error posting comment: {str(e)}")
            continue
    
    return comments_posted

# ============ MAIN EXECUTION ============

def main():
    """Main automation function"""
    print("=" * 60)
    print("🚀 REDDIT SAFE AUTOMATION - AI-POWERED KARMA BUILDER")
    print(f"⏰ Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"👤 User: u/{REDDIT_USERNAME}")
    print(f"🤖 AI Model: z.ai GML-4.6")
    print(f"📋 Link Policy: {LINK_POLICY}")
    print("=" * 60)
    
    # Validate credentials
    if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD]):
        print("❌ ERROR: Missing Reddit credentials")
        sys.exit(1)
    
    if not ZAI_API_KEY:
        print("❌ ERROR: Missing z.ai API key")
        sys.exit(1)
    
    try:
        # Connect to Reddit
        print("\n🔗 Connecting to Reddit...")
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            username=REDDIT_USERNAME,
            password=REDDIT_PASSWORD,
            user_agent=REDDIT_USER_AGENT
        )
        
        # Verify authentication
        reddit.user.me()
        print(f"✅ Authenticated as u/{reddit.user.me().name}")
        
        # 🛡️ STEP 1: Check 90/10 rule (CRITICAL)
        print("\n🛡️  Checking 90/10 engagement rule...")
        if not check_ninety_ten_rule(reddit):
            print("\n❌ STOPPING: 90/10 Rule Violated")
            log_to_supabase(
                action='ninety_ten_skip',
                platform='reddit',
                details={'reason': 'safety_rule_triggered'}
            )
            sys.exit(0)
        
        # 🛡️ STEP 2: Check rate limits
        print("\n🛡️  Checking rate limits...")
        if not check_rate_limits(reddit):
            print("\n⏱️  STOPPING: Rate limit exceeded")
            log_to_supabase(
                action='rate_limit_skip',
                platform='reddit',
                details={'reason': 'safety_rule_triggered'}
            )
            sys.exit(0)
        
        # 🔍 STEP 3: Search for threads
        threads = search_relevant_threads(reddit)
        
        if not threads:
            print("\n ℹ️  No relevant threads found")
            sys.exit(0)
        
        # 💬 STEP 4: Post helpful comments
        comments_posted = post_helpful_comments(reddit, threads)
        
        # ✅ Summary
        print("\n" + "=" * 60)
        print(f"✅ COMPLETED: Posted {comments_posted} helpful comment(s)")
        print("=" * 60)
        
        # Log completion
        log_to_supabase(
            action='automation_run_complete',
            platform='reddit',
            details={
                'comments_posted': comments_posted,
                'threads_searched': len(threads),
                'policy': LINK_POLICY,
                'safety_checks_passed': True
            }
        )
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        log_to_supabase(
            action='automation_error',
            platform='reddit',
            details={'error': str(e)}
        )
        sys.exit(1)

if __name__ == "__main__":
    main()


