#!/usr/bin/env python3
"""
Social Media Trend Analysis - Web Application
Flask app to run analysis and display results with download options
"""

from flask import Flask, render_template, jsonify, send_file, after_this_request
import os
import subprocess
import shutil
from datetime import datetime
import requests
from collections import Counter
import re
import random
from social_trends import fetch_social_trends

app = Flask(__name__)

# Resolve paths from this file so the app works locally and when deployed.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(PROJECT_ROOT, 'dataset', 'social_media.csv')
PYSPARK_SCRIPT = os.path.join(PROJECT_ROOT, 'pyspark-scripts', 'trend_analysis.py')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'pyspark-scripts', 'output')

# Debug: Print paths
print(f"PROJECT_ROOT: {PROJECT_ROOT}")
print(f"OUTPUT_DIR: {OUTPUT_DIR}")
print(f"OUTPUT_DIR exists: {os.path.exists(OUTPUT_DIR)}")

@app.route('/')
def index():
    """Home page with dashboard"""
    return render_template('index.html')

@app.route('/api/status')
def status():
    """Check if analysis has been run"""
    files_exist = {
        'hashtag_analysis': os.path.exists(os.path.join(OUTPUT_DIR, 'hashtag_analysis.csv')),
        'platform_analysis': os.path.exists(os.path.join(OUTPUT_DIR, 'platform_analysis.csv')),
        'daily_trends': os.path.exists(os.path.join(OUTPUT_DIR, 'daily_trends.csv')),
        'top_posts': os.path.exists(os.path.join(OUTPUT_DIR, 'top_posts.csv')),
        'user_analysis': os.path.exists(os.path.join(OUTPUT_DIR, 'user_analysis.csv'))
    }
    return jsonify({
        'status': 'ready' if all(files_exist.values()) else 'not_run',
        'files': files_exist
    })

@app.route('/api/run-analysis', methods=['POST'])
def run_analysis():
    """Run PySpark analysis"""
    try:
        # Since PySpark was already run in WSL2, just return success to display results
        return jsonify({
            'success': True,
            'message': 'Analysis results loaded successfully!',
            'note': 'PySpark analysis was previously run in WSL2. Displaying existing results.'
        })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/results/<analysis_type>')
def get_results(analysis_type):
    """Get analysis results as JSON - read from real PySpark output files"""
    csv_path = os.path.join(OUTPUT_DIR, f'{analysis_type}.csv')
    
    if not os.path.exists(csv_path):
        return jsonify({'error': f'Analysis not found at {csv_path}'}), 404
    
    # Find the part-00000 file
    part_file = None
    try:
        for file in os.listdir(csv_path):
            if file.startswith('part-00000') and file.endswith('.csv'):
                part_file = os.path.join(csv_path, file)
                break
    except Exception as e:
        return jsonify({'error': f'Error reading directory: {str(e)}'}), 404
    
    if not part_file:
        return jsonify({'error': 'No data file found'}), 404
    
    # Read CSV and convert to JSON
    import pandas as pd
    try:
        df = pd.read_csv(part_file)
        return jsonify({
            'data': df.to_dict(orient='records'),
            'columns': df.columns.tolist()
        })
    except Exception as e:
        return jsonify({'error': f'Error reading CSV: {str(e)}'}), 500

@app.route('/download/<analysis_type>')
def download_csv(analysis_type):
    """Download analysis results as CSV"""
    csv_path = os.path.join(OUTPUT_DIR, f'{analysis_type}.csv')
    
    if not os.path.exists(csv_path):
        return 'Analysis not found', 404
    
    # Find the part-00000 file
    part_file = None
    for file in os.listdir(csv_path):
        if file.startswith('part-00000') and file.endswith('.csv'):
            part_file = os.path.join(csv_path, file)
            break
    
    if not part_file:
        return 'No data file found', 404
    
    # Copy to a clean filename for download
    download_path = os.path.join(OUTPUT_DIR, f'{analysis_type}_download.csv')
    shutil.copy(part_file, download_path)
    
    @after_this_request
    def remove_file(response):
        try:
            os.remove(download_path)
        except:
            pass
        return response
    
    return send_file(download_path, as_attachment=True, download_name=f'{analysis_type}.csv')

@app.route('/api/dataset-info')
def dataset_info():
    """Get dataset information"""
    import pandas as pd
    if os.path.exists(DATASET_PATH):
        df = pd.read_csv(DATASET_PATH)
        return jsonify({
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': df.columns.tolist(),
            'sample': df.head(5).to_dict(orient='records')
        })
    return jsonify({'error': 'Dataset not found'}), 404

@app.route('/api/instagram-trends')
@app.route('/api/social-trends')
def instagram_trends():
    """Fetch trends from configured social providers with Instagram-first fallback."""
    access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
    instagram_user_id = os.getenv('INSTAGRAM_USER_ID')
    hashtags = os.getenv('INSTAGRAM_TREND_HASHTAGS', 'ai,travel,fashion,food,fitness')

    try:
        result = fetch_social_trends(
            access_token=access_token,
            instagram_user_id=instagram_user_id,
            hashtags=hashtags,
            api_version=os.getenv('META_GRAPH_API_VERSION', 'v22.0'),
            dataset_path=DATASET_PATH
        )
        return jsonify({'success': True, **result})
    except ValueError as error:
        return jsonify({'success': False, 'error': str(error)}), 400
    except LookupError as error:
        return jsonify({
            'success': False,
            'setup_required': True,
            'error': str(error)
        }), 503
    except Exception as error:
        app.logger.warning('Social trend providers failed: %s', error)
        return jsonify({
            'success': False,
            'error': 'All configured social trend providers failed. Check the provider credentials and logs.'
        }), 502

@app.route('/api/realtime-trends')
def realtime_trends():
    """Fetch real-time trending topics from NewsAPI"""
    try:
        news_api_key = os.getenv('NEWSAPI_API_KEY')
        if not news_api_key:
            return jsonify({
                'success': False,
                'error': 'Set NEWSAPI_API_KEY to enable the legacy news endpoint.'
            }), 503
        url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={news_api_key}'
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            # Show actual news without fake data
            trends_data = []
            
            for article in articles[:8]:
                title = article.get('title', '')
                description = article.get('description', '')
                source = article.get('source', {}).get('name', 'Unknown')
                url_link = article.get('url', '#')
                published_at = article.get('publishedAt', '')
                
                trends_data.append({
                    'title': title,
                    'description': description[:200] + '...' if len(description) > 200 else description,
                    'source': source,
                    'url': url_link,
                    'published_at': published_at,
                    'category': 'Breaking News'
                })
            
            return jsonify({
                'success': True,
                'trends': trends_data,
                'trending_hashtags': [],
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'note': 'Live news from NewsAPI'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'NewsAPI returned status {response.status_code}'
            }), 500
        
        # Fallback to sample real-time Twitter/X trending hashtags - prioritize protest/war
        protest_war_hashtags = [
            '#ProtestDelhi', '#WarUpdate', '#GlobalConflict', '#PeaceTalks',
            '#CivilRights', '#StopWar', '#Revolution2026', '#FreedomFight'
        ]
        
        other_hashtags = [
            '#ClimateCrisis', '#Election2026', '#BreakingNews', '#TrendingNow',
            '#SocialJustice', '#EconomicCrisis', '#TechNews', '#HealthEmergency',
            '#PoliticalScandal', '#NaturalDisaster', '#HumanRights', '#MarketCrash',
            '#ViralVideo', '#CelebrityNews', '#SportsUpdate', '#ScienceBreakthrough'
        ]
        
        trending_people_pool = [
            '@PMIndia', '@POTUS', '@UN', '@WHO', '@ElonMusk',
            '@BillGates', '@GretaThunberg', '@BarackObama', '@NASA'
        ]
        
        # Generate dynamic sample data
        import random
        random.seed(int(datetime.now().timestamp()))
        
        trending_data = []
        trending_hashtags = []
        
        # Always include protest/war hashtags first
        selected_hashtags = protest_war_hashtags + random.sample(other_hashtags, 4)
        
        for hashtag in selected_hashtags:
            trending_hashtags.append({
                'hashtag': hashtag,
                'posts': random.randint(50000, 5000000),
                'engagement': random.randint(100000, 10000000)
            })
        
        # Sort by engagement (protest/war will naturally be higher due to random)
        trending_hashtags.sort(key=lambda x: x['engagement'], reverse=True)
        
        # Create trend details with specific discussions
        trend_descriptions = {
            '#ProtestDelhi': 'Thousands of protesters gathered at India Gate demanding government action on unemployment and inflation. Police deployed in large numbers. #DelhiProtest #CivilRights',
            '#WarUpdate': 'Breaking: Peace talks resume in Geneva as international mediators push for ceasefire. Civilians evacuated from conflict zones. #Peace #StopWar',
            '#GlobalConflict': 'UN report warns of escalating tensions in disputed region. Diplomats urge restraint. #WorldNews #Peace',
            '#PeaceTalks': 'Historic peace agreement signed after decades of conflict. World leaders celebrate diplomatic breakthrough. #Peace #History',
            '#CivilRights': 'Activists demand justice for victims of police brutality. Protests continue across the country. #Justice #Equality',
            '#StopWar': 'Anti-war protests erupt worldwide as conflict escalates. Leaders call for calm. #Peace #NoWar',
            '#Revolution2026': 'Protesters clash with police as demonstrations turn violent. Government imposes curfew. #Protest #Revolution',
            '#FreedomFight': 'Activists mark anniversary of historic freedom movement. Rallies held across the country. #Freedom #Justice',
            '#ClimateCrisis': 'UN report warns of irreversible climate damage by 2030. Activists demand immediate action from world leaders. #ClimateAction #Green',
            '#Election2026': 'Exit polls show tight race in key battleground states. Voter turnout breaks records across the country. #Democracy #Vote',
            '#BreakingNews': 'Major tech company announces breakthrough in quantum computing. Stock markets react positively. #TechNews #Innovation',
            '#TrendingNow': 'Viral video of rescue operation goes viral with 10M views in 2 hours. Netizens praise the heroes. #Viral #Heroes',
            '#GlobalConflict': 'UN Security Council emergency meeting called as tensions escalate in disputed region. #WorldNews #Peace',
            '#SocialJustice': 'New legislation proposed to address systemic inequality. Advocates call for swift passage. #Justice #Equality',
            '#EconomicCrisis': 'Central banks coordinate interest rate cuts to stabilize markets. Investors cautious about recovery. #Economy #Finance',
            '#TechNews': 'AI regulation framework proposed by EU. Tech companies respond with concerns about innovation. #AI #Technology',
            '#HealthEmergency': 'WHO declares new health alert as virus variant detected in multiple countries. #Health #PublicSafety',
            '#PoliticalScandal': 'Leaked documents reveal corruption allegations against senior officials. Opposition demands investigation. #Politics #Corruption',
            '#NaturalDisaster': 'Earthquake strikes coastal region, emergency services deployed. International aid offered. #Disaster #Relief',
            '#HumanRights': 'Human rights organizations report violations in detention centers. International community expresses concern. #Rights #Freedom',
            '#PeaceTalks': 'Historic peace agreement signed after decades of conflict. World leaders celebrate diplomatic breakthrough. #Peace #History',
            '#MarketCrash': 'Global markets experience sharp decline amid trade tensions. Analysts predict volatility ahead. #Finance #Stocks',
            '#ViralVideo': 'Heartwarming video of reunion between separated family members trends worldwide. #Viral #Emotional',
            '#CelebrityNews': 'Popular actor announces retirement from films after 30-year career. Fans express sadness and gratitude. #Entertainment #Movies',
            '#SportsUpdate': 'Underdog team wins championship in stunning upset. Sports world celebrates the miracle victory. #Sports #Victory',
            '#ScienceBreakthrough': 'Scientists discover potential cure for rare genetic disease. Clinical trials to begin next year. #Science #Medical'
        }
        
        for hashtag in selected_hashtags[:5]:
            category = random.choice(['Politics', 'World News', 'Social Justice', 'Breaking', 'Viral', 'Technology', 'Health', 'Sports'])
            description = trend_descriptions.get(hashtag, f'Ongoing discussions about {hashtag} across social media platforms. Users sharing opinions and experiences. #Trending')
            
            trending_data.append({
                'hashtag': hashtag,
                'description': description,
                'category': category,
                'posts': random.randint(100000, 1000000),
                'engagement': random.randint(500000, 5000000),
                'top_contributor': random.choice(trending_people_pool)
            })
        
        return jsonify({
            'success': True,
            'trends': trending_data,
            'trending_hashtags': trending_hashtags,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'note': 'Live Twitter/X trending simulation - Refresh for new trends'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
