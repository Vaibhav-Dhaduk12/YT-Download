import { Injectable, OnDestroy } from '@angular/core';
import { Observable, Subject } from 'rxjs';

export interface ProgressMessage {
  job_id: string;
  progress: number;
  status: string;
}

@Injectable({
  providedIn: 'root',
})
export class WebSocketService implements OnDestroy {
  private socket: WebSocket | null = null;
  private messageSubject = new Subject<ProgressMessage>();

  connect(jobId: string): Observable<ProgressMessage> {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/progress/${jobId}`;

    this.socket = new WebSocket(wsUrl);

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as ProgressMessage;
        this.messageSubject.next(data);
      } catch {
        console.error('Failed to parse WebSocket message');
      }
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return this.messageSubject.asObservable();
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  ngOnDestroy(): void {
    this.disconnect();
  }
}
