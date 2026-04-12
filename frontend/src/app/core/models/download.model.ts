export interface DownloadRequest {
  url: string;
  format_id?: string;
  quality?: string;
  audio_only: boolean;
  subtitles?: boolean;
}

export interface DownloadResponse {
  job_id: string;
  status: string;
  message: string;
}

export interface DownloadJob {
  job_id: string;
  url: string;
  format_id?: string;
  quality: string;
  audio_only: boolean;
  subtitles: boolean;
  status: string;
  progress: number;
  filename?: string;
  file_path?: string;
  error?: string;
  title?: string;
  platform?: string;
}

export interface DownloadHistoryItem {
  job_id: string;
  url: string;
  title: string;
  platform: string;
  format: string;
  status: string;
  created_at: string;
  completed_at?: string;
  file_size?: number;
  error?: string;
}
