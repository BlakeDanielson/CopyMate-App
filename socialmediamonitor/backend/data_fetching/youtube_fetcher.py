import os
from googleapiclient.discovery import build

def fetch_subscribed_channel_ids(api_key=None):
    """
    Fetches subscribed channel IDs for the authenticated user.
    
    Args:
        api_key: Optional YouTube API key. If not provided, uses YOUTUBE_API_KEY from environment.
    """
    if api_key is None:
        api_key = os.environ.get('YOUTUBE_API_KEY')
        if not api_key:
            raise ValueError("YOUTUBE_API_KEY environment variable not set.")
    youtube = build('youtube', 'v3', developerKey=api_key)

    channel_ids = []
    next_page_token = None

    while True:
        request = youtube.subscriptions().list(
            part='snippet',
            mine=True,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response.get('items', []):
            channel_ids.append(item['snippet']['resourceId']['channelId'])

        next_page_token = response.get('nextPageToken')

        if not next_page_token:
            break

    return channel_ids

if __name__ == '__main__':
    # Example usage (replace with actual API key and authentication flow)
    # api_key = 'YOUR_API_KEY'
    # subscribed_channels = fetch_subscribed_channel_ids(api_key)
    # print(f"Subscribed Channel IDs: {subscribed_channels}")
    pass
def fetch_channel_metadata(channel_id, api_key=None):
    """
    Fetches metadata for a given channel ID.
    
    Args:
        channel_id: YouTube channel ID to fetch metadata for
        api_key: Optional YouTube API key. If not provided, uses YOUTUBE_API_KEY from environment.
    """
    if not channel_id or not isinstance(channel_id, str):
        raise ValueError("Invalid channel_id provided.")
    
    if api_key is None:
        api_key = os.environ.get('YOUTUBE_API_KEY')
        if not api_key:
            raise ValueError("YOUTUBE_API_KEY environment variable not set.")
    youtube = build('youtube', 'v3', developerKey=api_key)

    request = youtube.channels().list(
        part='snippet,statistics,topicDetails',
        id=channel_id
    )
    response = request.execute()

    items = response.get('items', [])
    if items:
        return items[0]
    return None
def fetch_recent_videos(channel_id, max_results=10, api_key=None):
    """
    Fetches recent video IDs and snippet metadata for a given channel ID.
    
    Args:
        channel_id: YouTube channel ID to fetch videos for
        max_results: Maximum number of results to return (default 10)
        api_key: Optional YouTube API key. If not provided, uses YOUTUBE_API_KEY from environment.
    """
    if not channel_id or not isinstance(channel_id, str):
        raise ValueError("Invalid channel_id provided.")
    if not isinstance(max_results, int) or max_results <= 0 or max_results > 50: # Assuming a reasonable max limit
        raise ValueError("Invalid max_results provided. Must be a positive integer up to 50.")

    if api_key is None:
        api_key = os.environ.get('YOUTUBE_API_KEY')
        if not api_key:
            raise ValueError("YOUTUBE_API_KEY environment variable not set.")
    youtube = build('youtube', 'v3', developerKey=api_key)

    request = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        type='video',
        order='date',
        maxResults=max_results
    )
    response = request.execute()

    video_data = []
    items = response.get('items', [])
    if not isinstance(items, list):
        # Log a warning or handle unexpected response format
        print("Warning: Unexpected response format from YouTube API.")
        return []

    for item in items:
        # Basic check for expected structure
        if isinstance(item, dict) and 'id' in item and 'snippet' in item and 'videoId' in item.get('id', {}):
            video_data.append({
                'id': item['id']['videoId'],
                'snippet': item['snippet']
            })
        else:
            # Log a warning for unexpected item structure
            print(f"Warning: Skipping item with unexpected structure: {item}")

    return video_data