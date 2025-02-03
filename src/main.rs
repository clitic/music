use reqwest::blocking::Client;
use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Clone, Debug, Deserialize, Serialize)]
struct Video {
    comment_count: usize,
    frequency: f32,
    id: String,
    like_count: usize,
    title: String,
    view_count: usize,
}

fn main() {
    let key = std::env::var("YT_API_KEY").expect("YT_API_KEY env variable not defined");
    let client = Client::new();

    println!("Querying available regions");

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

    let mut data_fresh: Vec<Video> = Vec::new();

    for (i, region) in regions.iter().enumerate() {
        println!(
            "[{:>3}/{:>3}] Fetching trending music ({})",
            i + 1,
            regions_count,
            region
        );

        // https://developers.google.com/youtube/v3/docs/videos/list
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

        for item in data["items"].as_array().unwrap().iter() {
            let id = item["id"].as_str().unwrap().to_owned();

            if let Some(video) = data_fresh.iter_mut().find(|x| (**x).id == id) {
                video.frequency += 1.0;
                continue;
            }

            let video = Video {
                comment_count: item["statistics"]["commentCount"]
                    .as_str()
                    .unwrap_or("0")
                    .parse::<usize>()
                    .unwrap(),
                frequency: 1.0,
                id,
                like_count: item["statistics"]["likeCount"]
                    .as_str()
                    .unwrap_or("0")
                    .parse::<usize>()
                    .unwrap(),
                title: item["snippet"]["title"]
                    .as_str()
                    .unwrap_or("Unknown Title")
                    .to_owned(),
                view_count: item["statistics"]["viewCount"]
                    .as_str()
                    .unwrap_or("0")
                    .parse::<usize>()
                    .unwrap(),
            };

            data_fresh.push(video);
        }
    }

    println!("Total {} unique videos information was fetched", data_fresh.len());
    
    // Filtering and sorting data
    
    data_fresh = data_fresh.into_iter().filter_map(|mut x| {
        if x.frequency >= 2.0 {
            x.frequency = (x.frequency / regions_count as f32) * 100.;
            Some(x)
        } else {
            None
        }
    }).collect();
    println!("After filtering only {} unique videos are kept", data_fresh.len());
    data_fresh.sort_by(|a, b| b.view_count.cmp(&a.view_count));

    if std::fs::exists("data.json").unwrap() {
        let file = std::fs::read("data.json").unwrap();
        let data_old = serde_json::from_slice::<Vec<Video>>(&file).unwrap();
        let mut data_new = Vec::new();

        for video in &data_fresh {
            if data_old.iter().find(|x| (**x).id == video.id).is_none() {
                data_new.push(video.clone());
            }
        }

        println!("Total {} unique videos new videos are added", data_new.len());
        data_new.sort_by(|a, b| b.view_count.cmp(&a.view_count));

        let file = std::fs::File::create("data-newly-added.json").unwrap();
        serde_json::to_writer(file, &data_new).unwrap();
    }

    let file = std::fs::File::create("data.json").unwrap();
    serde_json::to_writer(file, &data_fresh).unwrap();
    println!("Task completed successfully");
}
