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
    <section class="download-section">
      <div class="container">
        <!-- Header -->
        <div class="download-header">
          <h1 class="download-title">Get Your Video</h1>
          <p class="download-subtitle">Paste the link and choose your preferred quality</p>
        </div>

        <!-- URL Input -->
        <div class="download-input-card">
          <app-url-input
            [initialUrl]="currentUrl"
            (urlSubmitted)="onUrlSubmit($event)"
          ></app-url-input>
        </div>

        <!-- Loading state -->
        <div *ngIf="isLoadingMetadata" class="card loading-state">
          <div class="loading-content">
            <div class="loading-spinner"></div>
            <p class="loading-text">Analyzing your video...</p>
          </div>
        </div>

        <!-- Error state -->
        <div *ngIf="metadataError" class="card error-state">
          <div class="error-header">⚠️ Error</div>
          <p class="error-message">{{ metadataError }}</p>
        </div>

        <!-- Metadata display -->
        <div *ngIf="metadata && !isLoadingMetadata" class="metadata-card">
          <div class="video-info-header">
            <img
              *ngIf="metadata.thumbnail"
              [src]="metadata.thumbnail"
              [alt]="metadata.title"
              class="video-thumbnail"
            />
            <div class="video-metadata">
              <h2 class="video-title">{{ metadata.title }}</h2>
              <div class="video-meta-row">
                <span *ngIf="metadata.uploader" class="meta-item">
                  👤 {{ metadata.uploader }}
                </span>
                <span *ngIf="metadata.duration" class="meta-item">
                  ⏱️ {{ formatDuration(metadata.duration) }}
                </span>
                <span class="platform-badge" [ngClass]="'platform-' + metadata.platform">
                  {{ metadata.platform | titlecase }}
                </span>
              </div>
            </div>
          </div>

          <!-- Quality & Format Selection -->
          <div class="download-options">
            <h3 class="options-title">Quality Options</h3>
            
            <div class="option-type">
              <label class="checkbox-label">
                <input type="checkbox" [(ngModel)]="audioOnly" class="checkbox-input" />
                <span class="checkbox-text">🎵 Audio Only (MP3)</span>
              </label>
            </div>

            <div *ngIf="!audioOnly && metadata.formats.length > 0" class="quality-selector">
              <label class="quality-label">Video Quality:</label>
              <select [(ngModel)]="selectedFormatId" class="quality-select">
                <option value="">🎯 Best Available</option>
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
              class="btn btn-brand btn-download"
              (click)="startDownload()"
              [disabled]="isDownloading"
            >
              <span *ngIf="!isDownloading">📥 Download Now</span>
              <span *ngIf="isDownloading" class="download-loading">
                <span class="loading-spinner-inline"></span>
                Preparing...
              </span>
            </button>
          </div>
        </div>

        <!-- Download progress -->
        <div *ngIf="currentJob" class="progress-card">
          <div class="progress-header">
            <h3>Download Progress</h3>
            <span class="progress-percentage">{{ currentJob.progress }}%</span>
          </div>
          
          <div class="progress-bar">
            <div
              class="progress-bar-fill"
              [style.width.%]="currentJob.progress"
            ></div>
          </div>
          
          <p class="progress-status">
            <span class="status-indicator" [class.active]="currentJob.status === 'downloading'"></span>
            {{ currentJob.status | titlecase }}
          </p>

          <div *ngIf="currentJob.status === 'completed'" class="completion-section">
            <div class="success-message">✨ Download Complete!</div>
            <a
              [href]="getStreamUrl(currentJob.job_id)"
              class="btn btn-brand"
              download
            >
              💾 Save Your File
            </a>
          </div>

          <div *ngIf="currentJob.status === 'failed'" class="failure-section">
            <p class="failure-message">❌ Download failed: {{ currentJob.error }}</p>
          </div>
        </div>
      </div>
    </section>
  `,
  styles: [`
    .download-section {
      padding: 2rem 0;
    }

    .download-header {
      text-align: center;
      margin-bottom: 3rem;
    }

    .download-title {
      font-size: 42px;
      line-height: 1.2;
      margin-bottom: 0.5rem;
      background: linear-gradient(135deg, var(--claude-terracotta), var(--claude-coral));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    .download-subtitle {
      font-size: 16px;
      color: var(--claude-olive-gray);
    }

    .download-input-card {
      background: var(--claude-ivory);
      border: 1px solid var(--claude-border-cream);
      border-radius: 16px;
      padding: 2rem;
      margin-bottom: 2rem;
      box-shadow: rgba(0, 0, 0, 0.03) 0px 4px 12px;
    }

    .loading-state {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 3rem 2rem;
      background: linear-gradient(135deg, var(--claude-ivory), var(--claude-parchment));
    }

    .loading-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 1rem;
    }

    .loading-spinner {
      width: 40px;
      height: 40px;
      border: 4px solid var(--claude-border-cream);
      border-top-color: var(--claude-terracotta);
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }

    .loading-text {
      font-size: 16px;
      color: var(--claude-olive-gray);
    }

    .error-state {
      background: linear-gradient(135deg, rgba(181, 51, 51, 0.05), rgba(201, 100, 66, 0.03));
      border: 1px solid var(--claude-error);
      padding: 2rem;
    }

    .error-header {
      font-size: 16px;
      font-weight: 600;
      color: var(--claude-error);
      margin-bottom: 0.5rem;
    }

    .error-message {
      color: var(--claude-error);
      margin: 0;
    }

    .metadata-card {
      background: var(--claude-ivory);
      border: 1px solid var(--claude-border-cream);
      border-radius: 16px;
      padding: 2rem;
      margin-bottom: 2rem;
      box-shadow: rgba(0, 0, 0, 0.03) 0px 4px 12px;
    }

    .video-info-header {
      display: grid;
      grid-template-columns: 240px 1fr;
      gap: 2rem;
      margin-bottom: 2rem;
      align-items: start;
    }

    .video-thumbnail {
      width: 100%;
      height: auto;
      object-fit: cover;
      border-radius: 12px;
      box-shadow: rgba(0, 0, 0, 0.1) 0px 4px 12px;
    }

    .video-metadata {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .video-title {
      font-size: 24px;
      line-height: 1.3;
      color: var(--claude-near-black);
      font-family: 'Lora', serif;
      margin: 0;
    }

    .video-meta-row {
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      align-items: center;
    }

    .meta-item {
      font-size: 14px;
      color: var(--claude-olive-gray);
    }

    .platform-badge {
      display: inline-block;
      padding: 0.375rem 0.875rem;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;

      &.platform-youtube {
        background: rgba(201, 100, 66, 0.15);
        color: var(--claude-terracotta);
      }

      &.platform-instagram {
        background: rgba(56, 152, 236, 0.15);
        color: var(--claude-focus);
      }
    }

    .download-options {
      border-top: 1px solid var(--claude-border-cream);
      padding-top: 2rem;
    }

    .options-title {
      font-size: 18px;
      font-weight: 600;
      margin-bottom: 1.5rem;
      color: var(--claude-near-black);
      font-family: 'Lora', serif;
    }

    .option-type {
      margin-bottom: 1.5rem;
    }

    .checkbox-label {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      cursor: pointer;
      font-size: 15px;
      color: var(--claude-charcoal-warm);
    }

    .checkbox-input {
      width: 18px;
      height: 18px;
      cursor: pointer;
      accent-color: var(--claude-terracotta);
    }

    .checkbox-text {
      user-select: none;
    }

    .quality-selector {
      margin-bottom: 2rem;
    }

    .quality-label {
      display: block;
      font-size: 14px;
      font-weight: 600;
      margin-bottom: 0.75rem;
      color: var(--claude-near-black);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .quality-select {
      width: 100%;
      padding: 0.875rem 1rem;
      border: 2px solid var(--claude-border-cream);
      border-radius: 8px;
      background: var(--claude-white);
      color: var(--claude-near-black);
      font-size: 14px;
      cursor: pointer;
      transition: all 0.3s ease;

      &:hover {
        border-color: var(--claude-focus);
      }

      &:focus {
        outline: none;
        border-color: var(--claude-focus);
        box-shadow: 0px 0px 0px 3px rgba(56, 152, 236, 0.1);
      }
    }

    .btn-download {
      width: 100%;
      padding: 1rem 1.5rem;
      font-size: 16px;
      font-weight: 600;
      animation: slideUp 0.6s ease-out;
    }

    @keyframes slideUp {
      from {
        opacity: 0;
        transform: translateY(10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .download-loading {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.75rem;
    }

    .loading-spinner-inline {
      width: 14px;
      height: 14px;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-top-color: var(--claude-ivory);
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }

    /* Progress Card */
    .progress-card {
      background: var(--claude-ivory);
      border: 1px solid var(--claude-border-cream);
      border-radius: 16px;
      padding: 2rem;
      margin-bottom: 2rem;
      box-shadow: rgba(0, 0, 0, 0.03) 0px 4px 12px;
      animation: slideUp 0.6s ease-out;
    }

    .progress-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
    }

    .progress-header h3 {
      font-size: 18px;
      font-weight: 600;
      margin: 0;
      color: var(--claude-near-black);
      font-family: 'Lora', serif;
    }

    .progress-percentage {
      font-size: 24px;
      font-weight: 600;
      color: var(--claude-terracotta);
    }

    .progress-bar {
      width: 100%;
      height: 12px;
      background: var(--claude-border-cream);
      border-radius: 100px;
      overflow: hidden;
      margin-bottom: 1rem;
    }

    .progress-bar-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--claude-terracotta), var(--claude-coral));
      border-radius: 100px;
      transition: width 0.3s ease;
      box-shadow: 0 0 8px rgba(201, 100, 66, 0.3);
    }

    .progress-status {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      font-size: 14px;
      color: var(--claude-olive-gray);
      margin: 0;
    }

    .status-indicator {
      display: inline-block;
      width: 8px;
      height: 8px;
      background: var(--claude-stone-gray);
      border-radius: 50%;
      transition: all 0.3s ease;

      &.active {
        background: var(--claude-terracotta);
        box-shadow: 0 0 8px var(--claude-terracotta);
        animation: pulse-dot 1s ease-in-out infinite;
      }
    }

    @keyframes pulse-dot {
      0%, 100% {
        opacity: 1;
      }
      50% {
        opacity: 0.6;
      }
    }

    .completion-section {
      margin-top: 1.5rem;
      padding-top: 1.5rem;
      border-top: 1px solid var(--claude-border-cream);
      text-align: center;
    }

    .success-message {
      font-size: 16px;
      font-weight: 600;
      color: var(--claude-terracotta);
      margin-bottom: 1rem;
    }

    .failure-section {
      margin-top: 1.5rem;
      padding: 1rem;
      background: rgba(181, 51, 51, 0.05);
      border: 1px solid var(--claude-error);
      border-radius: 8px;
    }

    .failure-message {
      color: var(--claude-error);
      margin: 0;
      font-size: 14px;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    /* Responsive Design */
    @media (max-width: 768px) {
      .download-title {
        font-size: 28px;
      }

      .download-header {
        margin-bottom: 2rem;
      }

      .video-info-header {
        grid-template-columns: 1fr;
        gap: 1rem;
      }

      .video-thumbnail {
        max-width: 100%;
      }

      .metadata-card,
      .download-input-card {
        padding: 1.5rem;
      }

      .quality-selector {
        margin-bottom: 1rem;
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
