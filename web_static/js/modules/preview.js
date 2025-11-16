/**
 * Preview Module
 */

import { API } from "../api.js";
import { DOMUtils } from "../dom-utils.js";
import { Components } from "../components.js";
import { Utils } from "../utils.js";
import { SELECTORS } from "../config.js";
import { appState } from "../state.js";

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
  changeTrack(delta) {
    const newIndex = appState.preview.trackIndex + delta;
    if (newIndex >= 0 && newIndex < appState.preview.maxTracks) {
      appState.preview.trackIndex = newIndex;
      DOMUtils.get(SELECTORS.previewTrackIndex).value = newIndex + 1;
      this.load();
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
      Utils.showMessage(
        SELECTORS.importStatus,
        "Please select a CSV file",
        "error"
      );
      return;
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

        // Get max tracks for navigation
        fetch(csvPath)
          .then((r) => r.text())
          .then((text) => {
            const lines = text.split("\n").filter((l) => l.trim());
            appState.preview.maxTracks = Math.max(0, lines.length - 1);
          });
      }
    } catch (error) {
      DOMUtils.render(DOMUtils.get(SELECTORS.previewContainer), [
        Components.createEmptyState(`Error: ${error.message}`),
      ]);
    }
  },
};

