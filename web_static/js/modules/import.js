/**
 * Import Module
 */

import { API } from "../api.js";
import { DOMUtils } from "../dom-utils.js";
import { Utils } from "../utils.js";
import { SELECTORS } from "../config.js";
import { appState } from "../state.js";
import { CsvModule } from "./csv.js";
import { ProgressModule } from "./progress.js";

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
      const btn = DOMUtils.get(SELECTORS.importTracksBtn);
      if (btn) btn.disabled = true;
      
      ProgressModule.show("Importing tracks...");

      const result = await API.post("tracks/import", {});

      if (result.success) {
        Utils.showMessage(SELECTORS.importStatus, result.summary, "success");
        CsvModule.load();
        setTimeout(() => ProgressModule.hide(), 1000);
      }
    } catch (error) {
      ProgressModule.hide();
      Utils.showMessage(
        SELECTORS.importStatus,
        `Error: ${error.message}`,
        "error"
      );
    } finally {
      const btn = DOMUtils.get(SELECTORS.importTracksBtn);
      if (btn) btn.disabled = false;
    }
  },
};
