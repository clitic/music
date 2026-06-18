interface Video {
  comment_count: number;
  frequency: number;
  id: string;
  like_count: number;
  title: string;
  view_count: number;
}

interface RegionsResponse {
  items: { id: string }[];
}

interface YouTubeVideoItem {
  id: string;
  snippet: { title?: string };
  statistics: {
    viewCount?: string;
    likeCount?: string;
    commentCount?: string;
  };
}

interface VideosResponse {
  items?: YouTubeVideoItem[];
  error?: unknown;
}

async function main() {
  const key = process.env.YT_API_KEY;
  if (!key) {
    throw new Error("YT_API_KEY env variable not defined");
  }

  console.log("Querying available regions");

  // https://developers.google.com/youtube/v3/docs/i18nRegions/list
  const regionsRes = await fetch(
    `https://youtube.googleapis.com/youtube/v3/i18nRegions?part=snippet&key=${key}`
  );
  const regionsData: RegionsResponse = await regionsRes.json();
  const regions = regionsData.items.map((item) => item.id);
  const regionsCount = regions.length;

  console.log(`Total ${regionsCount} regions found`);

  let dataFresh: Video[] = [];

  for (let i = 0; i < regions.length; i++) {
    const region = regions[i];
    console.log(
      `[${String(i + 1).padStart(3)}/${String(regionsCount).padStart(3)}] Fetching trending music (${region})`
    );

    // https://developers.google.com/youtube/v3/docs/videos/list
    const params = new URLSearchParams({
      part: "statistics,snippet",
      chart: "mostPopular",
      maxResults: "50",
      regionCode: region,
      videoCategoryId: "10",
      key,
    });

    const res = await fetch(
      `https://www.googleapis.com/youtube/v3/videos?${params}`
    );
    const data: VideosResponse = await res.json();

    if (data.error) {
      continue;
    }

    for (const item of data.items ?? []) {
      const id = item.id;
      const existing = dataFresh.find((x) => x.id === id);

      if (existing) {
        existing.frequency += 1.0;
        continue;
      }

      dataFresh.push({
        comment_count: parseInt(item.statistics.commentCount ?? "0", 10),
        frequency: 1.0,
        id,
        like_count: parseInt(item.statistics.likeCount ?? "0", 10),
        title: item.snippet.title ?? "Unknown Title",
        view_count: parseInt(item.statistics.viewCount ?? "0", 10),
      });
    }
  }

  console.log(
    `Total ${dataFresh.length} unique videos information was fetched`
  );

  // Filtering and sorting
  dataFresh = dataFresh
    .filter((x) => x.frequency >= 2.0)
    .map((x) => ({
      ...x,
      frequency: (x.frequency / regionsCount) * 100,
    }));

  console.log(
    `After filtering only ${dataFresh.length} unique videos are kept`
  );

  dataFresh.sort((a, b) => b.view_count - a.view_count);

  // Compare with existing data to find newly added videos
  const dataJsonPath = "public/data.json";
  const newlyAddedPath = "public/data-newly-added.json";

  // On CI, the previous data.json doesn't exist locally — fetch it from the live site
  let dataOld: Video[] = [];
  if (await Bun.file(dataJsonPath).exists()) {
    dataOld = await Bun.file(dataJsonPath).json();
  } else {
    try {
      const liveUrl = "https://clitic.github.io/music/data.json";
      console.log(`Fetching previous data from ${liveUrl}`);
      const res = await fetch(liveUrl);
      if (res.ok) {
        dataOld = await res.json();
        console.log(`Loaded ${dataOld.length} videos from live site`);
      }
    } catch {
      console.log("No previous data available, skipping newly-added diff");
    }
  }

  if (dataOld.length > 0) {
    const dataNew = dataFresh.filter(
      (video) => !dataOld.some((x) => x.id === video.id)
    );

    console.log(`Total ${dataNew.length} unique new videos were added`);

    dataNew.sort((a, b) => b.view_count - a.view_count);
    await Bun.write(newlyAddedPath, JSON.stringify(dataNew));
  } else {
    await Bun.write(newlyAddedPath, JSON.stringify([]));
  }

  await Bun.write(dataJsonPath, JSON.stringify(dataFresh));
  console.log("Task completed successfully");
}

main();
