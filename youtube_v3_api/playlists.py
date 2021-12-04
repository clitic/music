from typing import Any, Dict, List, Optional, Tuple, Union
from tqdm import tqdm


class _Messages:
    """custom class for messages
    """
    add_msg = "adding videos"
    rm_msg = "removing videos"
    
class Playlists:
    """Playlists class interacts with youtube playlists
    """
    
    def __init__(self, playlist_id: str, youtube: Any, snippet: Optional[bool] = False, progress_bars: Optional[bool] = False) -> None:
        """Playlists class interacts with youtube playlists

        cost = 1 for playlist information + 1 per page for 50 max results

        Args:
            playlist_id (str): playlist id
            youtube (Any): a resource object with methods for interacting with the service.
            snippet (Optional[bool], optional): request playlist items with snippet part for more info. Defaults to False.
            progress_bars (Optional[bool], optional): display task status with progress bars. Defaults to False.
        
        Note:
            most of the methods require OAuth client access
                
        Examples:
            >>> pl = Playlists("PLQeIlACGt47P3nQEVGWmaU3669iw6q7mQ", youtube)
            >>> pl.responses
            >>> pl.video_ids
        """
        self._youtube, self._snippet, self._progress_bars = youtube, snippet, progress_bars 
        self.playlist_id = playlist_id
        self.link = f"https://www.youtube.com/playlist?list={playlist_id}"
        self.cost = 0
        self.title, self.desc, self.status = self._playlist_info()
        self.responses = self._pl_responses(snippet=self._snippet)
        self._playlist_items = self._playlist_item_ids()
        self.video_ids = list(self._playlist_items.keys())
        
    def __len__(self) -> int:
        return self.responses[0]["pageInfo"]["totalResults"]

    def _playlist_info(self) -> Tuple[str, str, str]:
        request = self._youtube.playlists().list(part="id,snippet,status", id=self.playlist_id)
        response = request.execute()
        self.cost += 1
        title = response["items"][0]["snippet"]["title"]
        desc = response["items"][0]["snippet"]["description"]
        status = response["items"][0]["status"]["privacyStatus"]

        return title, desc, status         

    def _pl_responses(self, playlist_id: Optional[Union[str, None]] = None, snippet: Optional[bool] = False):
        if playlist_id is None:
            playlist_id = self.playlist_id
        
        part = "id,snippet,contentDetails" if snippet else "id,contentDetails"
        responses = []
        playlist_api_queries = {"part": part, "playlistId": playlist_id, "maxResults": 50}
        request = self._youtube.playlistItems().list(**playlist_api_queries)
        response = request.execute()
        self.cost += 1
        responses.append(response)
        next_page_token = response.get("nextPageToken")
        
        while next_page_token:
            request = self._youtube.playlistItems().list(**playlist_api_queries, pageToken=next_page_token)
            response = request.execute()
            self.cost += 1
            responses.append(response)
            next_page_token = response.get("nextPageToken")
        
        return responses

    def _playlist_item_ids(self) -> Dict[str, List[str]]:
        video_ids_dict = {}
        
        for response in self.responses:
            for item in response["items"]:
                video_id = item["contentDetails"]["videoId"]
                if video_id in video_ids_dict:
                    video_ids_dict[video_id] = video_ids_dict[video_id].append(item["id"])
                else:
                    video_ids_dict[video_id] = [item["id"]]
            
        return video_ids_dict
    
    def refresh(self) -> None:
        """resfresh playlist responses
        
        cost = 1 per page for 50 max results
        """
        self.responses = self._pl_responses(snippet=self._snippet)
        self._playlist_items = self._playlist_item_ids()
        self.video_ids = list(self._playlist_items.keys())
            
    def update(self, title: str, desc: Optional[Union[str, None]] = None, status: Optional[Union[str, None]] = None) -> dict:
        """update playlist title, description and privacy status

        Args:
            title (str): title for playlist
            desc (Optional[str], optional): description for playlist. Defaults to "".
            status (Optional[str], optional): privacy status for playlist. Defaults to "private".

        Returns:
            dict: response
        """
        part = "id,snippet"
        request_body = {
            "id": self.playlist_id,
            "kind": "youtube#playlist",
            "snippet": {
                "title": title,
            }
        }
        
        if desc is not None:
            request_body["snippet"]["description"] = desc

        if status is not None:
            request_body["status"] = {
                "privacyStatus": status
            }
            part += ",status"
            
        request = self._youtube.playlists().insert(part=part, body=request_body)
        response = request.execute()
        self.cost += 50
        
        title = response["items"][0]["snippet"]["title"]
        desc = response["items"][0]["snippet"]["description"]
        status = response["items"][0]["status"]["privacyStatus"]
        self.title, self.desc, self.status = title, desc, status
        
        return response
           
    def delete(self) -> None:
        """delete the intialized playlist from youtube forever
        
        cost = 50
        """
        request = self._youtube.playlists().delete(id=self.playlist_id)
        request.execute()
        self.cost += 50
                                          
    def add_video(self, video_id: str) -> Union[dict, None]:
        """add videos to intialized playlist by using video id only if not present
        
        cost = 50

        Args:
            video_id (str): video id
            
        Returns:
            Union[dict, None]: returns response if video id is added to playlist else None
        """
        if video_id in self.video_ids:
            return None
        
        request_body = {
            "snippet": {
                "playlistId": self.playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
        
        request = self._youtube.playlistItems().insert(part="snippet", body=request_body)
        response = request.execute()
        self.cost += 50
        self.video_ids.append(video_id)
        return response

    def copy_from(self, playlist_id: str) -> None:
        """copy videos from a given playlist to intialized playlist

        Args:
            playlist_id (str): playlist id
        """
        copy_videos_ids = []
        
        for item in self._pl_responses(playlist_id)["items"]:
            video_id = item["contentDetails"]["videoId"]
            if video_id not in copy_videos_ids and video_id not in self.video_ids:
                copy_videos_ids.append(video_id)

        if self._progress_bars:
            copy_videos_ids = tqdm(copy_videos_ids, desc=_Messages.add_msg)
        
        for video_id in copy_videos_ids:
            self.add_video(video_id)
            
    def remove_video(self, video_id: str, recursive: Optional[bool] = True) -> Union[dict, None]:
        """remove video from intialized playlist by using video id only if it's present
        
        cost = 50 per removal of video
        
        Args:
            video_id (str): video id to remove
            recursive (Optional[bool], optional): remove all videos with same video id. Defaults to True.

        Returns:
            Union[dict, None]: returns last response if removed else None
        """
        if video_id not in self.video_ids:
            return None

        for playlist_item_id in self._playlist_items[video_id]:
            request = self._youtube.playlistItems().delete(id=playlist_item_id)
            response = request.execute()
            self.cost += 50
            self.video_ids.remove(video_id)
            if not recursive:
                break

        return response

    def clear(self, skip_ids: Optional[List[str]] = []) -> None:
        """clear/remove all videos from intialized playlist

        Args:
            skip_ids (Optional[List[str]], optional): list video ids to skip. Defaults to [].
        """
        remove_video_ids = [video_id for video_id in self.video_ids if video_id not in skip_ids]

        if self._progress_bars:
            remove_video_ids = tqdm(remove_video_ids, desc=_Messages.rm_msg)
        
        for video_id in remove_video_ids:
            self.remove_video(video_id)

    def remove_duplicate(self) -> None:
        """remove duplicate videos from intialized playlist
        """
        remove_video_ids = [
            video_id
            for video_id, playlist_item_id in self._playlist_items.items()
            if len(playlist_item_id) > 1
        ]

        if self._progress_bars:
            remove_video_ids = tqdm(remove_video_ids, desc=_Messages.rm_msg)

        for video_id in remove_video_ids:
            self.remove_video(video_id)            
