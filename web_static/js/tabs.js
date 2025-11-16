/**
 * Tab Management
 */

import { DOMUtils } from "./dom-utils.js";
import { CsvModule } from "./modules/csv.js";
import { LogsModule } from "./modules/logs.js";
import { GenerateModule } from "./modules/generate.js";

export const TabManager = {
  /**
   * Setup tab switching
   */
  setup() {
    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");

    tabBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        const tabId = btn.dataset.tab;

        // Update buttons
        tabBtns.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");

        // Update content
        tabContents.forEach((c) => c.classList.remove("active"));
        const tabContent = DOMUtils.get(`tab-${tabId}`);
        if (tabContent) {
          tabContent.classList.add("active");
        }

        // Load data for specific tabs
        if (tabId === "generate" || tabId === "preview") {
          CsvModule.load();
          if (tabId === "generate") {
            GenerateModule.loadGeneratedCards();
          }
        }
        if (tabId === "logs") {
          LogsModule.load();
        }
      });
    });
  },
};

