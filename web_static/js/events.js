/**
 * Event Handlers Setup
 */

import { DOMUtils } from "./dom-utils.js";
import { SELECTORS } from "./config.js";
import { PlaylistModule } from "./modules/playlist.js";
import { TrackCountModule } from "./modules/trackCount.js";
import { ImportModule } from "./modules/import.js";
import { GenerateModule } from "./modules/generate.js";
import { PreviewModule } from "./modules/preview.js";
import { LogsModule } from "./modules/logs.js";
import { ThemeModule } from "./modules/theme.js";

export const EventHandlers = {
  /**
   * Setup all event listeners
   */
  setup() {
    // Playlist
    this.safeAddEventListener(SELECTORS.setPlaylistBtn, "click", () =>
      PlaylistModule.set()
    );
    this.safeAddEventListener(SELECTORS.playlistUrl, "keypress", (e) => {
      if (e.key === "Enter") PlaylistModule.set();
    });

    // Track count
    this.safeAddEventListener(SELECTORS.setTrackCountBtn, "click", () =>
      TrackCountModule.set()
    );
    document.querySelectorAll("[data-count]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const trackCountInput = DOMUtils.get(SELECTORS.trackCount);
        if (trackCountInput) {
          trackCountInput.value = btn.dataset.count;
          TrackCountModule.set();
        }
      });
    });
    this.safeAddEventListener(SELECTORS.trackCount, "keypress", (e) => {
      if (e.key === "Enter") TrackCountModule.set();
    });

    // Import
    this.safeAddEventListener(SELECTORS.importTracksBtn, "click", () =>
      ImportModule.import()
    );

    // Generate
    this.safeAddEventListener(SELECTORS.generateCardsBtn, "click", () =>
      GenerateModule.generate()
    );

    // Preview
    this.safeAddEventListener(SELECTORS.loadPreviewBtn, "click", () =>
      PreviewModule.load()
    );
    this.safeAddEventListener(SELECTORS.prevTrackBtn, "click", () =>
      PreviewModule.changeTrack(-1)
    );
    this.safeAddEventListener(SELECTORS.nextTrackBtn, "click", () =>
      PreviewModule.changeTrack(1)
    );
    this.safeAddEventListener(SELECTORS.previewFrontBtn, "click", () =>
      PreviewModule.setSide("front")
    );
    this.safeAddEventListener(SELECTORS.previewBackBtn, "click", () =>
      PreviewModule.setSide("back")
    );
    this.safeAddEventListener(SELECTORS.applyEditBtn, "click", () =>
      PreviewModule.applyChanges()
    );
    this.safeAddEventListener(SELECTORS.saveEditBtn, "click", () =>
      PreviewModule.saveToCsv()
    );
    this.safeAddEventListener(SELECTORS.resetEditBtn, "click", () =>
      PreviewModule.resetEditor()
    );

    // Logs
    this.safeAddEventListener(SELECTORS.refreshLogsBtn, "click", () =>
      LogsModule.load()
    );

    // Playlist tabs
    document.addEventListener("click", (e) => {
      if (e.target?.id === SELECTORS.playlistTabRecent) {
        e.preventDefault();
        PlaylistModule.switchTab("recent");
      } else if (e.target?.id === SELECTORS.playlistTabAll) {
        e.preventDefault();
        PlaylistModule.switchTab("all");
      }
    });

    // Theme toggle
    const themeToggle = DOMUtils.get(SELECTORS.themeToggle);
    if (themeToggle) {
      themeToggle.addEventListener("change", () => ThemeModule.toggle());
    }
  },

  /**
   * Safely add event listener
   */
  safeAddEventListener(id, event, handler) {
    const element = DOMUtils.get(id);
    if (element) {
      element.addEventListener(event, handler);
    }
  },
};

