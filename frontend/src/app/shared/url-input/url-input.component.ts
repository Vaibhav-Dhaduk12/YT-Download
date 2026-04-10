import { Component, EventEmitter, Input, Output, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-url-input',
  standalone: true,
  imports: [FormsModule, CommonModule],
  template: `
    <div class="url-input-wrapper">
      <div class="url-input-group">
        <input
          type="url"
          class="url-input"
          [placeholder]="placeholder"
          [(ngModel)]="url"
          (keydown.enter)="submit()"
          autocomplete="off"
          spellcheck="false"
        />
        <button
          class="btn btn-brand url-input-btn"
          (click)="submit()"
          [disabled]="!url.trim()"
        >
          <span *ngIf="!loading">Download ↓</span>
          <span *ngIf="loading" class="loading-spinner-inline"></span>
        </button>
      </div>
      <p *ngIf="error" class="url-input-error text-error mt-1">{{ error }}</p>
      <p *ngIf="success" class="url-input-success mt-1">✨ {{ success }}</p>
    </div>
  `,
  styles: [`
    .url-input-wrapper {
      width: 100%;
    }

    .url-input-group {
      display: flex;
      gap: 0.75rem;
      align-items: stretch;
    }

    .url-input {
      flex: 1;
      padding: 1rem 1.25rem;
      background: var(--claude-white);
      border: 2px solid var(--claude-border-cream);
      border-radius: 12px;
      color: var(--claude-near-black);
      font-size: 16px;
      outline: none;
      transition: all 0.3s ease;
      font-family: 'Inter', sans-serif;

      &:focus {
        border-color: var(--claude-focus);
        box-shadow: 0px 0px 0px 3px rgba(56, 152, 236, 0.1);
      }

      &::placeholder {
        color: var(--claude-stone-gray);
      }

      &:disabled {
        background: var(--claude-warm-sand);
        cursor: not-allowed;
      }
    }

    .url-input-btn {
      white-space: nowrap;
      flex-shrink: 0;
      min-width: 140px;
      font-weight: 600;
      transition: all 0.3s ease;

      &:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: rgba(0, 0, 0, 0.1) 0px 8px 16px;
      }

      &:active:not(:disabled) {
        transform: translateY(0px);
      }

      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }
    }

    .loading-spinner-inline {
      display: inline-block;
      width: 16px;
      height: 16px;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-top-color: var(--claude-ivory);
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    .url-input-error {
      font-size: 13px;
      color: var(--claude-error);
      animation: slideDown 0.3s ease-out;
    }

    .url-input-success {
      font-size: 13px;
      color: var(--claude-terracotta);
      animation: slideDown 0.3s ease-out;
    }

    @keyframes slideDown {
      from {
        opacity: 0;
        transform: translateY(-8px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    @media (max-width: 640px) {
      .url-input {
        padding: 0.875rem 1rem;
        font-size: 14px;
      }

      .url-input-btn {
        min-width: 100px;
        padding: 0.75rem 1rem;
      }
    }
  `],
})
export class UrlInputComponent implements OnInit {
  @Input() initialUrl = '';
  @Input() placeholder = 'Paste YouTube or Instagram URL...';
  @Output() urlSubmitted = new EventEmitter<string>();

  url = '';
  error = '';
  success = '';
  loading = false;

  ngOnInit(): void {
    this.url = this.initialUrl;
  }

  submit(): void {
    const trimmed = this.url.trim();
    if (!trimmed) {
      this.error = 'Please enter a video URL';
      this.success = '';
      setTimeout(() => this.error = '', 3000);
      return;
    }

    // Basic URL validation
    if (!this.isValidUrl(trimmed)) {
      this.error = 'Please enter a valid YouTube or Instagram URL';
      this.success = '';
      setTimeout(() => this.error = '', 3000);
      return;
    }

    this.error = '';
    this.success = 'Processing your video...';
    this.loading = true;
    
    setTimeout(() => {
      this.urlSubmitted.emit(trimmed);
      this.loading = false;
      this.success = '';
    }, 500);
  }

  private isValidUrl(url: string): boolean {
    try {
      const urlObj = new URL(url);
      return urlObj.hostname.includes('youtube') || urlObj.hostname.includes('instagram') || 
             urlObj.hostname.includes('youtu.be') || urlObj.hostname.includes('instagram.com');
    } catch {
      return false;
    }
  }
}
