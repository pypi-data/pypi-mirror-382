/**
 * MCP Feedback Enhanced - 提示詞標籤 UI 模組
 * ==========================================
 *
 * 處理可拖拽的提示詞標籤顯示和交互
 */

(function() {
    'use strict';

    // 確保命名空間存在
    window.MCPFeedback = window.MCPFeedback || {};
    window.MCPFeedback.Prompt = window.MCPFeedback.Prompt || {};

    const Utils = window.MCPFeedback.Utils;

    /**
     * 提示詞標籤 UI 管理器
     */
    function PromptTagsUI(options) {
        options = options || {};

        // 依賴注入
        this.promptManager = options.promptManager || null;
        this.settingsManager = options.settingsManager || null;
        this.targetTextareaId = options.targetTextareaId || 'combinedFeedbackText';

        // UI 元素
        this.container = null;
        this.tagsContainer = null;

        // 拖拽狀態
        this.draggedElement = null;
        this.draggedIndex = null;

        // 標籤順序（存儲 prompt ID 的順序）
        this.tagOrder = [];

        // 狀態
        this.isInitialized = false;

        console.log('🏷️ PromptTagsUI 初始化完成');
    }

    /**
     * 初始化標籤 UI
     */
    PromptTagsUI.prototype.init = function(containerSelector) {
        console.log('🏷️ PromptTagsUI.init() 開始，容器選擇器:', containerSelector);

        if (this.isInitialized) {
            console.warn('⚠️ PromptTagsUI 已經初始化');
            return;
        }

        this.container = document.querySelector(containerSelector);
        if (!this.container) {
            console.error('❌ 找不到標籤容器:', containerSelector);
            return;
        }

        console.log('✅ 找到標籤容器:', this.container);

        // 創建 UI 結構
        this.createUI();

        // 載入標籤順序
        this.loadTagOrder();

        // 設置事件監聽器
        this.setupEventListeners();

        // 渲染標籤
        this.refreshTags();

        this.isInitialized = true;
        console.log('✅ PromptTagsUI 初始化完成');
    };

    /**
     * 創建 UI 結構
     */
    PromptTagsUI.prototype.createUI = function() {
        console.log('🏷️ createUI() 開始');

        const html = `
            <div class="prompt-tags-section">
                <div class="prompt-tags-header">
                    <h4 class="prompt-tags-title">
                        <span>🏷️</span>
                        <span data-i18n="prompts.tags.title">快速模板</span>
                    </h4>
                    <div class="prompt-tags-hint" data-i18n="prompts.tags.hint">
                        點擊標籤快速填入，拖拽調整順序
                    </div>
                </div>
                <div class="prompt-tags-list">
                    <!-- 標籤將在這裡動態生成 -->
                </div>
            </div>
        `;

        this.container.innerHTML = html;

        // 獲取 UI 元素引用
        this.tagsContainer = this.container.querySelector('.prompt-tags-list');

        console.log('🏷️ createUI() 完成, tagsContainer:', this.tagsContainer);
    };

    /**
     * 設置事件監聽器
     */
    PromptTagsUI.prototype.setupEventListeners = function() {
        const self = this;

        // 設置提示詞管理器回調
        if (this.promptManager) {
            this.promptManager.addPromptsChangeCallback(function(prompts) {
                console.log('🏷️ 提示詞列表變更，重新渲染標籤');
                self.refreshTags();
            });
        }
    };

    /**
     * 載入標籤順序
     */
    PromptTagsUI.prototype.loadTagOrder = function() {
        if (!this.settingsManager) {
            console.warn('⚠️ SettingsManager 未設定，無法載入標籤順序');
            return;
        }

        const savedOrder = this.settingsManager.get('promptTagOrder');
        if (savedOrder && Array.isArray(savedOrder)) {
            this.tagOrder = savedOrder;
            console.log('📥 從設定載入標籤順序:', this.tagOrder.length, '個標籤');
        }
    };

    /**
     * 保存標籤順序
     */
    PromptTagsUI.prototype.saveTagOrder = function() {
        if (!this.settingsManager) {
            console.warn('⚠️ SettingsManager 未設定，無法保存標籤順序');
            return false;
        }

        try {
            this.settingsManager.set('promptTagOrder', this.tagOrder);
            console.log('💾 標籤順序已保存');
            return true;
        } catch (error) {
            console.error('❌ 保存標籤順序失敗:', error);
            return false;
        }
    };

    /**
     * 刷新標籤顯示
     */
    PromptTagsUI.prototype.refreshTags = function() {
        console.log('🏷️ refreshTags() 開始');

        if (!this.tagsContainer) {
            console.error('❌ tagsContainer 不存在');
            return;
        }

        if (!this.promptManager) {
            console.error('❌ promptManager 不存在');
            return;
        }

        const prompts = this.promptManager.getAllPrompts();
        console.log('🏷️ 獲取到的提示詞數量:', prompts.length, prompts);

        if (prompts.length === 0) {
            console.log('🏷️ 沒有提示詞，顯示空狀態');
            this.tagsContainer.innerHTML = this.createEmptyStateHTML();
            return;
        }

        // 根據保存的順序排序提示詞
        const sortedPrompts = this.sortPromptsByOrder(prompts);
        console.log('🏷️ 排序後的提示詞:', sortedPrompts);

        // 更新標籤順序（添加新的提示詞）
        this.updateTagOrder(sortedPrompts);

        // 生成標籤 HTML
        this.tagsContainer.innerHTML = sortedPrompts.map((prompt, index) =>
            this.createTagHTML(prompt, index)
        ).join('');

        console.log('🏷️ 標籤 HTML 已生成');

        // 設置標籤事件監聽器
        this.setupTagEvents();

        // 更新翻譯
        this.updateTranslations();

        console.log('✅ refreshTags() 完成');
    };

    /**
     * 根據保存的順序排序提示詞
     */
    PromptTagsUI.prototype.sortPromptsByOrder = function(prompts) {
        const self = this;

        // 創建一個 Map 用於快速查找
        const promptMap = new Map();
        prompts.forEach(function(prompt) {
            promptMap.set(prompt.id, prompt);
        });

        // 根據保存的順序排序
        const sortedPrompts = [];

        // 先添加已排序的提示詞
        this.tagOrder.forEach(function(id) {
            if (promptMap.has(id)) {
                sortedPrompts.push(promptMap.get(id));
                promptMap.delete(id);
            }
        });

        // 添加新的提示詞（按創建時間排序）
        const newPrompts = Array.from(promptMap.values()).sort(function(a, b) {
            return new Date(b.createdAt) - new Date(a.createdAt);
        });

        return sortedPrompts.concat(newPrompts);
    };

    /**
     * 更新標籤順序
     */
    PromptTagsUI.prototype.updateTagOrder = function(sortedPrompts) {
        this.tagOrder = sortedPrompts.map(function(prompt) {
            return prompt.id;
        });
    };

    /**
     * 創建空狀態 HTML
     */
    PromptTagsUI.prototype.createEmptyStateHTML = function() {
        return `
            <div class="prompt-tags-empty">
                <div class="empty-icon">📝</div>
                <div class="empty-text" data-i18n="prompts.tags.emptyState">
                    尚未建立任何提示詞模板
                </div>
                <div class="empty-hint" data-i18n="prompts.tags.emptyHint">
                    前往設定頁面新增您的第一個提示詞模板
                </div>
            </div>
        `;
    };

    /**
     * 創建標籤 HTML
     */
    PromptTagsUI.prototype.createTagHTML = function(prompt, index) {
        const isAutoSubmit = prompt.isAutoSubmit || false;
        const tagClass = isAutoSubmit ? 'prompt-tag auto-submit-tag' : 'prompt-tag';

        return `
            <div class="${tagClass}"
                 data-prompt-id="${prompt.id}"
                 data-index="${index}"
                 draggable="true"
                 title="${Utils.escapeHtml(prompt.content)}">
                ${isAutoSubmit ? '<span class="tag-badge">⏰</span>' : ''}
                <span class="tag-name">${Utils.escapeHtml(prompt.name)}</span>
            </div>
        `;
    };

    /**
     * 設置標籤事件監聽器
     */
    PromptTagsUI.prototype.setupTagEvents = function() {
        const self = this;
        const tags = this.tagsContainer.querySelectorAll('.prompt-tag');

        tags.forEach(function(tag) {
            // 點擊事件 - 填入內容
            tag.addEventListener('click', function(e) {
                e.preventDefault();
                const promptId = tag.getAttribute('data-prompt-id');
                self.handleTagClick(promptId);
            });

            // 拖拽開始
            tag.addEventListener('dragstart', function(e) {
                self.handleDragStart(e, tag);
            });

            // 拖拽經過
            tag.addEventListener('dragover', function(e) {
                self.handleDragOver(e, tag);
            });

            // 拖拽進入
            tag.addEventListener('dragenter', function(e) {
                self.handleDragEnter(e, tag);
            });

            // 拖拽離開
            tag.addEventListener('dragleave', function(e) {
                self.handleDragLeave(e, tag);
            });

            // 放下
            tag.addEventListener('drop', function(e) {
                self.handleDrop(e, tag);
            });

            // 拖拽結束
            tag.addEventListener('dragend', function(e) {
                self.handleDragEnd(e);
            });
        });
    };

    /**
     * 處理拖拽開始
     */
    PromptTagsUI.prototype.handleDragStart = function(e, tag) {
        this.draggedElement = tag;
        this.draggedIndex = parseInt(tag.getAttribute('data-index'));

        tag.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/html', tag.innerHTML);

        console.log('🏷️ 開始拖拽標籤:', this.draggedIndex);
    };

    /**
     * 處理拖拽經過
     */
    PromptTagsUI.prototype.handleDragOver = function(e, tag) {
        if (e.preventDefault) {
            e.preventDefault();
        }
        e.dataTransfer.dropEffect = 'move';
        return false;
    };

    /**
     * 處理拖拽進入
     */
    PromptTagsUI.prototype.handleDragEnter = function(e, tag) {
        if (tag !== this.draggedElement) {
            tag.classList.add('drag-over');
        }
    };

    /**
     * 處理拖拽離開
     */
    PromptTagsUI.prototype.handleDragLeave = function(e, tag) {
        tag.classList.remove('drag-over');
    };

    /**
     * 處理放下
     */
    PromptTagsUI.prototype.handleDrop = function(e, tag) {
        if (e.stopPropagation) {
            e.stopPropagation();
        }

        tag.classList.remove('drag-over');

        if (this.draggedElement !== tag) {
            const targetIndex = parseInt(tag.getAttribute('data-index'));

            // 重新排序標籤順序
            this.reorderTags(this.draggedIndex, targetIndex);

            // 保存新順序
            this.saveTagOrder();

            // 重新渲染
            this.refreshTags();

            console.log('🏷️ 標籤已重新排序:', this.draggedIndex, '→', targetIndex);
        }

        return false;
    };

    /**
     * 處理拖拽結束
     */
    PromptTagsUI.prototype.handleDragEnd = function(e) {
        if (this.draggedElement) {
            this.draggedElement.classList.remove('dragging');
        }

        // 清除所有拖拽樣式
        const tags = this.tagsContainer.querySelectorAll('.prompt-tag');
        tags.forEach(function(tag) {
            tag.classList.remove('drag-over');
        });

        this.draggedElement = null;
        this.draggedIndex = null;
    };

    /**
     * 重新排序標籤
     */
    PromptTagsUI.prototype.reorderTags = function(fromIndex, toIndex) {
        const item = this.tagOrder.splice(fromIndex, 1)[0];
        this.tagOrder.splice(toIndex, 0, item);
    };

    /**
     * 顯示成功訊息
     */
    PromptTagsUI.prototype.showSuccess = function(message) {
        if (window.MCPFeedback && window.MCPFeedback.Utils && window.MCPFeedback.Utils.showMessage) {
            window.MCPFeedback.Utils.showMessage(message, 'success');
        }
    };

    /**
     * 顯示錯誤訊息
     */
    PromptTagsUI.prototype.showError = function(message) {
        if (window.MCPFeedback && window.MCPFeedback.Utils && window.MCPFeedback.Utils.showMessage) {
            window.MCPFeedback.Utils.showMessage(message, 'error');
        } else {
            alert(message);
        }
    };

    /**
     * 翻譯函數
     */
    PromptTagsUI.prototype.t = function(key, fallback) {
        if (window.i18nManager && typeof window.i18nManager.t === 'function') {
            return window.i18nManager.t(key, fallback);
        }
        return fallback || key;
    };

    /**
     * 更新翻譯
     */
    PromptTagsUI.prototype.updateTranslations = function() {
        if (window.i18nManager && typeof window.i18nManager.applyTranslations === 'function') {
            window.i18nManager.applyTranslations();
        }
    };

    /**
     * 處理標籤點擊
     */
    PromptTagsUI.prototype.handleTagClick = function(promptId) {
        if (!this.promptManager) {
            console.error('❌ PromptManager 未設定');
            return;
        }

        const prompt = this.promptManager.getPromptById(promptId);
        if (!prompt) {
            this.showError(this.t('prompts.tags.promptNotFound', '找不到指定的提示詞'));
            return;
        }

        // 獲取目標 textarea
        const textarea = document.getElementById(this.targetTextareaId);
        if (!textarea) {
            console.error('❌ 找不到目標 textarea:', this.targetTextareaId);
            return;
        }

        // 填入內容
        textarea.value = prompt.content;
        textarea.focus();

        // 更新使用記錄
        this.promptManager.usePrompt(promptId);

        // 顯示成功訊息
        this.showSuccess(this.t('prompts.tags.promptApplied', '已套用提示詞：') + prompt.name);
    };

    // 將 PromptTagsUI 加入命名空間
    window.MCPFeedback.Prompt.PromptTagsUI = PromptTagsUI;

    console.log('✅ PromptTagsUI 模組載入完成');

})();

