/**
 * Generate Module
 */

import { API } from "../api.js";
import { DOMUtils } from "../dom-utils.js";
import { Utils } from "../utils.js";
import { SELECTORS } from "../config.js";
import { Components } from "../components.js";

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
        // Reload generated cards list
        this.loadGeneratedCards();
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

  /**
   * Load list of generated card sets
   */
  async loadGeneratedCards() {
    try {
      const cardSets = await API.get("cards/generated");
      const container = DOMUtils.get(SELECTORS.generatedCardsList);
      if (!container) return;

      if (cardSets.length === 0) {
        DOMUtils.render(container, [
          Components.createEmptyState("No generated cards yet. Generate cards to see them here.")
        ]);
        return;
      }

      const sets = cardSets.map(set => this.createCardSetItem(set));
      DOMUtils.render(container, sets);
    } catch (error) {
      console.error("Failed to load generated cards:", error);
    }
  },

  /**
   * Create a card set item UI
   */
  createCardSetItem(set) {
    const setDiv = DOMUtils.create("div", { class: "card-set" });

    const header = DOMUtils.create("div", { class: "card-set-header" });
    header.appendChild(DOMUtils.create("h3", {}, [set.name]));
    header.appendChild(DOMUtils.create("span", { class: "card-set-count" }, [`${set.count} files`]));

    const filesDiv = DOMUtils.create("div", { class: "card-set-files" });
    
    // Group files by page
    const pages = {};
    set.files.forEach(file => {
      const pageMatch = file.name.match(/page(\d+)_/);
      if (pageMatch) {
        const pageNum = pageMatch[1];
        if (!pages[pageNum]) {
          pages[pageNum] = { front: null, back: null };
        }
        if (file.type === "front") {
          pages[pageNum].front = file;
        } else {
          pages[pageNum].back = file;
        }
      }
    });

    // Create buttons for each page
    Object.keys(pages).sort().forEach(pageNum => {
      const page = pages[pageNum];
      const pageDiv = DOMUtils.create("div", { class: "card-set-page" });
      
      const pageLabel = DOMUtils.create("div", { class: "page-label" }, [`Page ${pageNum}`]);
      pageDiv.appendChild(pageLabel);

      const buttonsDiv = DOMUtils.create("div", { class: "page-buttons" });

      if (page.front) {
        const frontBtn = DOMUtils.create("button", {
          class: "btn btn-secondary btn-sm",
        }, ["📄 Front"]);
        frontBtn.addEventListener("click", () => this.openForPrint(page.front.url));
        buttonsDiv.appendChild(frontBtn);
      }

      if (page.back) {
        const backBtn = DOMUtils.create("button", {
          class: "btn btn-secondary btn-sm",
        }, ["📄 Back"]);
        backBtn.addEventListener("click", () => this.openForPrint(page.back.url));
        buttonsDiv.appendChild(backBtn);
      }

      // Print both button
      if (page.front && page.back) {
        const printBothBtn = DOMUtils.create("button", {
          class: "btn btn-primary btn-sm",
        }, ["🖨️ Print Both"]);
        printBothBtn.addEventListener("click", () => this.printBothPages(page.front.url, page.back.url));
        buttonsDiv.appendChild(printBothBtn);
      }

      pageDiv.appendChild(buttonsDiv);
      filesDiv.appendChild(pageDiv);
    });

    // Print all button
    if (set.files.length > 0) {
      const printAllBtn = DOMUtils.create("button", {
        class: "btn btn-primary",
        style: "margin-top: 15px; width: 100%;"
      }, ["🖨️ Print All Pages"]);
      printAllBtn.addEventListener("click", () => this.printAllPages(set.files.map(f => f.url)));
      filesDiv.appendChild(printAllBtn);
    }

    setDiv.appendChild(header);
    setDiv.appendChild(filesDiv);
    return setDiv;
  },

  /**
   * Open HTML file in new window for printing
   */
  openForPrint(url) {
    const printWindow = window.open(url, "_blank");
    if (printWindow) {
      // Wait for window to fully load before printing
      const checkLoad = setInterval(() => {
        if (printWindow.document.readyState === "complete") {
          clearInterval(checkLoad);
          // Small delay to ensure rendering is complete
          setTimeout(() => {
            printWindow.print();
          }, 300);
        }
      }, 100);
      
      // Fallback timeout
      setTimeout(() => {
        clearInterval(checkLoad);
        if (printWindow.document.readyState === "complete") {
          printWindow.print();
        }
      }, 5000);
    }
  },

  /**
   * Print both front and back pages
   */
  printBothPages(frontUrl, backUrl) {
    // Open both windows first
    const frontWindow = window.open(frontUrl, "_blank");
    const backWindow = window.open(backUrl, "_blank");
    
    if (!frontWindow || !backWindow) {
      alert("Please allow popups for this site to print both pages.");
      return;
    }
    
    let frontLoaded = false;
    let backLoaded = false;
    
    const tryPrint = () => {
      if (frontLoaded && backLoaded) {
        // Print front first, then back after a delay
        setTimeout(() => {
          frontWindow.print();
        }, 500);
        
        setTimeout(() => {
          backWindow.print();
        }, 2000);
      }
    };
    
    // Check front window load
    const checkFrontLoad = setInterval(() => {
      if (frontWindow.document.readyState === "complete") {
        clearInterval(checkFrontLoad);
        frontLoaded = true;
        tryPrint();
      }
    }, 100);
    
    // Check back window load
    const checkBackLoad = setInterval(() => {
      if (backWindow.document.readyState === "complete") {
        clearInterval(checkBackLoad);
        backLoaded = true;
        tryPrint();
      }
    }, 100);
    
    // Fallback timeout
    setTimeout(() => {
      clearInterval(checkFrontLoad);
      clearInterval(checkBackLoad);
      if (frontWindow.document.readyState === "complete") frontLoaded = true;
      if (backWindow.document.readyState === "complete") backLoaded = true;
      tryPrint();
    }, 5000);
  },

  /**
   * Print all pages
   */
  printAllPages(urls) {
    // Print all pages sequentially
    urls.forEach((url, index) => {
      setTimeout(() => {
        this.openForPrint(url);
      }, index * 1000); // 1 second delay between each
    });
  },
};
