import unittest
from unittest.mock import patch, MagicMock

# Assume the fetcher module will be in backend/data_fetching/youtube_fetcher.py
from backend.data_fetching import youtube_fetcher

class TestYouTubeFetcher(unittest.TestCase):

    @patch('backend.data_fetching.youtube_fetcher.build')
    def test_fetch_subscribed_channel_ids(self, mock_build):
        # Create a complete mock chain for YouTube API
        mock_subscriptions = MagicMock()
        mock_list = MagicMock()
        mock_list_call_1 = MagicMock()
        mock_list_call_2 = MagicMock()
        
        # Configure mock return values
        mock_list_call_1.execute.return_value = {
            'items': [
                {'snippet': {'resourceId': {'channelId': 'channel_id_1'}}},
                {'snippet': {'resourceId': {'channelId': 'channel_id_2'}}},
            ],
            'nextPageToken': 'next_page_token_1'
        }
        
        mock_list_call_2.execute.return_value = {
            'items': [
                {'snippet': {'resourceId': {'channelId': 'channel_id_3'}}},
            ]
        }
        
        # Configure the mock call chain
        mock_list.side_effect = [mock_list_call_1, mock_list_call_2]
        mock_subscriptions.list = MagicMock(return_value=mock_list)
        mock_youtube = MagicMock()
        mock_youtube.subscriptions.return_value = mock_subscriptions
        mock_build.return_value = mock_youtube
        
        # Call the function
        channel_ids = youtube_fetcher.fetch_subscribed_channel_ids('mock_api_key')

        # Assert that build was called correctly
        mock_build.assert_called_once_with('youtube', 'v3', developerKey='mock_api_key')
        
        # Check first call parameters
        mock_subscriptions.list.assert_any_call(
            part='snippet',
            mine=True,
            maxResults=50,
            pageToken=None
        )
        
        # Check second call parameters
        mock_subscriptions.list.assert_any_call(
            part='snippet',
            mine=True,
            maxResults=50,
            pageToken='next_page_token_1'
        )
        
        # Assert the function returns the expected channel IDs
        self.assertEqual(channel_ids, ['channel_id_1', 'channel_id_2', 'channel_id_3'])

if __name__ == '__main__':
    @patch('googleapiclient.discovery.build')
    def test_fetch_channel_metadata(self, mock_build):
        # Mock the YouTube API response for channel list
        mock_channels_list = MagicMock()
        mock_channels_list.execute.return_value = {
            'items': [
                {
                    'snippet': {'title': 'Channel Title', 'description': 'Channel Description'},
                    'statistics': {'viewCount': '1000', 'subscriberCount': '100'},
                    'topicDetails': {'topicIds': ['/m/09s1f']}
                }
            ]
        }

        mock_youtube_service = MagicMock()
        mock_youtube_service.channels.return_value.list.return_value = mock_channels_list

        mock_build.return_value = mock_youtube_service

        channel_id = 'test_channel_id'
        # Call the function that will be implemented
        channel_metadata = youtube_fetcher.fetch_channel_metadata('mock_api_key', channel_id)

        # Assert that build was called correctly
        mock_build.assert_called_once_with('youtube', 'v3', developerKey='mock_api_key')

        # Assert that channels().list() was called correctly
        mock_youtube_service.channels.return_value.list.assert_called_once_with(
            part='snippet,statistics,topicDetails',
            id=channel_id
        )

        # Assert the function returns the expected metadata
        expected_metadata = {
            'snippet': {'title': 'Channel Title', 'description': 'Channel Description'},
            'statistics': {'viewCount': '1000', 'subscriberCount': '100'},
            'topicDetails': {'topicIds': ['/m/09s1f']}
        }
        self.assertEqual(channel_metadata, expected_metadata)

        # This test is currently failing as the function is not implemented.
        # The assertions for the function return value are commented out for now.

    unittest.main()
    @patch('googleapiclient.discovery.build')
    def test_fetch_recent_videos(self, mock_build):
        # Mock the YouTube API response for search list
        mock_search_list = MagicMock()
        mock_search_list.execute.return_value = {
            'items': [
                {
                    'id': {'videoId': 'video_id_1'},
                    'snippet': {'title': 'Video Title 1', 'description': 'Video Description 1'}
                },
                {
                    'id': {'videoId': 'video_id_2'},
                    'snippet': {'title': 'Video Title 2', 'description': 'Video Description 2'}
                },
            ]
        }

        mock_youtube_service = MagicMock()
        mock_youtube_service.search.return_value.list.return_value = mock_search_list

        mock_build.return_value = mock_youtube_service

        channel_id = 'test_channel_id'
        max_results = 10
        # Call the function that will be implemented
        video_data = youtube_fetcher.fetch_recent_videos('mock_api_key', channel_id, max_results)

        # Assert that build was called correctly
        mock_build.assert_called_once_with('youtube', 'v3', developerKey='mock_api_key')

        # Assert that search().list() was called correctly
        mock_youtube_service.search.return_value.list.assert_called_once_with(
            part='snippet',
            channelId=channel_id,
            type='video',
            order='date',
            maxResults=max_results
        )

        # Assert the function returns the expected video data
        expected_video_data = [
            {
                'id': 'video_id_1',
                'snippet': {'title': 'Video Title 1', 'description': 'Video Description 1'}
            },
            {
                'id': 'video_id_2',
                'snippet': {'title': 'Video Title 2', 'description': 'Video Description 2'}
            },
        ]
        self.assertEqual(video_data, expected_video_data)

        # This test is currently failing as the function is not implemented.
        # The assertions for the function return value are commented out for now.
