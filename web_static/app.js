// Hitsteripy Web App - Frontend JavaScript

let currentStatus = {
  playlist_url: null,
  playlist_name: null,
  track_count: null,
  spotify_connected: false,
};

let currentPreview = {
  csvPath: null,
  trackIndex: 0,
  side: "back",
  maxTracks: 0,
};

// Initialize app
document.addEventListener("DOMContentLoaded", function () {
  setupTabs();
  setupEventListeners();
  loadStatus();
  loadPlaylistHistory();
  loadTrackCountHistory();
  loadCsvFiles();

  // Auto-refresh status every 2 seconds
  setInterval(loadStatus, 2000);
});

// Tab switching
function setupTabs() {
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const tabId = btn.dataset.tab;

      // Update buttons
      tabBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      // Update content
      tabContents.forEach((c) => c.classList.remove("active"));
      document.getElementById(`tab-${tabId}`).classList.add("active");

      // Load data for specific tabs
      if (tabId === "generate" || tabId === "preview") {
        loadCsvFiles();
      }
      if (tabId === "logs") {
        loadLogs();
      }
    });
  });
}

// Event listeners
function setupEventListeners() {
  // Playlist
  document
    .getElementById("setPlaylistBtn")
    .addEventListener("click", setPlaylist);
  document.getElementById("playlistUrl").addEventListener("keypress", (e) => {
    if (e.key === "Enter") setPlaylist();
  });

  // Track count
  document
    .getElementById("setTrackCountBtn")
    .addEventListener("click", setTrackCount);
  document.querySelectorAll("[data-count]").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.getElementById("trackCount").value = btn.dataset.count;
      setTrackCount();
    });
  });
  document.getElementById("trackCount").addEventListener("keypress", (e) => {
    if (e.key === "Enter") setTrackCount();
  });

  // Import
  document
    .getElementById("importTracksBtn")
    .addEventListener("click", importTracks);

  // Generate
  document
    .getElementById("generateCardsBtn")
    .addEventListener("click", generateCards);

  // Preview
  document
    .getElementById("loadPreviewBtn")
    .addEventListener("click", loadPreview);
  document
    .getElementById("prevTrackBtn")
    .addEventListener("click", () => changePreviewTrack(-1));
  document
    .getElementById("nextTrackBtn")
    .addEventListener("click", () => changePreviewTrack(1));
  document
    .getElementById("previewFrontBtn")
    .addEventListener("click", () => setPreviewSide("front"));
  document
    .getElementById("previewBackBtn")
    .addEventListener("click", () => setPreviewSide("back"));

  // Logs
  document.getElementById("refreshLogsBtn").addEventListener("click", loadLogs);
}

// API calls
async function apiCall(endpoint, method = "GET", body = null) {
  try {
    const options = {
      method,
      headers: {
        "Content-Type": "application/json",
      },
    };

    if (body) {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(`/api/${endpoint}`, options);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Request failed");
    }

    return data;
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
}

// Status
async function loadStatus() {
  try {
    const status = await apiCall("status");
    currentStatus = status;

    // Update status bar
    document.getElementById("statusPlaylist").textContent =
      status.playlist_name || "None selected";
    document.getElementById("statusTrackCount").textContent =
      status.track_count || "N/A";

    const spotifyEl = document.getElementById("statusSpotify");
    if (status.spotify_connected) {
      spotifyEl.textContent = "Connected";
      spotifyEl.className = "status-value success";
    } else {
      spotifyEl.textContent = "Disconnected";
      spotifyEl.className = "status-value error";
    }
  } catch (error) {
    console.error("Failed to load status:", error);
  }
}

// Playlist
async function loadPlaylistHistory() {
  try {
    const history = await apiCall("playlists/history");
    const container = document.getElementById("playlistHistory");

    if (history.length === 0) {
      container.innerHTML = '<p class="info-text">No recent playlists</p>';
      return;
    }

    container.innerHTML = history
      .map(
        (item) => `
            <div class="history-item" onclick="selectPlaylist('${item.url}', '${item.name}')">
                <strong>${item.name}</strong>
                <div style="font-size: 0.85rem; color: var(--text-light);">${item.url}</div>
            </div>
        `
      )
      .join("");
  } catch (error) {
    console.error("Failed to load playlist history:", error);
  }
}

function selectPlaylist(url, name) {
  document.getElementById("playlistUrl").value = url;
  setPlaylist();
}

async function setPlaylist() {
  const url = document.getElementById("playlistUrl").value.trim();
  if (!url) {
    showMessage("importStatus", "Please enter a playlist URL", "error");
    return;
  }

  try {
    document.getElementById("setPlaylistBtn").disabled = true;
    document.getElementById("setPlaylistBtn").innerHTML =
      '<span class="spinner"></span> Setting...';

    const result = await apiCall("playlists/set", "POST", { url });

    if (result.success) {
      showMessage(
        "importStatus",
        `Playlist set: ${result.playlist_name}`,
        "success"
      );
      document.getElementById("playlistUrl").value = "";
      loadStatus();
      loadPlaylistHistory();
    }
  } catch (error) {
    showMessage("importStatus", `Error: ${error.message}`, "error");
  } finally {
    document.getElementById("setPlaylistBtn").disabled = false;
    document.getElementById("setPlaylistBtn").textContent = "Set Playlist";
  }
}

// Track count
async function loadTrackCountHistory() {
  try {
    const data = await apiCall("tracks/count/history");
    const container = document.getElementById("trackCountHistory");

    const allOptions = [
      ...data.defaults,
      ...data.history.filter((h) => !data.defaults.includes(h)),
    ];

    if (allOptions.length === 0) {
      container.innerHTML = '<p class="info-text">No recent counts</p>';
      return;
    }

    container.innerHTML = allOptions
      .slice(0, 10)
      .map(
        (count) => `
            <div class="history-item" onclick="selectTrackCount('${count}')">
                ${count}
            </div>
        `
      )
      .join("");
  } catch (error) {
    console.error("Failed to load track count history:", error);
  }
}

function selectTrackCount(count) {
  document.getElementById("trackCount").value = count;
  setTrackCount();
}

async function setTrackCount() {
  const count = document.getElementById("trackCount").value.trim();
  if (!count) {
    showMessage("importStatus", "Please enter a track count", "error");
    return;
  }

  try {
    const result = await apiCall("tracks/count/set", "POST", { count });

    if (result.success) {
      showMessage(
        "importStatus",
        `Track count set to: ${result.track_count}`,
        "success"
      );
      document.getElementById("trackCount").value = "";
      loadStatus();
      loadTrackCountHistory();
    }
  } catch (error) {
    showMessage("importStatus", `Error: ${error.message}`, "error");
  }
}

// Import
async function importTracks() {
  if (!currentStatus.playlist_url) {
    showMessage("importStatus", "Please set a playlist URL first", "error");
    return;
  }

  if (!currentStatus.track_count) {
    showMessage("importStatus", "Please set a track count first", "error");
    return;
  }

  try {
    const btn = document.getElementById("importTracksBtn");
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Importing...';

    const result = await apiCall("tracks/import", "POST");

    if (result.success) {
      showMessage("importStatus", result.summary, "success");
      loadCsvFiles();
    }
  } catch (error) {
    showMessage("importStatus", `Error: ${error.message}`, "error");
  } finally {
    const btn = document.getElementById("importTracksBtn");
    btn.disabled = false;
    btn.textContent = "📥 Import Tracks";
  }
}

// CSV files
async function loadCsvFiles() {
  try {
    const files = await apiCall("cards/csv-files");
    const selectGenerate = document.getElementById("csvFileSelect");
    const selectPreview = document.getElementById("previewCsvSelect");

    if (files.length === 0) {
      selectGenerate.innerHTML = '<option value="">No CSV files found</option>';
      selectPreview.innerHTML = '<option value="">No CSV files found</option>';
      return;
    }

    const options = files
      .map((file) => `<option value="${file.path}">${file.label}</option>`)
      .join("");

    selectGenerate.innerHTML = options;
    selectPreview.innerHTML = options;

    if (files.length > 0 && !currentPreview.csvPath) {
      currentPreview.csvPath = files[0].path;
      selectPreview.value = files[0].path;
    }
  } catch (error) {
    console.error("Failed to load CSV files:", error);
  }
}

// Generate
async function generateCards() {
  const csvPath = document.getElementById("csvFileSelect").value;

  if (!csvPath) {
    showMessage("generateStatus", "Please select a CSV file", "error");
    return;
  }

  try {
    const btn = document.getElementById("generateCardsBtn");
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Generating...';

    const result = await apiCall("cards/generate", "POST", {
      csv_path: csvPath,
    });

    if (result.success) {
      showMessage("generateStatus", result.summary, "success");
    }
  } catch (error) {
    showMessage("generateStatus", `Error: ${error.message}`, "error");
  } finally {
    const btn = document.getElementById("generateCardsBtn");
    btn.disabled = false;
    btn.textContent = "🎨 Generate Cards";
  }
}

// Preview
function setPreviewSide(side) {
  currentPreview.side = side;
  document
    .getElementById("previewFrontBtn")
    .classList.toggle("active", side === "front");
  document
    .getElementById("previewBackBtn")
    .classList.toggle("active", side === "back");
  if (currentPreview.csvPath) {
    loadPreview();
  }
}

function changePreviewTrack(delta) {
  const newIndex = currentPreview.trackIndex + delta;
  if (newIndex >= 0 && newIndex < currentPreview.maxTracks) {
    currentPreview.trackIndex = newIndex;
    document.getElementById("previewTrackIndex").value = newIndex + 1;
    loadPreview();
  }
}

async function loadPreview() {
  const csvPath = document.getElementById("previewCsvSelect").value;
  const trackIndex =
    parseInt(document.getElementById("previewTrackIndex").value) - 1;

  if (!csvPath) {
    showMessage("importStatus", "Please select a CSV file", "error");
    return;
  }

  currentPreview.csvPath = csvPath;
  currentPreview.trackIndex = trackIndex;

  try {
    const result = await apiCall("cards/preview", "POST", {
      csv_path: csvPath,
      track_index: trackIndex,
      side: currentPreview.side,
    });

    if (result.success) {
      const container = document.getElementById("previewContainer");

      // Create iframe to render HTML
      const iframe = document.createElement("iframe");
      iframe.style.width = "100%";
      iframe.style.minHeight = "600px";
      iframe.style.border = "none";

      container.innerHTML = "";
      container.appendChild(iframe);

      // Write HTML to iframe
      const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
      iframeDoc.open();
      iframeDoc.write(result.html);
      iframeDoc.close();

      // Get max tracks for navigation
      fetch(csvPath)
        .then((r) => r.text())
        .then((text) => {
          const lines = text.split("\n").filter((l) => l.trim());
          currentPreview.maxTracks = Math.max(0, lines.length - 1); // Subtract header
        });
    }
  } catch (error) {
    document.getElementById(
      "previewContainer"
    ).innerHTML = `<p class="info-text">Error: ${error.message}</p>`;
  }
}

// Logs
async function loadLogs() {
  try {
    const logs = await apiCall("logs");
    const container = document.getElementById("logsContainer");

    if (logs.length === 0) {
      container.innerHTML = "<p>No logs yet</p>";
      return;
    }

    container.innerHTML = logs
      .map((log) => {
        const type = log.includes("[INFO]")
          ? "info"
          : log.includes("[SUCCESS]")
          ? "success"
          : log.includes("[ERROR]")
          ? "error"
          : "info";
        return `<div class="log-entry log-${type}">${escapeHtml(log)}</div>`;
      })
      .reverse()
      .join("");

    container.scrollTop = 0;
  } catch (error) {
    console.error("Failed to load logs:", error);
  }
}

// Utility
function showMessage(elementId, message, type) {
  const element = document.getElementById(elementId);
  element.textContent = message;
  element.className = `status-message ${type}`;

  if (type === "success") {
    setTimeout(() => {
      element.className = "status-message";
    }, 5000);
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Expose functions for inline handlers
window.selectPlaylist = selectPlaylist;
window.selectTrackCount = selectTrackCount;
