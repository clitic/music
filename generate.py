import argparse
import os
import utils
from collections import Counter
from typing import Any, List, Optional, Tuple, Union
from tqdm import tqdm
from youtube_v3_api import YoutubeService, get_regions


def get_trending_mv_ids(youtube: Any, regions: Optional[Union[List[str], None]] = None) -> Tuple[dict, Counter]:
    """get trending music vedios ids
    
    cost = 1 per page for 50 max results
    
    Args:
        youtube (Any): a resource object with methods for interacting with the service
        regions (Optional[Union[List[str], None]], optional): list two letter region code for video ids. Defaults to None.

        Tuple[dict, Counter]: music vedios ids with some data, video ids counter object
    """

    def _process_response(response: dict, mv_ids: dict, id_counter: Counter):
        for item in response["items"]:
            video_id = item["id"]
            mv_ids[video_id] = [int(item["statistics"]["viewCount"]), item["snippet"]["title"], video_id]
            id_counter.update([video_id])

    cost = 0
    mv_ids = {}
    id_counter = Counter()
    
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
        _process_response(response, mv_ids, id_counter)
        next_page_token = response.get("nextPageToken")

        while next_page_token:
            request = youtube.videos().list(**videos_api_queries, regionCode=region, pageToken=next_page_token)
            response = request.execute()
            cost += 1
            _process_response(response, mv_ids, id_counter)   
            next_page_token = response.get("nextPageToken")
    
    return mv_ids, id_counter


def main(developer_key: Optional[str] = os.environ.get("YT_API_KEY"), load_cached: Optional[bool] = False):
    youtube = YoutubeService().create_service(developer_key)
    
    if not load_cached:
        mv_ids, id_counter = get_trending_mv_ids(youtube)
        utils.dump_pickle("safe/mv_ids.pkl", mv_ids)
        utils.dump_pickle("safe/id_counter.pkl", id_counter)
    else:
        mv_ids, id_counter = utils.load_pickle("safe/mv_ids.pkl"), utils.load_pickle("safe/id_counter.pkl")
        
    mv_ids_level2 = [mv_ids[video_id] for video_id, count in id_counter.items() if count >= 2]
    mv_ids_level2 = sorted(mv_ids_level2, reverse=True)

    print(f"total videos = {len(mv_ids_level2)}, total cost = {len(mv_ids_level2) * 50}")
    utils.dump_json("safe/data.json", mv_ids_level2)
    utils.dump_json("docs/data.json", mv_ids_level2)

    # hide_header = "---\nhide:\n- navigation\n---\n\n"
    
    with open("docs/index.md", "w", encoding="utf-8") as f:
        f.write("# Current Music Trends :material-music:\n\n")
        f.write(
            "[:material-download: JSON](/current-music-trends/data.json)"
            "{ .md-button .md-button--primary }\n"
            "[:material-youtube: Playlist](https://www.youtube.com/playlist?list=PLQeIlACGt47P3nQEVGWmaU3669iw6q7mQ)"
            "{ .md-button .md-button--primary }\n\n"
        )
        f.write("## Top 10 (by region)\n\n")

        for i, (video_id, count) in enumerate(id_counter.most_common(10), start=1):
            f.write(
                f'{i}. <a href="https://youtu.be/{video_id}" target="_blank">{mv_ids[video_id][1]}</a>\n'
                f"| {count} points\n"
            )
                
        f.write("\n[More](/current-music-trends/region-score)\n")
        f.write("\n## Top 10 (by views)\n\n")

        for i, (views, title, video_id) in enumerate(mv_ids_level2[:10], start=1):
            f.write(
                f'{i}. <a href="https://youtu.be/{video_id}" target="_blank">{title}</a>\n'
                f"| {utils.millify(views, precision=1)} views\n"
            )
            
        f.write("\n[More](/current-music-trends/playlist)\n\n")
        f.write(f"{utils.timestamp()}\n\n")

    with open("docs/playlist.md", "w", encoding="utf-8") as f:
        f.write("# Youtube Playlist (Level 2)\n\n")
        
        for i, (views, title, video_id) in enumerate(mv_ids_level2, start=1):
            f.write(
                f'{i}. <a href="https://youtu.be/{video_id}" target="_blank">{title}</a>\n'
                f"| {utils.millify(views, precision=1)} views\n"
            )
            
    with open("docs/region-score.md", "w", encoding="utf-8") as f:
        f.write("# Region Score\n\n")
        
        for i, (video_id, count) in enumerate(id_counter.most_common(len(mv_ids)), start=1):
            if count >= 3:
                f.write(
                    f'{i}. <a href="https://youtu.be/{video_id}" target="_blank">{mv_ids[video_id][1]}</a>\n'
                    f"| {count} points\n"
                )
                
                
if __name__ == "__main__":
    parser = argparse.ArgumentParser("generate", description="generates data.json and docs")
    parser.add_argument("developer_key", help="youtube v3 developer api key")
    parser.add_argument("-l", "--load", dest="load", default=False, action="store_true",
                        help="load cached data (default: false)")
    args = parser.parse_args()
    main(args.developer_key, args.load)
    