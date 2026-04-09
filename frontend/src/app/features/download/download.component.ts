import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subscription, interval } from 'rxjs';
import { switchMap, takeWhile } from 'rxjs/operators';
import { ApiService } from '../../core/services/api.service';
import { VideoMetadata, VideoFormat } from '../../core/models/metadata.model';
import { DownloadJob } from '../../core/models/download.model';
import { UrlInputComponent } from '../../shared/url-input/url-input.component';

@Component({
  selector: 'app-download',
  standalone: true,
  imports: [CommonModule, FormsModule, UrlInputComponent],
  template: `
    <div class="container">
      <h1 class="mt-3 mb-3">Download Video</h1>

      <app-url-input
        [initialUrl]="currentUrl"
        (urlSubmitted)="onUrlSubmit($event)"
      ></app-url-input>

      <!-- Loading state -->
      <div *ngIf="isLoadingMetadata" class="card mt-3 loading-card">
        <div class="loading-spinner"></div>
        <p class="text-muted mt-2">Fetching video information...</p>
      </div>

      <!-- Error state -->
      <div *ngIf="metadataError" class="card mt-3 error-card">
        <p class="text-error">{{ metadataError }}</p>
      </div>

      <!-- Metadata display -->
      <div *ngIf="metadata && !isLoadingMetadata" class="card mt-3">
        <div class="video-info">
          <img
            *ngIf="metadata.thumbnail"
            [src]="metadata.thumbnail"
            [alt]="metadata.title"
            class="video-thumbnail"
          />
          <div class="video-details">
            <h2 class="video-title">{{ metadata.title }}</h2>
            <p class="text-muted" *ngIf="metadata.uploader">By {{ metadata.uploader }}</p>
            <p class="text-muted" *ngIf="metadata.duration">
              Duration: {{ formatDuration(metadata.duration) }}
            </p>
            <span class="platform-badge platform-badge--{{ metadata.platform }}">
              {{ metadata.platform | titlecase }}
            </span>
          </div>
        </div>

        <!-- Format selection -->
        <div class="download-options mt-3">
          <h3 class="mb-2">Download Options</h3>

          <div class="option-group">
            <label class="option-label">
              <input type="checkbox" [(ngModel)]="audioOnly" />
              Audio Only (MP3)
            </label>
          </div>

          <div class="option-group mt-2" *ngIf="!audioOnly && metadata.formats.length > 0">
            <label>Quality:</label>
            <select [(ngModel)]="selectedFormatId" class="format-select mt-1">
              <option value="">Best Available</option>
              <option
                *ngFor="let fmt of getVideoFormats()"
                [value]="fmt.format_id"
              >
                {{ fmt.resolution || 'Unknown' }}
                {{ fmt.ext ? '(' + fmt.ext + ')' : '' }}
                {{ fmt.filesize ? '~ ' + formatFileSize(fmt.filesize) : '' }}
              </option>
            </select>
          </div>

          <button
            class="btn btn-primary mt-3"
            (click)="startDownload()"
            [disabled]="isDownloading"
          >
            <span *ngIf="!isDownloading">&#8681; Download</span>
            <span *ngIf="isDownloading" class="loading-inline">
              <span class="loading-spinner"></span>
              Downloading...
            </span>
          </button>
        </div>
      </div>

      <!-- Download progress -->
      <div *ngIf="currentJob" class="card mt-3">
        <h3 class="mb-2">Download Progress</h3>
        <div class="progress-bar">
          <div
            class="progress-bar__fill"
            [style.width.%]="currentJob.progress"
          ></div>
        </div>
        <p class="mt-1 text-muted">
          {{ currentJob.progress }}% &mdash; {{ currentJob.status | titlecase }}
        </p>

        <div *ngIf="currentJob.status === 'completed'" class="mt-2">
          <a
            [href]="getStreamUrl(currentJob.job_id)"
            class="btn btn-success"
            download
          >
            &#8681; Save File
          </a>
        </div>

        <p *ngIf="currentJob.status === 'failed'" class="text-error mt-1">
          Download failed: {{ currentJob.error }}
        </p>
      </div>
    </div>
  `,
  styles: [`
    .loading-card {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 2rem;
    }
    .error-card {
      border-color: var(--error);
    }
    .video-info {
      display: flex;
      gap: 1.5rem;
      align-items: flex-start;
    }
    .video-thumbnail {
      width: 200px;
      height: 112px;
      object-fit: cover;
      border-radius: var(--radius);
      flex-shrink: 0;
    }
    .video-details {
      flex: 1;
    }
    .video-title {
      font-size: 1.125rem;
      margin-bottom: 0.5rem;
      line-height: 1.4;
    }
    .platform-badge {
      display: inline-block;
      padding: 0.25rem 0.75rem;
      border-radius: 100px;
      font-size: 0.75rem;
      font-weight: 600;
      margin-top: 0.5rem;
      &--youtube {
        background: rgba(255,0,0,0.2);
        color: #ff4444;
      }
      &--instagram {
        background: rgba(64,93,230,0.2);
        color: #8a9de8;
      }
    }
    .option-group {
      label {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        cursor: pointer;
      }
    }
    .format-select {
      display: block;
      width: 100%;
      max-width: 400px;
      padding: 0.5rem;
      background: var(--bg-input);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      color: var(--text);
      font-size: 0.9rem;
    }
    .loading-inline {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    @media (max-width: 600px) {
      .video-info {
        flex-direction: column;
      }
      .video-thumbnail {
        width: 100%;
        height: auto;
      }
    }
  `],
})
export class DownloadComponent implements OnInit, OnDestroy {
  currentUrl = '';
  metadata: VideoMetadata | null = null;
  isLoadingMetadata = false;
  metadataError = '';

  selectedFormatId = '';
  audioOnly = false;

  currentJob: DownloadJob | null = null;
  isDownloading = false;

  private pollSub: Subscription | null = null;

  constructor(
    private route: ActivatedRoute,
    private apiService: ApiService,
  ) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe((params) => {
      if (params['url']) {
        this.currentUrl = params['url'];
        this.loadMetadata(this.currentUrl);
      }
    });
  }

  ngOnDestroy(): void {
    this.pollSub?.unsubscribe();
  }

  onUrlSubmit(url: string): void {
    this.currentUrl = url;
    this.loadMetadata(url);
  }

  loadMetadata(url: string): void {
    this.isLoadingMetadata = true;
    this.metadataError = '';
    this.metadata = null;
    this.currentJob = null;

    this.apiService.getMetadata(url).subscribe({
      next: (data) => {
        this.metadata = data;
        this.isLoadingMetadata = false;
      },
      error: (err) => {
        this.metadataError =
          err.error?.detail || 'Failed to fetch video info. Please check the URL.';
        this.isLoadingMetadata = false;
      },
    });
  }

  startDownload(): void {
    if (!this.currentUrl || this.isDownloading) return;

    this.isDownloading = true;
    this.currentJob = null;

    this.apiService
      .startDownload({
        url: this.currentUrl,
        format_id: this.selectedFormatId || undefined,
        audio_only: this.audioOnly,
        quality: 'best',
      })
      .subscribe({
        next: (response) => {
          this.pollJobStatus(response.job_id);
        },
        error: (err) => {
          this.isDownloading = false;
          this.metadataError =
            err.error?.detail || 'Failed to start download. Please try again.';
        },
      });
  }

  pollJobStatus(jobId: string): void {
    this.pollSub = interval(1000)
      .pipe(
        switchMap(() => this.apiService.getJobStatus(jobId)),
        takeWhile(
          (job) => job.status !== 'completed' && job.status !== 'failed',
          true,
        ),
      )
      .subscribe({
        next: (job) => {
          this.currentJob = job;
          if (job.status === 'completed' || job.status === 'failed') {
            this.isDownloading = false;
          }
        },
        error: () => {
          this.isDownloading = false;
        },
      });
  }

  getStreamUrl(jobId: string): string {
    return this.apiService.getDownloadUrl(jobId);
  }

  getVideoFormats(): VideoFormat[] {
    if (!this.metadata) return [];
    return this.metadata.formats.filter(
      (f) => f.vcodec && f.vcodec !== 'none' && f.resolution,
    );
  }

  formatDuration(seconds: number): string {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    return `${m}:${String(s).padStart(2, '0')}`;
  }

  formatFileSize(bytes: number): string {
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }
}
