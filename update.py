import argparse
import utils
import requests
from typing import List
from tqdm import tqdm
from youtube_v3_api import YoutubeService, Playlists


def video_ids_from_json(json_file: str, fetch: bool) -> List[str]:
    """get video ids to be added from json file"""
    
    def _parse_dict(data: list) -> List[str]:
        return [video_id for _, _, video_id in data]
    
    if fetch:
        data = requests.get("https://360modder.github.io/current-music-trends/data.json").json()
    else:
        data = utils.load_json(json_file)
    
    return _parse_dict(data)

def main(args: argparse.Namespace):
    add_video_ids = video_ids_from_json(args.input, args.fetch)
    youtube = YoutubeService().create_oauth_service(
        "safe/client_secrets.json", ["https://www.googleapis.com/auth/youtube"],
        token_file="safe/token_youtube_v3.pkl", relogin=args.relogin
    )
    pl = Playlists(args.playlist, youtube, progress_bars=True)

    if not args.no_clear:
        pl.clear(skip_ids=list(set(pl.video_ids).intersection(add_video_ids)))

    videos_not_added = 0
    add_video = True

    for video_id in tqdm(add_video_ids, desc="adding videos"):
        try:
            if add_video:
                pl.add_video(video_id)
            else:
                videos_not_added += 1
        except Exception as e:
            # TODO log e
            videos_not_added += 1
            add_video = False

    if videos_not_added > 0:
        time_left, clock_time = utils.time_left_for_pacific_midnight()
        print(f"total {videos_not_added} videos not added")
        print(f"re-run this script after {time_left} @ {clock_time}, when qouta is renewed")
    else:
        print("all videos added to playlist")

    print(f"script run-up costs {pl.cost} api units")
    print(f"visit here: {pl.link}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("update", description="updates youtube playlist")
    parser.add_argument("-p", "--playlist", dest="playlist", default="PLQeIlACGt47P3nQEVGWmaU3669iw6q7mQ",
                        help="youtube playlist id (default: PLQeIlACGt47P3nQEVGWmaU3669iw6q7mQ)")
    parser.add_argument("-i", "--input", dest="input", default="docs/data.json",
                        help="path of data.json file (default: docs/data.json)")
    parser.add_argument("-f", "--fetch", dest="fetch", default=False, action="store_true",
                        help="fetch data.json from github instead of local file (default: false)")
    parser.add_argument("--relogin", dest="relogin", default=False, action="store_true",
                        help="relogin to cloud project (default: false)")
    parser.add_argument("--no-clear", dest="no_clear", default=False, action="store_true",
                        help="skip clearing youtube playlist (default: false)")
    args = parser.parse_args()
    
    print("sometimes some videos are not added to playlist, try re-running the script")
    main(args)
