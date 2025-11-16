/**
 * Import Module
 */

import { API } from "../api.js";
import { DOMUtils } from "../dom-utils.js";
import { SELECTORS } from "../config.js";
import { appState } from "../state.js";
import { CsvModule } from "./csv.js";
import { ProgressModule } from "./progress.js";
import { ToastModule } from "./toast.js";

export const ImportModule = {
  /**
   * Import tracks
   */
  async import() {
    if (!appState.status.playlist_url) {
      ToastModule.error("Please set a playlist URL first");
      return;
    }

    if (!appState.status.track_count) {
      ToastModule.error("Please set a track count first");
      return;
    }

    try {
      const btn = DOMUtils.get(SELECTORS.importTracksBtn);
      if (btn) btn.disabled = true;
      
      const playlistName = appState.status.playlist_name || "playlist";
      const trackCount = appState.status.track_count === "all" ? "all tracks" : `${appState.status.track_count} tracks`;
      
      ProgressModule.show(`Importing ${trackCount} from "${playlistName}"...`);

      const result = await API.post("tracks/import", {});

      if (result.success) {
        // The summary already contains useful info like "243 tracks imported to imported_tracks\20251116_122459_all\TuneTrack Apa_tracks.csv"
        ToastModule.success(result.summary || "Tracks imported successfully");
        CsvModule.load();
        setTimeout(() => ProgressModule.hide(), 1000);
      }
    } catch (error) {
      ProgressModule.hide();
      ToastModule.error(`Import failed: ${error.message}`);
    } finally {
      const btn = DOMUtils.get(SELECTORS.importTracksBtn);
      if (btn) btn.disabled = false;
    }
  },
};
