import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, CommonModule],
  template: `
    <nav class="navbar">
      <div class="container navbar-container">
        <a routerLink="/" class="navbar-brand">
          <img src="assets/icons/site-icon.svg" alt="YT Download" class="navbar-logo" />
          <span class="navbar-name">YT Download</span>
        </a>
        <ul class="navbar-links">
          <li>
            <a routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{ exact: true }" class="nav-link">
              Home
            </a>
          </li>
          <li>
            <a routerLink="/download" routerLinkActive="active" class="nav-link">
              Download
            </a>
          </li>
        </ul>
      </div>
    </nav>
  `,
  styles: [`
    .navbar {
      background: linear-gradient(180deg, var(--claude-parchment) 0%, rgba(245, 244, 237, 0.95) 100%);
      border-bottom: 1px solid var(--claude-border-cream);
      padding: 1rem 0;
      position: sticky;
      top: 0;
      z-index: 100;
      backdrop-filter: blur(8px);
      box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.05);
    }

    .navbar-container {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 2rem;
    }

    .navbar-brand {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      text-decoration: none;
      color: var(--claude-near-black);
      font-weight: 600;
      font-size: 1.25rem;
      font-family: 'Lora', serif;
      transition: all 0.3s ease;
      white-space: nowrap;

      &:hover {
        transform: translateY(-2px);
      }
    }

    .navbar-logo {
      width: 28px;
      height: 28px;
      flex-shrink: 0;
    }

    .navbar-name {
      color: var(--claude-near-black);
    }

    .navbar-links {
      list-style: none;
      display: flex;
      gap: 0.5rem;
      margin: 0;
      padding: 0;

      .nav-link {
        color: var(--claude-olive-gray);
        text-decoration: none;
        font-size: 15px;
        font-weight: 500;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 0;

        &:hover {
          color: var(--claude-near-black);
          background: var(--claude-warm-sand);
        }

        &.active {
          color: var(--claude-near-black);
          background: var(--claude-warm-sand);
          font-weight: 600;
        }
      }
    }

    @media (max-width: 768px) {
      .navbar-container {
        gap: 1rem;
      }

      .navbar-links {
        display: none;
      }

      .navbar-brand {
        flex: 1;
      }
    }
  `],
})
export class NavbarComponent {}
