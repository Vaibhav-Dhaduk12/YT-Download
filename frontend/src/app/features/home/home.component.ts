import { Component } from '@angular/core';
import { UrlInputComponent } from '../../shared/url-input/url-input.component';
import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [UrlInputComponent],
  template: `
    <!-- Hero Section -->
    <section class="hero">
      <div class="container">
        <div class="hero-content">
          <h1 class="hero-title">
            Download <span class="hero-accent">YouTube</span> Videos<br />
            in Seconds
          </h1>
          <p class="hero-subtitle">
            The fastest, most elegant way to save your favorite videos. No registration, no ads, just pure simplicity.
          </p>

          <div class="hero-cta">
            <app-url-input (urlSubmitted)="onUrlSubmit($event)"></app-url-input>
          </div>

          <p class="hero-legal">
            ✨ Free and open source • Supports YouTube, Instagram &amp; more
          </p>
        </div>

        <div class="hero-visual">
          <div class="hero-shape hero-shape-1"></div>
          <div class="hero-shape hero-shape-2"></div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">Why Choose YT Download Studio?</h2>
          <p class="section-subtitle">Everything you need to download, all in one place</p>
        </div>

        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon youtube-icon">▶</div>
            <h3 class="feature-title">Multi-Platform</h3>
            <p class="feature-description">YouTube, Instagram, TikTok, and many more platforms supported.</p>
            <span class="feature-badge">Premium</span>
          </div>

          <div class="feature-card">
            <div class="feature-icon hd-icon">🎬</div>
            <h3 class="feature-title">4K Ultra HD</h3>
            <p class="feature-description">Download videos in stunning 4K quality with crystal-clear audio.</p>
            <span class="feature-badge">Fast</span>
          </div>

          <div class="feature-card">
            <div class="feature-icon audio-icon">♪</div>
            <h3 class="feature-title">Audio Extraction</h3>
            <p class="feature-description">Extract and save audio as MP3 or other formats instantly.</p>
            <span class="feature-badge">Easy</span>
          </div>

          <div class="feature-card">
            <div class="feature-icon lightning-icon">⚡</div>
            <h3 class="feature-title">Lightning Fast</h3>
            <p class="feature-description">Real-time progress tracking with blazingly fast download speeds.</p>
            <span class="feature-badge">Real-time</span>
          </div>

          <div class="feature-card">
            <div class="feature-icon batch-icon">📦</div>
            <h3 class="feature-title">Batch Downloads</h3>
            <p class="feature-description">Download multiple videos at once from playlists seamlessly.</p>
            <span class="feature-badge">Pro</span>
          </div>

          <div class="feature-card">
            <div class="feature-icon lock-icon">🔒</div>
            <h3 class="feature-title">100% Private</h3>
            <p class="feature-description">No tracking, no ads, no registration. Your downloads stay private.</p>
            <span class="feature-badge">Secure</span>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <div class="container cta-container">
        <div class="cta-content">
          <h2>Ready to get started?</h2>
          <p>Paste a video link above and download instantly. It's that simple.</p>
          <button class="btn btn-brand btn-lg" (click)="scrollToInput()">Start Downloading</button>
        </div>
      </div>
    </section>
  `,
  styles: [`
    /* Hero Section */
    .hero {
      padding: 4rem 0;
      background: linear-gradient(135deg, var(--claude-parchment) 0%, rgba(245, 244, 237, 0.7) 100%);
      position: relative;
      overflow: hidden;
    }

    .hero .container {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 4rem;
      align-items: center;
    }

    .hero-content {
      z-index: 2;
      animation: slideInLeft 0.8s ease-out;
    }

    .hero-title {
      font-size: 56px;
      line-height: 1.15;
      margin-bottom: 1.5rem;
      color: var(--claude-near-black);
      font-family: 'Lora', serif;
      font-weight: 500;
    }

    .hero-accent {
      background: linear-gradient(135deg, var(--claude-terracotta), var(--claude-coral));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    .hero-subtitle {
      font-size: 18px;
      color: var(--claude-olive-gray);
      line-height: 1.6;
      margin-bottom: 2rem;
      max-width: 500px;
    }

    .hero-cta {
      margin-bottom: 1.5rem;
    }

    .hero-legal {
      font-size: 14px;
      color: var(--claude-stone-gray);
    }

    .hero-visual {
      position: relative;
      height: 400px;
      animation: slideInRight 0.8s ease-out;
    }

    .hero-shape {
      position: absolute;
      border-radius: 32px;
      opacity: 0.1;
    }

    .hero-shape-1 {
      width: 300px;
      height: 300px;
      background: var(--claude-terracotta);
      top: 0;
      right: 0;
      animation: float 6s ease-in-out infinite;
    }

    .hero-shape-2 {
      width: 200px;
      height: 200px;
      background: var(--claude-coral);
      bottom: 0;
      left: 50px;
      animation: float 8s ease-in-out infinite reverse;
    }

    @keyframes slideInLeft {
      from {
        opacity: 0;
        transform: translateX(-50px);
      }
      to {
        opacity: 1;
        transform: translateX(0);
      }
    }

    @keyframes slideInRight {
      from {
        opacity: 0;
        transform: translateX(50px);
      }
      to {
        opacity: 1;
        transform: translateX(0);
      }
    }

    @keyframes float {
      0%, 100% {
        transform: translateY(0px);
      }
      50% {
        transform: translateY(-20px);
      }
    }

    /* Features Section */
    .features {
      padding: 5rem 0;
      background: var(--claude-parchment);
    }

    .section-header {
      text-align: center;
      margin-bottom: 3rem;
    }

    .section-title {
      font-size: 42px;
      margin-bottom: 1rem;
      color: var(--claude-near-black);
      font-family: 'Lora', serif;
      font-weight: 500;
    }

    .section-subtitle {
      font-size: 18px;
      color: var(--claude-olive-gray);
      margin: 0;
    }

    .features-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 2rem;
    }

    .feature-card {
      background: var(--claude-ivory);
      border: 1px solid var(--claude-border-cream);
      border-radius: 16px;
      padding: 2rem;
      text-align: center;
      transition: all 0.3s ease;
      position: relative;
      overflow: hidden;

      &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--claude-terracotta), var(--claude-coral));
        transform: scaleX(0);
        transform-origin: left;
        transition: transform 0.3s ease;
      }

      &:hover {
        transform: translateY(-8px);
        box-shadow: rgba(0, 0, 0, 0.08) 0px 8px 32px;

        &::before {
          transform: scaleX(1);
        }
      }
    }

    .feature-icon {
      font-size: 3rem;
      margin-bottom: 1rem;
      display: inline-block;
      animation: heartbeat 2s ease-in-out infinite;
    }

    @keyframes heartbeat {
      0%, 100% {
        transform: scale(1);
      }
      50% {
        transform: scale(1.1);
      }
    }

    .feature-title {
      font-size: 20px;
      margin-bottom: 0.75rem;
      color: var(--claude-near-black);
      font-family: 'Lora', serif;
      font-weight: 500;
    }

    .feature-description {
      font-size: 15px;
      color: var(--claude-olive-gray);
      line-height: 1.6;
      margin-bottom: 1rem;
    }

    .feature-badge {
      display: inline-block;
      background: linear-gradient(135deg, var(--claude-terracotta), var(--claude-coral));
      color: var(--claude-ivory);
      padding: 0.375rem 0.875rem;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    /* CTA Section */
    .cta-section {
      padding: 4rem 0;
      background: linear-gradient(135deg, var(--claude-near-black) 0%, #2a2a25 100%);
    }

    .cta-container {
      text-align: center;
    }

    .cta-content h2 {
      font-size: 36px;
      color: var(--claude-ivory);
      font-family: 'Lora', serif;
      margin-bottom: 0.75rem;
    }

    .cta-content p {
      font-size: 18px;
      color: var(--claude-warm-silver);
      margin-bottom: 2rem;
    }

    .btn-lg {
      padding: 1rem 2rem;
      font-size: 16px;
    }

    /* Responsive Design */
    @media (max-width: 1024px) {
      .hero .container {
        grid-template-columns: 1fr;
        gap: 2rem;
      }

      .hero-visual {
        display: none;
      }

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

      .section-title {
        font-size: 28px;
      }

      .cta-content h2 {
        font-size: 24px;
      }
    }
  `],
})
export class HomeComponent {
  constructor(private router: Router) {}

  onUrlSubmit(url: string): void {
    this.router.navigate(['/download'], { queryParams: { url } });
  }

  scrollToInput(): void {
    const element = document.querySelector('.hero-cta');
    element?.scrollIntoView({ behavior: 'smooth' });
  }
}
