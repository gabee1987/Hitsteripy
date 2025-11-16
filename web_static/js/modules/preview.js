/**
 * Preview Module
 */

import { API } from "../api.js";
import { DOMUtils } from "../dom-utils.js";
import { Components } from "../components.js";
import { SELECTORS } from "../config.js";
import { appState } from "../state.js";
import { ToastModule } from "./toast.js";

export const PreviewModule = {
  /**
   * Set preview side
   */
  setSide(side) {
    appState.preview.side = side;
    DOMUtils.get(SELECTORS.previewFrontBtn).classList.toggle(
      "active",
      side === "front"
    );
    DOMUtils.get(SELECTORS.previewBackBtn).classList.toggle(
      "active",
      side === "back"
    );
    if (appState.preview.csvPath) {
      this.load();
    }
  },

  /**
   * Change preview track
   */
  async changeTrack(delta) {
    const csvPath = DOMUtils.get(SELECTORS.previewCsvSelect).value;
    if (!csvPath) {
      ToastModule.error("Please select a CSV file first");
      return;
    }

    // Read current track index from input field
    const currentIndexInput = DOMUtils.get(SELECTORS.previewTrackIndex);
    const currentIndex = parseInt(currentIndexInput.value) - 1;
    const newIndex = currentIndex + delta;

    // Ensure maxTracks is available
    if (!appState.preview.maxTracks || appState.preview.maxTracks === 0) {
      try {
        const countResult = await API.post("cards/track-count", {
          csv_path: csvPath,
        });
        if (countResult.success) {
          appState.preview.maxTracks = countResult.total_tracks;
        } else {
          ToastModule.error("Failed to load track count");
          return;
        }
      } catch (error) {
        ToastModule.error("Failed to load track count");
        return;
      }
    }

    // Validate new index
    if (newIndex >= 0 && newIndex < appState.preview.maxTracks) {
      appState.preview.trackIndex = newIndex;
      currentIndexInput.value = newIndex + 1;
      this.load();
    } else {
      // Show feedback if at boundary
      if (newIndex < 0) {
        ToastModule.error("Already at first track");
      } else {
        ToastModule.error(`Maximum track number is ${appState.preview.maxTracks}`);
      }
    }
  },

  /**
   * Load preview
   */
  async load() {
    const csvPath = DOMUtils.get(SELECTORS.previewCsvSelect).value;
    const trackIndex =
      parseInt(DOMUtils.get(SELECTORS.previewTrackIndex).value) - 1;

    if (!csvPath) {
      ToastModule.error("Please select a CSV file to preview");
      return;
    }

    // Reset maxTracks if CSV file changed
    if (appState.preview.csvPath !== csvPath) {
      appState.preview.maxTracks = 0;
    }

    appState.preview.csvPath = csvPath;
    appState.preview.trackIndex = trackIndex;

    try {
      const result = await API.post("cards/preview", {
        csv_path: csvPath,
        track_index: trackIndex,
        side: appState.preview.side,
      });

      if (result.success) {
        const container = DOMUtils.get(SELECTORS.previewContainer);
        const iframe = DOMUtils.create("iframe", {
          style: "width: 100%; min-height: 600px; border: none;",
        });

        DOMUtils.render(container, [iframe]);

        const iframeDoc =
          iframe.contentDocument || iframe.contentWindow.document;
        iframeDoc.open();
        iframeDoc.write(result.html);
        iframeDoc.close();

        // Store max tracks from response or fetch if not available
        if (result.total_tracks !== undefined) {
          appState.preview.maxTracks = result.total_tracks;
        } else {
          // Fallback: fetch track count via API
          try {
            const countResult = await API.post("cards/track-count", {
              csv_path: csvPath,
            });
            if (countResult.success) {
              appState.preview.maxTracks = countResult.total_tracks;
            }
          } catch (error) {
            console.error("Failed to get track count:", error);
          }
        }
      }
    } catch (error) {
      DOMUtils.render(DOMUtils.get(SELECTORS.previewContainer), [
        Components.createEmptyState(`Error: ${error.message}`),
      ]);
    }
  },
};

