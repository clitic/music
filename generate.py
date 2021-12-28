import argparse
import utils
from collections import Counter
from typing import Any, List, Optional, Tuple, Union
import requests
from tqdm import tqdm
from youtube_v3_api import YoutubeService, Video, Videos, get_regions

    
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

def write_docs(mv_ids: List[str], id_counter: Counter, mv_ids_level2: list, videos_data: List[Video]):
    """write docs from docs/templates

    Args:
        mv_ids (List[str]): music vedios ids with some data
        id_counter (Counter): video ids counter object
        mv_ids_level2 (list): music vedios ids with some data (only count >= 2)
    """
    
    def _region_score(i: int, video_id: str, count: int):
        return f"{i}. [{mv_ids[video_id][1]}](https://youtu.be/{video_id}) " \
            f"| {count} points | {((count/107)*100):.1f}%\n"

    def _playlist(i: int, views: int, video_id: str):
        return f"{i}. [{mv_ids[video_id][1]}](https://youtu.be/{video_id}) " \
            f"| {utils.millify(views, precision=1)} views\n"

    def _time_to_views_ratio(i: int, video_id: str):
        return f"{i}. [{mv_ids[video_id][1]}](https://youtu.be/{video_id})\n"

    def _likes(i: int, likes: int, video_id: str):
        return f"{i}. [{mv_ids[video_id][1]}](https://youtu.be/{video_id}) " \
            f"| {utils.millify(likes, precision=1)} likes\n"

    def _comments(i: int, comments: int, video_id: str):
        return f"{i}. [{mv_ids[video_id][1]}](https://youtu.be/{video_id}) " \
            f"| {utils.millify(comments, precision=1)} comments\n"
                     
    old_mv_ids = requests.get("https://raw.githubusercontent.com/360modder/current-music-trends/gh-pages/data.json").json()
    
    # docs/home.md
    home_md = utils.MarkdownFile.from_file("docs/templates/home.md")
    home_md["timestamp"] = utils.timestamp()
    
    ## Top 10 (by ratio)
    old_mv_views = {}
    for views, _, video_id in old_mv_ids:
        old_mv_views[video_id] = views
    
    home_md["top_10_by_ratio"] = ""
    videos_days_to_views_ratio = []
    for video in videos_data:
        try:
            videos_days_to_views_ratio.append([utils.utc_seconds() / (video.views - old_mv_views[video.id]), video.id])
        except KeyError:
            pass
            
    videos_days_to_views_ratio = sorted(videos_days_to_views_ratio)
    
    for i, (_, video_id) in enumerate(videos_days_to_views_ratio, start=1):
        if i > 10:
            break
        
        home_md["top_10_by_ratio"] += _time_to_views_ratio(i, video_id)
        
    ## Top 10 (by region)
    home_md["top_10_by_region"] = ""
    for i, (video_id, count) in enumerate(id_counter.most_common(10), start=1):
        home_md["top_10_by_region"] += _region_score(i, video_id, count)
        
    ## Top 10 (by views)
    home_md["top_10_by_views"] = ""
    for i, (views, title, video_id) in enumerate(mv_ids_level2[:10], start=1):
        home_md["top_10_by_views"] += _playlist(i, views, video_id)
    
    ## Top 10 (by likes)
    home_md["top_10_by_likes"] = ""
    videos_likes = []
    for video in videos_data:
        videos_likes.append([video.likes, video.id])
    videos_likes = sorted(videos_likes, reverse=True)
    
    for i, (likes, video_id) in enumerate(videos_likes, start=1):
        if i > 10:
            break
        
        home_md["top_10_by_likes"] += _likes(i, likes, video_id)

    home_md.save("docs/home.md")

    ## Top 10 (by comments)
    home_md["top_10_by_comments"] = ""
    videos_comments = []
    for video in videos_data:
        videos_comments.append([video.comments, video.id])
    videos_comments = sorted(videos_comments, reverse=True)
    
    for i, (comments, video_id) in enumerate(videos_comments, start=1):
        if i > 10:
            break
        
        home_md["top_10_by_comments"] += _comments(i, comments, video_id)

    home_md.save("docs/home.md")
    
    # docs/days-to-views-ratio.md
    ratio_md = utils.MarkdownFile.from_file("docs/templates/time-to-views-ratio.md")
    ratio_md["time_to_views_ratio"] = ""
        
    for i, (_, video_id) in enumerate(videos_days_to_views_ratio, start=1):
        ratio_md["time_to_views_ratio"] += _time_to_views_ratio(i, video_id)
        
    ratio_md.save("docs/time-to-views-ratio.md")

    # docs/region-score.md
    region_score_md = utils.MarkdownFile.from_file("docs/templates/region-score.md")
    region_score_md["region_score"] = ""
    
    for i, (video_id, count) in enumerate(id_counter.most_common(len(mv_ids)), start=1):
        if count >= 2:
            region_score_md["region_score"] += _region_score(i, video_id, count)
    
    region_score_md.save("docs/region-score.md")
    
    # docs/playlist.md
    playlist_md = utils.MarkdownFile.from_file("docs/templates/playlist.md")
    playlist_md["yt_playlist"] = ""
        
    for i, (views, title, video_id) in enumerate(mv_ids_level2, start=1):
        playlist_md["yt_playlist"] += _playlist(i, views, video_id)
        
    playlist_md.save("docs/playlist.md")

    # docs/likes.md
    likes_md = utils.MarkdownFile.from_file("docs/templates/likes.md")
    likes_md["likes"] = ""

    for i, (likes, video_id) in enumerate(videos_likes, start=1):        
        likes_md["likes"] += _likes(i, likes, video_id)
        
    likes_md.save("docs/likes.md")

    # docs/comments.md
    comments_md = utils.MarkdownFile.from_file("docs/templates/comments.md")
    comments_md["comments"] = ""

    for i, (comments, video_id) in enumerate(videos_comments, start=1):
        comments_md["comments"] += _comments(i, comments, video_id)
        
    comments_md.save("docs/comments.md")

    # docs/newly-added.md
    newly_md = utils.MarkdownFile.from_file("docs/templates/newly-added.md")
    newly_md["newly_added"] = ""
        
    old_video_ids = [video_id for _, _, video_id in old_mv_ids]
    
    for i, (views, title, video_id) in enumerate(mv_ids_level2, start=1):
        if video_id not in old_video_ids:
            newly_md["newly_added"] += _playlist(i, views, video_id)
        
    newly_md.save("docs/newly-added.md") 

def main(developer_key: str, load_cached: Optional[bool] = False):
    if not load_cached:
        youtube = YoutubeService().create_service(developer_key)
        mv_ids, id_counter = get_trending_mv_ids(youtube)
        
        videos_data = Videos([video_id for video_id, count in id_counter.items() if count >= 2], youtube)
        videos_data = videos_data.parse_responses() 
        
        utils.dump_pickle("safe/mv_ids.pkl", mv_ids)
        utils.dump_pickle("safe/id_counter.pkl", id_counter)
        utils.dump_pickle("safe/videos_data.pkl", videos_data)
    else:
        mv_ids = utils.load_pickle("safe/mv_ids.pkl")
        id_counter = utils.load_pickle("safe/id_counter.pkl")
        videos_data = utils.load_pickle("safe/videos_data.pkl")
        
    mv_ids_level2 = [mv_ids[video_id] for video_id, count in id_counter.items() if count >= 2]
    mv_ids_level2 = sorted(mv_ids_level2, reverse=True)
    utils.dump_json("docs/data.json", mv_ids_level2)

    print(f"total videos = {len(mv_ids_level2)}, total cost = {len(mv_ids_level2) * 50}")
    
    write_docs(mv_ids, id_counter, mv_ids_level2, videos_data)

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser("generate", description="generates data.json and docs")
    parser.add_argument("developer_key", help="youtube v3 developer api key")
    parser.add_argument("-l", "--load", dest="load", default=False, action="store_true",
                        help="load cached data (default: false)")
    args = parser.parse_args()
    main(args.developer_key, args.load)
    