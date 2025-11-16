/**
 * Track Count Module
 */

import { API } from "../api.js";
import { DOMUtils } from "../dom-utils.js";
import { Components } from "../components.js";
import { CONFIG, SELECTORS } from "../config.js";
import { StatusModule } from "./status.js";
import { ToastModule } from "./toast.js";

export const TrackCountModule = {
  /**
   * Load track count history
   */
  async loadHistory() {
    try {
      const data = await API.get("tracks/count/history");
      const container = DOMUtils.get(SELECTORS.trackCountHistory);

      const allOptions = [
        ...data.defaults,
        ...data.history.filter((h) => !data.defaults.includes(h)),
      ];

      if (allOptions.length === 0) {
        DOMUtils.render(container, [
          Components.createEmptyState("No recent counts"),
        ]);
        return;
      }

      const items = allOptions
        .slice(0, CONFIG.RECENT_PLAYLIST_LIMIT)
        .map((count) =>
          Components.createTrackCountItem(count, this.select.bind(this))
        );

      DOMUtils.render(container, items);
    } catch (error) {
      console.error("Failed to load track count history:", error);
    }
  },

  /**
   * Select track count
   */
  select(count) {
    DOMUtils.get(SELECTORS.trackCount).value = count;
    this.set();
  },

  /**
   * Set track count
   */
  async set() {
    const count = DOMUtils.get(SELECTORS.trackCount).value.trim();
    if (!count) {
      ToastModule.error("Please enter a track count (number or 'all')");
      return;
    }

    try {
      const result = await API.post("tracks/count/set", { count });

      if (result.success) {
        const trackCount = result.track_count === "all" ? "all tracks" : `${result.track_count} tracks`;
        ToastModule.success(`Track count set to ${trackCount}`);
        DOMUtils.get(SELECTORS.trackCount).value = "";
        StatusModule.load();
        this.loadHistory();
      }
    } catch (error) {
      ToastModule.error(`Failed to set track count: ${error.message}`);
    }
  },
};
