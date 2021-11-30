# Global Music Trends 🎵

Global Music Trends is a youtube playlist which lists outs the trending music videos from youtube, across its all regions.

- <a href="https://www.youtube.com/playlist?list=PLQeIlACGt47P3nQEVGWmaU3669iw6q7mQ" target="_blank">Stream Youtube Playlist</a>
- <a href="https://360modder.github.io/global-music-trends/" target="_blank">Website</a>

The only criteria to add videos to playlist is that, the music video should trend in at least 2 regions.

## Usage

First install all dependecies by running the below command.

```bash
pip install -r requirements.txt
```

Now enable and generate a [youtube v3](https://console.cloud.google.com/apis/library/youtube.googleapis.com) api key from [cloud project](https://console.cloud.google.com/). Set the api key as envoirnment variable if you want. To generate playlist data just run the below command.

```bash
python generate.py $YT_API_KEY
```

Optionally you can serve site too.

```bash
pip install mkdocs-material
```

```bash
mkdocs serve
```

Visit [localhost](http://127.0.0.1:8000/) to view site.

## Creating A Youtube Playlist

To create a youtube playlist you need to create OAuth client in your [cloud project](https://console.cloud.google.com/). Add one redirect urls as http://localhost:8080 . After creating OAuth client download client_secrets.json file and save it in safe/client_secrets.json . Finally run this command.

```bash
python update.py -p <playlist id>
```

Or

```bash
python update.py -h
```

## Credits

- [millify](https://github.com/azaitsev/millify)'s module script

## License

&copy; 2021 360modder

This repository is licensed under the MIT license. See LICENSE for details.
