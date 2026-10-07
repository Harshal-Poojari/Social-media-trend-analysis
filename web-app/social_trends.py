"""Instagram-first trend providers with optional external and X fallbacks."""

import csv
import json
import os
import re
from datetime import datetime, timedelta, timezone

import requests

from instagram_trends import fetch_instagram_trends


def _normalize_external_instagram_items(items, hashtags):
    by_hashtag = {tag.lower().lstrip('#'): [] for tag in hashtags}
    for item in items:
        caption = str(item.get('caption') or item.get('text') or item.get('description') or '')
        explicit_tags = item.get('hashtags', [])
        if isinstance(explicit_tags, str):
            explicit_tags = re.findall(r'[a-zA-Z0-9_]+', explicit_tags)
        haystack = (caption + ' ' + ' '.join(map(str, explicit_tags))).lower()
        for hashtag in by_hashtag:
            if re.search(rf'(?<![a-z0-9_])#?{re.escape(hashtag)}(?![a-z0-9_])', haystack):
                by_hashtag[hashtag].append(item)

    trends = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    for hashtag, matched in by_hashtag.items():
        engagements = []
        recent_count = 0
        media = []
        for item in matched:
            likes = item.get('like_count', item.get('likes', item.get('likesCount', item.get('likeCount', 0)))) or 0
            comments = item.get('comments_count', item.get('comments', item.get('commentsCount', item.get('commentCount', 0)))) or 0
            engagement = int(likes) + int(comments)
            engagements.append(engagement)
            timestamp = item.get('timestamp') or item.get('publishedAt') or item.get('createdAt') or item.get('created_at')
            if timestamp:
                try:
                    published = datetime.fromisoformat(str(timestamp).replace('Z', '+00:00'))
                    if published >= cutoff:
                        recent_count += 1
                except ValueError:
                    pass
            media.append({
                'caption': str(item.get('caption') or item.get('text') or item.get('description') or ''),
                'media_type': str(item.get('media_type') or item.get('type') or 'POST'),
                'permalink': str(item.get('permalink') or item.get('url') or item.get('postUrl') or ''),
                'timestamp': timestamp,
                'engagement': engagement
            })
        trends.append({
            'hashtag': f'#{hashtag}',
            'posts_sampled': len(matched),
            'recent_posts_24h': recent_count,
            'avg_engagement': round(sum(engagements) / len(engagements), 1) if engagements else 0,
            'media': media[:3]
        })
    return _score_trends(trends)


def _score_trends(trends):
    max_engagement = max((trend['avg_engagement'] for trend in trends), default=0) or 1
    max_recent = max((trend['recent_posts_24h'] for trend in trends), default=0) or 1
    for trend in trends:
        engagement_score = trend['avg_engagement'] / max_engagement
        activity_score = trend['recent_posts_24h'] / max_recent
        trend['trend_score'] = round((0.6 * engagement_score + 0.4 * activity_score) * 100, 1)
    return sorted(trends, key=lambda trend: trend['trend_score'], reverse=True)


def _extract_items(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ('data', 'result', 'response', 'results', 'trends', 'trending', 'items', 'reels', 'trending_reels', 'posts'):
            value = payload.get(key)
            if isinstance(value, list):
                return value
            if isinstance(value, dict):
                nested = _extract_items(value)
                if nested:
                    return nested
    return []


def _number_from(item, *keys):
    for key in keys:
        value = item.get(key)
        if value is not None:
            try:
                return int(float(value))
            except (TypeError, ValueError):
                continue
    return 0


def _aisa_get(url, token, params=None):
    response = requests.get(
        url,
        params=params,
        headers={'Authorization': f'Bearer {token}'},
        timeout=20
    )
    response.raise_for_status()
    return response.json()


def _run_aisa_instagram():
    token = os.getenv('AISA_API_TOKEN')
    payload = _aisa_get('https://api.aisa.one/apis/v1/instagram/reels/trending', token)
    items = _extract_items(payload)
    if not items:
        raise RuntimeError('Aisa returned no Instagram trending Reels.')

    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    trends = []
    for index, item in enumerate(items[:30], start=1):
        caption = str(item.get('caption') or item.get('text') or item.get('title') or item.get('description') or '')
        likes = _number_from(item, 'like_count', 'likes', 'likesCount', 'likeCount')
        comments = _number_from(item, 'comments_count', 'comments', 'commentsCount', 'commentCount')
        views = _number_from(item, 'play_count', 'view_count', 'views', 'plays', 'video_views')
        engagement = likes + comments
        timestamp = item.get('timestamp') or item.get('taken_at') or item.get('created_at') or item.get('published_at')
        recent = 0
        if timestamp:
            try:
                published = datetime.fromisoformat(str(timestamp).replace('Z', '+00:00'))
                recent = int(published >= cutoff)
            except (ValueError, TypeError):
                pass
        permalink = item.get('permalink') or item.get('url') or item.get('link') or item.get('video_url') or ''
        extracted_tag = re.search(r'#[a-zA-Z0-9_]+', caption)
        label = extracted_tag.group(0) if extracted_tag else f'Reel {index}'
        trends.append({
            'hashtag': label,
            'title': label,
            'posts_sampled': 1,
            'recent_posts_24h': recent,
            'avg_engagement': engagement,
            'analysis_metric': views or engagement,
            'analysis_metric_label': 'video views' if views else 'likes + comments',
            'analysis_activity': recent,
            'analysis_activity_label': 'reels published in the last 24 hours',
            'summary': f'{views:,} views · {likes:,} likes · {comments:,} comments' if views else f'{likes:,} likes · {comments:,} comments',
            'media': [{
                'caption': caption,
                'media_type': 'REEL',
                'permalink': str(permalink),
                'timestamp': timestamp,
                'engagement': engagement
            }]
        })

    max_metric = max((trend['analysis_metric'] for trend in trends), default=0) or 1
    for trend in trends:
        trend['trend_score'] = round(trend['analysis_metric'] / max_metric * 100, 1)
    return {
        'platform': 'Instagram',
        'source': 'Aisa trending Reels API',
        'trends': sorted(trends, key=lambda trend: trend['trend_score'], reverse=True)[:12],
        'note': 'Trending Reels returned by Aisa; metrics depend on the fields exposed by that API.'
    }


def _run_aisa_twitter():
    token = os.getenv('AISA_API_TOKEN')
    count = min(max(int(os.getenv('AISA_TWITTER_TRENDS_COUNT', '30')), 1), 100)
    payload = _aisa_get(
        'https://api.aisa.one/apis/v1/twitter/trends',
        token,
        params={'count': count}
    )
    items = _extract_items(payload)
    if not items:
        raise RuntimeError('Aisa returned no Twitter trends.')

    trends = []
    for index, item in enumerate(items[:count], start=1):
        name = str(item.get('name') or item.get('hashtag') or item.get('trend') or item.get('query') or item.get('title') or f'Trend {index}')
        volume = _number_from(item, 'tweet_volume', 'tweetVolume', 'volume', 'post_count', 'posts_count', 'count', 'tweets')
        url = item.get('url') or item.get('link') or ''
        trends.append({
            'hashtag': name if name.startswith('#') else f'#{name}',
            'title': name,
            'posts_sampled': volume,
            'recent_posts_24h': 0,
            'avg_engagement': 0,
            'analysis_metric': volume,
            'analysis_metric_label': 'provider-reported tweet volume',
            'summary': f'Provider-reported volume: {volume:,}' if volume else f'Trend rank: {index}',
            'trend_score': round(volume / max((_number_from(row, 'tweet_volume', 'tweetVolume', 'volume', 'post_count', 'posts_count', 'count', 'tweets') for row in items), default=0) * 100, 1) if volume else round((count - index + 1) / count * 100, 1),
            'media': [{
                'caption': str(item.get('description') or item.get('name') or item.get('hashtag') or name),
                'media_type': 'TREND',
                'permalink': str(url),
                'timestamp': None,
                'engagement': volume
            }] if url else []
        })
    return {
        'platform': 'X / Twitter',
        'source': 'Aisa Twitter Trends API',
        'trends': sorted(trends, key=lambda trend: trend['trend_score'], reverse=True),
        'note': 'Trend names and volumes reported by Aisa; volume availability depends on the API response.'
    }


def _run_apify_instagram(hashtags):
    token = os.getenv('APIFY_API_TOKEN')
    actor_id = os.getenv('APIFY_INSTAGRAM_ACTOR_ID')
    if not token or not actor_id:
        raise RuntimeError('Apify Instagram fallback is not configured.')
    try:
        actor_input = json.loads(os.getenv('APIFY_INSTAGRAM_INPUT', '{}'))
    except json.JSONDecodeError as error:
        raise RuntimeError('APIFY_INSTAGRAM_INPUT must be valid JSON.') from error
    actor_input.setdefault('hashtags', hashtags)
    response = requests.post(
        f'https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items',
        params={'clean': 'true', 'format': 'json'},
        headers={'Authorization': f'Bearer {token}'},
        json=actor_input,
        timeout=60
    )
    response.raise_for_status()
    items = response.json()
    if not isinstance(items, list):
        raise RuntimeError('Apify actor response must be a JSON array of posts.')
    trends = _normalize_external_instagram_items(items, hashtags)
    if not any(trend['posts_sampled'] for trend in trends):
        raise RuntimeError('Apify returned no posts matching the configured hashtags.')
    return {
        'platform': 'Instagram',
        'source': 'Apify actor',
        'trends': trends,
        'note': 'Recent Instagram posts returned by your configured Apify actor; coverage and fields depend on that actor.'
    }


def _run_x_recent_search():
    bearer_token = os.getenv('X_API_BEARER_TOKEN')
    if not bearer_token:
        raise RuntimeError('X API fallback is not configured.')
    query = os.getenv('X_TREND_QUERY', '(#ai OR #travel OR #fashion OR #food OR #fitness) -is:retweet')
    response = requests.get(
        'https://api.x.com/2/tweets/search/recent',
        params={
            'query': query,
            'max_results': 100,
            'tweet.fields': 'created_at,public_metrics,entities'
        },
        headers={'Authorization': f'Bearer {bearer_token}'},
        timeout=20
    )
    response.raise_for_status()
    payload = response.json()
    tweets = payload.get('data', [])
    configured_tags = [tag.strip().lstrip('#').lower() for tag in os.getenv(
        'X_TREND_HASHTAGS', 'ai,travel,fashion,food,fitness'
    ).split(',') if tag.strip()]
    by_hashtag = {tag: [] for tag in configured_tags}
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    for tweet in tweets:
        tweet_tags = {
            str(tag.get('tag', '')).lower()
            for tag in tweet.get('entities', {}).get('hashtags', [])
        }
        metrics = tweet.get('public_metrics', {})
        engagement = sum(int(metrics.get(field, 0) or 0) for field in (
            'like_count', 'reply_count', 'retweet_count', 'quote_count'
        ))
        timestamp = tweet.get('created_at')
        recent = False
        if timestamp:
            try:
                recent = datetime.fromisoformat(timestamp.replace('Z', '+00:00')) >= cutoff
            except ValueError:
                pass
        for tag in tweet_tags.intersection(by_hashtag):
            by_hashtag[tag].append({
                'caption': tweet.get('text', ''),
                'media_type': 'POST',
                'permalink': f"https://x.com/i/web/status/{tweet.get('id', '')}" if tweet.get('id') else '',
                'timestamp': timestamp,
                'engagement': engagement,
                'recent': recent
            })

    trends = []
    for hashtag, posts in by_hashtag.items():
        engagements = [post['engagement'] for post in posts]
        trends.append({
            'hashtag': f'#{hashtag}',
            'posts_sampled': len(posts),
            'recent_posts_24h': sum(post['recent'] for post in posts),
            'avg_engagement': round(sum(engagements) / len(engagements), 1) if engagements else 0,
            'media': [{key: value for key, value in post.items() if key != 'recent'} for post in posts[:3]]
        })
    return {
        'platform': 'X',
        'source': 'X API recent search',
        'trends': _score_trends(trends),
        'note': 'Recent X posts matching your search query; scores compare only the returned sample.'
    }


def _automatic_insights(trends):
    active = [trend for trend in trends if trend['posts_sampled'] or trend.get('trend_score', 0) > 0]
    if not active:
        return ['No matching posts were returned for the configured hashtags.']
    top_score = max(active, key=lambda trend: trend['trend_score'])
    insights = [f"{top_score['hashtag']} leads the configured sample with a relative trend score of {top_score['trend_score']}/100."]
    metric_trends = [trend for trend in active if trend.get('analysis_metric')]
    if metric_trends:
        most_metric = max(metric_trends, key=lambda trend: trend['analysis_metric'])
        metric_label = most_metric.get('analysis_metric_label', 'average sampled engagement')
        insights.append(f"{most_metric['hashtag']} has the highest {metric_label} ({most_metric['analysis_metric']:,.1f}).")
    elif not any('analysis_metric' in trend for trend in active):
        most_engaging = max(active, key=lambda trend: trend['avg_engagement'])
        insights.append(f"{most_engaging['hashtag']} has the highest average sampled engagement ({most_engaging['avg_engagement']:,.1f} interactions per post).")
    activity_trends = [trend for trend in active if trend.get('analysis_activity_label')]
    if activity_trends:
        most_active = max(activity_trends, key=lambda trend: trend.get('analysis_activity', 0))
        insights.append(f"{most_active['hashtag']} has the most {most_active['analysis_activity_label']} ({most_active.get('analysis_activity', 0)}).")
    elif any(trend.get('recent_posts_24h') for trend in active):
        most_active = max(active, key=lambda trend: trend['recent_posts_24h'])
        insights.append(f"{most_active['hashtag']} has the most sampled posts from the last 24 hours ({most_active['recent_posts_24h']}).")
    return insights


def _run_local_dataset_analysis(dataset_path, provider_errors=None):
    if not dataset_path or not os.path.isfile(dataset_path):
        raise RuntimeError('The local social media sample dataset is unavailable.')

    grouped = {}
    dates = []
    with open(dataset_path, encoding='utf-8', newline='') as dataset_file:
        for row in csv.DictReader(dataset_file):
            try:
                post_date = datetime.fromisoformat(row.get('date', '')).date()
            except ValueError:
                post_date = None
            if post_date:
                dates.append(post_date)
            try:
                engagement = sum(int(row.get(field) or 0) for field in ('likes', 'shares', 'comments'))
            except ValueError:
                engagement = 0
            tags = set(re.findall(r'#[a-zA-Z0-9_]+', row.get('hashtags', '') or row.get('text', '')))
            for tag in tags:
                entry = grouped.setdefault(tag.lower(), {'engagements': [], 'total_engagement': 0, 'posts': []})
                entry['engagements'].append(engagement)
                entry['total_engagement'] += engagement
                entry['posts'].append({
                    'caption': row.get('text', ''),
                    'media_type': 'SAMPLE POST',
                    'permalink': '',
                    'timestamp': row.get('date'),
                    'engagement': engagement
                })

    if not grouped:
        raise RuntimeError('The local dataset contains no hashtagged posts to analyze.')

    latest_date = max(dates) if dates else None
    max_posts = max(len(entry['posts']) for entry in grouped.values()) or 1
    max_engagement = max(entry['total_engagement'] for entry in grouped.values()) or 1
    trends = []
    for hashtag, entry in grouped.items():
        avg_engagement = round(sum(entry['engagements']) / len(entry['engagements']), 1)
        latest_count = sum(
            1 for post in entry['posts']
            if latest_date and post['timestamp'] == latest_date.isoformat()
        )
        trend_score = round((
            0.4 * len(entry['posts']) / max_posts +
            0.6 * entry['total_engagement'] / max_engagement
        ) * 100, 1)
        trends.append({
            'hashtag': hashtag,
            'title': hashtag,
            'posts_sampled': len(entry['posts']),
            'recent_posts_24h': 0,
            'avg_engagement': avg_engagement,
            'analysis_metric': avg_engagement,
            'analysis_metric_label': 'average sample engagement',
            'analysis_activity': latest_count,
            'analysis_activity_label': f'posts on latest sample date ({latest_date.isoformat()})' if latest_date else 'posts on latest sample date',
            'summary': f"{len(entry['posts'])} sample posts · {avg_engagement:,.1f} average likes + shares + comments",
            'trend_score': trend_score,
            'media': entry['posts'][:3]
        })

    date_span = (
        f"{min(dates).isoformat()} to {latest_date.isoformat()}"
        if dates else 'dates unavailable'
    )
    failed_provider_note = ' Configured live providers were unavailable.' if provider_errors else ''
    return {
        'platform': 'Historical sample dataset',
        'source': 'Bundled CSV · not a live social feed',
        'trends': sorted(trends, key=lambda trend: trend['trend_score'], reverse=True)[:12],
        'automatic_insights': _automatic_insights(trends),
        'fallback_errors': provider_errors or [],
        'last_updated': datetime.now(timezone.utc).isoformat(),
        'note': f'Recalculated now from bundled sample posts dated {date_span}. This is not live Instagram or X data.{failed_provider_note}'
    }


def fetch_social_trends(access_token, instagram_user_id, hashtags, api_version, dataset_path=None):
    """Try official Instagram, Aisa/Apify Instagram, then Aisa/X trends."""
    candidates = []
    if access_token and instagram_user_id:
        candidates.append(('Meta Graph API', lambda: {
            'platform': 'Instagram',
            'source': 'Meta Instagram Graph API',
            **fetch_instagram_trends(access_token, instagram_user_id, hashtags, api_version)
        }))
    if os.getenv('AISA_API_TOKEN'):
        candidates.append(('Aisa Instagram Reels', _run_aisa_instagram))
    if os.getenv('APIFY_API_TOKEN') and os.getenv('APIFY_INSTAGRAM_ACTOR_ID'):
        candidates.append(('Apify actor', lambda: _run_apify_instagram(hashtags.split(','))))
    if os.getenv('AISA_API_TOKEN'):
        candidates.append(('Aisa Twitter Trends', _run_aisa_twitter))
    if os.getenv('X_API_BEARER_TOKEN'):
        candidates.append(('X API', _run_x_recent_search))

    if not candidates:
        return _run_local_dataset_analysis(dataset_path)

    errors = []
    for provider_name, provider in candidates:
        try:
            result = provider()
            result['automatic_insights'] = _automatic_insights(result['trends'])
            result['last_updated'] = datetime.now(timezone.utc).isoformat()
            result['fallback_errors'] = errors
            return result
        except Exception as error:
            errors.append({'provider': provider_name, 'message': str(error)[:200]})
    return _run_local_dataset_analysis(dataset_path, errors)