// Model Management functionality

// State variables for model management
let currentLoadedModel = null;
let installedModels = new Set(); // Track which models are actually installed

// Make installedModels accessible globally for the chat dropdown
window.installedModels = installedModels;
let currentCategory = 'hot';
let currentFilter = null;

// === Model Status Management ===

// Fetch installed models from the server
async function fetchInstalledModels() {
    try {
        const response = await httpJson(getServerBaseUrl() + '/api/v1/models');
        installedModels.clear();
        if (response && response.data) {
            response.data.forEach(model => {
                installedModels.add(model.id);
            });
        }
    } catch (error) {
        console.error('Error fetching installed models:', error);
        // If we can't fetch, assume all are installed to maintain current functionality
        const allModels = window.SERVER_MODELS || {};
        Object.keys(allModels).forEach(modelId => {
            installedModels.add(modelId);
        });
    }
}

// Check health endpoint to get current model status
async function checkModelHealth() {
    try {
        const response = await httpJson(getServerBaseUrl() + '/api/v1/health');
        return response;
    } catch (error) {
        console.error('Error checking model health:', error);
        return null;
    }
}

// Populate the model dropdown with all installed models
function populateModelDropdown() {
	const indicator = document.getElementById('model-status-indicator');
    const select = document.getElementById('model-select');
    select.innerHTML = '';
    
    // Add the default option
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Click to select a model ▼';
    select.appendChild(defaultOption);

	// Add the hidden 'Server Offline' option
	const hiddenOption = document.createElement('option');
	hiddenOption.value = 'server-offline';
	hiddenOption.textContent = 'Server Offline';
	hiddenOption.hidden = true;
	select.appendChild(hiddenOption);
	
    // Get all installed models from the global set
    const sortedModels = Array.from(installedModels).sort();
    
    // Add options for each installed model
    sortedModels.forEach(modelId => {
        const option = document.createElement('option');
        option.value = modelId;
        option.textContent = modelId;
        select.appendChild(option);
    });
}

// Update model status indicator
async function updateModelStatusIndicator() {
    const indicator = document.getElementById('model-status-indicator');
    const select = document.getElementById('model-select');
	const buttonIcons = document.querySelectorAll('button');
      
    // Fetch both health and installed models
    const [health] = await Promise.all([
        checkModelHealth(),
        fetchInstalledModels()
    ]);
	
	// Populate the dropdown with the newly fetched installed models
    populateModelDropdown();

    // Refresh model management UI if we're on the models tab
    const modelsTab = document.getElementById('content-models');
    if (modelsTab && modelsTab.classList.contains('active')) {
        // Use the display-only version to avoid re-fetching data we just fetched
        refreshModelMgmtUIDisplay();
        
        // Also refresh the model browser to show updated button states
        if (currentCategory === 'hot') displayHotModels();
        else if (currentCategory === 'recipes') displayModelsByRecipe(currentFilter);
        else if (currentCategory === 'labels') displayModelsByLabel(currentFilter);
    }
	
    if (health && health.model_loaded) {
        // Model is loaded - show model name with online status
		indicator.classList.remove('online', 'offline', 'loading'); 
        currentLoadedModel = health.model_loaded;
        indicator.classList.add('loaded');
        select.value = currentLoadedModel;
        select.disabled = false;
		buttonIcons.forEach(btn => btn.disabled = false);
    } else if (health !== null) {
        // Server is online but no model loaded
		indicator.classList.remove('loaded', 'offline', 'loading');
        currentLoadedModel = null;
        indicator.classList.add('online');
        select.value = ''; // Set to the "Click to select a model ▼" option
        select.disabled = false;
		buttonIcons.forEach(btn => btn.disabled = false);
    } else {
        // Server is offline
		indicator.classList.remove('loaded', 'online', 'loading');
        currentLoadedModel = null;
		// Add the hidden 'Server Offline' option
		const hiddenOption = document.createElement('option');
		hiddenOption.value = 'server-offline';
		hiddenOption.textContent = 'Server Offline';
		hiddenOption.hidden = true;
		select.appendChild(hiddenOption);
        indicator.classList.add('offline');
        select.value = 'server-offline';
        select.disabled = true;
		buttonIcons.forEach(btn => btn.disabled = true);
		return;
    }
}

// Unload current model
async function unloadModel() {
    if (!currentLoadedModel) return;
    
    try {
        // Set loading state
        const indicator = document.getElementById('model-status-indicator');
        const select = document.getElementById('model-select');
        indicator.classList.remove('loaded', 'online', 'offline');
        indicator.classList.add('loading');
        select.disabled = true;
        select.value = currentLoadedModel; // Keep the selected model visible during unload

        await httpRequest(getServerBaseUrl() + '/api/v1/unload', {
            method: 'POST'
        });
        
        await updateModelStatusIndicator();
        
        // Refresh model list to show updated button states
        if (currentCategory === 'hot') displayHotModels();
        else if (currentCategory === 'recipes') displayModelsByRecipe(currentFilter);
        else if (currentCategory === 'labels') displayModelsByLabel(currentFilter);
    } catch (error) {
        console.error('Error unloading model:', error);
        showErrorBanner('Failed to unload model: ' + error.message);
        await updateModelStatusIndicator(); // Revert state on error
    }
}

// === Model Browser Management ===

// Toggle category in model browser (only for Hot Models now)
function toggleCategory(categoryName) {
    const header = document.querySelector(`[data-category="${categoryName}"] .category-header`);
    const content = document.getElementById(`category-${categoryName}`);
    
    if (categoryName === 'hot') {
        // Check if hot models is already selected
        const isCurrentlyActive = header.classList.contains('active');
        
        // Clear all other active states
        document.querySelectorAll('.subcategory').forEach(s => s.classList.remove('active'));
        
        if (!isCurrentlyActive) {
            // Show hot models
            header.classList.add('active');
            content.classList.add('expanded');
            currentCategory = categoryName;
            currentFilter = null;
            displayHotModels();
        }
        // If already active, keep it active (don't toggle off)
    }
}

// Show add model form in main area
function showAddModelForm() {
    // Clear all sidebar active states
    document.querySelectorAll('.category-header').forEach(h => h.classList.remove('active'));
    document.querySelectorAll('.category-content').forEach(c => c.classList.remove('expanded'));
    document.querySelectorAll('.subcategory').forEach(s => s.classList.remove('active'));
    
    // Highlight "Add a Model" as selected
    const addModelHeader = document.querySelector('[data-category="add"] .category-header');
    if (addModelHeader) {
        addModelHeader.classList.add('active');
    }
    
    // Hide model list and show form
    document.getElementById('model-list').style.display = 'none';
    document.getElementById('add-model-form-main').style.display = 'block';
    
    // Set current state
    currentCategory = 'add';
    currentFilter = null;
}

// Select recipe filter
function selectRecipe(recipe) {
    // Clear hot models active state
    document.querySelectorAll('.category-header').forEach(h => h.classList.remove('active'));
    document.querySelectorAll('.category-content').forEach(c => c.classList.remove('expanded'));
    
    // Clear all subcategory selections
    document.querySelectorAll('.subcategory').forEach(s => s.classList.remove('active'));
    
    // Set this recipe as active
    document.querySelector(`[data-recipe="${recipe}"]`).classList.add('active');
    
    currentCategory = 'recipes';
    currentFilter = recipe;
    displayModelsByRecipe(recipe);
}

// Select label filter
function selectLabel(label) {
    // Clear hot models active state
    document.querySelectorAll('.category-header').forEach(h => h.classList.remove('active'));
    document.querySelectorAll('.category-content').forEach(c => c.classList.remove('expanded'));
    
    // Clear all subcategory selections
    document.querySelectorAll('.subcategory').forEach(s => s.classList.remove('active'));
    
    // Set this label as active
    document.querySelector(`[data-label="${label}"]`).classList.add('active');
    
    currentCategory = 'labels';
    currentFilter = label;
    displayModelsByLabel(label);
}

// Display suggested models (Qwen3-0.6B-GGUF as default)
function displaySuggestedModels() {
    const modelList = document.getElementById('model-list');
    const allModels = window.SERVER_MODELS || {};
    
    modelList.innerHTML = '';
    
    // First show Qwen3-0.6B-GGUF as the default suggested model
    if (allModels['Qwen3-0.6B-GGUF']) {
        createModelItem('Qwen3-0.6B-GGUF', allModels['Qwen3-0.6B-GGUF'], modelList);
    }
    
    // Then show other suggested models (excluding the one already shown)
    Object.entries(allModels).forEach(([modelId, modelData]) => {
        if (modelData.suggested && modelId !== 'Qwen3-0.6B-GGUF') {
            createModelItem(modelId, modelData, modelList);
        }
    });
    
    if (modelList.innerHTML === '') {
        modelList.innerHTML = '<p>No suggested models available</p>';
    }
}

// Display hot models
function displayHotModels() {
    const modelList = document.getElementById('model-list');
    const addModelForm = document.getElementById('add-model-form-main');
    const allModels = window.SERVER_MODELS || {};
    
    // Show model list, hide form
    modelList.style.display = 'block';
    addModelForm.style.display = 'none';
    
    modelList.innerHTML = '';
    
    Object.entries(allModels).forEach(([modelId, modelData]) => {
        if (modelData.labels && modelData.labels.includes('hot')) {
            createModelItem(modelId, modelData, modelList);
        }
    });
}

// Display models by recipe
function displayModelsByRecipe(recipe) {
    const modelList = document.getElementById('model-list');
    const addModelForm = document.getElementById('add-model-form-main');
    const allModels = window.SERVER_MODELS || {};
    
    // Show model list, hide form
    modelList.style.display = 'block';
    addModelForm.style.display = 'none';
    
    modelList.innerHTML = '';
    
    // Add FastFlowLM notice if this is the FLM recipe
    if (recipe === 'flm') {
        const notice = document.createElement('div');
        notice.className = 'flm-notice';
        notice.innerHTML = `
            <div class="flm-notice-content">
                <div class="flm-notice-icon">⚠️</div>
                <div class="flm-notice-text">
                    <strong><a href="https://github.com/FastFlowLM/FastFlowLM">FastFlowLM (FLM)</a> support in Lemonade is in Early Access.</strong> FLM is free for non-commercial use, however note that commercial licensing terms apply. Installing an FLM model will automatically launch the FLM installer, which will require you to accept the FLM license terms to continue. Contact <a href="mailto:lemonade@amd.com">lemonade@amd.com</a> for inquiries.
                </div>
            </div>
        `;
        modelList.appendChild(notice);
    }
    
    Object.entries(allModels).forEach(([modelId, modelData]) => {
        if (modelData.recipe === recipe) {
            createModelItem(modelId, modelData, modelList);
        }
    });
}

// Display models by label
function displayModelsByLabel(label) {
    const modelList = document.getElementById('model-list');
    const addModelForm = document.getElementById('add-model-form-main');
    const allModels = window.SERVER_MODELS || {};
    
    // Show model list, hide form
    modelList.style.display = 'block';
    addModelForm.style.display = 'none';
    
    modelList.innerHTML = '';
    
    Object.entries(allModels).forEach(([modelId, modelData]) => {
        if (label === 'custom') {
            // Show user-added models (those starting with 'user.')
            if (modelId.startsWith('user.')) {
                createModelItem(modelId, modelData, modelList);
            }
        } else if (modelData.labels && modelData.labels.includes(label)) {
            createModelItem(modelId, modelData, modelList);
        }
    });
}

// Create model item element
function createModelItem(modelId, modelData, container) {
    const item = document.createElement('div');
    item.className = 'model-item';
    
    const info = document.createElement('div');
    info.className = 'model-item-info';
    
    const name = document.createElement('div');
    name.className = 'model-item-name';
    name.appendChild(createModelNameWithLabels(modelId, window.SERVER_MODELS || {}));
    
    info.appendChild(name);
    
    // Only add description if it exists and is not empty
    if (modelData.description && modelData.description.trim()) {
        const description = document.createElement('div');
        description.className = 'model-item-description';
        description.textContent = modelData.description;
        info.appendChild(description);
    }
    
    const actions = document.createElement('div');
    actions.className = 'model-item-actions';
    
    // Check if model is actually installed by looking at the installedModels set
    const isInstalled = installedModels.has(modelId);
    const isLoaded = currentLoadedModel === modelId;
    
    if (!isInstalled) {
        const installBtn = document.createElement('button');
        installBtn.className = 'model-item-btn install';
        installBtn.textContent = '📥';
        installBtn.title = 'Install';
        installBtn.onclick = () => installModel(modelId);
        actions.appendChild(installBtn);
    } else {
        if (isLoaded) {
            const unloadBtn = document.createElement('button');
            unloadBtn.className = 'model-item-btn unload';
            unloadBtn.textContent = '⏏️';
            unloadBtn.title = 'Unload';
            unloadBtn.onclick = () => unloadModel();
            actions.appendChild(unloadBtn);
        } else {
            const loadBtn = document.createElement('button');
			const modelSelect = document.getElementById('model-select');
            loadBtn.className = 'model-item-btn load';
            loadBtn.textContent = '🚀';
            loadBtn.title = 'Load';
            loadBtn.onclick = () => {
                loadModelStandardized(modelId, {
                    loadButton: loadBtn,
                    onSuccess: (loadedModelId) => {
                        console.log(`Model ${loadedModelId} loaded successfully`);
                    },
                    onError: (error, failedModelId) => {
                        console.error(`Failed to load model ${failedModelId}:`, error);
                        showErrorBanner('Failed to load model: ' + error.message);
                    }
                });
            };
            actions.appendChild(loadBtn);
        }
        
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'model-item-btn delete';
        deleteBtn.textContent = '🗑️';
        deleteBtn.title = 'Delete';
        deleteBtn.onclick = () => deleteModel(modelId);
        actions.appendChild(deleteBtn);
    }
    
    item.appendChild(info);
    item.appendChild(actions);
    container.appendChild(item);
}

// Install model
async function installModel(modelId) {
    // Find the install button and show loading state
    const modelItems = document.querySelectorAll('.model-item');
    let installBtn = null;
    
    modelItems.forEach(item => {
        const nameElement = item.querySelector('.model-item-name .model-labels-container span');
        if (nameElement && nameElement.getAttribute('data-model-id') === modelId) {
            installBtn = item.querySelector('.model-item-btn.install');
        }
    });
    
    if (installBtn) {
        installBtn.disabled = true;
        installBtn.textContent = '⏳';
    }
    
    try {
        const modelData = window.SERVER_MODELS[modelId];
        await httpRequest(getServerBaseUrl() + '/api/v1/pull', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model_name: modelId, ...modelData })
        });
        
        // Refresh installed models and model status
        await fetchInstalledModels();
        await updateModelStatusIndicator();
        
        // Refresh model dropdown in chat
        if (window.initializeModelDropdown) {
            window.initializeModelDropdown();
        }
        
        // Refresh model list
        if (currentCategory === 'hot') displayHotModels();
        else if (currentCategory === 'recipes') displayModelsByRecipe(currentFilter);
        else if (currentCategory === 'labels') displayModelsByLabel(currentFilter);
    } catch (error) {
        console.error('Error installing model:', error);
        showErrorBanner('Failed to install model: ' + error.message);
        
        // Reset button state on error
        if (installBtn) {
            installBtn.disabled = false;
            installBtn.textContent = '📥';
        }
    }
}


// Delete model
async function deleteModel(modelId) {
    if (!confirm(`Are you sure you want to delete the model "${modelId}"?`)) {
        return;
    }
    
    // Find the delete button and show loading state
    const modelItems = document.querySelectorAll('.model-item');
    let deleteBtn = null;
    
    modelItems.forEach(item => {
        const nameElement = item.querySelector('.model-item-name .model-labels-container span');
        if (nameElement && nameElement.getAttribute('data-model-id') === modelId) {
            deleteBtn = item.querySelector('.model-item-btn.delete');
        }
    });
    
    if (deleteBtn) {
        deleteBtn.disabled = true;
        deleteBtn.textContent = '⏳';
    }
    
    try {
        await httpRequest(getServerBaseUrl() + '/api/v1/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model_name: modelId })
        });
        
        // Refresh installed models and model status
        await fetchInstalledModels();
        await updateModelStatusIndicator();
        
        // Refresh model dropdown in chat
        if (window.initializeModelDropdown) {
            window.initializeModelDropdown();
        }
        
        // Refresh model list
        if (currentCategory === 'hot') displayHotModels();
        else if (currentCategory === 'recipes') displayModelsByRecipe(currentFilter);
        else if (currentCategory === 'labels') displayModelsByLabel(currentFilter);
    } catch (error) {
        console.error('Error deleting model:', error);
        showErrorBanner('Failed to delete model: ' + error.message);
        
        // Reset button state on error
        if (deleteBtn) {
            deleteBtn.disabled = false;
            deleteBtn.textContent = '🗑️';
        }
    }
}

// === Model Name Display ===

// Create model name with labels
function createModelNameWithLabels(modelId, serverModels) {
    const modelData = serverModels[modelId];
    const container = document.createElement('div');
    container.className = 'model-labels-container';
    
    // Model name
    const nameSpan = document.createElement('span');

    // Store the original modelId as a data attribute for button finding
    nameSpan.setAttribute('data-model-id', modelId);
    
    // Append size if available
    let displayName = modelId;
    if (modelData && typeof modelData.size === 'number') {
        displayName += ` (${modelData.size} GB)`;
    }
    nameSpan.textContent = displayName;
    container.appendChild(nameSpan);
    
    // Labels
    if (modelData && modelData.labels && Array.isArray(modelData.labels)) {
        modelData.labels.forEach(label => {
            const labelLower = label.toLowerCase();
            
            // Skip "hot" labels since they have their own section
            if (labelLower === 'hot') {
                return;
            }
            
            const labelSpan = document.createElement('span');
            let labelClass = 'other';
            if (labelLower === 'vision') {
                labelClass = 'vision';
            } else if (labelLower === 'embeddings') {
                labelClass = 'embeddings';
            } else if (labelLower === 'reasoning') {
                labelClass = 'reasoning';
            } else if (labelLower === 'reranking') {
                labelClass = 'reranking';
            } else if (labelLower === 'coding') {
                labelClass = 'coding';
            } else if (labelLower === 'tool-calling') {
                labelClass = 'tool-calling';
            }
            labelSpan.className = `model-label ${labelClass}`;
            labelSpan.textContent = label;
            container.appendChild(labelSpan);
        });
    }
    
    return container;
}

// === Model Management Table (for models tab) ===

// Initialize model management functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', async function() {
    // Set up model status controls
    const unloadBtn = document.getElementById('model-unload-btn');
    if (unloadBtn) {
        unloadBtn.onclick = unloadModel;
    }
    
    const modelSelect = document.getElementById('model-select');
    if (modelSelect) {
        modelSelect.addEventListener('change', async function() {
            const modelId = this.value;
            if (modelId) {
                await loadModelStandardized(modelId, {
                    onSuccess: (loadedModelId) => {
                        console.log(`Model ${loadedModelId} loaded successfully`);
                    },
                    onError: (error, failedModelId) => {
                        console.error(`Failed to load model ${failedModelId}:`, error);
                        showErrorBanner('Failed to load model: ' + error.message);
                    }
                });
            }
        });
    }
    
    // Initial fetch of model data - this will populate installedModels
    await updateModelStatusIndicator();
    
    // Set up periodic refresh of model status
    setInterval(updateModelStatusIndicator, 1000); // Check every 1 seconds
    
    // Initialize model browser with hot models
    displayHotModels();
    
    // Initial load of model management UI - this will use the populated installedModels
    await refreshModelMgmtUI();
    
    // Refresh when switching to the models tab
    const modelsTab = document.getElementById('tab-models');
    if (modelsTab) {
        modelsTab.addEventListener('click', refreshModelMgmtUI);
    }
    
    // Set up register model form
    setupRegisterModelForm();
});

// Toggle Add Model form
function toggleAddModelForm() {
    const form = document.querySelector('.model-mgmt-register-form');
    form.classList.toggle('collapsed');
}

// Helper function to render a model table section
function renderModelTable(tbody, models, allModels, emptyMessage) {
    tbody.innerHTML = '';
    if (models.length === 0) {
        const tr = document.createElement('tr');
        const td = document.createElement('td');
        td.colSpan = 2;
        td.textContent = emptyMessage;
        td.style.textAlign = 'center';
        td.style.fontStyle = 'italic';
        td.style.color = '#666';
        td.style.padding = '1em';
        tr.appendChild(td);
        tbody.appendChild(tr);
    } else {
        models.forEach(mid => {
            const tr = document.createElement('tr');
            const tdName = document.createElement('td');
            
            tdName.appendChild(createModelNameWithLabels(mid, allModels));
            tdName.style.paddingRight = '1em';
            tdName.style.verticalAlign = 'middle';
            const tdBtn = document.createElement('td');
            tdBtn.style.width = '1%';
            tdBtn.style.verticalAlign = 'middle';
            const btn = document.createElement('button');
            btn.textContent = '+';
            btn.title = 'Install model';
            btn.onclick = async function() {
                btn.disabled = true;
                btn.textContent = '⏳';
                btn.classList.add('installing-btn');
                try {
                    await httpRequest(getServerBaseUrl() + '/api/v1/pull', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ model_name: mid })
                    });
                    await refreshModelMgmtUI();
                    // Update chat dropdown too if loadModels function exists
                    if (typeof loadModels === 'function') {
                        await loadModels();
                    }
                } catch (e) {
                    btn.textContent = 'Error';
                    btn.disabled = false;
                    showErrorBanner(`Failed to install model: ${e.message}`);
                }
            };
            tdBtn.appendChild(btn);
            tr.appendChild(tdName);
            tr.appendChild(tdBtn);
            tbody.appendChild(tr);
        });
    }
}

// Model Management Tab Logic
async function refreshModelMgmtUI() {
    // Get installed models from /api/v1/models
    let installed = [];
    try {
        const data = await httpJson(getServerBaseUrl() + '/api/v1/models');
        if (data.data && Array.isArray(data.data)) {
            installed = data.data.map(m => m.id || m.name || m);
        }
    } catch (e) {
        showErrorBanner(`Error loading models: ${e.message}`);
    }
    
    // Update the global installedModels set
    installedModels.clear();
    installed.forEach(modelId => {
        installedModels.add(modelId);
    });
    
    // All models from server_models.json (window.SERVER_MODELS)
    const allModels = window.SERVER_MODELS || {};
    
    // Separate hot models and regular suggested models not installed
    const hotModels = [];
    const regularSuggested = [];
    
    Object.keys(allModels).forEach(k => {
        if (allModels[k].suggested && !installed.includes(k)) {
            const modelData = allModels[k];
            const hasHotLabel = modelData.labels && modelData.labels.some(label => 
                label.toLowerCase() === 'hot'
            );
            
            if (hasHotLabel) {
                hotModels.push(k);
            } else {
                regularSuggested.push(k);
            }
        }
    });
    
    // Render installed models as a table (two columns, second is invisible)
    const installedTbody = document.getElementById('installed-models-tbody');
    if (installedTbody) {
        installedTbody.innerHTML = '';
        installed.forEach(function(mid) {
            var tr = document.createElement('tr');
            var tdName = document.createElement('td');
            
            tdName.appendChild(createModelNameWithLabels(mid, allModels));
            tdName.style.paddingRight = '1em';
            tdName.style.verticalAlign = 'middle';
            
            var tdBtn = document.createElement('td');
            tdBtn.style.width = '1%';
            tdBtn.style.verticalAlign = 'middle';
            const btn = document.createElement('button');
            btn.textContent = '−';
            btn.title = 'Delete model';
            btn.style.cursor = 'pointer';
            btn.onclick = async function() {
                if (!confirm(`Are you sure you want to delete the model "${mid}"?`)) {
                    return;
                }
                btn.disabled = true;
                btn.textContent = '⏳';
                btn.style.backgroundColor = '#888';
                try {
                    await httpRequest(getServerBaseUrl() + '/api/v1/delete', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ model_name: mid })
                    });
                    await refreshModelMgmtUI();
                    // Update chat dropdown too if loadModels function exists
                    if (typeof loadModels === 'function') {
                        await loadModels();
                    }
                } catch (e) {
                    btn.textContent = 'Error';
                    btn.disabled = false;
                    btn.style.backgroundColor = '';
                    showErrorBanner(`Failed to delete model: ${e.message}`);
                }
            };
            tdBtn.appendChild(btn);
            tr.appendChild(tdName);
            tr.appendChild(tdBtn);
            installedTbody.appendChild(tr);
        });
    }
    
    // Render hot models and suggested models using the helper function
    const hotTbody = document.getElementById('hot-models-tbody');
    const suggestedTbody = document.getElementById('suggested-models-tbody');
    
    if (hotTbody) {
        renderModelTable(hotTbody, hotModels, allModels, "Nice, you've already installed all these models!");
    }
    if (suggestedTbody) {
        renderModelTable(suggestedTbody, regularSuggested, allModels, "Nice, you've already installed all these models!");
    }
    
    // Refresh model dropdown in chat after updating installed models
    if (window.initializeModelDropdown) {
        window.initializeModelDropdown();
    }
    
    // Update system message when installed models change
    if (window.displaySystemMessage) {
        window.displaySystemMessage();
    }
}

// Make refreshModelMgmtUI globally accessible
window.refreshModelMgmtUI = refreshModelMgmtUI;

// Display-only version that uses already-fetched installedModels data
function refreshModelMgmtUIDisplay() {
    // Use the already-populated installedModels set
    const installed = Array.from(installedModels);
    
    // All models from server_models.json (window.SERVER_MODELS)
    const allModels = window.SERVER_MODELS || {};
    
    // Separate hot models and regular suggested models not installed
    const hotModels = [];
    const regularSuggested = [];
    
    Object.keys(allModels).forEach(k => {
        if (allModels[k].suggested && !installed.includes(k)) {
            if (allModels[k].labels && allModels[k].labels.some(label => label.toLowerCase() === 'hot')) {
                hotModels.push(k);
            } else {
                regularSuggested.push(k);
            }
        }
    });
    
    // Render installed models as a table (two columns, second is invisible)
    const installedTbody = document.getElementById('installed-models-tbody');
    if (installedTbody) {
        installedTbody.innerHTML = '';
        installed.forEach(function(mid) {
            var tr = document.createElement('tr');
            var tdName = document.createElement('td');
            
            tdName.appendChild(createModelNameWithLabels(mid, allModels));
            tdName.style.paddingRight = '1em';
            tdName.style.verticalAlign = 'middle';
            
            var tdBtn = document.createElement('td');
            tdBtn.style.width = '1%';
            tdBtn.style.verticalAlign = 'middle';
            const btn = document.createElement('button');
            btn.textContent = '−';
            btn.className = 'btn-remove-model';
            btn.style.minWidth = '24px';
            btn.style.padding = '2px 8px';
            btn.style.fontSize = '16px';
            btn.style.lineHeight = '1';
            btn.style.border = '1px solid #ddd';
            btn.style.backgroundColor = '#f8f9fa';
            btn.style.cursor = 'pointer';
            btn.style.borderRadius = '4px';
            btn.title = 'Remove this model';
            btn.onclick = async function() {
                if (confirm(`Are you sure you want to remove the model "${mid}"?`)) {
                    btn.disabled = true;
                    btn.textContent = '⏳';
                    const originalBgColor = btn.style.backgroundColor;
                    btn.style.backgroundColor = '#888';
                    try {
                        await httpRequest(getServerBaseUrl() + '/api/v1/delete', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ model_name: mid })
                        });
                        await refreshModelMgmtUI();
                    } catch (error) {
                        console.error('Error removing model:', error);
                        showErrorBanner('Failed to remove model: ' + error.message);
                        // Reset button state on error
                        btn.disabled = false;
                        btn.textContent = '−';
                        btn.style.backgroundColor = originalBgColor;
                    }
                }
            };
            tdBtn.appendChild(btn);
            tr.appendChild(tdName);
            tr.appendChild(tdBtn);
            installedTbody.appendChild(tr);
        });
    }
    
    // Render hot models and suggested models using the helper function
    const hotTbody = document.getElementById('hot-models-tbody');
    const suggestedTbody = document.getElementById('suggested-models-tbody');
    
    if (hotTbody) {
        renderModelTable(hotTbody, hotModels, allModels, "Nice, you've already installed all these models!");
    }
    if (suggestedTbody) {
        renderModelTable(suggestedTbody, regularSuggested, allModels, "Nice, you've already installed all these models!");
    }
    
    // Refresh model dropdown in chat after updating installed models
    if (window.initializeModelDropdown) {
        window.initializeModelDropdown();
    }
}

// Set up the register model form
function setupRegisterModelForm() {
    const registerForm = document.getElementById('register-model-form');
    const registerStatus = document.getElementById('register-model-status');
    
    if (registerForm && registerStatus) {
        registerForm.onsubmit = async function(e) {
            e.preventDefault();
            registerStatus.textContent = '';
            let name = document.getElementById('register-model-name').value.trim();
            
            // Always prepend 'user.' if not already present
            if (!name.startsWith('user.')) {
                name = 'user.' + name;
            }
            
            const checkpoint = document.getElementById('register-checkpoint').value.trim();
            const recipe = document.getElementById('register-recipe').value;
            const reasoning = document.getElementById('register-reasoning').checked;
            const vision = document.getElementById('register-vision').checked;
            const mmproj = document.getElementById('register-mmproj').value.trim();
            
            if (!name || !recipe) { 
                return; 
            }
            
            const payload = { model_name: name, recipe, reasoning, vision };
            if (checkpoint) payload.checkpoint = checkpoint;
            if (mmproj) payload.mmproj = mmproj;
            
            const btn = document.getElementById('register-submit');
            btn.disabled = true;
            btn.textContent = 'Installing...';
            
            try {
                await httpRequest(getServerBaseUrl() + '/api/v1/pull', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                registerStatus.textContent = 'Model installed!';
                registerStatus.style.color = '#27ae60';
                registerStatus.className = 'register-status success';
                registerForm.reset();
                await refreshModelMgmtUI();
                // Update chat dropdown too if loadModels function exists
                if (typeof loadModels === 'function') {
                    await loadModels();
                }
            } catch (e) {
                registerStatus.textContent = e.message + ' See the Lemonade Server log for details.';
                registerStatus.style.color = '#dc3545';
                registerStatus.className = 'register-status error';
                showErrorBanner(`Model install failed: ${e.message}`);
            }
            
            btn.disabled = false;
            btn.textContent = 'Install';
            refreshModelMgmtUI();
        };
    }
}

// Make functions globally available for HTML onclick handlers and other components
window.toggleCategory = toggleCategory;
window.selectRecipe = selectRecipe;
window.selectLabel = selectLabel;
window.showAddModelForm = showAddModelForm;
window.unloadModel = unloadModel;
window.installModel = installModel;
window.deleteModel = deleteModel;