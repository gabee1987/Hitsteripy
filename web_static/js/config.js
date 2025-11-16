/**
 * Configuration and Constants
 */

export const CONFIG = {
  STATUS_REFRESH_INTERVAL: 2000,
  RECENT_PLAYLIST_LIMIT: 10,
  THEME_KEY: "theme",
  DEFAULT_THEME: "light",
  DELETE_CONFIRM_MESSAGE:
    "Are you sure you want to delete this playlist from history?",
};

export const SELECTORS = {
  // Status
  statusPlaylist: "statusPlaylist",
  statusTrackCount: "statusTrackCount",
  statusSpotify: "statusSpotify",

  // Playlist
  playlistUrl: "playlistUrl",
  setPlaylistBtn: "setPlaylistBtn",
  playlistHistory: "playlistHistory",
  playlistTabRecent: "playlistTabRecent",
  playlistTabAll: "playlistTabAll",

  // Track Count
  trackCount: "trackCount",
  setTrackCountBtn: "setTrackCountBtn",
  trackCountHistory: "trackCountHistory",

  // Import
  importTracksBtn: "importTracksBtn",
  importStatus: "importStatus",

  // Generate
  csvFileSelect: "csvFileSelect",
  generateCardsBtn: "generateCardsBtn",
  generateStatus: "generateStatus",
  generatedCardsList: "generatedCardsList",

  // Preview
  previewCsvSelect: "previewCsvSelect",
  previewTrackIndex: "previewTrackIndex",
  previewFrontBtn: "previewFrontBtn",
  previewBackBtn: "previewBackBtn",
  loadPreviewBtn: "loadPreviewBtn",
  previewContainer: "previewContainer",
  prevTrackBtn: "prevTrackBtn",
  nextTrackBtn: "nextTrackBtn",

  // Logs
  logsContainer: "logsContainer",
  refreshLogsBtn: "refreshLogsBtn",

  // Theme
  themeToggle: "themeToggle",
  htmlVersionCheck: "htmlVersionCheck",
};
