import { Component } from '@angular/core';

@Component({
  selector: 'app-footer',
  standalone: true,
  template: `
    <footer class="footer">
      <div class="container">
        <div class="footer-content">
          <div class="footer-section">
            <h4 class="footer-title">YT Download Studio</h4>
            <p class="footer-text">Download your favorite YouTube content with ease and efficiency.</p>
          </div>
          
          <div class="footer-links">
            <h5 class="footer-subtitle">Quick Links</h5>
            <ul>
              <li><a href="#home">Home</a></li>
              <li><a href="#download">Download</a></li>
              <li><a href="#about">About</a></li>
            </ul>
          </div>

          <div class="footer-legal">
            <h5 class="footer-subtitle">Legal</h5>
            <p class="footer-text-small">
              ⚠️ For educational purposes only. Respect content creators' rights and platform Terms of Service.
            </p>
          </div>
        </div>

        <div class="footer-divider"></div>

        <div class="footer-bottom">
          <p class="footer-text-small">Built with <span class="highlight">FastAPI + Angular 17</span> • Powered by <span class="highlight">yt-dlp</span></p>
          <p class="footer-text-small">&copy; 2024 YT Download Studio. All rights reserved.</p>
        </div>
      </div>
    </footer>
  `,
  styles: [`
    .footer {
      background: linear-gradient(180deg, var(--claude-ivory) 0%, var(--claude-parchment) 100%);
      border-top: 1px solid var(--claude-border-cream);
      padding: 3rem 0 2rem;
      margin-top: 4rem;
    }

    .footer-content {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 2rem;
      margin-bottom: 2rem;
    }

    .footer-section {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    .footer-title {
      font-size: 18px;
      font-weight: 600;
      color: var(--claude-near-black);
      font-family: 'Lora', serif;
    }

    .footer-subtitle {
      font-size: 14px;
      font-weight: 600;
      color: var(--claude-near-black);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .footer-text {
      font-size: 14px;
      color: var(--claude-olive-gray);
      line-height: 1.6;
    }

    .footer-text-small {
      font-size: 13px;
      color: var(--claude-stone-gray);
      line-height: 1.6;
    }

    .footer-links ul {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      padding: 0;
      margin: 0;

      li a {
        color: var(--claude-olive-gray);
        text-decoration: none;
        font-size: 14px;
        transition: all 0.3s ease;

        &:hover {
          color: var(--claude-terracotta);
          transform: translateX(4px);
        }
      }
    }

    .footer-divider {
      height: 1px;
      background: var(--claude-border-cream);
      margin: 2rem 0;
    }

    .footer-bottom {
      text-align: center;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;

      .highlight {
        color: var(--claude-terracotta);
        font-weight: 600;
      }
    }

    @media (max-width: 768px) {
      .footer-content {
        grid-template-columns: 1fr;
        gap: 1.5rem;
      }

      .footer {
        padding: 2rem 0 1.5rem;
      }
    }
  `],
})
export class FooterComponent {}
