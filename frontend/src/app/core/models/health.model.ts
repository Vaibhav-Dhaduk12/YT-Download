export interface ToolStatus {
  ffmpeg?: boolean;
  ffprobe?: boolean;
  yt_dlp?: boolean;
  [tool: string]: boolean | undefined;
}

export interface HealthResponse {
  status: string;
  version: string;
  environment: string;
  python_version: string;
  tools: ToolStatus;
}
