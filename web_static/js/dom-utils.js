/**
 * DOM Utilities
 */

export const DOMUtils = {
  /**
   * Safely get an element by ID
   */
  get(id) {
    return document.getElementById(id);
  },

  /**
   * Create an element with optional attributes and children
   */
  create(tag, attributes = {}, children = []) {
    const element = document.createElement(tag);
    Object.entries(attributes).forEach(([key, value]) => {
      if (key === "class") {
        element.className = value;
      } else if (key === "dataset") {
        Object.entries(value).forEach(([dataKey, dataValue]) => {
          element.dataset[dataKey] = dataValue;
        });
      } else if (key.startsWith("on")) {
        element.addEventListener(key.substring(2).toLowerCase(), value);
      } else {
        element.setAttribute(key, value);
      }
    });
    children.forEach((child) => {
      if (typeof child === "string") {
        element.appendChild(document.createTextNode(child));
      } else {
        element.appendChild(child);
      }
    });
    return element;
  },

  /**
   * Clear container and append new elements
   */
  render(container, elements) {
    if (typeof container === "string") {
      container = DOMUtils.get(container);
    }
    if (!container) return;
    container.innerHTML = "";
    elements.forEach((element) => container.appendChild(element));
  },

  /**
   * Show loading state on button
   */
  setButtonLoading(buttonId, loadingText) {
    const btn = DOMUtils.get(buttonId);
    if (!btn) return;
    btn.disabled = true;
    const spinner = DOMUtils.create("span", { class: "spinner" });
    btn.innerHTML = "";
    btn.appendChild(spinner);
    btn.appendChild(document.createTextNode(loadingText));
  },

  /**
   * Reset button to normal state
   */
  resetButton(buttonId, text) {
    const btn = DOMUtils.get(buttonId);
    if (!btn) return;
    btn.disabled = false;
    btn.textContent = text;
  },
};
