/**
 * Playlist Module
 */

import { API } from "../api.js";
import { DOMUtils } from "../dom-utils.js";
import { Components } from "../components.js";
import { Utils } from "../utils.js";
import { CONFIG, SELECTORS } from "../config.js";
import { appState } from "../state.js";
import { StatusModule } from "./status.js";

export const PlaylistModule = {
  /**
   * Load playlist history
   */
  async loadHistory(type = "recent") {
    try {
      const history = await API.get("playlists/history");
      const container = DOMUtils.get(SELECTORS.playlistHistory);

      let filteredHistory = history;
      if (type === "recent") {
        filteredHistory = history.slice(0, CONFIG.RECENT_PLAYLIST_LIMIT);
      }

      if (filteredHistory.length === 0) {
        DOMUtils.render(container, [
          Components.createEmptyState(`No ${type} playlists`),
        ]);
        return;
      }

      const items = filteredHistory.map((item) =>
        Components.createPlaylistHistoryItem(
          item,
          this.select.bind(this),
          this.delete.bind(this)
        )
      );

      DOMUtils.render(container, items);
    } catch (error) {
      console.error("Failed to load playlist history:", error);
    }
  },

  /**
   * Select a playlist
   */
  select(url, name) {
    DOMUtils.get(SELECTORS.playlistUrl).value = url;
    this.set();
  },

  /**
   * Set playlist URL
   */
  async set() {
    const url = DOMUtils.get(SELECTORS.playlistUrl).value.trim();
    if (!url) {
      Utils.showMessage(
        SELECTORS.importStatus,
        "Please enter a playlist URL",
        "error"
      );
      return;
    }

    try {
      DOMUtils.setButtonLoading(SELECTORS.setPlaylistBtn, " Setting...");

      const result = await API.post("playlists/set", { url });

      if (result.success) {
        Utils.showMessage(
          SELECTORS.importStatus,
          `Playlist set: ${result.playlist_name}`,
          "success"
        );
        DOMUtils.get(SELECTORS.playlistUrl).value = "";
        StatusModule.load();
        this.loadHistory(appState.playlistHistoryType);
      }
    } catch (error) {
      Utils.showMessage(
        SELECTORS.importStatus,
        `Error: ${error.message}`,
        "error"
      );
    } finally {
      DOMUtils.resetButton(SELECTORS.setPlaylistBtn, "Set Playlist");
    }
  },

  /**
   * Delete playlist from history
   */
  async delete(url) {
    if (!confirm(CONFIG.DELETE_CONFIRM_MESSAGE)) {
      return;
    }

    try {
      const result = await API.post("playlists/delete", { url });
      if (result.success) {
        this.loadHistory(appState.playlistHistoryType);
        StatusModule.load();
        Utils.showMessage(
          SELECTORS.importStatus,
          "Playlist deleted from history",
          "success"
        );
      }
    } catch (error) {
      Utils.showMessage(
        SELECTORS.importStatus,
        `Error: ${error.message}`,
        "error"
      );
    }
  },

  /**
   * Switch playlist history tab
   */
  switchTab(type) {
    appState.playlistHistoryType = type;
    DOMUtils.get(SELECTORS.playlistTabRecent).classList.toggle(
      "active",
      type === "recent"
    );
    DOMUtils.get(SELECTORS.playlistTabAll).classList.toggle(
      "active",
      type === "all"
    );
    this.loadHistory(type);
  },
};

