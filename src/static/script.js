document.addEventListener('DOMContentLoaded', function() {
    const generateBtn = document.getElementById('generate-btn');
    const statusDiv = document.getElementById('status');
    const imagesContainer = document.getElementById('images-container');
    const modal = document.getElementById('image-modal');
    const modalImg = document.getElementById('modal-image');
    const modalDetails = document.getElementById('modal-details');
    const closeBtn = document.getElementsByClassName('close')[0];
    const refreshLogsBtn = document.getElementById('refresh-logs');
    const logLevelFilter = document.getElementById('log-level-filter');
    const logDaysFilter = document.getElementById('log-days-filter');
    const logsContainer = document.getElementById('logs-container');
    
    // Load images on page load
    loadImages();
    
    // Generate new art
    generateBtn.addEventListener('click', function() {
        statusDiv.textContent = 'Generating art...';
        statusDiv.className = 'status loading';
        generateBtn.disabled = true;
        
        // Add loading animation to button
        generateBtn.innerHTML = '<span class="spinner"></span> Generating...';
        
        fetch('/trigger-generation', {
            method: 'POST'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            statusDiv.textContent = data.message;
            statusDiv.className = 'status success';
            
            // Start polling for new images
            let pollCount = 0;
            const maxPolls = 12; // Poll for up to 60 seconds (12 * 5s)
            
            const pollForNewImages = function() {
                if (pollCount >= maxPolls) {
                    // Stop polling after max attempts
                    generateBtn.innerHTML = 'Generate New Art';
                    generateBtn.disabled = false;
                    return;
                }
                
                fetch('/images?limit=1')
                .then(response => response.json())
                .then(data => {
                    if (data.length > 0) {
                        // Check if this is a new image by comparing with the first image in our current view
                        const currentFirstImage = document.querySelector('.image-card');
                        const currentFirstImageId = currentFirstImage ? currentFirstImage.dataset.id : null;
                        
                        if (!currentFirstImageId || data[0].id !== currentFirstImageId) {
                            // New image found, reload the gallery
                            loadImages();
                            generateBtn.innerHTML = 'Generate New Art';
                            generateBtn.disabled = false;
                            statusDiv.textContent = 'New artwork generated successfully!';
                            return;
                        }
                    }
                    
                    // No new image yet, continue polling
                    pollCount++;
                    setTimeout(pollForNewImages, 5000);
                })
                .catch(error => {
                    console.error('Error polling for new images:', error);
                    pollCount++;
                    setTimeout(pollForNewImages, 5000);
                });
            };
            
            // Start polling after a short delay
            setTimeout(pollForNewImages, 5000);
        })
        .catch(error => {
            statusDiv.textContent = 'Error: ' + error.message;
            statusDiv.className = 'status error';
            generateBtn.innerHTML = 'Generate New Art';
            generateBtn.disabled = false;
        });
    });
    
    // Load images from API
    function loadImages() {
        statusDiv.textContent = 'Loading images...';
        statusDiv.className = 'status loading';
        
        fetch('/images?limit=20')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            imagesContainer.innerHTML = '';
            
            if (data.length === 0) {
                // Show empty state
                imagesContainer.innerHTML = `
                    <div class="empty-state">
                        <p>No images found. Generate some art!</p>
                        <button class="btn primary" onclick="document.getElementById('generate-btn').click()">Create First Artwork</button>
                    </div>
                `;
                statusDiv.textContent = 'No images found';
                statusDiv.className = 'status';
                return;
            }
            
            // Create a document fragment for better performance
            const fragment = document.createDocumentFragment();
            
            data.forEach(image => {
                const card = document.createElement('div');
                card.className = 'image-card';
                card.dataset.id = image.id; // Store the image ID for comparison
                
                // Create image wrapper for hover effects
                const imgWrapper = document.createElement('div');
                imgWrapper.className = 'image-wrapper';
                
                const img = document.createElement('img');
                img.src = `/proxy-image/${image.id}`;
                img.alt = 'Generated art';
                
                // Add loading state and fade-in effect
                img.className = 'loading';
                img.onload = function() {
                    this.classList.remove('loading');
                    this.classList.add('loaded');
                };
                
                const prompt = document.createElement('p');
                prompt.className = 'prompt';
                prompt.textContent = image.prompts.text.substring(0, 100) + (image.prompts.text.length > 100 ? '...' : '');
                
                const date = document.createElement('p');
                date.className = 'date';
                date.textContent = formatDate(new Date(image.created_at));
                
                imgWrapper.appendChild(img);
                card.appendChild(imgWrapper);
                card.appendChild(prompt);
                card.appendChild(date);
                
                card.addEventListener('click', function() {
                    openModal(image);
                });
                
                fragment.appendChild(card);
            });
            
            imagesContainer.appendChild(fragment);
            
            statusDiv.textContent = `Loaded ${data.length} images`;
            statusDiv.className = 'status success';
            
            // Add fade-in animation to cards
            setTimeout(() => {
                document.querySelectorAll('.image-card').forEach((card, index) => {
                    setTimeout(() => {
                        card.classList.add('visible');
                    }, index * 50);
                });
            }, 100);
        })
        .catch(error => {
            console.error('Error loading images:', error);
            statusDiv.textContent = 'Error loading images: ' + error.message;
            statusDiv.className = 'status error';
            
            // Show error state
            imagesContainer.innerHTML = `
                <div class="empty-state">
                    <p>Failed to load images. Please try again.</p>
                    <button class="btn primary" onclick="location.reload()">Reload Page</button>
                </div>
            `;
        });
    }
    
    // Format date in a more readable way
    function formatDate(date) {
        const now = new Date();
        const diff = now - date;
        
        // Less than a day
        if (diff < 24 * 60 * 60 * 1000) {
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ' today';
        }
        
        // Less than a week
        if (diff < 7 * 24 * 60 * 60 * 1000) {
            const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
            return days[date.getDay()] + ' at ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
        
        // Otherwise, show full date
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    // Open modal with image details
    function openModal(image) {
        // Set loading state
        modalImg.src = '';
        modalImg.classList.add('loading');
        modalDetails.innerHTML = '<div class="loading-spinner"></div>';
        
        // Show modal immediately
        modal.style.display = 'block';
        
        // Set image source (will load in background)
        modalImg.src = `/proxy-image/${image.id}`;
        
        // When image loads, remove loading state
        modalImg.onload = function() {
            modalImg.classList.remove('loading');
        };
        
        // Format the settings for better readability
        let formattedSettings = '';
        if (image.settings) {
            const settings = image.settings;
            formattedSettings = `
                <ul class="settings-list">
                    <li><span>Model:</span> ${settings.model || 'dall-e-3'}</li>
                    <li><span>Size:</span> ${settings.size || '1024x1024'}</li>
                    <li><span>Quality:</span> ${settings.quality || 'standard'}</li>
                </ul>
            `;
        }
        
        // Format the date
        const generatedDate = new Date(image.created_at);
        const formattedDate = generatedDate.toLocaleDateString() + ' at ' + 
                             generatedDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        // Update modal details
        modalDetails.innerHTML = `
            <h3>Image Details</h3>
            <div class="detail-section">
                <h4>Prompt</h4>
                <p class="prompt-text">${image.prompts.text}</p>
            </div>
            <div class="detail-section">
                <h4>Generation Details</h4>
                <p><strong>Generated:</strong> ${formattedDate}</p>
                <p><strong>Settings:</strong></p>
                ${formattedSettings}
            </div>
            <div class="detail-actions">
                <a href="/proxy-image/${image.id}" target="_blank" class="btn secondary">Open Image in New Tab</a>
            </div>
        `;
    }
    
    // Close modal
    closeBtn.addEventListener('click', function() {
        modal.style.display = 'none';
    });
    
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    // Load logs from API
    function loadLogs() {
        if (!logsContainer) return;
        
        const level = logLevelFilter ? logLevelFilter.value : '';
        const days = logDaysFilter ? logDaysFilter.value : '7';
        
        logsContainer.innerHTML = '<div class="loading-spinner"></div>';
        
        fetch(`/logs?limit=100&days=${days}${level ? '&level=' + level : ''}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(logs => {
            if (logs.length === 0) {
                logsContainer.innerHTML = '<p class="empty-message">No logs found for the selected criteria.</p>';
                return;
            }
            
            // Create a document fragment for better performance
            const fragment = document.createDocumentFragment();
            
            logs.forEach(log => {
                const logEntry = document.createElement('div');
                logEntry.className = `log-entry log-level-${log.level.toLowerCase()}`;
                
                const logDate = new Date(log.created_at);
                const formattedDate = logDate.toLocaleDateString() + ' ' + 
                                     logDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
                
                const logHeader = document.createElement('div');
                logHeader.className = 'log-header';
                logHeader.innerHTML = `
                    <span class="log-level">${log.level}</span>
                    <span class="log-source">${log.source}</span>
                    <span class="log-date">${formattedDate}</span>
                `;
                
                const logMessage = document.createElement('div');
                logMessage.className = 'log-message';
                logMessage.textContent = log.message;
                
                logEntry.appendChild(logHeader);
                logEntry.appendChild(logMessage);
                
                // Add metadata if present
                if (log.metadata && Object.keys(log.metadata).length > 0) {
                    const metadataStr = JSON.stringify(log.metadata, null, 2);
                    if (metadataStr !== '{}') {
                        const logMetadata = document.createElement('pre');
                        logMetadata.className = 'log-metadata';
                        logMetadata.textContent = metadataStr;
                        logEntry.appendChild(logMetadata);
                    }
                }
                
                fragment.appendChild(logEntry);
            });
            
            logsContainer.innerHTML = '';
            logsContainer.appendChild(fragment);
        })
        .catch(error => {
            console.error('Error loading logs:', error);
            logsContainer.innerHTML = `<p class="error-message">Error loading logs: ${error.message}</p>`;
        });
    }
    
    // Add event listeners for log controls
    if (refreshLogsBtn) {
        refreshLogsBtn.addEventListener('click', loadLogs);
    }
    
    if (logLevelFilter) {
        logLevelFilter.addEventListener('change', loadLogs);
    }
    
    if (logDaysFilter) {
        logDaysFilter.addEventListener('change', loadLogs);
    }
    
    // Load logs on page load
    if (logsContainer) {
        loadLogs();
    }
});
