import { Component } from '@angular/core';

@Component({
  selector: 'app-footer',
  standalone: true,
  template: `
    <footer class="footer">
      <div class="container">
        <p class="text-muted">
          &#9888;&#65039; For educational purposes only. Respect content creators' rights and platform Terms of Service.
        </p>
        <p class="text-muted mt-1">
          Built with FastAPI + Angular 17 &middot; Powered by yt-dlp
        </p>
      </div>
    </footer>
  `,
  styles: [`
    .footer {
      padding: 2rem 0;
      text-align: center;
      border-top: 1px solid var(--border);
      margin-top: 3rem;
      font-size: 0.875rem;
    }
  `],
})
export class FooterComponent {}
