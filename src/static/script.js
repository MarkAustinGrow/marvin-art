document.addEventListener('DOMContentLoaded', function() {
    const generateBtn = document.getElementById('generate-btn');
    const statusDiv = document.getElementById('status');
    const imagesContainer = document.getElementById('images-container');
    const modal = document.getElementById('image-modal');
    const modalImg = document.getElementById('modal-image');
    const modalDetails = document.getElementById('modal-details');
    const closeBtn = document.getElementsByClassName('close')[0];
    
    // Load images on page load
    loadImages();
    
    // Generate new art
    generateBtn.addEventListener('click', function() {
        statusDiv.textContent = 'Generating art...';
        generateBtn.disabled = true;
        
        fetch('/trigger-generation', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            statusDiv.textContent = data.message;
            setTimeout(() => {
                loadImages();
                generateBtn.disabled = false;
            }, 5000); // Wait 5 seconds before refreshing
        })
        .catch(error => {
            statusDiv.textContent = 'Error: ' + error;
            generateBtn.disabled = false;
        });
    });
    
    // Load images from API
    function loadImages() {
        statusDiv.textContent = 'Loading images...';
        
        fetch('/images?limit=20')
        .then(response => response.json())
        .then(data => {
            imagesContainer.innerHTML = '';
            
            if (data.length === 0) {
                statusDiv.textContent = 'No images found. Generate some art!';
                return;
            }
            
            data.forEach(image => {
                const card = document.createElement('div');
                card.className = 'image-card';
                
                const img = document.createElement('img');
                img.src = image.image_url;
                img.alt = 'Generated art';
                
                const prompt = document.createElement('p');
                prompt.className = 'prompt';
                prompt.textContent = image.prompts.text.substring(0, 100) + '...';
                
                const date = document.createElement('p');
                date.className = 'date';
                date.textContent = new Date(image.created_at).toLocaleString();
                
                card.appendChild(img);
                card.appendChild(prompt);
                card.appendChild(date);
                
                card.addEventListener('click', function() {
                    openModal(image);
                });
                
                imagesContainer.appendChild(card);
            });
            
            statusDiv.textContent = `Loaded ${data.length} images`;
        })
        .catch(error => {
            statusDiv.textContent = 'Error loading images: ' + error;
        });
    }
    
    // Open modal with image details
    function openModal(image) {
        modalImg.src = image.image_url;
        
        modalDetails.innerHTML = `
            <h3>Image Details</h3>
            <p><strong>Prompt:</strong> ${image.prompts.text}</p>
            <p><strong>Generated:</strong> ${new Date(image.created_at).toLocaleString()}</p>
            <p><strong>Settings:</strong> ${JSON.stringify(image.settings)}</p>
        `;
        
        modal.style.display = 'block';
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
});
