import argparse
import os
import utils
from tqdm import tqdm
from youtube_v3_api import YoutubeService, Playlists


parser = argparse.ArgumentParser("update", description="updates youtube playlist")
parser.add_argument("-i", "--input", dest="input", default="safe/data.json", help="path of data.json file (default: safe/data.json)")
parser.add_argument("--no-clear", dest="no_clear", default=False, action="store_true", help="skip clearing youtube playlist (default: false)")
args = parser.parse_args()

PLAYLIST_ID = "PLQeIlACGt47P3nQEVGWmaU3669iw6q7mQ"

youtube = YoutubeService().create_oauth_service("safe/client_secrets.json", ["https://www.googleapis.com/auth/youtube"], token_file="safe/token_youtube_v3.pkl")
pl = Playlists(youtube, PLAYLIST_ID, progress_bars=True)
pl_video_ids, _ = pl.video_ids(remove_comman=True)

if not args.no_clear:
    add_video_ids = [video_id for _, _, video_id in utils.load_json(args.input)]
    skip_ids = list(set(pl_video_ids).intersection(add_video_ids))
    pl.clear(skip_ids=skip_ids)

videos_not_added = []
add_video = True

for views, title, video_id in tqdm(utils.load_json(args.input), desc="adding videos"):
    if video_id not in pl_video_ids:
        try:
            if add_video:
                pl.add_video(video_id)
            else:
                videos_not_added.append([views, title, video_id])
        except:
            videos_not_added.append([views, title, video_id])
            add_video = False

if videos_not_added != []:
    utils.dump_json(args.input, videos_not_added)
    time_left, clock_time = utils.time_left_for_pacific_midnight()
    print(f"total {len(videos_not_added)} videos not added")
    print(f"re-run this script with --no-clear flag after {time_left} @ {clock_time}, when your qouta is renewed")
else:
    if os.path.exists(args.input):
        os.remove(args.input)

    print("all videos added to playlist")

print(f"visit here: https://www.youtube.com/playlist?list={PLAYLIST_ID}")
