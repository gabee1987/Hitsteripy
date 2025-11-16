/**
 * Utility Functions
 */

export const Utils = {
  /**
   * Escape HTML to prevent XSS
   */
  escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  },

  /**
   * Show status message
   */
  showMessage(elementId, message, type) {
    const element = document.getElementById(elementId);
    if (!element) return;

    element.textContent = message;
    element.className = `status-message ${type}`;

    if (type === "success") {
      setTimeout(() => {
        element.className = "status-message";
      }, 5000);
    }
  },
};

