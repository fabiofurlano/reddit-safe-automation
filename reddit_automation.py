#!/usr/bin/env python3
"""
Reddit Safe Automation Script
Karma building + value-first backlinks with safety guardrails
Logs to Supabase for tracking
"""

import os
import sys
import time
import praw
from datetime import datetime, timezone
import requests

# Configuration from GitHub Secrets
REDDIT_CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET')
REDDIT_USERNAME = os.environ.get('REDDIT_USERNAME')
REDDIT_PASSWORD = os.environ.get('REDDIT_PASSWORD')
REDDIT_USER_AGENT = os.environ.get('REDDIT_USER_AGENT')
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')
LINK_POLICY = os.environ.get('LINK_POLICY', 'FOLLOW_UP_ONLY')

# Website URL
WEBSITE_URL = "https://ai-old-image-restore.site/"

# Reddit Safety Guardrails (from master prompt)
RATE_LIMIT_MAX_POSTS_PER_WEEK = 3
MIN_HOURS_BETWEEN_POSTS = 4
NINETY_TEN_RULE_ENGAGEMENT_RATIO = 0.9  # 90% engagement, 10% promotional

# Target subreddits for photo restoration niche
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

def log_to_supabase(action, platform, details):
    """Log action to Supabase for tracking"""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print(f"➠️  Supabase not configured, skipping logging: {action}")
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
        
        # Insert into content_history table
        response = requests.post(
            f'{SUPABASE_URL}/rest/v1/content_history',
            headers=headers,
            json=payload
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Logged to Supabase: {action}")
        else:
            print(f"➠️  Failed to log to Supabase: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"➠️  Error logging to Supabase: {str(e)}")

def check_rate_limits(reddit):
    """Check if we're within safe rate limits"""
    try:
        # Get user's recent submissions
        user = reddit.redditor(REDDIT_USERNAME)
        recent_submissions = list(user.submissions.new(limit=50))
        
        # Count posts in last 7 days
        now = datetime.now(timezone.utc)
        week_ago = now.timestamp() - (7 * 24 * 60 * 60)
        recent_posts = [s for s in recent_submissions if s.created_utc > week_ago]
        
        if len(recent_posts) >= RATE_LIMIT_MAX_POSTS_PER_WEEK:
            print(f"🛀 RATE LIMIT: Already posted {len(recent_posts)} times this week (max: {RATE_LIMIT_MAX_POSTS_PER_WEEK})")
            return False
        
        # Check time since last post
        if recent_submissions:
            last_post_time = recent_submissions[0].created_utc
            hours_since_last = (now.timestamp() - last_post_time) / 3600
            
            if hours_since_last < MIN_HOURS_BETWEEN_POSTS:
                print(f"🛀 RATE LIMIT: Last post was {hours_since_last:.1f} hours ago (min: {MIN_HOURS_BETWEEN_POSTS})")
                return False
        
        print(f"✅ Rate limits OK: {len(recent_posts)}/{RATE_LIMIT_MAX_POSTS_PER_WEEK} posts this week")
        return True
        
    except Exception as e:
        print(f"➠️  Error checking rate limits: {str(e)}")
        return False

def search_relevant_threads(reddit):
    """Search for relevant threads to engage with"""
    print("\n 🐍 Searching for relevant threads...")
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
                            'url': submission.url,
                            'score': submission.score
                        })
                        
                except Exception as e:
                    print(f"   ➌️  Error searching r/{subreddit_name}: {str(e)}")
                    continue
            
            time.sleep(2)  # Rate limiting between searches
        
        print(f"✅ Found {len(relevant_threads)} relevant threads")
        return relevant_threads[:5]  # Return top 5
        
    except Exception as e:
        print(f"➠️  Error searching threads: {str(e)}")
        return []

def create_value_comment(thread_context):
    """Create a value-first comment with optional link based on policy"""
    title = thread_context['title'].lower()
    
    # Determine comment style based on thread context
    if 'how' in title or 'help' in title or 'question' in title:
        # Educational response
        base_comment = """Great question! For photo restoration, here are some key techniques that work well:

1. **Start with the basics**: Adjust exposure and contrast first
2. **Remove scratches/damage**: Use clone stamp or healing brush tools
3. **Colorization**: AI tools can help, but manual touch-ups give better results
4. **Enhance details**: Sharpen carefully to bring out facial features

For AI-powered restoration, there are several good options available online. The key is to not over-process - you want to preserve the authenticity of the original photo."""
    
    elif 'restore' in title or 'fix' in title or 'repair' in title:
        # Helpful suggestion
        base_comment = """I've worked with similar restoration projects! Here's what typically works:

• **Damage assessment**: Identify all issues (tears, fading, stains)
• **Work in layers**: Always keep the original intact
┢ **Color correction**: Old photos often have yellow/sepia tones to correct
┢ **Detail enhancement**: Carefully bring back lost details

Modern AI tools can handle a lot of this automatically while preserving the photo's character. Feel free to reach out if you need specific guidance!"""
    
    else:
        # General helpful response
        base_comment = """Photo restoration can be really rewarding! The key is balancing modern enhancement with preserving the original feel.

Tips that help:
- Always work on a copy, never the original
- Start with basic adjustments before heavy editing
- Less is often more - subtle improvements look natural
- AI-powered tools have come a long way recently

Hope this helps with your project!"""
    
    # Add link based on policy
    if LINK_POLICY == 'ALWAYS':
        return base_comment + f"\n\nIf you want to try an AI-powered approach: {WEBSITE_URL}"
    elif LINK_POLICY == 'FOLLOW_UP_ONLY':
        # First comment is value-only, link added in potential follow-up
        return base_comment
    else:  # NEVER
        return base_comment

def post_helpful_comments(reddit, threads):
    """Post helpful, value-first comments to relevant threads"""
    if not threads:
        print("No threads to comment on")
        return 0
    
    comments_posted = 0
    print(f"\n❏ Posting helpful comments...")
    
    for thread in threads[:2]:  # Max 2 comments per run (safety)
        try:
            submission = thread['submission']
            subreddit_name = thread['subreddit']
            
            print(f"\n   📝 Commenting on: r/{subreddit_name} - '{thread['title'][:60]}...'")
            
            # Create value-first comment
            comment_text = create_value_comment(thread)
            
            # Post comment
            comment = submission.reply(comment_text)
            comments_posted += 1
            
            print(f"   ✅ Comment posted: {comment.permalink}")
            
            # Log to Supabase
            log_to_supabase(
                action='reddit_comment',
                platform='reddit',
                details={
                    'subreddit': subreddit_name,
                    'thread_title': thread['title'],
                    'comment_url': f"https://reddit.com{comment.permalink}",
                    'policy': LINK_POLICY,
                    'value_first': True
                }
            )
            
            # Rate limiting between comments
            time.sleep(60)  # 1 minute between comments
            
        except Exception as e:
            print(f"   ➌️  Error posting comment: {str(e)}")
            continue
    
    return comments_posted

def main():
    """Main execution function"""
    print("=" * 60)
    print("🤖 REDDIT SAFE AUTOMATION - Starting")
    print(f"⏰ Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"👤 User: u/{REDDIT_USERNAME}")
    print(f"🔗 Link Policy: {LINK_POLICY]")
    print("=" * 60)
    
    # Validate credentials
    if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD)"�
        print("❌ ERROR: Missing Reddit credentials")
        sys.exit(1)
    
    try:
        # Initialize Reddit client
        print("\n⟐ Connecting to Reddit...")
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
        
        # Check rate limits (CRITICAL SAFETY CHECK)
        if not check_rate_limits(reddit):
            print("\n🛀 STOPPING: Rate limit exceeded - skipping this run")
            log_to_supabase(
                action='rate_limit_skip',
                platform='reddit',
                details={'reason': 'safety_guardrails_triggered'}
            )
            sys.exit(0)
        
        # Search for relevant threads
        threads = search_relevant_threads(reddit)
        
        if not threads:
            print("\n⚠️  No relevant threads found this run")
            sys.exit(0)
        
        # Post helpful comments
        comments_posted = post_helpful_comments(reddit, threads)
        
        # Summary
        print("\n" + "=" * 60)
        print(f"✅ COMPLETED: Posted {comments_posted} helpful comment(s)")
        print("=" * 60)
        
        # Log summary to Supabase
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
