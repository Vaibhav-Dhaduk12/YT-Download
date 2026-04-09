import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { UrlInputComponent } from '../../shared/url-input/url-input.component';
import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [RouterLink, UrlInputComponent],
  template: `
    <div class="container">
      <section class="hero mt-4">
        <h1 class="hero__title">
          Download <span class="hero__accent">YouTube</span> &amp;
          <span class="hero__accent">Instagram</span> Videos
        </h1>
        <p class="hero__subtitle text-muted">
          Fast, free, and easy. Download videos in HD quality &mdash; no registration required.
        </p>

        <div class="hero__input mt-4">
          <app-url-input (urlSubmitted)="onUrlSubmit($event)"></app-url-input>
        </div>

        <p class="hero__legal text-muted mt-2">
          &#9888;&#65039; Educational use only. Respect platform Terms of Service.
        </p>
      </section>

      <section class="features mt-4">
        <div class="features__grid">
          <div class="card feature-card">
            <div class="feature-card__icon">&#9654;</div>
            <h3>YouTube Support</h3>
            <p class="text-muted">Videos, Shorts, playlists &mdash; all formats and qualities.</p>
          </div>
          <div class="card feature-card">
            <div class="feature-card__icon">&#128247;</div>
            <h3>Instagram Support</h3>
            <p class="text-muted">Posts, Reels, and IGTV videos.</p>
          </div>
          <div class="card feature-card">
            <div class="feature-card__icon">&#127925;</div>
            <h3>Audio Extraction</h3>
            <p class="text-muted">Extract audio as MP3 from any video.</p>
          </div>
          <div class="card feature-card">
            <div class="feature-card__icon">&#9889;</div>
            <h3>Real-time Progress</h3>
            <p class="text-muted">Live download progress via WebSocket.</p>
          </div>
        </div>
      </section>
    </div>
  `,
  styles: [`
    .hero {
      text-align: center;
      padding: 3rem 0 2rem;
    }
    .hero__title {
      font-size: 2.5rem;
      font-weight: 700;
      line-height: 1.2;
      margin-bottom: 1rem;
    }
    .hero__accent {
      color: var(--primary);
    }
    .hero__subtitle {
      font-size: 1.125rem;
      max-width: 600px;
      margin: 0 auto;
    }
    .hero__input {
      max-width: 700px;
      margin: 0 auto;
    }
    .hero__legal {
      font-size: 0.8rem;
    }
    .features__grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
    }
    .feature-card {
      text-align: center;
      padding: 1.5rem;
    }
    .feature-card__icon {
      font-size: 2rem;
      margin-bottom: 0.75rem;
    }
    .feature-card h3 {
      margin-bottom: 0.5rem;
      font-size: 1rem;
    }
    .feature-card p {
      font-size: 0.875rem;
    }
  `],
})
export class HomeComponent {
  constructor(private router: Router) {}

  onUrlSubmit(url: string): void {
    this.router.navigate(['/download'], { queryParams: { url } });
  }
}
