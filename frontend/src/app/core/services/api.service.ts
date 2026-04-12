import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { VideoMetadata } from '../models/metadata.model';
import { DownloadRequest, DownloadResponse, DownloadJob, DownloadHistoryItem } from '../models/download.model';
import { HealthResponse } from '../models/health.model';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private readonly baseUrl = '/api/v1';

  constructor(private http: HttpClient) {}

  getMetadata(url: string): Observable<VideoMetadata> {
    return this.http.post<VideoMetadata>(`${this.baseUrl}/metadata`, { url });
  }

  startDownload(request: DownloadRequest): Observable<DownloadResponse> {
    return this.http.post<DownloadResponse>(`${this.baseUrl}/download`, request);
  }

  getJobStatus(jobId: string): Observable<DownloadJob> {
    return this.http.get<DownloadJob>(`${this.baseUrl}/download/${jobId}/status`);
  }

  getDownloadUrl(jobId: string): string {
    return `${this.baseUrl}/download/${jobId}/stream`;
  }

  getHistory(): Observable<DownloadHistoryItem[]> {
    return this.http.get<DownloadHistoryItem[]>(`${this.baseUrl}/history`);
  }

  clearHistory(): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.baseUrl}/history`);
  }

  healthCheck(): Observable<HealthResponse> {
    return this.http.get<HealthResponse>(`${this.baseUrl}/health`);
  }
}
