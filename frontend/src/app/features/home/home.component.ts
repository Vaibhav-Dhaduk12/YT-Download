import { Component } from '@angular/core';
import { UrlInputComponent } from '../../shared/url-input/url-input.component';
import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [UrlInputComponent],
  template: `
    <section class="hero">
      <div class="container">
        <div class="hero-content">
          <h1 class="hero-title">
            Download Videos
          </h1>
          <p class="hero-subtitle">
            Paste a YouTube or Instagram link to start.
          </p>

          <div class="hero-cta">
            <app-url-input (urlSubmitted)="onUrlSubmit($event)"></app-url-input>
          </div>
        </div>
      </div>
    </section>

    <section class="features">
      <div class="container">
        <div class="features-grid">
          <div class="feature-card">
            <h3 class="feature-title">Fast</h3>
            <p class="feature-description">Quick metadata and download start.</p>
          </div>

          <div class="feature-card">
            <h3 class="feature-title">Simple</h3>
            <p class="feature-description">Clean flow with minimal steps.</p>
          </div>

          <div class="feature-card">
            <h3 class="feature-title">Reliable</h3>
            <p class="feature-description">Progress tracking and file save support.</p>
          </div>
        </div>
      </div>
    </section>
  `,
  styles: [`
    .hero {
      padding: 3rem 0 2rem;
      background: linear-gradient(135deg, var(--claude-parchment) 0%, rgba(245, 244, 237, 0.7) 100%);
    }

    .hero .container {
      max-width: 860px;
    }

    .hero-content {
      text-align: center;
    }

    .hero-title {
      font-size: 42px;
      line-height: 1.2;
      margin-bottom: 1rem;
    }

    .hero-subtitle {
      font-size: 18px;
      color: var(--claude-olive-gray);
      line-height: 1.6;
      margin-bottom: 2rem;
      max-width: 540px;
      margin-left: auto;
      margin-right: auto;
    }

    .hero-cta {
      max-width: 760px;
      margin: 0 auto;
    }

    .features {
      padding: 1rem 0 3rem;
      background: var(--claude-parchment);
    }

    .features-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 1rem;
    }

    .feature-card {
      background: var(--claude-ivory);
      border: 1px solid var(--claude-border-cream);
      border-radius: 12px;
      padding: 1.25rem;
    }

    .feature-title {
      font-size: 20px;
      margin-bottom: 0.75rem;
      color: var(--claude-near-black);
      font-family: 'Lora', serif;
      font-weight: 500;
    }

    .feature-description {
      font-size: 14px;
      color: var(--claude-olive-gray);
      line-height: 1.6;
    }

    @media (max-width: 1024px) {
      .hero-title {
        font-size: 40px;
      }
    }

    @media (max-width: 768px) {
      .hero {
        padding: 2rem 0;
      }

      .hero-title {
        font-size: 32px;
      }

      .hero-subtitle {
        font-size: 16px;
      }

      .features-grid {
        grid-template-columns: 1fr;
      }
    }
  `],
})
export class HomeComponent {
  constructor(private router: Router) {}

  onUrlSubmit(url: string): void {
    this.router.navigate(['/download'], { queryParams: { url } });
  }
}
