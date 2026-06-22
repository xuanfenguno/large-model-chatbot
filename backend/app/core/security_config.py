"""
安全配置模块
包含各种安全相关的配置和策略
"""

# API 速率限制配置
RATE_LIMIT_CONFIG = {
    # 聊天相关
    'chat_api': {
        'max_requests': 30,      # 每分钟最大请求数
        'window_size': 60,       # 时间窗口（秒）
        'block_malicious': True  # 是否阻止恶意请求
    },
    'stream_chat_api': {
        'max_requests': 30,
        'window_size': 60,
        'block_malicious': True
    },
    
    # 用户认证相关
    'login_api': {
        'max_requests': 10,       # 5分钟内最多10次登录尝试（开发环境放宽）
        'window_size': 300,
        'block_malicious': False  # 开发环境设为False，避免误判正常登录
    },
    'register_api': {
        'max_requests': 3,       # 1小时内最多3次注册
        'window_size': 3600,
        'block_malicious': True
    },
    'password_reset_request_api': {
        'max_requests': 3,       # 5分钟内最多3次密码重置请求
        'window_size': 300,
        'block_malicious': True
    },
    'password_reset_api': {
        'max_requests': 5,       # 5分钟内最多5次密码重置尝试
        'window_size': 300,
        'block_malicious': True
    },
    
    # 功能相关
    'function_router_api': {
        'max_requests': 20,
        'window_size': 60,
        'block_malicious': True
    },
    
    # 测试相关
    'test_password_reset_api': {
        'max_requests': 10,      # 每分钟最多10次测试重置请求
        'window_size': 60,
        'block_malicious': True
    }
}

# 输入验证配置
INPUT_VALIDATION_CONFIG = {
    'max_message_length': 5000,      # 消息最大长度
    'max_image_url_length': 2000,    # 图片URL最大长度
    'max_model_name_length': 100,    # 模型名称最大长度
    'max_input_length': 2000,        # 输入最大长度
    'dangerous_patterns': [
        r'<script', r'javascript:', r'on\w+\s*=', r'eval\(', r'document\.cookie',
        r'window\.location', r'expression\(', r'<iframe', r'<object', r'<embed',
        r'\\<script', r'\\<iframe', r'\\<object', r'\\<embed'  # 转义版本
    ]
}

# 数据清理配置
DATA_CLEANUP_CONFIG = {
    'auto_clean_old_conversations': True,    # 自动清理旧对话
    'conversation_retention_days': 30,       # 对话保留天数
    'auto_clean_old_password_resets': True,  # 自动清理旧密码重置令牌
    'password_reset_token_expiry_hours': 1,  # 密码重置令牌过期时间（小时）
}

# 安全日志配置
SECURITY_LOGGING_CONFIG = {
    'enable_security_logging': True,         # 启用安全日志
    'log_suspicious_activities': True,       # 记录可疑活动
    'log_rate_limit_exceeded': True,         # 记录速率限制超出
    'log_malicious_requests': True,          # 记录恶意请求
    'security_log_level': 'WARNING'          # 安全日志级别
}

# IP 黑名单配置
IP_BLACKLIST_CONFIG = {
    'enable_ip_blacklist': True,             # 启用IP黑名单
    'auto_block_suspicious_ips': True,       # 自动封禁可疑IP
    'blacklist_duration_minutes': 10,        # 黑名单持续时间（分钟，默认10分钟，适合开发环境）
    'max_failed_attempts_per_ip': 10,        # 每个IP的最大失败尝试次数
}