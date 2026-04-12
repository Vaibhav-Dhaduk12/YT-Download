import { Component } from '@angular/core';

@Component({
  selector: 'app-footer',
  standalone: true,
  template: `
    <footer class="footer">
      <div class="container">
        <div class="footer-bottom">
          <p class="footer-text-small">YT Download</p>
          <p class="footer-text-small">For educational use only.</p>
        </div>
      </div>
    </footer>
  `,
  styles: [`
    .footer {
      background: linear-gradient(180deg, var(--claude-ivory) 0%, var(--claude-parchment) 100%);
      border-top: 1px solid var(--claude-border-cream);
      padding: 1.25rem 0;
      margin-top: 2rem;
    }

    .footer-text-small {
      font-size: 13px;
      color: var(--claude-stone-gray);
      line-height: 1.6;
    }

    .footer-bottom {
      text-align: center;
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }

    @media (max-width: 768px) {
      .footer {
        padding: 1rem 0;
      }
    }
  `],
})
export class FooterComponent {}
