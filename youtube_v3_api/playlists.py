from typing import Any, List, Optional, Tuple
from tqdm import tqdm
from .utils import get_response_item_ids


class Playlists:
    
    def __init__(self, youtube: Any, playlist_id: str, progress_bars: Optional[bool] = False) -> None:
        """Playlists class to interact with youtube playlists

        Args:
            youtube (Any): a resource object with methods for interacting with the service.
            playlist_id (str): playlist id
            progress_bars (Optional[bool], optional): display task status with progress bars. Defaults to False.
        """
        self.youtube = youtube
        self.playlist_id = playlist_id
        self.progress_bars = progress_bars
        
    def add_video(self, video_id: str) -> dict:
        """add videos to intialized playlist
        
        cost = 50

        Args:
            video_id (str): video id
            
        Returns:
            dict: response
        """
        request_body = {
            'snippet': {
                'playlistId': self.playlist_id,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': video_id
                }
            }
        }

        request = self.youtube.playlistItems().insert(part='snippet', body=request_body)
        return request.execute()
    
    def remove_video(self, playlist_item_id: str) -> dict:
        """remove video of playlist using its id
        
        cost = 50
        
        Args:
            playlist_item_id (str): id

        Returns:
            dict: response
        """
        request = self.youtube.playlistItems().delete(id=playlist_item_id)
        return request.execute()

    def copy_from(self, playlist_id: str) -> int:
        """copy videos from a given playlist to intialized playlist
        
        cost = 1 per page for 50 max results + 50 per insert of video
        
        Args:
            playlist_id (str): playlist id
            
        Returns:
            int: total cost
        """
        
        def _process_response(response, copy_videos_ids):
            for item in response["items"]:
                video_id = item["contentDetails"]["videoId"]
                if video_id not in copy_videos_ids:
                    copy_videos_ids.append(video_id)

        cost = 0
        copy_videos_ids = []
        playlist_api_queries = {"part": "contentDetails", "playlistId": playlist_id, "maxResults": 50}
        request = self.youtube.playlistItems().list(**playlist_api_queries)
        response = request.execute()
        cost += 1
        _process_response(response, copy_videos_ids)
        next_page_token = response.get('nextPageToken')
        
        while next_page_token:
            request = self.youtube.playlistItems().list(**playlist_api_queries, pageToken=next_page_token)
            response = request.execute()
            cost += 1
            _process_response(response, copy_videos_ids)
            next_page_token = response.get('nextPageToken')
        
        copy_videos_ids = tqdm(copy_videos_ids) if self.progress_bars else copy_videos_ids
        
        for video_id in copy_videos_ids:
            self.add_video(video_id)
            cost += 50
            
        return cost

    def remove_duplicate(self) -> int:
        """removes duplicate videos from intialized playlist
        
        cost = 1 per page for 50 max results + 50 per removal of video
        
        Returns:
            int: total cost
        """
        
        def _process_response(response, unique_video_ids, delete_playlist_ids):
            for item in response["items"]:
                video_id = item["contentDetails"]["videoId"]
                
                if video_id not in unique_video_ids:
                    unique_video_ids.append(video_id)
                else:
                    delete_playlist_ids.append(item["id"])
        
        cost = 0
        delete_playlist_ids = []
        unique_video_ids = []
        playlist_api_queries = {"part": "id,contentDetails", "playlistId": self.playlist_id, "maxResults": 50}
        
        request = self.youtube.playlistItems().list(**playlist_api_queries)
        response = request.execute()
        cost += 1
        _process_response(response, unique_video_ids, delete_playlist_ids)
        next_page_token = response.get('nextPageToken')

        while next_page_token:
            request = self.youtube.playlistItems().list(**playlist_api_queries, pageToken=next_page_token)
            response = request.execute()
            cost += 1
            _process_response(response, unique_video_ids, delete_playlist_ids)
            next_page_token = response.get('nextPageToken')
        
        delete_playlist_ids = tqdm(delete_playlist_ids) if self.progress_bars else delete_playlist_ids
        
        for playlist_item_id in delete_playlist_ids:
            self.remove_video(playlist_item_id)  
            cost += 50
            
        return cost                  

    def clear(self, skip_ids: List[str] = []) -> int:
        """clear/removes all videos from intialized playlist
        
        cost = 1 per page for 50 max results + 50 per removal of video

        Args:
            skip_ids (List[str], optional): list video ids to skip. Defaults to [].
                    
        Returns:
            int: total cost
        """
                
        def _process_response(response, delete_playlist_ids, skip_ids):
            for item in response["items"]:
                video_id = item["contentDetails"]["videoId"]
                if video_id not in skip_ids:
                    delete_playlist_ids.append(item["id"])
                    
        cost = 0
        delete_playlist_ids = []
        playlist_api_queries = {"part": "id,contentDetails", "playlistId": self.playlist_id, "maxResults": 50}
        
        request = self.youtube.playlistItems().list(**playlist_api_queries)
        response = request.execute()
        cost += 1
        _process_response(response, delete_playlist_ids, skip_ids)
        next_page_token = response.get('nextPageToken')
        
        while next_page_token:
            request = self.youtube.playlistItems().list(**playlist_api_queries, pageToken=next_page_token)
            response = request.execute()
            cost += 1
            _process_response(response, delete_playlist_ids, skip_ids)
            next_page_token = response.get('nextPageToken')
        
        delete_playlist_ids = tqdm(delete_playlist_ids) if self.progress_bars else delete_playlist_ids
        
        for playlist_item_id in delete_playlist_ids:
            self.remove_video(playlist_item_id)
            cost += 50
            
        return cost

    def video_ids(self, remove_comman: Optional[bool] = False) -> Tuple[List[str], int]:
        """this method returns list of video ids in intialized playlist 
        
        cost = 1 per page for 50 max results
        
        Args:
            remove_comman (Optional[bool], optional): remove comman video ids. Defaults to False.

        Returns:
            Tuple[List[str], int]: videos ids list, cost
        """
        
        def _process_response(response, videos_ids, remove_comman):
            for item in response["items"]:
                video_id = item["contentDetails"]["videoId"]
                if (remove_comman and video_id not in videos_ids) or not remove_comman:
                    videos_ids.append(video_id)

        cost = 0
        videos_ids = []
        playlist_api_queries = {"part": "contentDetails", "playlistId": self.playlist_id, "maxResults": 50}
        request = self.youtube.playlistItems().list(**playlist_api_queries)
        response = request.execute()
        cost += 1
        _process_response(response, videos_ids, remove_comman)
        next_page_token = response.get('nextPageToken')
        
        while next_page_token:
            request = self.youtube.playlistItems().list(**playlist_api_queries, pageToken=next_page_token)
            response = request.execute()
            cost += 1
            _process_response(response, videos_ids, remove_comman)
            next_page_token = response.get('nextPageToken')
        
        return videos_ids, cost
