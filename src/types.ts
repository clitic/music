export interface Video {
  comment_count: number;
  frequency: number;
  id: string;
  like_count: number;
  title: string;
  view_count: number;
}

export type SortKey = "views" | "likes" | "comments" | "frequency";
export type Theme = "adaptive" | "light" | "dark";
