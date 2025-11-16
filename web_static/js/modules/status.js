/**
 * Status Module
 */

import { API } from "../api.js";
import { DOMUtils } from "../dom-utils.js";
import { SELECTORS } from "../config.js";
import { appState } from "../state.js";

export const StatusModule = {
  /**
   * Load and display current status
   */
  async load() {
    try {
      const status = await API.get("status");
      appState.status = status;
      this.updateDisplay(status);
    } catch (error) {
      console.error("Failed to load status:", error);
    }
  },

  /**
   * Update status display
   */
  updateDisplay(status) {
    DOMUtils.get(SELECTORS.statusPlaylist).textContent =
      status.playlist_name || "None selected";
    DOMUtils.get(SELECTORS.statusTrackCount).textContent =
      status.track_count || "N/A";

    const spotifyEl = DOMUtils.get(SELECTORS.statusSpotify);
    if (status.spotify_connected) {
      spotifyEl.textContent = "Connected";
      spotifyEl.className = "status-value success";
    } else {
      spotifyEl.textContent = "Disconnected";
      spotifyEl.className = "status-value error";
    }
  },
};
