<template>
  <div class="container">
    <h1>YouTube Downloader</h1>
    
    <form @submit.prevent="getVideoInfo">
      <div class="form-group">
        <div class="url-input-container">
          <input 
            type="text" 
            v-model="url" 
            placeholder="https://www.youtube.com/..." 
            required
            @input="onUrlInput"
          >
        </div>
        <div class="url-hint">
          Only YouTube URLs are supported (videos and shorts). 
          Video information will load automatically when you paste a valid YouTube URL.
        </div>
        <button style="display:none;" type="submit">Get Video Info</button>
      </div>
    </form>

    <!-- Video Info Section -->
    <div 
      class="video-info" 
      v-show="showVideoInfo" 
      :class="{ 
        'show': showVideoInfo, 
        'loading': isLoadingVideoInfo, 
        'error': videoInfoError 
      }"
    >
      <div v-if="isLoadingVideoInfo" class="loading">
        <div class="loading-spinner"></div>
        Getting video information...
      </div>
      
      <div v-else-if="videoInfoError" class="error">
        <div style="margin-bottom: 15px;">
          <strong>⚠️ {{ videoInfoErrorMessage }}</strong>
        </div>
        <div style="margin-bottom: 15px;">
          <button @click="retryVideoInfo" class="download-button" style="margin-right: 10px;">
            🔄 Try Again
          </button>
          <button @click="reloadWithUrl" class="download-button">
            🔄 Reload & Keep URL
          </button>
        </div>
        <div style="font-size: 0.9em; color: #666;">
          💡 Tip: If the problem persists, try reloading the page or check your internet connection.
        </div>
      </div>
      
      <div v-else-if="videoInfo">
        <img 
          v-if="videoInfo.thumbnail" 
          :src="videoInfo.thumbnail" 
          alt="Video thumbnail" 
          class="video-thumbnail"
        >
        <div class="video-title">{{ videoInfo.title || 'Unknown Title' }}</div>
        <div class="video-meta">
          <strong>Duration:</strong> {{ videoInfo.duration || 'Unknown' }} | 
          <strong>Uploader:</strong> {{ videoInfo.uploader || 'Unknown' }} | 
          <strong>Views:</strong> {{ videoInfo.view_count || 'Unknown' }}
          <span v-if="videoInfo.height"> | <strong>Quality:</strong> {{ videoInfo.height }}p</span>
          <span v-if="videoInfo.format_info"> | <strong>Format:</strong> {{ videoInfo.format_info }}</span>
        </div>
        <div class="video-description">{{ videoInfo.description || 'No description available' }}</div>
        <button @click="startDownload" class="download-button">
          📥 Download Video
        </button>
      </div>
    </div>

    <!-- Progress Section -->
    <div 
      class="progress-section" 
      v-show="showProgress" 
      :class="{ 'show': showProgress }"
    >
      <div id="progress-container">
        <div 
          id="progress-bar" 
          :style="{ width: progressData.progress || '0%' }" 
          :class="progressBarClass"
        >
          {{ progressData.progress_text || '0%' }}
        </div>
      </div>
      <div id="extra-info">{{ extraInfo }}</div>
      
      <div v-if="downloadError" class="button-container" style="margin-top: 15px;">
        <button @click="retryDownload" class="download-button">🔄 Try Again</button>
        <button @click="reloadWithUrl" class="download-button">🔄 Reload & Keep URL</button>
      </div>
      
      <div v-if="downloadComplete" class="button-container">
        <button @click="reloadPage" class="download-button">🔄 Reload Page</button>
        <button @click="downloadAnother" class="download-button">📥 Download Another Video</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      url: '',
      urlTimeout: null,
      showVideoInfo: false,
      isLoadingVideoInfo: false,
      videoInfoError: false,
      videoInfoErrorMessage: '',
      videoInfo: null,
      currentInfoId: null,
      showProgress: false,
      progressData: {},
      extraInfo: '',
      downloadError: false,
      downloadComplete: false,
      currentDownloadId: null
    }
  },
  computed: {
    isValidYouTubeUrl() {
      const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com\/(watch\?v=|shorts\/)|youtu\.be\/)[a-zA-Z0-9_-]{11}/;
      return youtubeRegex.test(this.url.trim());
    },
    progressBarClass() {
      if (this.downloadError) return 'error';
      if (this.progressData.status === 'starting') return 'warning';
      return '';
    }
  },
  watch: {
    url(newUrl) {
      if (newUrl && this.isValidYouTubeUrl) {
        // Clear any existing timeout
        if (this.urlTimeout) {
          clearTimeout(this.urlTimeout);
        }
        
        // Set a timeout to get video info after user stops typing
        this.urlTimeout = setTimeout(() => {
          this.getVideoInfo();
        }, 1000);
      }
    }
  },
  mounted() {
    this.initializeApp();
  },
  methods: {
    initializeApp() {
      // Restore URL from sessionStorage if available
      const savedUrl = sessionStorage.getItem('retryUrl');
      if (savedUrl) {
        this.url = savedUrl;
        sessionStorage.removeItem('retryUrl');
      }

      // Deep link logic
      const path = window.location.pathname;
      const search = window.location.search;
      let youtubeUrl = null;
      if (path.startsWith('/watch')) {
        youtubeUrl = `https://www.youtube.com${path}${search}`;
      } else if (path.startsWith('/shorts')) {
        youtubeUrl = `https://www.youtube.com${path}${search}`;
      }
      if (youtubeUrl) {
        this.url = youtubeUrl;
        // Automatically fetch video info when URL is parsed and filled
        setTimeout(() => {
          this.getVideoInfo();
        }, 300);
      }
    },
    onUrlInput() {
      // This method is called on input, but the actual logic is in the watcher
    },
    async getVideoInfo() {
      if (!this.url.trim()) {
        this.showError("Please enter a YouTube URL");
        return;
      }
      
      if (!this.isValidYouTubeUrl) {
        this.showError("Please enter a valid YouTube URL. Only YouTube videos are supported.");
        return;
      }

      this.resetStates();
      this.isLoadingVideoInfo = true;
      this.showVideoInfo = true;
      this.showProgress = false;

      try {
        const formData = new FormData();
        formData.append("url", this.url.trim());

        const response = await fetch("/get-video-info", {
          method: "POST",
          body: formData
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        this.currentInfoId = data.info_id;
        this.pollVideoInfo(data.info_id);
      } catch (error) {
        console.error('Error:', error);
        this.showVideoInfoError("Failed to get video information. Please try again.");
      }
    },
    pollVideoInfo(infoId) {
      let attempts = 0;
      const maxAttempts = 30;

      const poll = async () => {
        attempts++;

        try {
          const response = await fetch(`/video-info/${infoId}`);

          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          const data = await response.json();

          if (data.error) {
            this.showVideoInfoError(`Error getting video info: ${data.error}`);
            return;
          }

          if (data.status === "ready") {
            this.displayVideoInfo(data);
            return;
          }

          // Continue polling
          if (attempts < maxAttempts) {
            setTimeout(poll, 1000);
          } else {
            this.showVideoInfoError("Timeout: Video info request took too long. Please try again.");
          }
        } catch (error) {
          console.error('Error polling video info:', error);

          if (attempts >= maxAttempts) {
            this.showVideoInfoError("Timeout: Video info request took too long. Please try again.");
          } else {
            this.videoInfoError = true;
            this.videoInfoErrorMessage = `Lost connection to server. Trying to reconnect... (${attempts}/${maxAttempts})`;
            setTimeout(poll, 1000);
          }
        }
      };

      setTimeout(poll, 1000);
    },
    displayVideoInfo(videoData) {
      this.isLoadingVideoInfo = false;
      this.videoInfoError = false;
      this.videoInfo = videoData;
    },
    async startDownload() {
      if (!this.currentInfoId) return;

      console.log('Starting download for info_id:', this.currentInfoId);

      this.showProgress = true;
      this.showVideoInfo = false;
      this.resetProgressState();

      try {
        const formData = new FormData();
        formData.append("info_id", this.currentInfoId);

        const response = await fetch("/start-download", {
          method: "POST",
          body: formData
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Download response:', data);
        this.currentDownloadId = data.download_id;
        this.pollProgress(data.download_id);
      } catch (error) {
        console.error('Error starting download:', error);
        this.showDownloadError("Failed to start download. Please try again.");
      }
    },
    pollProgress(downloadId) {
      let attempts = 0;
      const maxAttempts = 300;

      const poll = async () => {
        attempts++;

        try {
          const response = await fetch(`/progress/${downloadId}`);

          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          const data = await response.json();
          console.log('Progress data:', data);

          if (data.error) {
            this.showDownloadError(`Download failed: ${data.error}`);
            return;
          }

          this.progressData = data;
          this.updateExtraInfo(data);

          if (data.status === "finished" && data.download_ready && data.filename) {
            this.progressData.progress = "100%";
            this.progressData.progress_text = "Starting Download...";
            this.extraInfo = "Download will start automatically...";

            // Automatically start the download
            this.downloadFile(downloadId, data.filename);
            return;
          }

          // Continue polling
          if (attempts < maxAttempts) {
            setTimeout(poll, 1000);
          } else {
            this.showDownloadError("Timeout: Download took too long. Please try again.");
          }
        } catch (error) {
          console.error('Error polling progress:', error);

          if (attempts >= maxAttempts) {
            this.showDownloadError("Timeout: Download took too long. Please try again.");
          } else {
            this.extraInfo = `Lost connection to server. Trying to reconnect... (${attempts}/${maxAttempts})`;
            setTimeout(poll, 1000);
          }
        }
      };

      setTimeout(poll, 1000);
    },
    updateExtraInfo(data) {
      const status = data.status || "";
      const eta = data.eta || "...";
      const speed = data.speed || "...";
      const filename = data.filename || "";

      let extraInfo = "";
      if (status === "starting") {
        extraInfo = "Status: Preparing download...";
      } else if (status === "downloading") {
        extraInfo = `ETA: ${eta} | Speed: ${speed}`;
      } else if (status === "streaming") {
        extraInfo = "Status: Downloading to your browser...";
      } else if (status === "finished") {
        extraInfo = "Status: Ready for download";
      }

      if (filename) {
        extraInfo += ` | File: ${filename}`;
      }

      this.extraInfo = extraInfo;
    },
    downloadFile(downloadId, filename) {
      console.log('Downloading file:', downloadId, filename);

      this.progressData.progress_text = "Download Started";
      this.extraInfo = `Downloading: ${filename}`;

      // Use the streaming download endpoint for direct browser download
      const link = document.createElement('a');
      link.href = `/stream-download/${downloadId}`;
      link.download = filename;
      link.style.display = 'none';

      // Add to DOM, click, and remove
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Show completion message after a short delay
      setTimeout(() => {
        this.progressData.progress_text = "Download Complete";
        this.extraInfo = "File downloaded successfully!";
        this.downloadComplete = true;
      }, 1000);
    },
    retryVideoInfo() {
      this.getVideoInfo();
    },
    retryDownload() {
      if (this.currentInfoId) {
        this.startDownload();
      } else {
        this.getVideoInfo();
      }
    },
    reloadWithUrl() {
      if (this.url.trim()) {
        sessionStorage.setItem('retryUrl', this.url.trim());
      }
      window.location.reload();
    },
    reloadPage() {
      window.location.reload();
    },
    downloadAnother() {
      this.url = '';
      this.resetStates();
      this.resetProgressState();
      this.$nextTick(() => {
        const input = document.querySelector('input[type="text"]');
        if (input) input.focus();
      });
    },
    showError(message) {
      this.showVideoInfo = true;
      this.videoInfoError = true;
      this.videoInfoErrorMessage = message;
      this.isLoadingVideoInfo = false;
    },
    showVideoInfoError(message) {
      this.isLoadingVideoInfo = false;
      this.videoInfoError = true;
      this.videoInfoErrorMessage = message;
    },
    showDownloadError(message) {
      this.downloadError = true;
      this.progressData.progress_text = "Download Failed";
      this.extraInfo = message;
    },
    resetStates() {
      this.videoInfoError = false;
      this.videoInfoErrorMessage = '';
      this.videoInfo = null;
      this.isLoadingVideoInfo = false;
    },
    resetProgressState() {
      this.progressData = { progress: '0%', progress_text: '0%' };
      this.extraInfo = '';
      this.downloadError = false;
      this.downloadComplete = false;
      this.currentDownloadId = null;
    }
  }
}
</script>
