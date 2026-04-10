export interface VideoFormat {
  format_id: string;
  ext: string;
  resolution?: string;
  fps?: number;
  vcodec?: string;
  acodec?: string;
  filesize?: number;
  filesize_approx?: number;
  tbr?: number;
  format_note?: string;
}

export interface VideoMetadata {
  url: string;
  platform: string;
  video_id: string;
  title: string;
  description?: string;
  duration?: number;
  thumbnail?: string;
  uploader?: string;
  upload_date?: string;
  view_count?: number;
  like_count?: number;
  formats: VideoFormat[];
  is_live: boolean;
}
