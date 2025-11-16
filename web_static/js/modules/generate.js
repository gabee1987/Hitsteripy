/**
 * Generate Module
 */

import { API } from "../api.js";
import { DOMUtils } from "../dom-utils.js";
import { SELECTORS } from "../config.js";
import { Components } from "../components.js";
import { ProgressModule } from "./progress.js";
import { ToastModule } from "./toast.js";

export const GenerateModule = {
  /**
   * Generate cards
   */
  async generate() {
    const csvPath = DOMUtils.get(SELECTORS.csvFileSelect).value;

    if (!csvPath) {
      ToastModule.error("Please select a CSV file to generate cards");
      return;
    }

    try {
      const btn = DOMUtils.get(SELECTORS.generateCardsBtn);
      if (btn) btn.disabled = true;
      
      ProgressModule.show("Generating cards...");

      const result = await API.post("cards/generate", { csv_path: csvPath });
      
      if (result.success) {
        // Extract useful info from summary
        const summary = result.summary || "Cards generated successfully";
        ToastModule.success(summary);
        // Reload generated cards list
        this.loadGeneratedCards();
      }
      
      setTimeout(() => ProgressModule.hide(), 1000);
    } catch (error) {
      ProgressModule.hide();
      ToastModule.error(`Failed to generate cards: ${error.message}`);
    } finally {
      const btn = DOMUtils.get(SELECTORS.generateCardsBtn);
      if (btn) btn.disabled = false;
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

    // Create action buttons container at the top
    const actionsDiv = DOMUtils.create("div", { class: "card-set-actions" });
    
    // Generate PDFs button
    const generatePdfBtn = DOMUtils.create("button", {
      class: "btn btn-secondary",
    }, [set.has_all_pdfs ? "✅ All PDFs Generated" : "📄 Generate All PDFs"]);
    
    if (!set.has_all_pdfs) {
      generatePdfBtn.addEventListener("click", () => this.generatePdfs(set.path));
    } else {
      generatePdfBtn.disabled = true;
    }
    actionsDiv.appendChild(generatePdfBtn);

    // Print all button
    if (set.files.length > 0) {
      const printAllBtn = DOMUtils.create("button", {
        class: "btn btn-primary",
      }, ["🖨️ Print All Pages"]);
      printAllBtn.addEventListener("click", () => this.printAllPages(set.files.map(f => f.url)));
      actionsDiv.appendChild(printAllBtn);
    }

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

      pageDiv.appendChild(buttonsDiv);
      filesDiv.appendChild(pageDiv);
    });

    setDiv.appendChild(header);
    setDiv.appendChild(actionsDiv);
    setDiv.appendChild(filesDiv);
    return setDiv;
  },

  /**
   * Open HTML file in new window for printing
   */
  openForPrint(url) {
    const printWindow = window.open(url, "_blank");
    if (!printWindow) return;
    
    let hasPrinted = false;
    
    // Wait for window to fully load before printing
    const checkLoad = setInterval(() => {
      try {
        if (printWindow.document.readyState === "complete" && !hasPrinted) {
          clearInterval(checkLoad);
          hasPrinted = true;
          // Small delay to ensure rendering is complete
          setTimeout(() => {
            try {
              printWindow.print();
            } catch (e) {
              console.error("Print error:", e);
            }
          }, 500);
        }
      } catch (e) {
        // Window might be closed or cross-origin
        clearInterval(checkLoad);
      }
    }, 100);
    
    // Fallback timeout - only print once
    setTimeout(() => {
      clearInterval(checkLoad);
      if (!hasPrinted) {
        try {
          if (printWindow.document.readyState === "complete") {
            hasPrinted = true;
            printWindow.print();
          }
        } catch (e) {
          console.error("Print error:", e);
        }
      }
    }, 5000);
  },

  /**
   * Print both front and back pages
   */
  printBothPages(frontUrl, backUrl) {
    // Store URLs for sequential opening to avoid popup blocking
    const urls = [frontUrl, backUrl];
    let currentIndex = 0;
    
    const openNext = () => {
      if (currentIndex >= urls.length) return;
      
      const url = urls[currentIndex];
      const windowName = `printWindow_${currentIndex}`;
      
      // Open window with unique name to avoid blocking
      const printWindow = window.open(url, windowName, "width=800,height=600");
      
      if (!printWindow) {
        if (currentIndex === 0) {
          alert("Please allow popups for this site to print both pages.");
        }
        return;
      }
      
      let hasPrinted = false;
      const isFirst = currentIndex === 0;
      const isLast = currentIndex === urls.length - 1;
      
      // Wait for window to load, then print
      const checkLoad = setInterval(() => {
        try {
          if (printWindow.document.readyState === "complete" && !hasPrinted) {
            clearInterval(checkLoad);
            hasPrinted = true;
            
            // Focus and print
            setTimeout(() => {
              try {
                printWindow.focus();
                printWindow.print();
                
                // After printing, open next window (if not last)
                if (!isLast) {
                  setTimeout(() => {
                    currentIndex++;
                    openNext();
                  }, 1000);
                }
              } catch (e) {
                console.error(`Print error for window ${currentIndex}:`, e);
                if (!isLast) {
                  currentIndex++;
                  openNext();
                }
              }
            }, isFirst ? 800 : 500);
          }
        } catch (e) {
          clearInterval(checkLoad);
          if (!isLast) {
            currentIndex++;
            openNext();
          }
        }
      }, 100);
      
      // Fallback timeout
      setTimeout(() => {
        clearInterval(checkLoad);
        if (!hasPrinted) {
          try {
            if (printWindow.document.readyState === "complete") {
              hasPrinted = true;
              printWindow.focus();
              printWindow.print();
            }
          } catch (e) {
            console.error(`Print error for window ${currentIndex}:`, e);
          }
        }
        if (!isLast) {
          currentIndex++;
          openNext();
        }
      }, 5000);
    };
    
    // Start opening windows sequentially
    openNext();
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

  /**
   * Generate PDFs from HTML files
   */
  async generatePdfs(cardSetPath) {
    const statusElement = DOMUtils.get(SELECTORS.generateStatus);
    
    try {
      ProgressModule.show("Generating PDFs...");

      const result = await API.post("cards/generate-pdfs", { path: cardSetPath });
      
      if (result.success) {
        const pdfCount = result.generated?.length || 0;
        if (pdfCount > 0) {
          ToastModule.success(`Generated ${pdfCount} PDF file${pdfCount === 1 ? '' : 's'} and saved to pdfs/ folder`);
        } else {
          ToastModule.info("PDF generation completed");
        }
        // Reload the generated cards list to show updated PDF status
        this.loadGeneratedCards();
        setTimeout(() => ProgressModule.hide(), 1500);
      } else {
        ProgressModule.hide();
        const errorMsg = result.error || "Failed to generate PDFs";
        ToastModule.error(errorMsg.includes("GTK") || errorMsg.includes("WeasyPrint") 
          ? errorMsg 
          : `PDF generation failed: ${errorMsg}`);
      }
    } catch (error) {
      ProgressModule.hide();
      ToastModule.error(`PDF generation error: ${error.message}`);
    }
  },
};
