/**
 * Generate Module
 */

import { API } from "../api.js";
import { DOMUtils } from "../dom-utils.js";
import { Utils } from "../utils.js";
import { SELECTORS } from "../config.js";

export const GenerateModule = {
  /**
   * Generate cards
   */
  async generate() {
    const csvPath = DOMUtils.get(SELECTORS.csvFileSelect).value;

    if (!csvPath) {
      Utils.showMessage(
        SELECTORS.generateStatus,
        "Please select a CSV file",
        "error"
      );
      return;
    }

    try {
      DOMUtils.setButtonLoading(SELECTORS.generateCardsBtn, " Generating...");

      const result = await API.post("cards/generate", { csv_path: csvPath });

      if (result.success) {
        Utils.showMessage(SELECTORS.generateStatus, result.summary, "success");
      }
    } catch (error) {
      Utils.showMessage(
        SELECTORS.generateStatus,
        `Error: ${error.message}`,
        "error"
      );
    } finally {
      DOMUtils.resetButton(SELECTORS.generateCardsBtn, "🎨 Generate Cards");
    }
  },
};
