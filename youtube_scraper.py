import os
from dotenv import load_dotenv
import pandas as pd
from googleapiclient.discovery import build
import isodate
from datetime import datetime, timezone

load_dotenv()

API_KEY = os.getenv('YOUTUBE_API_KEY')
SEARCH_QUERY = 'Exercise'
TOTAL_VIDEOS = 500
RESULTS_PER_PAGE = 50

def calculate_video_age_days(published_at_string):
    pub_date = datetime.strptime(published_at_string, "%Y-%m-%dT%H:%M:%SZ")
    pub_date = pub_date.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    delta = now - pub_date
    return delta.days

def get_youtube_data(api_key, query, total_videos):
    youtube = build('youtube', 'v3', developerKey=api_key)

    print(f"Searching for: '{query}'...")
    video_ids = []
    next_page_token = None
    pages_needed = (total_videos + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE

    for page in range(pages_needed):
        remaining = total_videos - len(video_ids)
        if remaining <= 0:
            break

        max_results = min(RESULTS_PER_PAGE, remaining)
        request_params = {
            'q': query,
            'part': 'id,snippet',
            'maxResults': max_results,
            'videoDuration': 'medium',
            'type': 'video',
            'order': 'viewCount'
        }
        
        if next_page_token:
            request_params['pageToken'] = next_page_token

        search_response = youtube.search().list(**request_params).execute()
        video_ids.extend([item['id']['videoId'] for item in search_response['items']])
        next_page_token = search_response.get('nextPageToken')
        
        print(f"Fetched {len(video_ids)}/{total_videos} video IDs...")
        
        if not next_page_token:
            break

    video_ids = video_ids[:total_videos]
    print(f"Processing {len(video_ids)} videos...")

    all_video_data = []
    for i in range(0, len(video_ids), RESULTS_PER_PAGE):
        batch = video_ids[i:i + RESULTS_PER_PAGE]
        vid_response = youtube.videos().list(
            part='statistics,snippet,contentDetails',
            id=','.join(batch)
        ).execute()
        all_video_data.extend(vid_response['items'])

    channel_ids = list(set([item['snippet']['channelId'] for item in all_video_data]))
    
    channel_subs = {}
    for i in range(0, len(channel_ids), RESULTS_PER_PAGE):
        batch = channel_ids[i:i + RESULTS_PER_PAGE]
        chan_response = youtube.channels().list(
            part='statistics',
            id=','.join(batch)
        ).execute()
        
        for item in chan_response['items']:
            subs = item['statistics'].get('subscriberCount', 0)
            channel_subs[item['id']] = int(subs)

    print("Compiling data...")
    videos = []
    for item in all_video_data:
        vid_id = item['id']
        title = item['snippet']['title']
        channel_id = item['snippet']['channelId']
        channel_title = item['snippet']['channelTitle']
        publish_date = item['snippet']['publishedAt']
        thumbnail_url = item['snippet']['thumbnails']['high']['url']
        
        views = int(item['statistics'].get('viewCount', 0))
        likes = int(item['statistics'].get('likeCount', 0))
        comment_count = int(item['statistics'].get('commentCount', 0))
        
        duration_iso = item['contentDetails']['duration']
        duration_seconds = isodate.parse_duration(duration_iso).total_seconds()
        
        subs = channel_subs.get(channel_id, 0)
        
        vs_ratio = round(views / subs, 2) if subs > 0 else 0
        likeview_ratio = round(likes / views, 2) if views > 0 else 0
        commentview_ratio = round(comment_count / views, 5) if views > 0 else 0
        video_age = calculate_video_age_days(publish_date)

        videos.append({
            'Title': title,
            'VS_Ratio': vs_ratio,
            'LikeView_Ratio': likeview_ratio,
            'CommentView_Ratio': commentview_ratio,
            'Duration_Sec': duration_seconds,
            'Video_Age': video_age,
            'Views': views,
            'Subscribers': subs,
            'Likes': likes,
            'Comments': comment_count,
            'Channel': channel_title,
            'Thumbnail_URL': thumbnail_url,
            'Publish_Date': publish_date,
            'Video_ID': vid_id,
            'Video_URL': f"https://www.youtube.com/watch?v={vid_id}"
        })

    return pd.DataFrame(videos)

if __name__ == "__main__":
    try:
        df = get_youtube_data(API_KEY, SEARCH_QUERY, TOTAL_VIDEOS)
        df_sorted = df.sort_values(by='VS_Ratio', ascending=False)
        
        filename = f"youtube_data_{SEARCH_QUERY.replace(' ', '_')}.xlsx"
        df_sorted.to_excel(filename, index=False)
        
        print(f"\nData saved to '{filename}'")
        print(f"Top video: {df_sorted.iloc[0]['Title']} (Ratio: {df_sorted.iloc[0]['VS_Ratio']})")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Check your API key and internet connection.")