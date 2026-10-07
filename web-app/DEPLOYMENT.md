# Web App Deployment

## Run locally

From the repository root, install the web app dependencies and start Flask:

```powershell
py -m pip install -r web-app/requirements.txt
$env:AISA_API_TOKEN = "your-aisa-token"
py web-app/app.py
```

Open `http://localhost:5000`. The existing Spark result folders and `dataset/social_media.csv` need to be present for the offline dashboard panels. Without social API credentials, the live-trends panel recalculates the bundled CSV and labels it as historical sample data, not a live platform feed.

## Deploy to Render

1. Push this repository to a GitHub repository.
2. In Render, choose **New +** then **Blueprint**, and select that repository. Render will read `render.yaml` from the repository root.
3. The Blueprint selects Render's free web-service plan and does not require API credentials to deploy. Without a live provider, the app analyzes its bundled sample dataset.
4. Deploy. Render builds from the repository root so the dataset and checked-in analysis outputs are available to the app.

The hosted app uses Gunicorn. `PROJECT_ROOT` is resolved from the app's location, so it does not depend on the original Windows/WSL path.

## Instagram API setup

Instagram hashtag search is not an unauthenticated public trending API. Create a Meta app, connect an Instagram Business or Creator account, obtain an access token and Instagram account ID, and request `instagram_basic` plus the approved Instagram Public Content Access feature. Meta reviews are required for public hashtag content access.

The provider order is Meta Instagram Graph API, Aisa Instagram trending Reels, optional Apify Instagram actor, Aisa Twitter trends, then optional X recent search. After deployment, add `AISA_API_TOKEN` under the Render service's Environment settings to enable Aisa; add credentials for any other fallback you want available. The app skips providers without credentials and moves to the next provider when one fails. Never commit tokens.

The Aisa integration calls `GET https://api.aisa.one/apis/v1/instagram/reels/trending` and `GET https://api.aisa.one/apis/v1/twitter/trends?count=30`, sending `Authorization: Bearer $AISA_API_TOKEN`. Set `AISA_TWITTER_TRENDS_COUNT` to adjust the requested count (1-100). The dashboard normalizes common response envelopes and metric field names; exact metrics shown depend on the fields Aisa returns for your account and plan.

For the external Instagram fallback, set `APIFY_API_TOKEN`, `APIFY_INSTAGRAM_ACTOR_ID`, and `APIFY_INSTAGRAM_INPUT`. Choose an Apify actor whose use complies with its terms and the platform's terms. The actor input must be valid JSON and match that actor's schema; its result should be an array of post objects containing hashtags/caption, likes/comments, timestamp, and permalink/url fields. Output field names from common actor conventions are normalized where possible, but actor schemas vary.

For X fallback, set `X_API_BEARER_TOKEN`. X recent search access is subject to X API plan availability, rate limits, and query rules. `X_TREND_QUERY` controls the recent-search query, and `X_TREND_HASHTAGS` controls which hashtags are grouped in results.

Set `INSTAGRAM_TREND_HASHTAGS` to a comma-separated list (for example `ai,travel,fashion`). The app intentionally limits this to 10 hashtags per configured Meta request, below Meta's limit of 30 unique hashtag searches per rolling seven-day period. Results come from a short-lived sample of recent public media; scores compare sampled engagement and activity among the configured hashtags. They are not global Instagram post totals or a worldwide trending ranking. Each successful provider response includes automatic analysis identifying the strongest relative score, average sampled engagement, and 24-hour sample activity. Responses are cached for five minutes.

For production, configure a long-lived token and arrange token renewal before it expires. If Meta access is not configured or approved, the section reports that it is unavailable while the rest of the dashboard continues to work.