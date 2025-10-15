#!/usr/bin/env python3
"""
Reddit Safe Automation with AI-Generated Comments
Powered by z.ai GML-4.6 + PRAW + Supabase
Production-Ready for Real Karma Building
Following: TWO-COMMENT STRATGGY + 2-3 posts/week limit
"""

import os
import sys
import time
import praw
from datetime import datetime, timezone
import requests
import json
import uuid

# ===================== CONFIGURATION =====================

# Reddit Credentials (from GitHub Secrets)
REDDIT_CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET')
REDDIT_USERNAME = os.environ.get('REDDIT_USERNAME')
REDDIT_PASSWORD = os.environ.get('REDDIT_PASSWORD')
REDDIT_USER_AGENT = os.environ.get('REDDIT_USER_AGENT')

# z.ai GML-4.6 Configuration
ZAI_API_KEY = os.environ.get('ZAI_API_KEY')
ZAI_API_ENDPOINT = "https://api.z.ai/v1/chat/completions"
ZAI_MODEL = "gml-4.6"

# Supabase Configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')

# Website URL
WEBSITE_URL = "https://ai-old-image-restore.site/"

# SAFETY GUARDRAILS (FROM MASTER PROMPT)
RATE_LIMIT_MAX_POSTS_PER_WEEK = 2  # Only 2-3 per week
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
    'Photography',
    'DataHoarder',
    'Darkroom'
]

# Search queries for finding relevant threads
SEARCH_QUERIES = [
    'restore old photo',
    'photo restoration help',
    'AI photo repair',
    'colorize old photo',
    'fix damaged photo',
    'enhance old picture',
    'restore black and white',
    'fix scratched photos',
    'AI upscale image',
    'recover old damaged photo'
]
