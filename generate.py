import argparse
import os
import utils
from typing import Any, List, Optional, Tuple, Union
from tqdm import tqdm
from youtube_v3_api import YoutubeService, get_regions


markdown_header = """---
hide:
- navigation
---

[:material-download: JSON](data.json)
[:material-youtube: Playlist](https://www.youtube.com/playlist?list=PLQeIlACGt47P3nQEVGWmaU3669iw6q7mQ)

# Global Music Trends :material-music:\n
"""


def get_trending_music_vedios_ids(youtube: Any, regions: Optional[Union[List[str], None]] = None) -> Tuple[list, list, int]:
    """get trending music vedios ids
    
    cost = 1 per page for 50 max results
    
    Args:
        youtube (Any): a resource object with methods for interacting with the service
        regions (Optional[Union[List[str], None]], optional): list two letter region code for video ids. Defaults to None.

        Tuple[list, list, int]: list of trending music vedios ids, list of global trending music vedios ids, cost
    """

    def _process_response(response, mv_ids, global_mv_ids):
        for item in response["items"]:
            video_id = item["id"]
            video_data = [int(item["statistics"]["viewCount"]), item["snippet"]["title"], video_id]
            
            if video_id in mv_ids.keys() and video_id not in global_mv_ids.keys():
                global_mv_ids[video_id] = video_data
            else:
                mv_ids[video_id] = video_data

    cost = 0
    mv_ids = {}
    global_mv_ids = {}
    
    if regions is None:
        regions = get_regions(youtube).keys()
        
    videos_api_queries = {
        "part": "id,snippet,statistics", 
        "chart": "mostPopular",
        "videoCategoryId": "10",
        "maxResults": 50
    }
            
    for region in tqdm(regions, desc="querying trending music"):
        request = youtube.videos().list(**videos_api_queries, regionCode=region)
        response = request.execute()
        cost += 1
        _process_response(response, mv_ids, global_mv_ids)
        next_page_token = response.get("nextPageToken")

        while next_page_token:
            request = youtube.videos().list(**videos_api_queries, regionCode=region, pageToken=next_page_token)
            response = request.execute()
            cost += 1
            _process_response(response, mv_ids, global_mv_ids)   
            next_page_token = response.get("nextPageToken")

    return list(mv_ids.values()), sorted(global_mv_ids.values(), reverse=True), cost


def main(developer_key: Optional[str] = os.environ.get("YT_API_KEY")):
    youtube = YoutubeService().create_service(developer_key)

    _, global_mv_ids, _ = get_trending_music_vedios_ids(youtube)
    print(f"total videos = {len(global_mv_ids)}, total cost = {len(global_mv_ids) * 50}")
    utils.dump_json("safe/data.json", global_mv_ids)
    utils.dump_json("docs/data.json", global_mv_ids)

    with open("docs/index.md", "w", encoding="utf-8") as f:
        f.write(markdown_header)
        for i, (views, title, video_id) in enumerate(global_mv_ids, start=1):
            f.write(
                f'{i}. <a href="https://youtu.be/{video_id}" target="_blank">{title}</a>\n'
                f"@ {utils.millify(views, precision=1)} views\n"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser("generate", description="generates data.json and docs/index.md")
    parser.add_argument("developer_key", help="youtube v3 developer api key")
    main(parser.parse_args().developer_key)
    # bash: python generate.py $YT_API_KEY
    # powershell: python generate.py $env:YT_API_KEY
    # cmd: python generate.py %YT_API_KEY%
    