/**
 * Logs Module
 */

import { API } from "../api.js";
import { DOMUtils } from "../dom-utils.js";
import { Components } from "../components.js";
import { SELECTORS } from "../config.js";

export const LogsModule = {
  /**
   * Load application logs
   */
  async load() {
    try {
      const logs = await API.get("logs");
      const container = DOMUtils.get(SELECTORS.logsContainer);

      if (logs.length === 0) {
        DOMUtils.render(container, [
          Components.createEmptyState("No logs yet"),
        ]);
        return;
      }

      const entries = logs
        .reverse()
        .map((log) => Components.createLogEntry(log));

      DOMUtils.render(container, entries);
      container.scrollTop = 0;
    } catch (error) {
      console.error("Failed to load logs:", error);
    }
  },
};

