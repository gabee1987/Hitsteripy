/**
 * Hitsteripy Web App - Main Entry Point
 */

import { CONFIG, SELECTORS } from "./js/config.js";
import { DOMUtils } from "./js/dom-utils.js";
import { TabManager } from "./js/tabs.js";
import { EventHandlers } from "./js/events.js";
import { StatusModule } from "./js/modules/status.js";
import { PlaylistModule } from "./js/modules/playlist.js";
import { TrackCountModule } from "./js/modules/trackCount.js";
import { CsvModule } from "./js/modules/csv.js";
import { ThemeModule } from "./js/modules/theme.js";

// ============================================================================
// Initialization
// ============================================================================

document.addEventListener("DOMContentLoaded", () => {
  // Clear cached data
  if ("caches" in window) {
    caches.keys().then((names) => {
      names.forEach((name) => caches.delete(name));
    });
  }

  // Check for cached version
  const fullHtmlText = document.documentElement.outerHTML;
  const versionIndicator = DOMUtils.get(SELECTORS.htmlVersionCheck);

  if (!fullHtmlText.includes("Version check: v2")) {
    console.error(
      "⚠️ WARNING: Page appears to be cached! Please hard refresh (Ctrl+Shift+R)."
    );
    if (versionIndicator) {
      versionIndicator.style.display = "block";
    }
  } else if (versionIndicator) {
    versionIndicator.style.display = "none";
  }

  // Initialize app
  TabManager.setup();
  EventHandlers.setup();
  ThemeModule.setup();
  StatusModule.load();
  PlaylistModule.loadHistory("recent");
  TrackCountModule.loadHistory();
  CsvModule.load();

  // Auto-refresh status
  setInterval(() => StatusModule.load(), CONFIG.STATUS_REFRESH_INTERVAL);
});

// ============================================================================
// Global Functions (for inline handlers if needed)
// ============================================================================

window.selectPlaylist = (url, name) => PlaylistModule.select(url, name);
window.selectTrackCount = (count) => TrackCountModule.select(count);
window.deletePlaylist = (url) => PlaylistModule.delete(url);
