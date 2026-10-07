"""Small client for Instagram's public hashtag media endpoints."""

from datetime import datetime, timedelta, timezone
import re
import threading
import time

import requests


_CACHE_TTL_SECONDS = 300
_cache = {}
_cache_lock = threading.Lock()


def _graph_get(url, params, access_token):
    response = requests.get(
        url,
        params=params,
        headers={'Authorization': f'Bearer {access_token}'},
        timeout=15
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get('error'):
        raise RuntimeError(payload['error'].get('message', 'Meta Graph API error'))
    return payload


def fetch_instagram_trends(access_token, instagram_user_id, hashtags, api_version):
    """Return ranked summaries based on recent hashtag media, not global totals."""
    normalized_hashtags = []
    for hashtag in hashtags.split(','):
        value = hashtag.strip().lstrip('#').lower()
        if value and value not in normalized_hashtags:
            if not re.fullmatch(r'[a-z0-9_]{1,100}', value):
                raise ValueError(f'Invalid Instagram hashtag: {hashtag.strip()}')
            normalized_hashtags.append(value)

    if not normalized_hashtags:
        raise ValueError('Configure at least one hashtag in INSTAGRAM_TREND_HASHTAGS.')
    if len(normalized_hashtags) > 10:
        raise ValueError('Configure no more than 10 hashtags to stay within Meta API limits.')

    cache_key = (instagram_user_id, api_version, tuple(normalized_hashtags))
    now = time.time()
    with _cache_lock:
        cached = _cache.get(cache_key)
        if cached and now - cached['cached_at'] < _CACHE_TTL_SECONDS:
            return cached['result']

    base_url = f'https://graph.facebook.com/{api_version}'
    raw_trends = []
    errors = []
    recent_cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    for hashtag in normalized_hashtags:
        try:
            search = _graph_get(
                f'{base_url}/ig_hashtag_search',
                {'user_id': instagram_user_id, 'q': hashtag},
                access_token
            )
            hashtag_id = search.get('data', [{}])[0].get('id')
            if not hashtag_id:
                errors.append({'hashtag': hashtag, 'message': 'No hashtag results returned.'})
                continue

            media = _graph_get(
                f'{base_url}/{hashtag_id}/recent_media',
                {
                    'user_id': instagram_user_id,
                    'fields': 'id,caption,media_type,permalink,timestamp,like_count,comments_count',
                    'limit': 25
                },
                access_token
            ).get('data', [])

            engagements = []
            recent_count = 0
            media_items = []
            for item in media:
                likes = item.get('like_count', 0) or 0
                comments = item.get('comments_count', 0) or 0
                engagement = likes + comments
                engagements.append(engagement)

                timestamp = item.get('timestamp')
                if timestamp:
                    try:
                        published_at = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        if published_at >= recent_cutoff:
                            recent_count += 1
                    except ValueError:
                        pass

                media_items.append({
                    'caption': item.get('caption', ''),
                    'media_type': item.get('media_type', 'MEDIA'),
                    'permalink': item.get('permalink', ''),
                    'timestamp': timestamp,
                    'engagement': engagement
                })

            raw_trends.append({
                'hashtag': f'#{hashtag}',
                'posts_sampled': len(media),
                'recent_posts_24h': recent_count,
                'avg_engagement': round(sum(engagements) / len(engagements), 1) if engagements else 0,
                'media': media_items[:3]
            })
        except (requests.RequestException, RuntimeError, KeyError, IndexError) as error:
            errors.append({'hashtag': hashtag, 'message': str(error)[:200]})

    if not raw_trends:
        raise RuntimeError('No hashtag data was returned. Check API access and hashtag permissions.')

    max_engagement = max((item['avg_engagement'] for item in raw_trends), default=0) or 1
    max_recent = max((item['recent_posts_24h'] for item in raw_trends), default=0) or 1
    for item in raw_trends:
        engagement_score = item['avg_engagement'] / max_engagement
        recency_score = item['recent_posts_24h'] / max_recent
        item['trend_score'] = round((0.6 * engagement_score + 0.4 * recency_score) * 100, 1)

    result = {
        'trends': sorted(raw_trends, key=lambda item: item['trend_score'], reverse=True),
        'errors': errors,
        'last_updated': datetime.now(timezone.utc).isoformat(),
        'note': 'Relative score from sampled recent public media and engagement; not Instagram-wide post totals.'
    }
    with _cache_lock:
        _cache[cache_key] = {'cached_at': now, 'result': result}
    return result