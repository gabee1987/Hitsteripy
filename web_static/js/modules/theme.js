/**
 * Theme Module
 */

import { DOMUtils } from "../dom-utils.js";
import { CONFIG, SELECTORS } from "../config.js";

export const ThemeModule = {
  /**
   * Initialize theme
   */
  setup() {
    const savedTheme =
      localStorage.getItem(CONFIG.THEME_KEY) || CONFIG.DEFAULT_THEME;
    document.documentElement.setAttribute("data-theme", savedTheme);
    setTimeout(() => {
      this.updateToggle(savedTheme);
    }, 100);
  },

  /**
   * Toggle theme
   */
  toggle() {
    const currentTheme =
      document.documentElement.getAttribute("data-theme") ||
      CONFIG.DEFAULT_THEME;
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", newTheme);
    localStorage.setItem(CONFIG.THEME_KEY, newTheme);
    this.updateToggle(newTheme);
  },

  /**
   * Update toggle checkbox
   */
  updateToggle(theme) {
    const toggle = DOMUtils.get(SELECTORS.themeToggle);
    if (toggle) {
      toggle.checked = theme === "dark";
    }
  },
};
