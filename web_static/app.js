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
import { GenerateModule } from "./js/modules/generate.js";
import { ThemeModule } from "./js/modules/theme.js";
import { ProgressModule } from "./js/modules/progress.js";

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

  // Fixed header with dynamic padding
  const header = document.getElementById("appHeader");
  const appContainer = document.querySelector(".app-container");

  function updateLayout() {
    if (header && appContainer) {
      const headerHeight = header.offsetHeight;
      appContainer.style.paddingTop = `${headerHeight + 20}px`;
    }
  }

  function handleScroll() {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

    if (header) {
      if (scrollTop > 20) {
        header.classList.add("stuck");
      } else {
        header.classList.remove("stuck");
      }
    }
  }

  // Update layout on load and resize
  updateLayout();
  window.addEventListener("resize", updateLayout);
  window.addEventListener("scroll", handleScroll);
  handleScroll(); // Initial check
});

// ============================================================================
// Global Functions (for inline handlers if needed)
// ============================================================================

window.selectPlaylist = (url, name) => PlaylistModule.select(url, name);
window.selectTrackCount = (count) => TrackCountModule.select(count);
window.deletePlaylist = (url) => PlaylistModule.delete(url);
