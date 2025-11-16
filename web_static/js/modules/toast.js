/**
 * Toast Module - Dedicated toast message system
 */

import { DOMUtils } from "../dom-utils.js";

const SELECTORS = {
  toastContainer: "toastContainer",
};

export const ToastModule = {
  /**
   * Show a toast message
   * @param {string} message - The message to display
   * @param {string} type - Type: 'success', 'error', 'info'
   */
  show(message, type = "info") {
    const toastContainer = DOMUtils.get(SELECTORS.toastContainer);
    if (!toastContainer) {
      console.warn("Toast container not found");
      return;
    }

    // Create toast element
    const toast = DOMUtils.create("div", {
      class: `toast toast-${type}`,
    }, [message]);

    // Add to container
    toastContainer.appendChild(toast);

    // Trigger animation
    setTimeout(() => {
      toast.classList.add("show");
    }, 10);

    // Auto remove after delay
    const delay = type === "error" ? 6000 : 5000;
    setTimeout(() => {
      toast.classList.remove("show");
      setTimeout(() => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast);
        }
      }, 300);
    }, delay);
  },

  /**
   * Show success message
   */
  success(message) {
    this.show(message, "success");
  },

  /**
   * Show error message
   */
  error(message) {
    this.show(message, "error");
  },

  /**
   * Show info message
   */
  info(message) {
    this.show(message, "info");
  },
};

