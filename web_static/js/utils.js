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
   * Show toast message (delegates to ToastModule)
   * @deprecated Use ToastModule directly for better control
   */
  showMessage(message, type = "info") {
    // Import dynamically to avoid circular dependencies
    import("./modules/toast.js").then(({ ToastModule }) => {
      ToastModule.show(message, type);
    });
  },
};

