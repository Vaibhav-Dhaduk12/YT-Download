import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./features/home/home.component').then((m) => m.HomeComponent),
  },
  {
    path: 'download',
    loadComponent: () =>
      import('./features/download/download.component').then((m) => m.DownloadComponent),
  },
  {
    path: '**',
    redirectTo: '',
  },
];
