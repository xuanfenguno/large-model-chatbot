<template>
  <div class="markdown-renderer" v-html="renderedContent"></div>
</template>

<script setup>
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'
import 'katex/dist/katex.min.css'
import markdownItTexmath from 'markdown-it-texmath'

// 引入 katex 用于数学公式渲染
import katex from 'katex'

// 创建 markdown-it 实例并配置插件
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: function (str, lang) {
    // 代码高亮
    if (lang && hljs.getLanguage(lang)) {
      try {
        return `<pre class="hljs"><code>${hljs.highlight(str, { language: lang, ignoreIllegals: true }).value}</code></pre>`
      } catch (__) {}
    }
    return `<pre class="hljs"><code>${md.utils.escapeHtml(str)}</code></pre>`
  }
})

// 配置数学公式支持
md.use(markdownItTexmath, {
  engine: katex,
  delimiters: 'dollars',
  katexOptions: {
    macros: {
      '\\RR': '\\mathbb{R}',
      '\\NN': '\\mathbb{N}',
      '\\ZZ': '\\mathbb{Z}',
      '\\QQ': '\\mathbb{Q}',
      '\\CC': '\\mathbb{C}'
    }
  }
})

// 支持行内公式 $...$ 和块级公式 $$...$$
md.use(markdownItTexmath, {
  engine: katex,
  delimiters: 'brackets',
  katexOptions: {
    throwOnError: false
  }
})

const props = defineProps({
  source: {
    type: String,
    default: ''
  },
  streaming: {
    type: Boolean,
    default: false
  }
})

const cleanStreamingMarkdown = (text) => {
  if (!text) return ''
  
  let cleaned = text
  
  // 移除末尾未完成的加粗符号 **
  cleaned = cleaned.replace(/\*\*$/, '')
  
  // 移除末尾未完成的斜体符号 *
  cleaned = cleaned.replace(/(?<!\*)\*(?!\*)$/, '')
  
  // 移除末尾未完成的删除线 ~~
  cleaned = cleaned.replace(/~~$/, '')
  
  // 移除末尾未完成的行内代码 `
  cleaned = cleaned.replace(/`$/, '')
  
  // 移除末尾未完成的链接 [text](
  cleaned = cleaned.replace(/\[[^\]]*\]\($/, '')
  
  // 移除末尾未完成的图片 ![alt](
  cleaned = cleaned.replace(/!\[[^\]]*\]\($/, '')
  
  // 移除末尾未完成的标题 #
  cleaned = cleaned.replace(/#+\s*$/, '')
  
  // 移除末尾未完成的任务列表 - [ ] 或 - [x]
  cleaned = cleaned.replace(/-\s+\[[ xX]\]\s*$/, '- ')
  
  // 移除末尾未完成的无序列表符号
  cleaned = cleaned.replace(/^[-*+]\s*$/, '')
  
  // 移除末尾未完成的有序列表 1. 
  cleaned = cleaned.replace(/^\d+\.\s*$/, '')
  
  // 移除末尾未完成的引用 >
  cleaned = cleaned.replace(/^>\s*$/, '')
  
  // 移除末尾未完成的表格分隔符 |
  cleaned = cleaned.replace(/\|\s*$/, '')
  
  // 移除末尾未完成的水平线 ---
  cleaned = cleaned.replace(/-{3,}$/, '')
  cleaned = cleaned.replace(/\*{3,}$/, '')
  
  return cleaned
}

const renderedContent = computed(() => {
  if (!props.source) return ''
  try {
    const contentToRender = props.streaming ? cleanStreamingMarkdown(props.source) : props.source
    return md.render(contentToRender)
  } catch (error) {
    console.error('Markdown 渲染错误:', error)
    return props.source
  }
})
</script>

<style scoped>
.markdown-renderer {
  line-height: 1.2;
  color: #606266;
  font-size: 13px;
}

/* 代码块样式 */
.markdown-renderer :deep(pre) {
  background: #f6f8fa;
  border-radius: 3px;
  padding: 6px;
  overflow-x: auto;
  margin: 0.05em 0;
  border: 1px solid #eaecef;
  font-size: 11px;
}

.markdown-renderer :deep(code) {
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 11px;
  background: rgba(27, 31, 35, 0.05);
  padding: 0.05em 0.15em;
  border-radius: 2px;
}

.markdown-renderer :deep(pre code) {
  background: transparent;
  padding: 0;
  color: #24292e;
}

/* 行内代码样式 */
.markdown-renderer :deep(p code) {
  background: #f6f8fa;
  color: #e83e8c;
}

/* 数学公式样式 */
.markdown-renderer :deep(.katex) {
  font-size: 1em;
}

.markdown-renderer :deep(.katex-display) {
  overflow-x: auto;
  overflow-y: hidden;
  padding: 0.05em 0;
}

/* 表格样式 */
.markdown-renderer :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 0.05em 0;
  display: block;
  overflow-x: auto;
  font-size: 11px;
}

.markdown-renderer :deep(th),
.markdown-renderer :deep(td) {
  border: 1px solid #dfe2e5;
  padding: 2px 4px;
}

.markdown-renderer :deep(tr:nth-child(2n)) {
  background-color: #f6f8fa;
}

/* 引用块样式 */
.markdown-renderer :deep(blockquote) {
  border-left: 2px solid #667eea;
  padding-left: 0.3em;
  margin: 0.02em 0;
  color: #6a737d;
  font-style: italic;
  font-size: 12px;
}

.markdown-renderer :deep(blockquote p) {
  margin: 0;
}

/* 列表样式 */
.markdown-renderer :deep(ul),
.markdown-renderer :deep(ol) {
  padding-left: 1em;
  margin: 0;
}

.markdown-renderer :deep(li) {
  margin: 0;
  padding: 0.005em 0;
  line-height: 1.1;
}

.markdown-renderer :deep(li p) {
  margin: 0;
}

/* 嵌套列表样式 */
.markdown-renderer :deep(li > ul),
.markdown-renderer :deep(li > ol) {
  margin: 0;
  padding-left: 1em;
}

/* 图片样式 */
.markdown-renderer :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 3px;
  margin: 0.02em 0;
}

/* 链接样式 */
.markdown-renderer :deep(a) {
  color: #667eea;
  text-decoration: none;
}

.markdown-renderer :deep(a:hover) {
  text-decoration: underline;
}

/* 标题样式 */
.markdown-renderer :deep(h1),
.markdown-renderer :deep(h2),
.markdown-renderer :deep(h3),
.markdown-renderer :deep(h4),
.markdown-renderer :deep(h5),
.markdown-renderer :deep(h6) {
  margin: 0.01em 0;
  font-weight: 600;
  line-height: 1;
  color: #24292e;
}

.markdown-renderer :deep(h1) {
  font-size: 1.4em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.02em;
}

.markdown-renderer :deep(h2) {
  font-size: 1.2em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.02em;
}

.markdown-renderer :deep(h3) {
  font-size: 1em;
}

.markdown-renderer :deep(h4) {
  font-size: 0.9em;
}

.markdown-renderer :deep(h5) {
  font-size: 0.85em;
}

.markdown-renderer :deep(h6) {
  font-size: 0.8em;
  color: #6a737d;
}

/* 段落样式 */
.markdown-renderer :deep(p) {
  margin: 0;
  padding: 0.005em 0;
}

/* 水平线样式 */
.markdown-renderer :deep(hr) {
  border: 0;
  border-top: 1px solid #eaecef;
  margin: 0.02em 0;
}
</style>
