import { EMPTY, of, throwError } from 'rxjs';

import { DownloadComponent } from './download.component';
import { VideoMetadata } from '../../core/models/metadata.model';

describe('DownloadComponent', () => {
  const routeStub = {
    queryParams: EMPTY,
  };

  const createComponent = () => {
    const apiService = jasmine.createSpyObj('ApiService', [
      'getMetadata',
      'startDownload',
      'getJobStatus',
      'getDownloadUrl',
      'healthCheck',
    ]);
    apiService.getDownloadUrl.and.returnValue('/api/v1/download/fake/stream');
    apiService.healthCheck.and.returnValue(
      of({
        status: 'healthy',
        version: '1.0.0',
        environment: 'test',
        python_version: '3.11.0',
        tools: { ffmpeg: true, ffprobe: true, yt_dlp: true },
      }),
    );

    const component = new DownloadComponent(routeStub as any, apiService);
    return { component, apiService };
  };

  const metadataFixture: VideoMetadata = {
    url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    platform: 'youtube',
    video_id: 'dQw4w9WgXcQ',
    title: 'Never Gonna Give You Up',
    formats: [
      {
        format_id: '137',
        ext: 'mp4',
        resolution: '1920x1080',
        vcodec: 'avc1.640028',
        acodec: 'none',
      },
      {
        format_id: '22',
        ext: 'mp4',
        resolution: '1280x720',
        vcodec: 'avc1.64001F',
        acodec: 'mp4a.40.2',
      },
    ],
    is_live: false,
  };

  it('filters out video-only formats when merge is unavailable', () => {
    const { component } = createComponent();
    component.metadata = metadataFixture;
    component.isMergeCapable = false;

    const formats = component.getVideoFormats();
    expect(formats.length).toBe(1);
    expect(formats[0].format_id).toBe('22');
  });

  it('does not send format_id when merge is unavailable', () => {
    const { component, apiService } = createComponent();
    apiService.startDownload.and.returnValue(
      throwError(() => ({ error: { detail: 'forced error' } })),
    );

    component.currentUrl = metadataFixture.url;
    component.selectedFormatId = '137';
    component.audioOnly = false;
    component.isMergeCapable = false;

    component.startDownload();

    expect(apiService.startDownload).toHaveBeenCalled();
    const payload = apiService.startDownload.calls.mostRecent().args[0];
    expect(payload.format_id).toBeUndefined();
    expect(payload.quality).toBe('best');
  });

  it('sends selected format_id when merge is available', () => {
    const { component, apiService } = createComponent();
    apiService.startDownload.and.returnValue(
      throwError(() => ({ error: { detail: 'forced error' } })),
    );

    component.currentUrl = metadataFixture.url;
    component.selectedFormatId = '137';
    component.audioOnly = false;
    component.isMergeCapable = true;

    component.startDownload();

    expect(apiService.startDownload).toHaveBeenCalled();
    const payload = apiService.startDownload.calls.mostRecent().args[0];
    expect(payload.format_id).toBe('137');
    expect(payload.quality).toBeUndefined();
  });
});
