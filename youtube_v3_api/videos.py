from typing import Any, List
import isodate


class Video:
    """Video class interacts with a single youtube videos
    """
    
    def __init__(self, video_data) -> None:
        # class
        self.video_data = video_data
        # response
        self.id = video_data["id"]
        # snippet
        self.date = video_data["snippet"]["publishedAt"]
        self.title = video_data["snippet"]["title"]
        self.description = video_data["snippet"]["description"]
        self.channel_id = video_data["snippet"]["channelId"]
        self.thumbnails = video_data["snippet"]["thumbnails"]
        self.channel_title = video_data["snippet"]["channelTitle"]
        # self.tags = video_data["snippet"]["tags"]
        self.category = video_data["snippet"]["categoryId"]
        # self.language = video_data["snippet"]["defaultAudioLanguage"]
        # statistics
        self.views = int(video_data["statistics"]["viewCount"])
        self.likes = self.handle_key_error('int(self.video_data["statistics"]["likeCount"])', 0)
        self.comments = self.handle_key_error('int(self.video_data["statistics"]["commentCount"])', 0)
        # parsing
        self.seconds = self.yt_duration(video_data["snippet"]["publishedAt"]) # "2021-12-24T01:15:09Z"
        
    @classmethod
    def get(cls, video_id: str, youtube: Any):
        """Construct Video class from video id and get video details
        
        cost = 1
        
        Args:
            video_id (str): video id
            youtube (Any): a resource object with methods for interacting with the service.

        Returns:
            Video: instance of Video class
        """
        request = youtube.videos().list(part="id,snippet,statistics", id=video_id)
        response = request.execute()
        return cls(response["items"][0])

    def handle_key_error(self, query_string, default):
        try:
            return eval(query_string)
        except KeyError:
            return default    

    @staticmethod
    def yt_duration(date):
        dt = isodate.parse_datetime(date)
        seconds = (dt.hour * 3600) + (dt.minute * 60) + dt.second
        seconds += (dt.year * 3.154e+7) + (dt.month * 2.628e+6) + (dt.day * 86400)
        return int(seconds)

class Videos:
    """Videos class interacts with multiple youtube videos
    """
    
    def __init__(self, video_ids: List[str], youtube: Any) -> None:
        """Videos class interacts with multiple youtube videos

        cost = 1 per page for 50 max results, min cost = 1

        Args:
            video_ids (List[str]): list of video ids
            youtube (Any): a resource object with methods for interacting with the service.
        """
        
        self.video_ids = video_ids
        self._youtube = youtube
        self.cost = 0
        self.responses = self._videos_responses()
        
    def _videos_responses(self) -> list:
        def _chunks(lst: list, size: int = 50):
            for i in range(0, len(lst), size):
                yield lst[i:i + size]
        
        responses = []
        video_ids = list(_chunks(self.video_ids))
        videos_api_queries = {"part": "id,snippet,statistics", "maxResults": 50}
            
        for video_ids_chunk in video_ids:
            request = self._youtube.videos().list(id=",".join(video_ids_chunk), **videos_api_queries)
            response = request.execute()
            self.cost += 1
            responses.append(response)
        
        return responses

    def parse_responses(self) -> List[Video]:
        """parse videos title, description etc. from responses using Video class

        Returns:
            List[YTVideo]: list YTVideo class objects
        """
        videos_data = []
        
        for response in self.responses:
            for item in response["items"]:
                videos_data.append(Video(item))
            
        return videos_data
