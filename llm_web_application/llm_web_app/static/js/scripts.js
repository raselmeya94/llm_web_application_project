

// // Own file handler
// document.addEventListener('DOMContentLoaded', () => {
//     const uploadArea = document.getElementById('upload-area');
//     const uploadText = document.getElementById('upload-file-name');
//     const resultsArea = document.querySelector('.summary');
//     const loader = document.getElementById('loader');

//     // Handle file selection via click
//     uploadArea.addEventListener('click', async () => {
//         handleFileSelection();
//     });

//     // Handle file selection via drag-and-drop
//     uploadArea.addEventListener('dragover', (event) => {
//         event.preventDefault();
//         uploadArea.classList.add('dragging'); // Optional: Add some visual indication
//     });

//     uploadArea.addEventListener('dragleave', () => {
//         uploadArea.classList.remove('dragging'); // Optional: Remove visual indication
//     });

//     uploadArea.addEventListener('drop', async (event) => {
//         event.preventDefault();
//         uploadArea.classList.remove('dragging'); // Optional: Remove visual indication
//         const file = event.dataTransfer.files[0];
//         // await processFiles(files);
//         if (file) {
//             await processFile(file);
//         }
//     }); 
//     async function handleFileSelection() {

//         // loader.style.display = 'block';
//         // document.querySelector('.loader-text').textContent = 'Uploading...';

//         try {
//             const files = await window.showOpenFilePicker({
//                 multiple: false,
//                 types: [
//                     {
//                         description: 'Documents',
//                         accept: {
//                             'application/pdf': ['.pdf'],
//                             'text/plain': ['.txt'],
//                             'application/msword': ['.doc', '.docx'],
//                             'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
//                         }
//                     }
//                 ]
//             });

//             const selectedFiles = await Promise.all(files.map(fileHandle => fileHandle.getFile()));
//             await processFile(selectedFiles);
//         } catch (error) {
//             console.error('File selection was canceled or failed', error);
//         }
//     }

    
//     async function processFile(selectedFiles) {

//         uploadText.innerHTML = Array.from(selectedFiles).map(file => file.name).join('<br>'); // Display file names

//         const formData = new FormData();
//         Array.from(selectedFiles).forEach(file => formData.append('files', file));
//         // Show the loader and set initial text to "Uploading..."
//         // loader.style.display = 'block';
//         // document.querySelector('.loader-text').textContent = 'Uploading...'; 

//         // Change loader text to "Processing..."
//         // document.querySelector('.loader-text').textContent = 'Processing...';

//         const response = await fetch('/own_upload_file/', {
//             method: 'POST',
//             body: formData,
//             headers: {
//                 'X-CSRFToken': '{{ csrf_token }}'  // Ensure CSRF protection if needed
//             }
//         });

        
//         // response
//         if (response.ok) {
//             const data = await response.json();
//             resultsArea.innerHTML = `
//                 <h3>File Name: ${data.filename}</h3>
//                 <div class="analysis-results">
//                     ${data.summary_of_own_file.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
//                                          .replace(/## (.*?)\n/g, '<h4>$1</h4>')
//                                          .replace(/\* (.*?)\n/g, '<li>$1</li>')
//                                          .replace(/\n/g, '<br>')}
//                 </div>
//             `;
//         } else {
//             console.error('Failed to upload files');
//         }
        
//             // Hide the loader after the upload is done
//             // loader.style.display = 'none';
        
//     }
// });

// Sep 1 
document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('upload-area');
    const uploadText = document.getElementById('upload-file-name');
    const resultsArea = document.querySelector('.summary');
    const loader = document.getElementById('loader');

    // Helper function to display selected files
    function displaySelectedFiles(files) {
        uploadText.innerHTML = Array.from(files).map(file => file.name).join('<br>');
    }

    // Helper function to handle drag-and-drop events
    function handleDragEvents(event, action) {
        event.preventDefault();
        if (action === 'over') {
            uploadArea.classList.add('dragging');
        } else {
            uploadArea.classList.remove('dragging');
        }
    }

    // Fallback file input for browsers that don't support showOpenFilePicker
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.style.display = 'none';
    document.body.appendChild(fileInput);

    // Event listeners for drag-and-drop
    uploadArea.addEventListener('dragover', (event) => handleDragEvents(event, 'over'));
    uploadArea.addEventListener('dragleave', (event) => handleDragEvents(event, 'leave'));
    uploadArea.addEventListener('drop', async (event) => {
        handleDragEvents(event, 'leave');
        const files = event.dataTransfer.files;
        if (files.length > 0) {
            await processFiles(files);
        }
    });

    // Handle file selection via click
    uploadArea.addEventListener('click', async () => {
        if (window.showOpenFilePicker) {
            await handleFileSelection();
        } else {
            fileInput.click();
        }
    });

    // Handle file selection via input file element
    fileInput.addEventListener('change', async (event) => {
        const files = event.target.files;
        if (files.length > 0) {
            await processFiles(files);
        }
    });

    // Handle file selection using showOpenFilePicker
    async function handleFileSelection() {
        try {
            const fileHandles = await window.showOpenFilePicker({
                multiple: false,
                types: [
                    {
                        description: 'Documents',
                        accept: {
                            'application/pdf': ['.pdf'],
                            'text/plain': ['.txt'],
                            'application/msword': ['.doc', '.docx'],
                            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
                        }
                    }
                ]
            });
            const files = await Promise.all(fileHandles.map(fileHandle => fileHandle.getFile()));
            await processFiles(files);
        } catch (error) {
            console.error('File selection was canceled or failed', error);
        }
    }

    // Process selected files and send to the server
    async function processFiles(files) {
        displaySelectedFiles(files);

        const formData = new FormData();
        Array.from(files).forEach(file => formData.append('files', file));

        try {
            loader.style.display = 'block';  // Show loader
            const response = await fetch('/own_upload_file/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}'  // Ensure CSRF protection if needed
                }
            });

            if (response.ok) {
                const data = await response.json();
                displayResults(data);
            } else {
                console.error('Failed to upload files');
                resultsArea.innerHTML = '<p>Failed to upload files.</p>';
            }
        } catch (error) {
            console.error('Error during file upload:', error);
            resultsArea.innerHTML = '<p>Error occurred during file upload.</p>';
        } finally {
            loader.style.display = 'none';  // Hide loader
        }
    }

    // Display results after file upload and processing
    function displayResults(data) {
        resultsArea.innerHTML = `
            <h3>File Name: ${data.filename}</h3>
            <div class="analysis-results">
                ${data.summary_of_own_file.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                          .replace(/## (.*?)\n/g, '<h4>$1</h4>')
                                          .replace(/\ (.?)\n/g, '<li>$1</li>')
                                          .replace(/\n/g, '<br>')}
            </div>
        `;
    }
});


// others files handler

document.addEventListener('DOMContentLoaded', () => {
    const DocumentUploadArea = document.getElementById('document-upload');
    const ArticlesUploadArea = document.getElementById('news-upload');
    const linkInput = document.getElementById('news-link');
    const DocumentResultsArea = document.getElementById('results-area');
    const KEC = document.getElementById('KEC');

    DocumentUploadArea.addEventListener('change', async (event) => {
        const files = event.target.files;
        console.log("Selected file:", files[0]);

        if (files.length > 0) {
            const formData = new FormData();
            formData.append('file', files[0]);
            console.log("form Data::", formData);
            DocumentResultsArea.innerHTML = '<p>Uploading...</p>';
            KEC.innerHTML = '<p>Processing...</p>';
            try {
                const response = await fetch('/other_upload_file/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCSRFToken()  // Ensure this function is correct
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    console.log("Data::", data);
                    DocumentResultsArea.innerHTML = `
                        <div class="analysis-results">
                            ${data.comparative_summary_of_files.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                                .replace(/## (.*?)\n/g, '<h4>$1</h4>')
                                                .replace(/\* (.*?)\n/g, '<li>$1</li>')
                                                .replace(/\n/g, '<br>')}
                        </div>
                    `;
                    KEC.innerHTML = `
                    <h3>File Name: ${data.filename}</h3>
                    <div class="analysis-results">
                        ${data.summary_of_other_file.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                            .replace(/## (.*?)\n/g, '<h4>$1</h4>')
                                            .replace(/\* (.*?)\n/g, '<li>$1</li>')
                                            .replace(/\n/g, '<br>')}
                    </div>
                `;
                } else {
                    console.error('Failed to upload files');
                    DocumentResultsArea.innerHTML = '<p>Failed to upload files.</p>';
                }
            } catch (error) {
                console.error('Error:', error);
                DocumentResultsArea.innerHTML = '<p>Error occurred during file upload.</p>';
            }
        } else {
            DocumentResultsArea.innerHTML = '<p>No files selected.</p>';
        }
    });

    ArticlesUploadArea.addEventListener('change', async (event) => {
        const files = event.target.files;
        console.log("Selected file:", files[0]);

        if (files.length > 0) {
            const formData = new FormData();
            formData.append('file', files[0]);
            console.log("form Data::", formData);
            DocumentResultsArea.innerHTML = '<p>Uploading...</p>';
            KEC.innerHTML = '<p>Processing...</p>';

            try {
                const response = await fetch('/other_upload_file/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCSRFToken()  // Ensure this function is correct
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    console.log("Data::", data);
                    DocumentResultsArea.innerHTML = `
                        <div class="analysis-results">
                            ${data.comparative_summary_of_files.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                                .replace(/## (.*?)\n/g, '<h4>$1</h4>')
                                                .replace(/\* (.*?)\n/g, '<li>$1</li>')
                                                .replace(/\n/g, '<br>')}
                        </div>
                    `;
                    KEC.innerHTML = `
                    <h3>File Name: ${data.filename}</h3>
                        <div class="analysis-results">
                            ${data.summary_of_other_file.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                                .replace(/## (.*?)\n/g, '<h4>$1</h4>')
                                                .replace(/\* (.*?)\n/g, '<li>$1</li>')
                                                .replace(/\n/g, '<br>')}
                        </div>
                    `;
                } else {
                    console.error('Failed to upload files');
                    DocumentResultsArea.innerHTML = '<p>Failed to upload files.</p>';
                }
            } catch (error) {
                console.error('Error:', error);
                DocumentResultsArea.innerHTML = '<p>Error occurred during file upload.</p>';
            }
        } else {
            DocumentResultsArea.innerHTML = '<p>No files selected.</p>';
        }
    });

    document.getElementById('submit-btn').addEventListener('click', async () => {
        const linkInput = document.getElementById('news-link');
        const link = linkInput.value;
        const DocumentResultsArea = document.getElementById('results-area');
        const KEC = document.getElementById('KEC');
        
        console.log("Link:", link);

        if (link) {
            DocumentResultsArea.innerHTML = '<p>Uploading...</p>';
        }
    
        try {
            const response = await fetch('/submit-link/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken() 
                },
                body: JSON.stringify({ link })
            });
    
            if (response.ok) {
                const data = await response.json();
                console.log("Data:", data);
    
                DocumentResultsArea.innerHTML = `
                    <div class="analysis-results">
                        ${data.comparative_summary_of_files.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        .replace(/## (.*?)\n/g, '<h4>$1</h4>')
                        .replace(/\* (.*?)\n/g, '<li>$1</li>')
                        .replace(/\n/g, '<br>')}
                    </div>
                `;
                KEC.innerHTML = `
                    <h3>File Name: ${data.filename}</h3>
                    <div class="analysis-results">
                        ${data.summary_of_link.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                            .replace(/## (.*?)\n/g, '<h4>$1</h4>')
                            .replace(/\* (.*?)\n/g, '<li>$1</li>')
                            .replace(/\n/g, '<br>')}
                    </div>
                `;
            } else {
                console.error('Failed to submit link');
                DocumentResultsArea.innerHTML = '<p>Failed to submit link.</p>';
            }
        } catch (error) {
            console.error('Error:', error);
            DocumentResultsArea.innerHTML = '<p>Error occurred during link submission.</p>';
        }
    });


    function getCSRFToken() {
        const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        return tokenElement ? tokenElement.value : '';
    }
});
