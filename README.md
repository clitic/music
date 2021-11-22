# Global Music Trends 🎵

Global Music Trends is a youtube playlist which lists outs the trending music videos from youtube across its all regions.

- [Stream Youtube Playlist](https://www.youtube.com/playlist?list=PLQeIlACGt47P3nQEVGWmaU3669iw6q7mQ)
- [Website](https://360modder.github.io/global-music-trends/)

The only criteria to add videos to playlist is that, the music video should trend in at least 2 countries.

## Usage

First install all dependecies by running the below command.

```bash
pip install -r requirements.txt
```

Now generate a youtube v3 api key from [cloud project](https://console.cloud.google.com/). Set the api key as envoirnment variable if you want. To generate playlist data just run the below command.

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

To create a youtube playlist you need to create OAuth client in your [cloud project](https://console.cloud.google.com/). Add one redirect urls as http://127.0.0.1:8080 . After creating OAuth client download clients_secrets.json file and save it in safe/clients_secrets.json . Open update.py and change its `PLAYLIST_ID` to yours playlist id, and run this command.

```bash
python update.py
```

## Credits

- [millify](https://github.com/azaitsev/millify)'s module script

## License

&copy; 2021 360modder

This repository is licensed under the MIT license. See LICENSE for details.
