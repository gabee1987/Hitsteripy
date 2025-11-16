/**
 * UI Components
 */

import { DOMUtils } from "./dom-utils.js";
import { Utils } from "./utils.js";

export const Components = {
  /**
   * Create a delete button with X icon
   */
  createDeleteButton(onClick, title = "Delete") {
    const button = DOMUtils.create(
      "button",
      {
        class: "history-item-delete",
        title,
      },
      ["×"]
    );

    // Add click event listener properly
    button.addEventListener("click", onClick);

    return button;
  },

  /**
   * Create a playlist history item
   */
  createPlaylistHistoryItem(item, onSelect, onDelete) {
    const itemDiv = DOMUtils.create("div", { class: "history-item" });

    const contentDiv = DOMUtils.create(
      "div",
      {
        class: "history-item-content",
        dataset: { url: item.url, name: item.name },
      },
      [
        DOMUtils.create("strong", {}, [item.name]),
        DOMUtils.create(
          "div",
          { style: "font-size: 0.85rem; color: var(--text-light);" },
          [item.url]
        ),
      ]
    );

    contentDiv.addEventListener("click", () => onSelect(item.url, item.name));

    const deleteBtn = Components.createDeleteButton((e) => {
      e.stopPropagation();
      e.preventDefault();
      onDelete(item.url);
    }, "Delete playlist");

    itemDiv.appendChild(contentDiv);
    itemDiv.appendChild(deleteBtn);
    return itemDiv;
  },

  /**
   * Create a track count history item
   */
  createTrackCountItem(count, onSelect) {
    const item = DOMUtils.create(
      "div",
      {
        class: "history-item",
      },
      [count.toString()]
    );

    item.addEventListener("click", () => onSelect(count));
    return item;
  },

  /**
   * Create an empty state message
   */
  createEmptyState(message, className = "info-text") {
    return DOMUtils.create("p", { class: className }, [message]);
  },

  /**
   * Create a log entry
   */
  createLogEntry(log) {
    let type = "info";
    if (log.includes("[SUCCESS]")) type = "success";
    else if (log.includes("[ERROR]")) type = "error";

    // Escape HTML for security
    const escapedLog = Utils.escapeHtml(log);
    return DOMUtils.create("div", { class: `log-entry log-${type}` }, [
      escapedLog,
    ]);
  },
};
