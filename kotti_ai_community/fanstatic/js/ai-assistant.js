/**
 * AI共创社区 - g4f AI 助手客户端
 * 
 * 使用 g4f 官方 JS 客户端，在浏览器中直接调用 AI 模型
 * 无需后端处理，减轻服务器压力
 */

class AIAssistant {
    constructor(options = {}) {
        this.client = null;
        this.model = options.model || 'gpt-4.1-mini';
        this.availableModels = [
            { id: 'gpt-4.1', name: 'GPT-4.1', description: '最新最强模型' },
            { id: 'gpt-4.1-mini', name: 'GPT-4.1 Mini', description: '快速响应，性价比高' },
            { id: 'gpt-4o', name: 'GPT-4o', description: '多模态模型' },
            { id: 'deepseek-v3', name: 'DeepSeek V3', description: '国产大模型' },
            { id: 'claude-3.5-sonnet', name: 'Claude 3.5 Sonnet', description: 'Anthropic 模型' },
            { id: 'llama-3.3-70b', name: 'Llama 3.3 70B', description: '开源大模型' },
        ];
        this.conversationHistory = [];
        this.isInitialized = false;
    }

    /**
     * 初始化 g4f 客户端
     */
    async init() {
        if (this.isInitialized) return true;

        try {
            // 动态加载 g4f 客户端
            const module = await import('https://g4f.dev/dist/js/client.js');
            this.client = new module.default();
            this.isInitialized = true;
            console.log('AI Assistant initialized successfully');
            return true;
        } catch (error) {
            console.error('Failed to initialize AI Assistant:', error);
            return false;
        }
    }

    /**
     * 发送聊天消息
     */
    async chat(message, options = {}) {
        if (!this.isInitialized) {
            await this.init();
        }

        const model = options.model || this.model;
        const systemPrompt = options.systemPrompt || this.getDefaultSystemPrompt();

        try {
            // 添加到对话历史
            this.conversationHistory.push({ role: 'user', content: message });

            const result = await this.client.chat.completions.create({
                model: model,
                messages: [
                    { role: 'system', content: systemPrompt },
                    ...this.conversationHistory
                ],
                temperature: options.temperature || 0.7,
                max_tokens: options.maxTokens || 2000,
            });

            const response = result.choices[0].message.content;
            
            // 添加助手回复到历史
            this.conversationHistory.push({ role: 'assistant', content: response });

            return {
                success: true,
                content: response,
                model: model
            };
        } catch (error) {
            console.error('Chat error:', error);
            return {
                success: false,
                error: error.message || 'AI 调用失败，请稍后重试'
            };
        }
    }

    /**
     * 流式聊天（支持打字机效果）
     */
    async *chatStream(message, options = {}) {
        if (!this.isInitialized) {
            await this.init();
        }

        const model = options.model || this.model;
        const systemPrompt = options.systemPrompt || this.getDefaultSystemPrompt();

        try {
            this.conversationHistory.push({ role: 'user', content: message });

            const stream = await this.client.chat.completions.create({
                model: model,
                messages: [
                    { role: 'system', content: systemPrompt },
                    ...this.conversationHistory
                ],
                stream: true,
                temperature: options.temperature || 0.7,
            });

            let fullResponse = '';
            for await (const chunk of stream) {
                const content = chunk.choices[0]?.delta?.content || '';
                if (content) {
                    fullResponse += content;
                    yield { type: 'chunk', content: content };
                }
            }

            this.conversationHistory.push({ role: 'assistant', content: fullResponse });
            yield { type: 'done', content: fullResponse };

        } catch (error) {
            yield { type: 'error', error: error.message };
        }
    }

    /**
     * 优化点子描述
     */
    async optimizeIdea(ideaData) {
        const prompt = `请帮我优化以下 AI 点子的描述，使其更加清晰、专业、有吸引力：

标题：${ideaData.title}
分类：${ideaData.category}
当前描述：${ideaData.description}
需要的资源：${ideaData.neededResources || '未填写'}
预期成果：${ideaData.expectedOutcome || '未填写'}

请从以下几个方面进行优化：
1. 点子背景和动机
2. 核心创新点
3. 技术可行性分析
4. 预期价值和影响
5. 实施建议

请用中文回复，格式清晰。`;

        return await this.chat(prompt, {
            systemPrompt: '你是一位 AI 产品专家和技术顾问，擅长帮助用户完善和优化 AI 项目点子。'
        });
    }

    /**
     * 生成标签建议
     */
    async suggestTags(content, type = 'idea') {
        const prompt = `请根据以下内容，生成 5-10 个合适的标签：

类型：${type === 'idea' ? '点子' : '资源'}
内容：${content}

要求：
1. 标签要准确反映内容主题
2. 包含技术领域标签（如：NLP、CV、LLM等）
3. 包含应用场景标签（如：智能客服、图像生成等）
4. 标签简洁，每个 2-8 个字
5. 只输出标签，用逗号分隔`;

        const result = await this.chat(prompt, {
            systemPrompt: '你是一位标签分类专家，擅长为内容生成准确的分类标签。',
            maxTokens: 200
        });

        if (result.success) {
            // 解析标签
            const tags = result.content
                .split(/[,，、\n]/)
                .map(tag => tag.trim())
                .filter(tag => tag.length > 0 && tag.length <= 10);
            return { success: true, tags: tags };
        }
        return result;
    }

    /**
     * 推荐相关资源
     */
    async recommendResources(ideaDescription, availableResources) {
        const prompt = `根据以下点子需求，从可用资源列表中推荐最相关的资源：

点子描述：
${ideaDescription}

可用资源：
${availableResources.map((r, i) => `${i + 1}. ${r.title} - ${r.description?.substring(0, 100)}...`).join('\n')}

请推荐 3-5 个最相关的资源，并说明推荐理由。格式：
- 资源编号: 推荐理由`;

        return await this.chat(prompt, {
            systemPrompt: '你是一位 AI 资源匹配专家，擅长根据项目需求推荐合适的资源。'
        });
    }

    /**
     * 匹配点子和资源
     */
    async matchIdeaResource(idea, resource) {
        const prompt = `分析以下点子和资源的匹配度：

点子：
- 标题：${idea.title}
- 描述：${idea.description}
- 需要的资源：${idea.neededResources}

资源：
- 标题：${resource.title}
- 描述：${resource.description}
- 分类：${resource.category}

请分析：
1. 匹配度评分（0-100分）
2. 匹配理由
3. 使用建议`;

        return await this.chat(prompt, {
            systemPrompt: '你是一位项目匹配专家，擅长分析点子和资源的契合度。'
        });
    }

    /**
     * 清空对话历史
     */
    clearHistory() {
        this.conversationHistory = [];
    }

    /**
     * 获取默认系统提示
     */
    getDefaultSystemPrompt() {
        return `你是 AI共创社区的 AI 助手，帮助用户：
1. 完善和优化 AI 点子
2. 推荐合适的 AI 资源
3. 匹配点子和资源
4. 回答 AI 相关问题

请用中文回复，语言简洁专业。`;
    }

    /**
     * 获取可用模型列表
     */
    getAvailableModels() {
        return this.availableModels;
    }

    /**
     * 设置模型
     */
    setModel(modelId) {
        this.model = modelId;
    }
}

// 导出全局实例
window.AIAssistant = AIAssistant;
