/**
 * Preview Module
 */

import { API } from "../api.js";
import { DOMUtils } from "../dom-utils.js";
import { Components } from "../components.js";
import { SELECTORS } from "../config.js";
import { appState } from "../state.js";
import { ToastModule } from "./toast.js";

export const PreviewModule = {
  /**
   * Current track data (for editing)
   */
  currentTrackData: null,

  /**
   * Set preview side
   */
  setSide(side) {
    appState.preview.side = side;
    DOMUtils.get(SELECTORS.previewFrontBtn).classList.toggle(
      "active",
      side === "front"
    );
    DOMUtils.get(SELECTORS.previewBackBtn).classList.toggle(
      "active",
      side === "back"
    );
    if (appState.preview.csvPath) {
      this.load();
    }
  },

  /**
   * Load track data into editor fields
   */
  loadTrackDataIntoEditor(trackData) {
    if (!trackData) return;
    
    this.currentTrackData = { ...trackData };
    DOMUtils.get(SELECTORS.editArtist).value = trackData.artist || "";
    DOMUtils.get(SELECTORS.editYear).value = trackData.year || "";
    DOMUtils.get(SELECTORS.editSongName).value = trackData.song_name || "";
    DOMUtils.get(SELECTORS.editSpotifyUrl).value = trackData.spotify_url || "";
  },

  /**
   * Get edited track data from form
   */
  getEditedTrackData() {
    return {
      artist: DOMUtils.get(SELECTORS.editArtist).value.trim(),
      year: DOMUtils.get(SELECTORS.editYear).value.trim(),
      song_name: DOMUtils.get(SELECTORS.editSongName).value.trim(),
      spotify_url: DOMUtils.get(SELECTORS.editSpotifyUrl).value.trim(),
    };
  },

  /**
   * Apply edited changes to preview
   */
  async applyChanges() {
    const csvPath = DOMUtils.get(SELECTORS.previewCsvSelect).value;
    const trackIndex =
      parseInt(DOMUtils.get(SELECTORS.previewTrackIndex).value) - 1;
    const editedData = this.getEditedTrackData();

    if (!csvPath) {
      ToastModule.error("Please select a CSV file first");
      return;
    }

    // Validate required fields
    if (!editedData.artist || !editedData.year || !editedData.song_name) {
      ToastModule.error("Please fill in all required fields (Artist, Year, Song Name)");
      return;
    }

    // Reload preview with edited data
    await this.loadWithData(editedData);
  },

  /**
   * Save edited changes to CSV
   */
  async saveToCsv() {
    const csvPath = DOMUtils.get(SELECTORS.previewCsvSelect).value;
    const trackIndex =
      parseInt(DOMUtils.get(SELECTORS.previewTrackIndex).value) - 1;
    const editedData = this.getEditedTrackData();

    if (!csvPath) {
      ToastModule.error("Please select a CSV file first");
      return;
    }

    // Validate required fields
    if (!editedData.artist || !editedData.year || !editedData.song_name) {
      ToastModule.error("Please fill in all required fields (Artist, Year, Song Name)");
      return;
    }

    try {
      const result = await API.post("cards/update-track", {
        csv_path: csvPath,
        track_index: trackIndex,
        track_data: editedData,
      });

      if (result.success) {
        ToastModule.success(result.message || "Track saved successfully!");
        // Update current track data
        this.currentTrackData = { ...editedData };
        // Reload preview to show saved data
        await this.load();
      }
    } catch (error) {
      ToastModule.error(error.message || "Failed to save track");
    }
  },

  /**
   * Reset editor to original values
   */
  resetEditor() {
    if (this.currentTrackData) {
      this.loadTrackDataIntoEditor(this.currentTrackData);
    }
  },

  /**
   * Load preview with custom track data
   */
  async loadWithData(trackData) {
    const csvPath = DOMUtils.get(SELECTORS.previewCsvSelect).value;
    const trackIndex =
      parseInt(DOMUtils.get(SELECTORS.previewTrackIndex).value) - 1;

    if (!csvPath) {
      ToastModule.error("Please select a CSV file to preview");
      return;
    }

    appState.preview.csvPath = csvPath;
    appState.preview.trackIndex = trackIndex;

    try {
      const result = await API.post("cards/preview", {
        csv_path: csvPath,
        track_index: trackIndex,
        side: appState.preview.side,
        track_data: trackData,
      });

      if (result.success) {
        const container = DOMUtils.get(SELECTORS.previewContainer);
        const iframe = DOMUtils.create("iframe", {
          style: "width: 100%; height: 100%; border: none; display: block;",
        });

        DOMUtils.render(container, [iframe]);

        const iframeDoc =
          iframe.contentDocument || iframe.contentWindow.document;
        iframeDoc.open();
        iframeDoc.write(result.html);
        iframeDoc.close();
        
        // Inject CSS to remove all margins and padding and show only first card centered
        const style = iframeDoc.createElement('style');
        style.textContent = `
          * {
            margin: 0 !important;
            padding: 0 !important;
          }
          html, body {
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
            width: 100% !important;
            height: 100% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
          }
          .page {
            margin: 0 !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 100% !important;
            height: 100% !important;
            grid-template-columns: 1fr !important;
            grid-template-rows: 1fr !important;
            gap: 0 !important;
          }
          .card {
            margin: 0 !important;
            width: 60mm !important;
            height: 60mm !important;
            max-width: 90% !important;
            max-height: 90% !important;
          }
          .card:not(:first-child) {
            display: none !important;
          }
          @page {
            margin: 0 !important;
          }
        `;
        iframeDoc.head.appendChild(style);
        
        // Also set inline styles as backup
        if (iframeDoc.body) {
          iframeDoc.body.style.margin = "0";
          iframeDoc.body.style.padding = "0";
          iframeDoc.body.style.overflow = "hidden";
          iframeDoc.body.style.display = "flex";
          iframeDoc.body.style.alignItems = "center";
          iframeDoc.body.style.justifyContent = "center";
        }
        if (iframeDoc.documentElement) {
          iframeDoc.documentElement.style.margin = "0";
          iframeDoc.documentElement.style.padding = "0";
          iframeDoc.documentElement.style.overflow = "hidden";
        }
        const pageDiv = iframeDoc.querySelector('.page');
        if (pageDiv) {
          pageDiv.style.margin = "0";
          pageDiv.style.padding = "0";
          pageDiv.style.display = "flex";
          pageDiv.style.alignItems = "center";
          pageDiv.style.justifyContent = "center";
        }

        // Update editor with returned track data
        if (result.track_data) {
          this.loadTrackDataIntoEditor(result.track_data);
        }
      }
    } catch (error) {
      DOMUtils.render(DOMUtils.get(SELECTORS.previewContainer), [
        Components.createEmptyState(`Error: ${error.message}`),
      ]);
    }
  },

  /**
   * Change preview track
   */
  async changeTrack(delta) {
    const csvPath = DOMUtils.get(SELECTORS.previewCsvSelect).value;
    if (!csvPath) {
      ToastModule.error("Please select a CSV file first");
      return;
    }

    // Read current track index from input field
    const currentIndexInput = DOMUtils.get(SELECTORS.previewTrackIndex);
    const currentIndex = parseInt(currentIndexInput.value) - 1;
    const newIndex = currentIndex + delta;

    // Ensure maxTracks is available
    if (!appState.preview.maxTracks || appState.preview.maxTracks === 0) {
      try {
        const countResult = await API.post("cards/track-count", {
          csv_path: csvPath,
        });
        if (countResult.success) {
          appState.preview.maxTracks = countResult.total_tracks;
        } else {
          ToastModule.error("Failed to load track count");
          return;
        }
      } catch (error) {
        ToastModule.error("Failed to load track count");
        return;
      }
    }

    // Validate new index
    if (newIndex >= 0 && newIndex < appState.preview.maxTracks) {
      appState.preview.trackIndex = newIndex;
      currentIndexInput.value = newIndex + 1;
      // Reset current track data so editor loads fresh data
      this.currentTrackData = null;
      this.load();
    } else {
      // Show feedback if at boundary
      if (newIndex < 0) {
        ToastModule.error("Already at first track");
      } else {
        ToastModule.error(`Maximum track number is ${appState.preview.maxTracks}`);
      }
    }
  },

  /**
   * Load preview
   */
  async load() {
    const csvPath = DOMUtils.get(SELECTORS.previewCsvSelect).value;
    const trackIndex =
      parseInt(DOMUtils.get(SELECTORS.previewTrackIndex).value) - 1;

    if (!csvPath) {
      ToastModule.error("Please select a CSV file to preview");
      return;
    }

    // Reset maxTracks if CSV file changed
    if (appState.preview.csvPath !== csvPath) {
      appState.preview.maxTracks = 0;
    }

    appState.preview.csvPath = csvPath;
    appState.preview.trackIndex = trackIndex;

    try {
      const result = await API.post("cards/preview", {
        csv_path: csvPath,
        track_index: trackIndex,
        side: appState.preview.side,
      });

      if (result.success) {
        const container = DOMUtils.get(SELECTORS.previewContainer);
        const iframe = DOMUtils.create("iframe", {
          style: "width: 100%; height: 100%; border: none; display: block;",
        });

        DOMUtils.render(container, [iframe]);

        const iframeDoc =
          iframe.contentDocument || iframe.contentWindow.document;
        iframeDoc.open();
        iframeDoc.write(result.html);
        iframeDoc.close();
        
        // Inject CSS to remove all margins and padding and show only first card centered
        const style = iframeDoc.createElement('style');
        style.textContent = `
          * {
            margin: 0 !important;
            padding: 0 !important;
          }
          html, body {
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
            width: 100% !important;
            height: 100% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
          }
          .page {
            margin: 0 !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 100% !important;
            height: 100% !important;
            grid-template-columns: 1fr !important;
            grid-template-rows: 1fr !important;
            gap: 0 !important;
          }
          .card {
            margin: 0 !important;
            width: 60mm !important;
            height: 60mm !important;
            max-width: 90% !important;
            max-height: 90% !important;
          }
          .card:not(:first-child) {
            display: none !important;
          }
          @page {
            margin: 0 !important;
          }
        `;
        iframeDoc.head.appendChild(style);
        
        // Also set inline styles as backup
        if (iframeDoc.body) {
          iframeDoc.body.style.margin = "0";
          iframeDoc.body.style.padding = "0";
          iframeDoc.body.style.overflow = "hidden";
          iframeDoc.body.style.display = "flex";
          iframeDoc.body.style.alignItems = "center";
          iframeDoc.body.style.justifyContent = "center";
        }
        if (iframeDoc.documentElement) {
          iframeDoc.documentElement.style.margin = "0";
          iframeDoc.documentElement.style.padding = "0";
          iframeDoc.documentElement.style.overflow = "hidden";
        }
        const pageDiv = iframeDoc.querySelector('.page');
        if (pageDiv) {
          pageDiv.style.margin = "0";
          pageDiv.style.padding = "0";
          pageDiv.style.display = "flex";
          pageDiv.style.alignItems = "center";
          pageDiv.style.justifyContent = "center";
        }

        // Show editor and load track data
        const editor = DOMUtils.get(SELECTORS.cardEditor);
        if (editor) {
          editor.style.display = "block";
        }
        if (result.track_data) {
          this.loadTrackDataIntoEditor(result.track_data);
        }

        // Store max tracks from response or fetch if not available
        if (result.total_tracks !== undefined) {
          appState.preview.maxTracks = result.total_tracks;
        } else {
          // Fallback: fetch track count via API
          try {
            const countResult = await API.post("cards/track-count", {
              csv_path: csvPath,
            });
            if (countResult.success) {
              appState.preview.maxTracks = countResult.total_tracks;
            }
          } catch (error) {
            console.error("Failed to get track count:", error);
          }
        }
      }
    } catch (error) {
      DOMUtils.render(DOMUtils.get(SELECTORS.previewContainer), [
        Components.createEmptyState(`Error: ${error.message}`),
      ]);
    }
  },
};

