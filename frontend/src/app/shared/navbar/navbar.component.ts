import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  template: `
    <nav class="navbar">
      <div class="container navbar__inner">
        <a routerLink="/" class="navbar__brand">
          <span class="navbar__logo">&#9654;</span>
          <span class="navbar__name">YT Download</span>
        </a>
        <ul class="navbar__links">
          <li><a routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{ exact: true }">Home</a></li>
          <li><a routerLink="/download" routerLinkActive="active">Download</a></li>
        </ul>
      </div>
    </nav>
  `,
  styles: [`
    .navbar {
      background: #111;
      border-bottom: 1px solid var(--border);
      padding: 1rem 0;
      position: sticky;
      top: 0;
      z-index: 100;
      backdrop-filter: blur(10px);
    }
    .navbar__inner {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .navbar__brand {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      text-decoration: none;
      color: var(--text);
      font-weight: 700;
      font-size: 1.25rem;
    }
    .navbar__logo {
      font-size: 1.5rem;
      color: var(--primary);
    }
    .navbar__links {
      list-style: none;
      display: flex;
      gap: 1.5rem;
      a {
        color: var(--text-muted);
        text-decoration: none;
        transition: color 0.2s;
        &:hover, &.active {
          color: var(--text);
        }
      }
    }
  `],
})
export class NavbarComponent {}
