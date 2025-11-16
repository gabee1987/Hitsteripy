/**
 * CSV Module
 */

import { API } from "../api.js";
import { DOMUtils } from "../dom-utils.js";
import { SELECTORS } from "../config.js";
import { appState } from "../state.js";

export const CsvModule = {
  /**
   * Load available CSV files
   */
  async load() {
    try {
      const files = await API.get("cards/csv-files");
      const selectGenerate = DOMUtils.get(SELECTORS.csvFileSelect);
      const selectPreview = DOMUtils.get(SELECTORS.previewCsvSelect);

      if (files.length === 0) {
        selectGenerate.innerHTML =
          '<option value="">No CSV files found</option>';
        selectPreview.innerHTML =
          '<option value="">No CSV files found</option>';
        return;
      }

      // Clear and populate selects
      [selectGenerate, selectPreview].forEach((select) => {
        select.innerHTML = "";
        files.forEach((file) => {
          const option = DOMUtils.create("option", { value: file.path }, [
            file.label,
          ]);
          select.appendChild(option);
        });
      });

      if (files.length > 0 && !appState.preview.csvPath) {
        appState.preview.csvPath = files[0].path;
        selectPreview.value = files[0].path;
      }
    } catch (error) {
      console.error("Failed to load CSV files:", error);
    }
  },
};

