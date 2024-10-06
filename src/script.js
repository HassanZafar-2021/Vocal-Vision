// Selectors for input elements
const maleAvatarUpload = document.querySelector('#maleAvatar');
const maleAvatarPreview = document.createElement('img'); // Create a preview element for male avatar
maleAvatarPreview.id = 'malePreview'; // Assign ID for the preview
document.body.appendChild(maleAvatarPreview); // Append to body or a specific section

const femaleAvatarUpload = document.querySelector('#femaleAvatar');
const femaleAvatarPreview = document.createElement('img'); // Create a preview element for female avatar
femaleAvatarPreview.id = 'femalePreview'; // Assign ID for the preview
document.body.appendChild(femaleAvatarPreview); // Append to body or a specific section

const audioUpload = document.querySelector('#audioUpload');
const audioPreview = document.createElement('audio'); // Create an audio preview element
audioPreview.controls = true; // Add controls for the audio player
audioPreview.id = 'audioPreview'; // Assign ID for the preview
document.body.appendChild(audioPreview); // Append to body or a specific section

// Function to handle image uploads
function handleImageUpload(uploadElement, previewElement) {
    uploadElement.addEventListener("change", (evt) => {
        const file = evt.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                previewElement.src = e.target.result; // Set preview image source
                previewElement.style.display = 'block'; // Show the image
                previewElement.style.width = '100px'; // Set a fixed width for the preview
                previewElement.style.height = '100px'; // Set a fixed height for the preview
                previewElement.alt = "Avatar Preview"; // Add alt text for accessibility
            };
            reader.readAsDataURL(file); // Read the uploaded file as a data URL
        }
    });
}

// Function to handle audio uploads
function handleAudioUpload(uploadElement, previewElement) {
    uploadElement.addEventListener("change", (evt) => {
        const file = evt.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                previewElement.src = e.target.result; // Set preview audio source
                previewElement.style.display = 'block'; // Show the audio element
            };
            reader.readAsDataURL(file); // Read the uploaded file as a data URL
        }
    });
}

// Initialize image uploads
handleImageUpload(maleAvatarUpload, maleAvatarPreview);
handleImageUpload(femaleAvatarUpload, femaleAvatarPreview);

// Initialize audio upload
handleAudioUpload(audioUpload, audioPreview);

// Function to generate a random color for the banner
function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

// Get the title element and banner
const title = document.getElementById('title');
const banner = document.querySelector('.banner');

// Add mouseover event to change the banner color
title.addEventListener('mouseover', function() {
    // Change the banner color
    banner.style.backgroundColor = getRandomColor();
});
