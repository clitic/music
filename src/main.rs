use reqwest::blocking::Client;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashSet;
use std::hash::{Hash, Hasher};

#[derive(Clone, Debug, Deserialize, Eq, Serialize)]
struct Video {
    comment_count: usize,
    id: String,
    like_count: usize,
    title: String,
    view_count: usize,
}

impl Hash for Video {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.id.hash(state);
    }
}

impl PartialEq for Video {
    fn eq(&self, other: &Self) -> bool {
        self.id == other.id
    }

    fn ne(&self, other: &Self) -> bool {
        self.id != other.id
    }
}

fn main() {
    let key = std::env::var("YT_API_KEY").expect("YT_API_KEY env variable not defined");
    let client = Client::new();

    println!("Fetching available regions");

    // https://developers.google.com/youtube/v3/docs/i18nRegions/list
    let res = client
        .get("https://youtube.googleapis.com/youtube/v3/i18nRegions")
        .query(&[("part", "snippet"), ("key", &key)])
        .send()
        .unwrap();
    let text = res.text().unwrap();
    let data: Value = serde_json::from_str(&text).unwrap();

    let regions = data
        .get("items")
        .unwrap()
        .as_array()
        .unwrap()
        .iter()
        .map(|x| x.get("id").unwrap().as_str().unwrap().to_owned())
        .collect::<Vec<String>>();
    let regions_count = regions.len();

    println!("Total {} regions found", regions_count);

    let mut all_videos = HashSet::new();

    for (i, region) in regions.iter().enumerate() {
        println!(
            "[{:>3}/{:>3}] Fetching trending music ({})",
            i + 1,
            regions_count,
            region
        );

        // https://developers.google.com/youtube/v3/docs/i18nRegions/list
        let res = client
            .get("https://www.googleapis.com/youtube/v3/videos")
            .query(&[
                ("part", "statistics,snippet"),
                ("chart", "mostPopular"),
                ("maxResults", "50"),
                ("regionCode", &region),
                ("videoCategoryId", "10"),
                ("key", &key),
            ])
            .send()
            .unwrap();

        let text = res.text().unwrap();
        let data: Value = serde_json::from_str(&text).unwrap();

        if data.get("error").is_some() {
            continue;
        }

        let videos = data["items"]
            .as_array()
            .unwrap()
            .iter()
            .map(|x| Video {
                comment_count: x["statistics"]["commentCount"]
                    .as_str()
                    .unwrap_or("0")
                    .parse::<usize>()
                    .unwrap(),
                id: x["id"].as_str().unwrap().to_owned(),
                like_count: x["statistics"]["likeCount"]
                    .as_str()
                    .unwrap_or("0")
                    .parse::<usize>()
                    .unwrap(),
                title: x["snippet"]["title"]
                    .as_str()
                    .unwrap_or("Unknown Title")
                    .to_owned(),
                view_count: x["statistics"]["viewCount"]
                    .as_str()
                    .unwrap_or("0")
                    .parse::<usize>()
                    .unwrap(),
            })
            .collect::<HashSet<Video>>();

        all_videos.extend(videos);
    }

    println!("Total {} videos information was fetched", all_videos.len());

    if std::fs::exists("data.json").unwrap() {
        std::fs::copy("data.json", "data_old.json").unwrap();

        let file = std::fs::read("data_old.json").unwrap();
        let data_old = serde_json::from_slice::<HashSet<Video>>(&file).unwrap();

        let mut data_new = all_videos
            .difference(&all_videos.intersection(&data_old).cloned().collect())
            .cloned()
            .into_iter()
            .collect::<Vec<Video>>();
        data_new.sort_by(|a, b| b.view_count.cmp(&a.view_count));

        let file = std::fs::File::create("data_new.json").unwrap();
        serde_json::to_writer(file, &data_new).unwrap();
    }

    let mut all_videos = all_videos.into_iter().collect::<Vec<Video>>();
    all_videos.sort_by(|a, b| b.view_count.cmp(&a.view_count));

    let file = std::fs::File::create("data.json").unwrap();
    serde_json::to_writer(file, &all_videos).unwrap();
}
