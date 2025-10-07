// Paste this into browser console to verify tags are working

console.log('=== Prompt Tags Verification ===');

// 1. Check if container exists
const container = document.querySelector('#promptTagsContainer');
console.log('1. Container exists:', !!container);
if (container) {
    console.log('   Container HTML:', container.innerHTML.substring(0, 200));
}

// 2. Check if PromptTagsUI class is loaded
console.log('2. PromptTagsUI class loaded:', !!window.MCPFeedback?.Prompt?.PromptTagsUI);

// 3. Check if app has promptTagsUI instance
console.log('3. App has promptTagsUI:', !!window.app?.promptTagsUI);

// 4. Check if promptManager has prompts
if (window.app?.promptManager) {
    const prompts = window.app.promptManager.getAllPrompts();
    console.log('4. Number of prompts:', prompts.length);
    prompts.forEach((p, i) => {
        console.log(`   ${i+1}. ${p.name} (${p.id})`);
    });
} else {
    console.log('4. PromptManager not found');
}

// 5. Check tags container content
const tagsSection = document.querySelector('.prompt-tags-section');
console.log('5. Tags section exists:', !!tagsSection);
if (tagsSection) {
    const tagsList = tagsSection.querySelector('.prompt-tags-list');
    console.log('   Tags list exists:', !!tagsList);
    if (tagsList) {
        console.log('   Tags list HTML:', tagsList.innerHTML.substring(0, 200));
        const tags = tagsList.querySelectorAll('.prompt-tag');
        console.log('   Number of tag elements:', tags.length);
    }
}

// 6. Try to manually refresh tags
if (window.app?.promptTagsUI) {
    console.log('6. Attempting manual refresh...');
    try {
        window.app.promptTagsUI.refreshTags();
        console.log('   ✅ Refresh successful');
    } catch (error) {
        console.log('   ❌ Refresh failed:', error.message);
    }
} else {
    console.log('6. Cannot refresh - promptTagsUI not initialized');
}

console.log('=== Verification Complete ===');
