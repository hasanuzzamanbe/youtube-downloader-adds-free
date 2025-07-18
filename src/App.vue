<template>
  <div class="app">
    <!-- Header Section -->
    <header class="header">
      <div class="header-content">
        <div class="logo-section">
          <div class="logo">
            <svg viewBox="0 0 24 24" class="logo-icon">
              <path fill="currentColor" d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 3.993-8 4.007z"/>
            </svg>
            <span class="logo-text">GetsTube</span>
          </div>
          <p class="tagline">Download YouTube videos instantly</p>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <div class="container">
        <!-- Input Section -->
        <div class="input-section">
<!--          <h2 class="section-title">Enter YouTube URL</h2>-->
          <form @submit.prevent="getVideoInfo" class="url-form">
            <div class="input-wrapper">
              <div class="input-icon">
                <svg viewBox="0 0 24 24">
                  <path fill="currentColor" d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z"/>
                </svg>
              </div>
              <input
                type="text"
                v-model="url"
                placeholder="Paste YouTube URL here (e.g., https://www.youtube.com/watch?v=...)"
                required
                @input="onUrlInput"
                class="url-input"
              >
              <button
                type="button"
                @click="clearUrl"
                v-if="url"
                class="clear-btn"
                title="Clear URL"
              >
                <svg viewBox="0 0 24 24">
                  <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
              </button>
            </div>
            <div class="url-hint">
              <svg viewBox="0 0 24 24" class="hint-icon">
                <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
              </svg>
              Supports YouTube videos and shorts. Videos stream directly, audio files are auto-cleaned after download.
            </div>
          </form>

          <!-- Demo section when no input -->
          <div v-if="!url.trim()" class="demo-section">
            <div class="demo-placeholder">
              <p class="demo-text">Paste any YouTube URL above or replace youTube link with getsTube anywhere!</p>

              <!--                gif add/-->
              <img style="border-radius: 0.5rem;" src="../public/getstube-demo.gif" alt="Demo GIF" class="demo-gif">

              <div class="demo-features">
                <!--                  <div class="feature-item">-->
                <!--                    <svg viewBox="0 0 24 24" class="feature-icon">-->
                <!--                      <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>-->
                <!--                    </svg>-->
                <!--                    <span>Multiple video qualities</span>-->
                <!--                  </div>-->
                <!--                  <div class="feature-item">-->
                <!--                    <svg viewBox="0 0 24 24" class="feature-icon">-->
                <!--                      <path fill="currentColor" d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>-->
                <!--                    </svg>-->
                <!--                    <span>MP3 audio extraction</span>-->
                <!--                  </div>-->
                <!--                  <div class="feature-item">-->
                <!--                    <svg viewBox="0 0 24 24" class="feature-icon">-->
                <!--                      <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>-->
                <!--                    </svg>-->
                <!--                    <span>Direct streaming to browser</span>-->
                <!--                  </div>-->
              </div>
            </div>
          </div>
        </div>

        <!-- Video Info Section -->
        <div
          class="video-info-section"
          v-show="showVideoInfo"
        >
          <div class="card" :class="{ 'loading': isLoadingVideoInfo, 'error': videoInfoError }">
            <div v-if="isLoadingVideoInfo" class="loading-state">
              <div class="loading-spinner"></div>
              <h3>Getting video information...</h3>
              <p>Please wait while we fetch the video details</p>
            </div>

            <div v-else-if="videoInfoError" class="error-state">
              <div class="error-icon">
                <svg viewBox="0 0 24 24">
                  <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                </svg>
              </div>
              <h3>{{ videoInfoErrorMessage }}</h3>
              <div class="error-actions">
                <button @click="retryVideoInfo" class="btn btn-primary">
                  <svg viewBox="0 0 24 24">
                    <path fill="currentColor" d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
                  </svg>
                  Try Again
                </button>
                <button @click="reloadWithUrl" class="btn btn-secondary">
                  <svg viewBox="0 0 24 24">
                    <path fill="currentColor" d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
                  </svg>
                  Reload & Keep URL
                </button>
              </div>
              <p class="error-tip">
                💡 If the problem persists, try reloading the page or check your internet connection.
              </p>
            </div>

            <div v-else-if="videoInfo" class="video-info">
              <div class="video-thumbnail-container">
                <img
                  v-if="videoInfo.thumbnail"
                  :src="videoInfo.thumbnail"
                  alt="Video thumbnail"
                  class="video-thumbnail"
                >
                <div class="video-overlay">
                  <svg viewBox="0 0 24 24" class="play-icon">
                    <path fill="currentColor" d="M8 5v14l11-7z"/>
                  </svg>
                </div>
              </div>

              <div class="video-details">
                <h3 class="video-title">{{ videoInfo.title || 'Unknown Title' }}</h3>

                <div class="video-meta">
                  <div class="meta-item">
                    <svg viewBox="0 0 24 24">
                      <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                    </svg>
                    <span>{{ videoInfo.duration || 'Unknown' }}</span>
                  </div>
                  <div class="meta-item">
                    <svg viewBox="0 0 24 24">
                      <path fill="currentColor" d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                    </svg>
                    <span>{{ videoInfo.uploader || 'Unknown' }}</span>
                  </div>
                  <div class="meta-item">
                    <svg viewBox="0 0 24 24">
                      <path fill="currentColor" d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
                    </svg>
                    <span>{{ videoInfo.view_count || 'Unknown' }}</span>
                  </div>
                  <div v-if="videoInfo.height" class="meta-item">
                    <svg viewBox="0 0 24 24">
                      <path fill="currentColor" d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z"/>
                    </svg>
                    <span>{{ videoInfo.height }}p</span>
                  </div>
                  <div>
                    more
                    <svg @click="showDescription = !showDescription" style="float:right; cursor: pointer;"
                         viewBox="0 0 24 24"
                         class="collapse-icon"
                         :class="{ expanded: showDescription }"
                    >
                      <path fill="currentColor" d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/>
                    </svg>
                  </div>
                </div>

                <p class="video-description">
                  <span v-if="showDescription">{{ videoInfo.description || 'No description available' }}</span>
                </p>

                <div class="format-tabs">
                  <button
                      @click="selectedFormat = 'video'"
                      :class="['format-tab', { active: selectedFormat === 'video' }]"
                  >
                    <svg viewBox="0 0 24 24">
                      <path fill="currentColor" d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/>
                    </svg>
                    Video
                  </button>
                  <button
                      @click="selectedFormat = 'audio'"
                      :class="['format-tab', { active: selectedFormat === 'audio' }]"
                  >
                    <svg viewBox="0 0 24 24">
                      <path fill="currentColor" d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
                    </svg>
                    Audio (MP3)
                  </button>
                </div>
                <!-- Format Selection -->
                <div class="format-selection">

                    <button @click="startDownload" class="btn btn-download">
                      <svg viewBox="0 0 24 24">
                        <path fill="currentColor" d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
                      </svg>
                      Download {{ selectedFormat === 'video' ? 'Video - ' + getSelectedQualityLabel() : getSelectedAudioQualityLabel() }}
                    </button>
                    <div>
                    </div>

                  <!-- Video Quality Options -->
                  <div v-if="selectedFormat === 'video'" class="quality-options">
                    <!-- Collapsible Video Quality Options -->
                    <div class="quality-collapse-header" @click="showVideoOptions = !showVideoOptions">
                      <h5 class="quality-title">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none"
                             stroke="rgb(0, 212, 255)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <circle cx="12" cy="12" r="3" />
                          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33
                             1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51
                             1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0
                             .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09a1.65 1.65 0 0 0
                             1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65
                             0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65
                             0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1
                             2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0
                             1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
                        </svg>

                      </h5>
                    </div>

                    <div v-show="showVideoOptions" class="quality-grid">
                      <button
                          v-for="quality in availableQualities"
                          :key="quality.value"
                          @click="selectedQuality = quality.value"
                          :class="['quality-btn', { active: selectedQuality === quality.value }]"
                      >
                        <div class="quality-info">
                          <span class="quality-label">{{ quality.label }}</span>
                          <span class="quality-desc">{{ quality.description }}</span>
                        </div>
                        <svg v-if="selectedQuality === quality.value" viewBox="0 0 24 24" class="check-icon">
                          <path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                        </svg>
                      </button>
                    </div>
                  </div>

                  <!-- Audio Quality Options -->
                  <div v-if="selectedFormat === 'audio'" class="quality-options">
                    <div v-if="!ffmpegAvailable" class="audio-notice">
                      <svg viewBox="0 0 24 24" class="notice-icon">
                        <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                      </svg>
                      <div>
                        <h5>FFmpeg Required</h5>
                        <p>Audio extraction requires FFmpeg. Please install FFmpeg to enable audio downloads. <a href="#" @click.prevent="showFFmpegGuide = true">Installation Guide</a></p>
                      </div>
                    </div>

                    <div v-else>
                      <!-- Collapsible Audio Quality Options -->
                      <div class="quality-collapse-header" @click="showAudioOptions = !showAudioOptions">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none"
                             stroke="rgb(0, 212, 255)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <circle cx="12" cy="12" r="3" />
                          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33
                             1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51
                             1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0
                             .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09a1.65 1.65 0 0 0
                             1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65
                             0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65
                             0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1
                             2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0
                             1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
                        </svg>

                      </div>

                      <div v-show="showAudioOptions" class="quality-grid">
                        <button
                            v-for="quality in audioQualities"
                            :key="quality.value"
                            @click="selectedAudioQuality = quality.value"
                            :class="['quality-btn', { active: selectedAudioQuality === quality.value }]"
                        >
                          <div class="quality-info">
                            <span class="quality-label">{{ quality.label }}</span>
                            <span class="quality-desc">{{ quality.description }}</span>
                          </div>
                          <svg v-if="selectedAudioQuality === quality.value" viewBox="0 0 24 24" class="check-icon">
                            <path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                          </svg>
                        </button>
                      </div>

                      <!--                      <div class="audio-info">-->
                      <!--                        <svg viewBox="0 0 24 24" class="info-icon">-->
                      <!--                          <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>-->
                      <!--                        </svg>-->
                      <!--                        <p>Audio files are processed on the server and automatically deleted after download to keep storage clean.</p>-->
                      <!--                      </div>-->
                    </div>
                  </div>

                </div>


              </div>
            </div>
          </div>
        </div>

        <!-- Progress Section -->
        <div
          class="progress-section"
          v-show="showProgress"
        >
          <div class="card">
            <h3 class="section-title">Download Progress</h3>

            <div class="progress-container">
              <div class="progress-bar-wrapper">
                <div
                  class="progress-bar"
                  :style="{ width: progressData.progress || '0%' }"
                  :class="progressBarClass"
                >
                  <span class="progress-text">{{ progressData.progress_text || '0%' }}</span>
                </div>
              </div>
              <div class="progress-info">{{ extraInfo }}</div>

              <!-- Detailed Progress Info -->
              <div v-if="progressData.status === 'downloading'" class="detailed-progress">
                <div class="progress-stats">
                  <div class="stat-item" v-if="progressData.downloaded">
                    <span class="stat-label">Downloaded:</span>
                    <span class="stat-value">{{ progressData.downloaded }}</span>
                  </div>
                  <div class="stat-item" v-if="progressData.total && progressData.total !== 'Unknown'">
                    <span class="stat-label">Total Size:</span>
                    <span class="stat-value">{{ progressData.total }}</span>
                  </div>
                  <div class="stat-item" v-if="progressData.speed && progressData.speed !== '...'">
                    <span class="stat-label">Speed:</span>
                    <span class="stat-value">{{ progressData.speed }}</span>
                  </div>
                  <div class="stat-item" v-if="progressData.eta && progressData.eta !== '...'">
                    <span class="stat-label">ETA:</span>
                    <span class="stat-value">{{ progressData.eta }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="downloadError" class="action-buttons">
              <button @click="retryDownload" class="btn btn-primary">
                <svg viewBox="0 0 24 24">
                  <path fill="currentColor" d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
                </svg>
                Try Again
              </button>
              <button @click="reloadWithUrl" class="btn btn-secondary">
                <svg viewBox="0 0 24 24">
                  <path fill="currentColor" d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
                </svg>
                Reload & Keep URL
              </button>
            </div>

            <div v-if="downloadComplete" class="action-buttons">
              <button @click="reloadPage" class="btn btn-secondary">
                <svg viewBox="0 0 24 24">
                  <path fill="currentColor" d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
                </svg>
                Reload Page
              </button>
              <button @click="downloadAnother" class="btn btn-primary">
                <svg viewBox="0 0 24 24">
                  <path fill="currentColor" d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
                </svg>
                Download Another Video
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="footer">
      <div class="footer-content">
        <div class="footer-links">
          <a href="#" class="footer-link">Privacy Policy</a>
          <a href="#" class="footer-link">Terms of Service</a>
          <a href="#" class="footer-link">Support</a>
        </div>
        <div class="copyright">
          <p>&copy; 2025 <strong>www.getstube.com</strong> - All rights reserved</p>
          <p class="disclaimer">For personal use only. Please respect YouTube's terms of service.</p>
        </div>
      </div>
    </footer>
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
      showDescription: false,
      downloadError: false,
      downloadComplete: false,
      currentDownloadId: null,
      selectedFormat: 'video',
      selectedQuality: 'best',
      selectedAudioQuality: 'high',
      availableQualities: [
        { value: 'best', label: 'Best Quality', description: 'Highest available quality' },
        { value: '1080', label: '1080p HD', description: 'Full HD (1920x1080)' },
        { value: '720', label: '720p HD', description: 'HD Ready (1280x720)' },
        { value: '480', label: '480p', description: 'Standard Definition' },
        { value: '360', label: '360p', description: 'Low Quality (smaller file)' },
        // { value: '240', label: '240p', description: 'Very Low Quality' }
      ],
      audioQualities: [
        { value: 'high', label: '320 kbps', description: 'High Quality MP3' },
        { value: 'medium', label: '192 kbps', description: 'Medium Quality MP3' },
        { value: 'low', label: '128 kbps', description: 'Standard Quality MP3' }
      ],
      systemInfo: null,
      ffmpegAvailable: true,
      showFFmpegGuide: false,
      showAudioOptions: false,
      showVideoOptions: false
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
    this.checkSystemInfo();
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
    clearUrl() {
      this.url = '';
      this.resetStates();
      this.resetProgressState();
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
        formData.append("format", this.selectedFormat);

        if (this.selectedFormat === 'video') {
          formData.append("quality", this.selectedQuality);
        } else {
          formData.append("audio_quality", this.selectedAudioQuality);
        }

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
          console.log(`Progress poll ${attempts}/${maxAttempts}:`, data);
          console.log(`Status: ${data.status}, Progress: ${data.progress_text}`);

          if (data.error) {
            this.showDownloadError(`Download failed: ${data.error}`);
            return;
          }

          this.progressData = data;
          this.updateExtraInfo(data);

          if (data.status === "finished" && data.download_ready && data.filename) {
            this.progressData.progress = "100%";
            this.progressData.progress_text = "Download Complete";
            this.extraInfo = "File ready for download...";

            // Automatically start the download
            this.downloadFile(downloadId, data.filename);
            return;
          }

          // Continue polling with faster updates during active processing
          if (attempts < maxAttempts) {
            const activeStatuses = ['downloading', 'processing', 'starting'];
            const pollInterval = activeStatuses.includes(data.status) ? 500 : 1000; // 500ms during active processing, 1s otherwise
            setTimeout(poll, pollInterval);
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

      setTimeout(poll, 500); // Start polling faster
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

      this.progressData.progress_text = "Starting Download...";
      this.extraInfo = `Preparing: ${filename}`;

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
        this.progressData.progress_text = "Download Started";
        this.extraInfo = "File download initiated successfully!";
        this.downloadComplete = true;
      }, 2000);
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
    },
    getSelectedQualityLabel() {
      const quality = this.availableQualities.find(q => q.value === this.selectedQuality);
      return quality ? quality.label : 'Best Quality';
    },
    getSelectedAudioQualityLabel() {
      const quality = this.audioQualities.find(q => q.value === this.selectedAudioQuality);
      return quality ? quality.label : 'High Quality';
    },
    async checkSystemInfo() {
      try {
        const response = await fetch('/system-info');
        if (response.ok) {
          this.systemInfo = await response.json();
          this.ffmpegAvailable = this.systemInfo.ffmpeg_available;

          if (!this.ffmpegAvailable) {
            console.warn('FFmpeg not available - audio downloads will show warning');
          }
        }
      } catch (error) {
        console.error('Failed to check system info:', error);
        // Assume audio is not available on error
        this.ffmpegAvailable = false;
      }
    }
  }
}
</script>
