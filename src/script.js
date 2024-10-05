const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileButton = document.getElementById('fileButton');
const errorMessage = document.getElementById('error-message');

// Show file explorer when button is clicked
fileButton.addEventListener('click', () => {
  fileInput.click();
});

// Handle drag and drop functionality
dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.style.borderColor = 'green';
});

dropZone.addEventListener('dragleave', () => {
  dropZone.style.borderColor = 'grey';
});

dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  handleFiles(e.dataTransfer.files);
  dropZone.style.borderColor = 'grey';
});

// Handle file input via button
fileInput.addEventListener('change', () => {
  handleFiles(fileInput.files);
});

// Function to handle file validation
function handleFiles(files) {
  const file = files[0];
  if (file && file.type.startsWith('audio/')) {
    errorMessage.style.display = 'none';
    alert(`Audio file "${file.name}" selected successfully!`);
  } else {
    errorMessage.style.display = 'block';
    errorMessage.textContent = 'Please select a valid audio file.';
  }
}
