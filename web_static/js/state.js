/**
 * Application State Management
 */

export const appState = {
  status: {
    playlist_url: null,
    playlist_name: null,
    track_count: null,
    spotify_connected: false,
  },
  preview: {
    csvPath: null,
    trackIndex: 0,
    side: "back",
    maxTracks: 0,
  },
  playlistHistoryType: "recent",
};
