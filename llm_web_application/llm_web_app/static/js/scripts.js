

let newPolicyUploaded = false;
let existingPolicyUploaded = false;

// new policy file handling function and summary function
document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('upload-new_policy');
    const uploadText = document.getElementById('upload-file-name-new_policy');
    const summaryPreview = document.getElementById('summaryPreview');
    const toggleButton = document.getElementById('toggleButton');
    const modelSelect = document.getElementById('modelSelect');
    const loader = document.createElement('div'); // Create a loader element

    let uploadedFilename = '';        // Variable to store the uploaded file's name
    let uploadedFilePath = '';        // Variable to store the absolute file path
    let selectedModel = '';           // Variable to store the selected model

    // Hide the "Show Summary" button initially
    toggleButton.style.display = 'none'; 
    toggleButton.style.opacity = 0;
    toggleButton.style.transition = 'opacity 0.5s';

    // Disable the toggle button initially
    toggleButton.disabled = true;

    // Helper function to display selected files
    function displaySelectedFiles(files) {
        uploadText.innerHTML = Array.from(files)
            .map(file => `<strong>${file.name}</strong>`)
            .join('<br>');
    }

    // Handle model selection
    modelSelect.addEventListener('change', (event) => {
        selectedModel = event.target.value;
        // Enable the toggle button only if a model is selected and a file is uploaded
        if (selectedModel && uploadedFilename) {
            toggleButton.disabled = false;
            showToggleButton();
        } else {
            toggleButton.disabled = true;
            toggleButton.style.opacity = 0;
        }
    });

    // Fallback file input for browsers that don't support showOpenFilePicker
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.style.display = 'none';
    document.body.appendChild(fileInput);

    // Handle file selection via click
    uploadArea.addEventListener('click', async (event) => {
        if (event.target.id === 'toggleButton') {
            return;
        }
        fileInput.click();
    });

    // Handle file selection via input file element
    fileInput.addEventListener('change', async (event) => {
        const files = event.target.files;
        if (files.length > 0) {
            await new_policy_file_handle(files);
        }
    });

    // Handle selected files and send to the server
    async function new_policy_file_handle(files) {
        displaySelectedFiles(files);

        const formData = new FormData();
        Array.from(files).forEach(file => formData.append('files', file));

        try {
            const response = await fetch('/new_policy_file_upload/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}'
                }
            });

            console.log('Upload response status:', response.status);
            if (response.ok) {
                const data = await response.json();
                console.log('Upload response data:', data);
                if (data.filename) {
                    uploadedFilename = data.filename;
                    uploadedFilePath = data.absolute_file_path;
                    newPolicyUploaded = true;
                    // Enable the toggle button only if a model is selected
                    if (selectedModel) {
                        toggleButton.disabled = false;
                        showToggleButton();
                    }
                } else {
                    summaryPreview.innerHTML = '<p>Failed to upload files.</p>';
                }
            } else {
                summaryPreview.innerHTML = '<p>Failed to upload files. Status: ' + response.status + '</p>';
            }
        } catch (error) {
            console.error('Error during file upload:', error);
            summaryPreview.innerHTML = '<p>Error occurred during file upload.</p>';
        }
    }

    // Show the "Show Summary" button with a fade-in effect
    function showToggleButton() {
        toggleButton.style.display = 'block';
        setTimeout(() => {
            toggleButton.style.opacity = 1;
        }, 100);
    }

    // Show the loader for summary processing
    function showLoader() {
        loader.classList.add('summary-loader'); // Use new class name
        loader.innerHTML = `
            <div class="spinner"></div>  
            <p>Processing summary...</p>
        `;
        summaryPreview.innerHTML = ''; // Clear any existing content
        summaryPreview.appendChild(loader); // Add loader to the summary preview area
        summaryPreview.style.display = 'block'; // Make sure it's visible
    }

    // Hide the loader
    function hideLoader() {
        if (loader.parentNode) {
            loader.parentNode.removeChild(loader); // Remove the loader if it exists
        }
    }

    // Handle summary toggle functionality
    toggleButton.addEventListener('click', async function(event) {
        event.stopPropagation();
        // Disable the button to prevent multiple clicks
        toggleButton.disabled = true;
        if (summaryPreview.style.display === 'none' || !summaryPreview.innerHTML.trim()) {
            if (!selectedModel) {
                summaryPreview.innerHTML = '<p>Please select a model to generate the summary.</p>';
                // Re-enable the button
                toggleButton.disabled = false;
                return;
            }

            showLoader(); // Show loader while processing
            try {
                const file_response = await fetch('/new_policy_file_summary/', {
                    method: 'POST',
                    body: JSON.stringify({
                        filename: uploadedFilename,                // Send the uploaded file's name
                        absolute_file_path: uploadedFilePath,      // Send the absolute file path
                        model: selectedModel                        // Send the selected model
                    }),
                    headers: {
                        'X-CSRFToken': '{{ csrf_token }}',
                        'Content-Type': 'application/json'        // Ensure correct content type for JSON payload
                    }
                });

                if (file_response.ok) {
                    const file_data = await file_response.json();
                    hideLoader(); // Hide the loader once processing is complete
                    displayResults(file_data); // Display the summary results
                } else {
                    hideLoader();
                    summaryPreview.innerHTML = '<p>Failed to process summary.</p>';
                }
            } catch (error) {
                hideLoader();
                summaryPreview.innerHTML = '<p>Error occurred while processing summary.</p>';
            }

            // Update button text to "Hide Summary" when summary is shown
            toggleButton.textContent = 'Hide Summary';
        } else {
            // Hide summary
            summaryPreview.style.display = 'none';
            // Update button text to "Show Summary" when summary is hidden
            toggleButton.textContent = 'Show Summary';
        }
        // Re-enable the button after processing
        toggleButton.disabled = false;
    });

    // Display results after file upload and processing
    function displayResults(data) {
        const summary = `
            <h3>File Name: ${data.filename}</h3>
            <div class="analysis-results" style="overflow: hidden;">
                ${data.summary_of_own_file
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold text
                    .replace(/## (.*?)\n/g, '<h4>$1</h4>') // Headings
                    .replace(/^- (.*)/gm, '<li>$1</li>') // Bullet points
                    .replace(/\n/g, '<br>') // Newline to <br>
                }
            </div>
        `;
        summaryPreview.innerHTML = summary;
    }
});


// existing policy file handling

document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('upload-existing_policy');
    const uploadText = document.getElementById('upload-file-name-existing_policy');

    // Helper function to display selected files
    function displaySelectedFiles(files) {
        uploadText.innerHTML = Array.from(files)
            .map(file => `<strong>${file.name}</strong>`)
            .join('<br>');
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
        Array.from(files).forEach(file => formData.append('file', file));

        try {
            const response = await fetch('/existing_policy_file_upload/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}'  // Ensure CSRF protection if needed
                }
            });

            if (response.ok) {
                const data = await response.json();
                displayResults(data);
                existingPolicyUploaded = true; //  Set flag to true
            } else {
                console.error('Failed to upload files');
            }
        } catch (error) {
            console.error('Error during file upload:', error);
        } 
    }

    // Display results after file upload and processing
    function displayResults(data) {
        console.log(data);
    }
});


// others files handler

// document.addEventListener('DOMContentLoaded', () => {
//     const DocumentUploadArea = document.getElementById('document-upload');
//     const ArticlesUploadArea = document.getElementById('news-upload');
//     const DocumentResultsArea = document.getElementById('results-area');
//     const KEC = document.getElementById('KEC');

//     DocumentUploadArea.addEventListener('change', async (event) => {
//         const files = event.target.files;
//         console.log("Selected file:", files[0]);

//         if (files.length > 0) {
//             const formData = new FormData();
//             formData.append('file', files[0]);
//             console.log("form Data::", formData);
//             DocumentResultsArea.innerHTML = '<p>Uploading...</p>';
//             KEC.innerHTML = '<p>Processing...</p>';
//             try {
//                 const response = await fetch('/other_upload_file/', {
//                     method: 'POST',
//                     body: formData,
//                     headers: {
//                         'X-CSRFToken': getCSRFToken()  // Ensure this function is correct
//                     }
//                 });

//                 if (response.ok) {
//                     const data = await response.json();
//                     console.log("Data::", data);
//                     DocumentResultsArea.innerHTML = `
//                         <div class="analysis-results">
//                             ${data.comparative_summary_of_files.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
//                                                 .replace(/## (.*?)\n/g, '<h4>$1</h4>')
//                                                 .replace(/\* (.*?)\n/g, '<li>$1</li>')
//                                                 .replace(/\n/g, '<br>')}
//                         </div>
//                     `;
//                     KEC.innerHTML = `
//                     <h3>File Name: ${data.filename}</h3>
//                     <div class="analysis-results">
//                         ${data.summary_of_other_file.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
//                                             .replace(/## (.*?)\n/g, '<h4>$1</h4>')
//                                             .replace(/\* (.*?)\n/g, '<li>$1</li>')
//                                             .replace(/\n/g, '<br>')}
//                     </div>
//                 `;
//                 } else {
//                     console.error('Failed to upload files');
//                     DocumentResultsArea.innerHTML = '<p>Failed to upload files.</p>';
//                 }
//             } catch (error) {
//                 console.error('Error:', error);
//                 DocumentResultsArea.innerHTML = '<p>Error occurred during file upload.</p>';
//             }
//         } else {
//             DocumentResultsArea.innerHTML = '<p>No files selected.</p>';
//         }
//     });

//     ArticlesUploadArea.addEventListener('change', async (event) => {
//         const files = event.target.files;
//         console.log("Selected file:", files[0]);

//         if (files.length > 0) {
//             const formData = new FormData();
//             formData.append('file', files[0]);
//             console.log("form Data::", formData);
//             DocumentResultsArea.innerHTML = '<p>Uploading...</p>';
//             KEC.innerHTML = '<p>Processing...</p>';

//             try {
//                 const response = await fetch('/other_upload_file/', {
//                     method: 'POST',
//                     body: formData,
//                     headers: {
//                         'X-CSRFToken': getCSRFToken()  // Ensure this function is correct
//                     }
//                 });

//                 if (response.ok) {
//                     const data = await response.json();
//                     console.log("Data::", data);
//                     DocumentResultsArea.innerHTML = `
//                         <div class="analysis-results">
//                             ${data.comparative_summary_of_files.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
//                                                 .replace(/## (.*?)\n/g, '<h4>$1</h4>')
//                                                 .replace(/\* (.*?)\n/g, '<li>$1</li>')
//                                                 .replace(/\n/g, '<br>')}
//                         </div>
//                     `;
//                     KEC.innerHTML = `
//                     <h3>File Name: ${data.filename}</h3>
//                         <div class="analysis-results">
//                             ${data.summary_of_other_file.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
//                                                 .replace(/## (.*?)\n/g, '<h4>$1</h4>')
//                                                 .replace(/\* (.*?)\n/g, '<li>$1</li>')
//                                                 .replace(/\n/g, '<br>')}
//                         </div>
//                     `;
//                 } else {
//                     console.error('Failed to upload files');
//                     DocumentResultsArea.innerHTML = '<p>Failed to upload files.</p>';
//                 }
//             } catch (error) {
//                 console.error('Error:', error);
//                 DocumentResultsArea.innerHTML = '<p>Error occurred during file upload.</p>';
//             }
//         } else {
//             DocumentResultsArea.innerHTML = '<p>No files selected.</p>';
//         }
//     });

//     document.getElementById('submit-btn').addEventListener('click', async () => {
//         const linkInput = document.getElementById('news-link');
//         const link = linkInput.value;
//         const DocumentResultsArea = document.getElementById('results-area');
//         const KEC = document.getElementById('KEC');
        
//         console.log("Link:", link);

//         if (link) {
//             DocumentResultsArea.innerHTML = '<p>Uploading...</p>';
//         }
    
//         try {
//             const response = await fetch('/submit-link/', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                     'X-CSRFToken': getCSRFToken() 
//                 },
//                 body: JSON.stringify({ link })
//             });
    
//             if (response.ok) {
//                 const data = await response.json();
//                 console.log("Data:", data);
    
//                 DocumentResultsArea.innerHTML = `
//                     <div class="analysis-results">
//                         ${data.comparative_summary_of_files.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
//                         .replace(/## (.*?)\n/g, '<h4>$1</h4>')
//                         .replace(/\* (.*?)\n/g, '<li>$1</li>')
//                         .replace(/\n/g, '<br>')}
//                     </div>
//                 `;
//                 KEC.innerHTML = `
//                     <h3>File Name: ${data.filename}</h3>
//                     <div class="analysis-results">
//                         ${data.summary_of_link.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
//                             .replace(/## (.*?)\n/g, '<h4>$1</h4>')
//                             .replace(/\* (.*?)\n/g, '<li>$1</li>')
//                             .replace(/\n/g, '<br>')}
//                     </div>
//                 `;
//             } else {
//                 console.error('Failed to submit link');
//                 DocumentResultsArea.innerHTML = '<p>Failed to submit link.</p>';
//             }
//         } catch (error) {
//             console.error('Error:', error);
//             DocumentResultsArea.innerHTML = '<p>Error occurred during link submission.</p>';
//         }
//     });


//     function getCSRFToken() {
//         const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
//         return tokenElement ? tokenElement.value : '';
//     }
// });


// Analyzer Section :: analyzer btn and QA 
document.addEventListener('DOMContentLoaded', () => {
    // Get the elements
    const modelSelect = document.getElementById('modelSelect');
    const analyzeButton = document.getElementById('analyzeButton');
    const spinnerContainer = document.getElementById('spinner');
    
    // Get question texts
    const question1 = document.querySelector('.question_1').textContent;
    const question2 = document.querySelector('.question_2').textContent;
    const question3 = document.querySelector('.question_3').textContent;

    // Get result containers
    const result1Container = document.querySelector('.textbox_1');
    const result2Container = document.querySelector('.textbox_2');
    const result3Container = document.querySelector('.textbox_3');

    // Add event listener to the Analyze button
    analyzeButton.addEventListener('click', async () => {
        // Check upload status
        if (!newPolicyUploaded || !existingPolicyUploaded) {
            showError('Please upload both new policy and existing policy files.');
            spinnerContainer.style.display = 'none';
            return;
        }

        // Disable the button and show the spinner
        analyzeButton.disabled = true;
        spinnerContainer.style.display = 'grid';
        //display result containers Analysis is processing
        result1Container.innerHTML = `Analysis is processing...`;
        result2Container.innerHTML = `Analysis is processing...`;
        result3Container.innerHTML = `Analysis is processing...`;

        // Simulate asynchronous analysis
        await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate delay of 2 seconds


        // Get the selected model
        const selectedModel = modelSelect.value;

        // Create a data object to send to the server
        const data = {
            model: selectedModel,
            questions: {
                'question_1': question1,
                'question_2': question2,
                'question_3': question3
            }
        };

        try {
            // Send the data to the server
            const response = await fetch('/analyze_document/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}' // Ensure CSRF protection if needed
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                // Process the response
                const result = await response.json();
                displayResults(result);
            } else {
                showError('Failed to perform analysis. Please try again.');
            }
        } catch (error) {
            console.error('Error during analysis:', error);
            showError('An unexpected error occurred. Please try again later.');
        } finally {
            // Hide the spinner and re-enable the button
            spinnerContainer.style.display = 'none';
            analyzeButton.disabled = false;
        }
    });

    // Function to format and display the results from the server
    function displayResults(result) {
        function textFormatter(text) {
            if (!text) return 'No results available.';

            // Remove any extra line breaks
            text = text.replace(/\n+/g, '\n');
    
            // Replace **bold** with <strong>
            text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
            // Replace ## Header with <h4>
            text = text.replace(/## (.*?)\n/g, '<h4>$1</h4>');
    
            // Replace * List item with <li> inside <ul>
            text = text.replace(/\* (.*?)\n/g, '<li>$1</li>');
            // Replace - List item with <li> inside <ul>
            text = text.replace(/\- (.*?)\n/g, '<li>$1</li>');
    
            // Wrap list items with <ul> tag
            text = text.replace(/(<li>.*<\/li>)/g, '<ul>$1</ul>');
    
            // Replace newline characters with <br> for line breaks
            text = text.replace(/\n/g, '<br>');
    
            return text;
        }

        // Apply formatting to each result
        if (result) {
            result1Container.innerHTML = `
                <div class="analysis-results" style="overflow: hidden;">
                    ${textFormatter(result.answer_1) || 'No results available.'}
                </div>
            `;
            result2Container.innerHTML = `
                <div class="analysis-results" style="overflow: hidden;">
                    ${textFormatter(result.answer_2) || 'No results available.'}
                </div>
            `;
            result3Container.innerHTML = `
                <div class="analysis-results" style="overflow: hidden;">
                    ${textFormatter(result.answer_3)|| 'No results available.'}
                </div>
            `;
        }
    }

    // Function to display an error message in a pop-up
    function showError(message) {
        // Create a container for the pop-up
        const errorContainer = document.createElement('div');
        errorContainer.className = 'error-container';

        // Create a pop-up element
        const errorPopup = document.createElement('div');
        errorPopup.className = 'error-popup';
        errorPopup.textContent = message;

        // Append the pop-up to the container
        errorContainer.appendChild(errorPopup);

        // Append the container to the body
        document.body.appendChild(errorContainer);

        // Remove the pop-up after 3 seconds
        setTimeout(() => {
            errorContainer.remove();
        }, 3000);
    }
});


// Model Description::  Model Selector with description preview
document.addEventListener('DOMContentLoaded', () => {
    // Get the elements
    const modelSelect = document.getElementById('modelSelect');
    const descriptionContainer = document.getElementById('selected-model-description');

    // Define descriptions for each model
    const descriptions = {
        huggingface: `
            <div >
                <h3>Model Description</h3>
                <h4>Huggingface Model</h4>
                <ul>
                    <li><p><strong>Model:</strong>google/flan-t5-large</p></li>
                    <li><p><strong>Model Function:</strong> Performs a variety of NLP tasks including text generation, summarization, and translation.<br> It is based on the T-5 architecture from Huggingface's model hub.</p></li>
                    <li><p><strong>Context:</strong> Utilizes a text-to-text framework where the input and output are both text. The model can handle tasks like summarizing long documents into concise summaries.</p></li>
                    <li><p><strong>Response:</strong> The output is generated text based on the provided context. It returns results such as summaries or translations depending on the task.</p></li>
                </ul>
            </div>
        `,
        gemini: `
            <div >
                <h3>Model Description</h3>
                <h4>Gemini Model</h4>
                <ul>
                    <li><p><strong>Model:</strong> Gemini API Model (Gemini-1.5-flash)</p></li>
                    <li><p><strong>Model Function:</strong> model.generate_content(Context)</p></li>
                    <li><p><strong>Context:</strong> (Query + Document text) [Query = "Summarize the entire context comprehensively, highlighting all important details in a narrative format including the use of bullet points."]</p></li>
                    <li><p><strong>Response:</strong> (response.text): return as an output of model.generate_content(Context)</p></li>
                </ul>
            </div>
        `,
        chatgpt: `
            <div >
                <h3>Model Description</h3>
                <h4>ChatGPT Model</h4>
                <ul>
                    <li><p><strong>Model:</strong> ChatGPT 3.5</p></li>
                    <li><p><strong>Model Function:</strong> Designed for conversational purposes, it generates human-like responses in a dialogue format.<br>It is suitable for interactive tasks and generating text based on conversational context.</p></li>
                    <li><p><strong>Context:</strong> Processes conversational prompts and generates relevant responses based on the input text.<br>It can handle varied dialogue scenarios and provide contextual replies.</p></li>
                    <li><p><strong>Response:</strong> The output is a text response generated based on the input prompt, tailored to maintain a natural conversational flow.</p></li>
                </ul>
            </div>
        `
    };

    // Update the description container based on the selected model
    modelSelect.addEventListener('change', (event) => {
        const selectedModel = event.target.value;
        const description = descriptions[selectedModel] || '';
        
        // Show the container if description exists
        if (description) {
            descriptionContainer.innerHTML = description;
            descriptionContainer.style.display = 'block'; // Show the container
        } else {
            descriptionContainer.innerHTML = '<p>Select a model to see the description.</p>';
            descriptionContainer.style.display = 'none'; // Hide the container if no model is selected
        }
    });
});
