document.getElementById("video-info-form").addEventListener("submit", function(e) {
    e.preventDefault();
    getVideoInfo();
});

// Add automatic detection when URL is pasted
document.querySelector('input[name="url"]').addEventListener('input', function(e) {
    const url = e.target.value.trim();
    if (url && isValidYouTubeUrl(url)) {
        // Clear any existing timeout
        if (window.urlTimeout) {
            clearTimeout(window.urlTimeout);
        }
        
        // Set a timeout to get video info after user stops typing
        window.urlTimeout = setTimeout(() => {
            getVideoInfo();
        }, 1000); // Wait 1 second after user stops typing
    }
});

function isValidYouTubeUrl(url) {
    // More specific YouTube URL validation
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)[a-zA-Z0-9_-]{11}/;
    return youtubeRegex.test(url);
}

function showError(message) {
    const videoInfoSection = document.getElementById("video-info");
    videoInfoSection.classList.remove("loading", "show");
    videoInfoSection.classList.add("show", "error");
    videoInfoSection.innerHTML = `
        <div class="error">
            ${message}
        </div>
    `;
}

function getVideoInfo() {
    const urlInput = document.querySelector('input[name="url"]');
    const url = urlInput.value.trim();
    
    if (!url) {
        showError("Please enter a YouTube URL");
        return;
    }
    
    if (!isValidYouTubeUrl(url)) {
        showError("Please enter a valid YouTube URL. Only YouTube videos are supported.");
        return;
    }

    const submitButton = document.querySelector('#video-info-form button[type="submit"]');
    const originalText = submitButton.textContent;
    const videoInfoSection = document.getElementById("video-info");
    
    // Disable button and show loading state
    submitButton.disabled = true;
    submitButton.textContent = "Getting Video Info...";
    
    // Show video info section with loading state
    videoInfoSection.classList.add("show", "loading");
    videoInfoSection.innerHTML = `
        <div class="loading">
            <div class="loading-spinner"></div>
            Getting video information...
        </div>
    `;
    
    // Hide progress section if it was showing
    const progressSection = document.getElementById("progress-section");
    progressSection.classList.remove("show");

    const formData = new FormData();
    formData.append("url", url);

    fetch("/get-video-info", {
        method: "POST",
        body: formData
    })
    .then(res => {
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
    })
    .then(data => {
        const infoId = data.info_id;
        pollVideoInfo(infoId);
    })
    .catch(error => {
        console.error('Error:', error);
        videoInfoSection.classList.remove("loading");
        videoInfoSection.classList.add("error");
        videoInfoSection.innerHTML = `
            <div class="error">
                Failed to get video information. Please try again.
            </div>
        `;
    })
    .finally(() => {
        // Re-enable button
        submitButton.disabled = false;
        submitButton.textContent = originalText;
    });
}

function pollVideoInfo(info_id) {
    const interval = setInterval(() => {
        fetch(`/video-info/${info_id}`)
            .then(res => {
                if (!res.ok) {
                    throw new Error(`HTTP error! status: ${res.status}`);
                }
                return res.json();
            })
            .then(data => {
                if (data.error) {
                    const videoInfoSection = document.getElementById("video-info");
                    videoInfoSection.classList.remove("loading");
                    videoInfoSection.classList.add("error");
                    videoInfoSection.innerHTML = `
                        <div class="error">
                            Error: ${data.error}
                        </div>
                    `;
                    clearInterval(interval);
                    return;
                }

                if (data.status === "ready") {
                    clearInterval(interval);
                    displayVideoInfo(data, info_id);
                }
            })
            .catch(error => {
                console.error('Error polling video info:', error);
                const videoInfoSection = document.getElementById("video-info");
                videoInfoSection.classList.remove("loading");
                videoInfoSection.classList.add("error");
                videoInfoSection.innerHTML = `
                    <div class="error">
                        Lost connection to server. Trying to reconnect...
                    </div>
                `;
            });
    }, 1000);
}

function displayVideoInfo(videoData, info_id) {
    const videoInfoSection = document.getElementById("video-info");
    videoInfoSection.classList.remove("loading", "error");
    
    const thumbnail = videoData.thumbnail || '';
    const title = videoData.title || 'Unknown Title';
    const duration = videoData.duration || 'Unknown';
    const uploader = videoData.uploader || 'Unknown';
    const viewCount = videoData.view_count || 'Unknown';
    const description = videoData.description || 'No description available';
    const formatInfo = videoData.format_info || '';
    const height = videoData.height || 0;
    
    videoInfoSection.innerHTML = `
        ${thumbnail ? `<img src="${thumbnail}" alt="Video thumbnail" class="video-thumbnail">` : ''}
        <div class="video-title">${title}</div>
        <div class="video-meta">
            <strong>Duration:</strong> ${duration} | 
            <strong>Uploader:</strong> ${uploader} | 
            <strong>Views:</strong> ${viewCount}
            ${height ? ` | <strong>Quality:</strong> ${height}p` : ''}
            ${formatInfo ? ` | <strong>Format:</strong> ${formatInfo}` : ''}
        </div>
        <div class="video-description">${description}</div>
        <button onclick="startDownload('${info_id}')" class="download-button">
            📥 Download Video
        </button>
    `;
}

function startDownload(info_id) {
    console.log('Starting download for info_id:', info_id); // Debug log
    
    const videoInfoSection = document.getElementById("video-info");
    const progressSection = document.getElementById("progress-section");
    
    // Show progress section and hide video info
    progressSection.classList.add("show");
    videoInfoSection.classList.remove("show");
    
    // Reset progress bar
    const progressBar = document.getElementById("progress-bar");
    progressBar.style.width = "0%";
    progressBar.style.backgroundColor = "";
    progressBar.className = "";
    progressBar.innerText = "0%";
    document.getElementById("extra-info").innerText = "";
    
    // Remove any existing download button
    const existingDownloadBtn = document.getElementById("download-btn");
    if (existingDownloadBtn) {
        existingDownloadBtn.remove();
    }

    const formData = new FormData();
    formData.append("info_id", info_id);

    fetch("/start-download", {
        method: "POST",
        body: formData
    })
    .then(res => {
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
    })
    .then(data => {
        console.log('Download response:', data); // Debug log
        const downloadId = data.download_id;
        pollProgress(downloadId);
    })
    .catch(error => {
        console.error('Error starting download:', error);
        progressBar.classList.add("error");
        progressBar.innerText = "Error";
        document.getElementById("extra-info").innerText = "Failed to start download. Please try again.";
    });
}

function pollProgress(download_id) {
    const interval = setInterval(() => {
        fetch(`/progress/${download_id}`)
            .then(res => {
                if (!res.ok) {
                    throw new Error(`HTTP error! status: ${res.status}`);
                }
                return res.json();
            })
            .then(data => {
                console.log('Progress data:', data); // Debug log
                
                if (data.error) {
                    document.getElementById("progress-bar").classList.add("error");
                    document.getElementById("progress-bar").innerText = "Error";
                    document.getElementById("extra-info").innerText = `Failed: ${data.error}`;
                    clearInterval(interval);
                    return;
                }

                const progress = data.progress || "0%";
                const progressText = data.progress_text || "0.0%";
                const eta = data.eta || "...";
                const speed = data.speed || "...";
                const filename = data.filename || "";
                const downloadReady = data.download_ready || false;
                const status = data.status || "";

                // Update progress bar width (CSS expects percentage)
                document.getElementById("progress-bar").style.width = progress;
                document.getElementById("progress-bar").innerText = progressText;

                // Update extra info
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
                document.getElementById("extra-info").innerText = extraInfo;

                if (status === "finished" && downloadReady && filename) {
                    clearInterval(interval);
                    document.getElementById("progress-bar").style.width = "100%";
                    document.getElementById("progress-bar").innerText = "Starting Download...";
                    document.getElementById("progress-bar").style.backgroundColor = "";
                    document.getElementById("progress-bar").className = "";
                    document.getElementById("extra-info").innerText = "Download will start automatically...";
                    
                    // Automatically start the download
                    downloadFile(download_id, filename);
                }
            })
            .catch(error => {
                console.error('Error polling progress:', error);
                document.getElementById("progress-bar").classList.add("warning");
                document.getElementById("progress-bar").innerText = "Connection Error";
                document.getElementById("extra-info").innerText = "Lost connection to server. Trying to reconnect...";
            });
    }, 1000);
}

function addReloadButtons() {
    // Remove any existing buttons
    const existingButtons = document.querySelectorAll("#reload-btn, #download-another-btn, .button-container");
    existingButtons.forEach(btn => btn.remove());
    
    // Create button container
    const buttonContainer = document.createElement("div");
    buttonContainer.className = "button-container";
    
    // Create reload button
    const reloadBtn = document.createElement("button");
    reloadBtn.id = "reload-btn";
    reloadBtn.textContent = "🔄 Reload Page";
    reloadBtn.className = "download-button";
    reloadBtn.onclick = () => window.location.reload();
    
    // Create download another button
    const downloadAnotherBtn = document.createElement("button");
    downloadAnotherBtn.id = "download-another-btn";
    downloadAnotherBtn.textContent = "📥 Download Another Video";
    downloadAnotherBtn.className = "download-button";
    downloadAnotherBtn.onclick = () => {
        // Clear the form and reset the page state
        document.querySelector('input[name="url"]').value = "";
        document.getElementById("video-info").classList.remove("show", "loading", "error");
        document.getElementById("progress-section").classList.remove("show");
        
        // Focus on the URL input
        document.querySelector('input[name="url"]').focus();
    };
    
    // Add buttons to container
    buttonContainer.appendChild(reloadBtn);
    buttonContainer.appendChild(downloadAnotherBtn);
    
    // Add container to the progress section
    const progressSection = document.getElementById("progress-section");
    progressSection.appendChild(buttonContainer);
}

function addDownloadButton(download_id, filename) {
    // Remove any existing download button
    const existingDownloadBtn = document.getElementById("download-btn");
    if (existingDownloadBtn) {
        existingDownloadBtn.remove();
    }
    
    // Create download button
    const downloadBtn = document.createElement("button");
    downloadBtn.id = "download-btn";
    downloadBtn.textContent = `📥 Download ${filename}`;
    downloadBtn.className = "download-button";
    downloadBtn.onclick = () => downloadFile(download_id, filename);
    
    // Add button to the progress section
    const progressSection = document.getElementById("progress-section");
    progressSection.appendChild(downloadBtn);
}

function downloadFile(download_id, filename) {
    console.log('Downloading file:', download_id, filename); // Debug log
    
    // Update progress bar to show download is starting
    const progressBar = document.getElementById("progress-bar");
    progressBar.innerText = "Download Started";
    document.getElementById("extra-info").innerText = `Downloading: ${filename}`;
    
    // Use the streaming download endpoint for direct browser download
    const link = document.createElement('a');
    link.href = `/stream-download/${download_id}`;
    link.download = filename;
    link.style.display = 'none';
    
    // Add to DOM, click, and remove
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Show completion message after a short delay
    setTimeout(() => {
        progressBar.innerText = "Download Complete";
        progressBar.style.backgroundColor = "#4CAF50";
        document.getElementById("extra-info").innerText = "File downloaded successfully!";
        
        // Add reload and download another buttons
        addReloadButtons();
    }, 1000);
}
