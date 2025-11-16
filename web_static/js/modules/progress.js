/**
 * Loading Indicator Module
 */

import { DOMUtils } from "../dom-utils.js";

const SELECTORS = {
  progressContainer: "progressBarContainer",
  progressLabel: "progressLabel",
  progressFill: "progressFill",
  progressPercent: "progressPercent",
};

export const ProgressModule = {
  /**
   * Show loading indicator with label
   */
  show(label = "Processing...") {
    const container = DOMUtils.get(SELECTORS.progressContainer);
    const labelEl = DOMUtils.get(SELECTORS.progressLabel);
    const fill = DOMUtils.get(SELECTORS.progressFill);
    const percentEl = DOMUtils.get(SELECTORS.progressPercent);
    
    if (container && labelEl && fill && percentEl) {
      labelEl.textContent = label;
      // Hide percent display for indeterminate loading
      percentEl.style.display = "none";
      // Set fill to indeterminate mode
      fill.classList.add("indeterminate");
      container.style.display = "block";
    }
  },

  /**
   * Hide loading indicator
   */
  hide() {
    const container = DOMUtils.get(SELECTORS.progressContainer);
    const fill = DOMUtils.get(SELECTORS.progressFill);
    
    if (container) {
      container.style.display = "none";
    }
    if (fill) {
      fill.classList.remove("indeterminate");
    }
  },

  /**
   * Update label
   */
  setLabel(label) {
    const labelEl = DOMUtils.get(SELECTORS.progressLabel);
    if (labelEl) {
      labelEl.textContent = label;
    }
  },
};

