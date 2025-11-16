/**
 * Import Module
 */

import { API } from "../api.js";
import { DOMUtils } from "../dom-utils.js";
import { Utils } from "../utils.js";
import { SELECTORS } from "../config.js";
import { appState } from "../state.js";
import { CsvModule } from "./csv.js";

export const ImportModule = {
  /**
   * Import tracks
   */
  async import() {
    if (!appState.status.playlist_url) {
      Utils.showMessage(
        SELECTORS.importStatus,
        "Please set a playlist URL first",
        "error"
      );
      return;
    }

    if (!appState.status.track_count) {
      Utils.showMessage(
        SELECTORS.importStatus,
        "Please set a track count first",
        "error"
      );
      return;
    }

    try {
      DOMUtils.setButtonLoading(SELECTORS.importTracksBtn, " Importing...");

      const result = await API.post("tracks/import", {});

      if (result.success) {
        Utils.showMessage(SELECTORS.importStatus, result.summary, "success");
        CsvModule.load();
      }
    } catch (error) {
      Utils.showMessage(
        SELECTORS.importStatus,
        `Error: ${error.message}`,
        "error"
      );
    } finally {
      DOMUtils.resetButton(SELECTORS.importTracksBtn, "📥 Import Tracks");
    }
  },
};
