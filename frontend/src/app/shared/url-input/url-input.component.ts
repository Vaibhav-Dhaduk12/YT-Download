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
          class="btn btn-primary url-input__btn"
          (click)="submit()"
          [disabled]="!url.trim()"
        >
          Get Info
        </button>
      </div>
      <p *ngIf="error" class="url-input__error text-error mt-1">{{ error }}</p>
    </div>
  `,
  styles: [`
    .url-input-group {
      display: flex;
      gap: 0.5rem;
    }
    .url-input {
      flex: 1;
      padding: 0.75rem 1rem;
      background: var(--bg-input);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      color: var(--text);
      font-size: 1rem;
      outline: none;
      transition: border-color 0.2s;
      &:focus {
        border-color: var(--primary);
      }
      &::placeholder {
        color: var(--text-muted);
      }
    }
    .url-input__btn {
      white-space: nowrap;
      flex-shrink: 0;
    }
    .url-input__error {
      font-size: 0.875rem;
    }
  `],
})
export class UrlInputComponent implements OnInit {
  @Input() initialUrl = '';
  @Input() placeholder = 'Paste YouTube or Instagram URL...';
  @Output() urlSubmitted = new EventEmitter<string>();

  url = '';
  error = '';

  ngOnInit(): void {
    this.url = this.initialUrl;
  }

  submit(): void {
    const trimmed = this.url.trim();
    if (!trimmed) {
      this.error = 'Please enter a URL';
      return;
    }
    this.error = '';
    this.urlSubmitted.emit(trimmed);
  }
}
