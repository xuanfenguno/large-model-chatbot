/**
 * 图片URL工具 - 自动纠正图片URL为相对路径
 * 这样无论后端运行在哪个端口，都能通过Vite代理正确访问
 */

/**
 * 将绝对URL转换为相对路径
 * 例如: http://127.0.0.1:8000/media/xxx -> /media/xxx
 * 例如: http://127.0.0.1:8080/media/xxx -> /media/xxx
 */
export function normalizeImageUrl(url) {
  if (!url) return null
  
  // 如果已经是相对路径，直接返回
  if (url.startsWith('/media/') || url.startsWith('/api/')) {
    return url
  }
  
  try {
    // 解析URL，提取路径部分
    const parsed = new URL(url)
    return parsed.pathname + parsed.search
  } catch {
    // 如果解析失败，返回原始URL
    return url
  }
}

/**
 * 批量规范化消息中的图片URL
 */
export function normalizeMessagesImageUrls(messages) {
  return messages.map(msg => ({
    ...msg,
    image_url: normalizeImageUrl(msg.image_url)
  }))
}
