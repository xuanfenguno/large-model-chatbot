/**
 * 国际化语言包管理工具
 * 
 * 此文件为外包开发预留的语言包接口框架
 * 后续开发人员需要实现完整的国际化功能
 * 
 * 功能需求：
 * 1. 支持多语言动态切换
 * 2. 支持语言包热加载
 * 3. 支持语言包按需加载
 * 4. 支持语言包版本管理
 * 5. 支持语言包回退机制
 */

// 语言包配置
const languageConfig = {
  // 支持的语言列表
  supportedLanguages: [
    { code: 'zh', name: '中文', flag: '🇨🇳' },
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'ja', name: '日本語', flag: '🇯🇵' },
    { code: 'ko', name: '한국어', flag: '🇰🇷' }
  ],
  
  // 默认语言
  defaultLanguage: 'zh',
  
  // 语言包存储路径
  languagePath: '/locales/',
  
  // 语言包文件命名规则
  fileNamePattern: '{lang}.json'
}

// 语言包存储
let currentLanguage = languageConfig.defaultLanguage
let languagePacks = {}

// 默认语言包内容
const defaultLanguagePack = {
  // 通用词汇
  common: {
    submit: {
      zh: '提交',
      en: 'Submit',
      ja: '送信',
      ko: '제출'
    },
    cancel: {
      zh: '取消',
      en: 'Cancel',
      ja: 'キャンセル',
      ko: '취소'
    },
    save: {
      zh: '保存',
      en: 'Save',
      ja: '保存',
      ko: '저장'
    },
    delete: {
      zh: '删除',
      en: 'Delete',
      ja: '削除',
      ko: '삭제'
    },
    edit: {
      zh: '编辑',
      en: 'Edit',
      ja: '編集',
      ko: '편집'
    },
    close: {
      zh: '关闭',
      en: 'Close',
      ja: '閉じる',
      ko: '닫기'
    },
    confirm: {
      zh: '确认',
      en: 'Confirm',
      ja: '確認',
      ko: '확인'
    },
    loading: {
      zh: '加载中...',
      en: 'Loading...',
      ja: '読み込み中...',
      ko: '로드 중...'
    },
    success: {
      zh: '成功',
      en: 'Success',
      ja: '成功',
      ko: '성공'
    },
    error: {
      zh: '错误',
      en: 'Error',
      ja: 'エラー',
      ko: '오류'
    }
  },
  // 导航栏
  nav: {
    home: {
      zh: '首页',
      en: 'Home',
      ja: 'ホーム',
      ko: '홈'
    },
    chat: {
      zh: '聊天',
      en: 'Chat',
      ja: 'チャット',
      ko: '채팅'
    },
    settings: {
      zh: '设置',
      en: 'Settings',
      ja: '設定',
      ko: '설정'
    },
    profile: {
      zh: '个人资料',
      en: 'Profile',
      ja: 'プロフィール',
      ko: '프로필'
    }
  },
  // 登录页面
  login: {
    title: {
      zh: '登录',
      en: 'Login',
      ja: 'ログイン',
      ko: '로그인'
    },
    username: {
      zh: '用户名',
      en: 'Username',
      ja: 'ユーザー名',
      ko: '사용자 이름'
    },
    password: {
      zh: '密码',
      en: 'Password',
      ja: 'パスワード',
      ko: '비밀번호'
    },
    rememberMe: {
      zh: '记住我',
      en: 'Remember Me',
      ja: 'ログイン状態を保持',
      ko: '로그인 상태 유지'
    },
    forgotPassword: {
      zh: '忘记密码？',
      en: 'Forgot Password?',
      ja: 'パスワードをお忘れですか？',
      ko: '비밀번호를 잊으셨나요?'
    },
    loginButton: {
      zh: '登录',
      en: 'Sign In',
      ja: 'サインイン',
      ko: '로그인'
    },
    registerLink: {
      zh: '还没有账户？立即注册',
      en: 'Don\'t have an account? Sign up now',
      ja: 'アカウントをお持ちでないですか？今すぐ登録',
      ko: '계정이 없으신가요? 지금 가입하세요'
    }
  },
  // 设置页面
  settings: {
    title: {
      zh: '设置',
      en: 'Settings',
      ja: '設定',
      ko: '설정'
    },
    general: {
      zh: '常规',
      en: 'General',
      ja: '一般',
      ko: '일반'
    },
    appearance: {
      zh: '外观',
      en: 'Appearance',
      ja: '外観',
      ko: '모양'
    },
    language: {
      zh: '语言',
      en: 'Language',
      ja: '言語',
      ko: '언어'
    },
    theme: {
      zh: '主题',
      en: 'Theme',
      ja: 'テーマ',
      ko: '테마'
    },
    security: {
      zh: '安全',
      en: 'Security',
      ja: 'セキュリティ',
      ko: '보안'
    }
  },
  // 聊天界面
  chat: {
    newChat: {
      zh: '新建聊天',
      en: 'New Chat',
      ja: '新しいチャット',
      ko: '새 채팅'
    },
    sendMessage: {
      zh: '发送消息',
      en: 'Send Message',
      ja: 'メッセージを送信',
      ko: '메시지 보내기'
    },
    placeholder: {
      zh: '请输入消息...',
      en: 'Type your message...',
      ja: 'メッセージを入力してください...',
      ko: '메시지를 입력하세요...'
    },
    attachment: {
      zh: '附件',
      en: 'Attachment',
      ja: '添付ファイル',
      ko: '첨부 파일'
    }
  },
  // 错误信息
  errors: {
    networkError: {
      zh: '网络错误，请检查连接',
      en: 'Network error, please check your connection',
      ja: 'ネットワークエラーです。接続を確認してください',
      ko: '네트워크 오류입니다. 연결을 확인해주세요'
    },
    unauthorized: {
      zh: '未授权，请重新登录',
      en: 'Unauthorized, please log in again',
      ja: '認証されていません。再度ログインしてください',
      ko: '권한이 없습니다. 다시 로그인해주세요'
    },
    serverError: {
      zh: '服务器错误，请稍后再试',
      en: 'Server error, please try again later',
      ja: 'サーバーエラーです。後ほど再試行してください',
      ko: '서버 오류입니다. 나중에 다시 시도해주세요'
    }
  }
};

/**
 * 初始化语言包系统
 * @param {string} lang - 初始语言代码
 */
export const initI18n = async (lang = languageConfig.defaultLanguage) => {
  try {
    // 加载默认语言包
    const defaultLang = languageConfig.defaultLanguage;
    languagePacks[defaultLang] = defaultLanguagePack;
    
    // 设置当前语言
    currentLanguage = lang;
    
    // 如果不是默认语言，尝试加载对应语言包
    if (lang !== defaultLang) {
      await loadLanguagePack(lang);
    }
    
    // 应用语言到HTML文档
    applyLanguageToDocument(lang);
    
    return true;
  } catch (error) {
    console.error('[i18n] 语言包初始化失败:', error);
    return false;
  }
};

/**
 * 切换语言
 * @param {string} lang - 目标语言代码
 */
export const switchLanguage = async (lang) => {
  try {
    if (!isLanguageSupported(lang)) {
      console.warn(`[i18n] 不支持的语言: ${lang}`);
      return false;
    }
    
    // 如果语言包不存在，先加载它
    if (!languagePacks[lang]) {
      await loadLanguagePack(lang);
    }
    
    console.log(`[i18n] 切换语言到: ${lang}`);
    currentLanguage = lang;
    
    // 应用语言到HTML文档
    applyLanguageToDocument(lang);
    
    // 触发语言切换事件
    window.dispatchEvent(new CustomEvent('languageChanged', { 
      detail: { language: lang } 
    }));
    
    // 保存用户选择的语言
    localStorage.setItem('selectedLanguage', lang);
    
    return true;
  } catch (error) {
    console.error('[i18n] 语言切换失败:', error);
    return false;
  }
};

/**
 * 获取翻译文本
 * @param {string} key - 翻译键 (例如 'common.submit' 或 'nav.home')
 * @param {Object} params - 参数对象
 * @returns {string} 翻译后的文本
 */
export const t = (key, params = {}) => {
  try {
    // 按照层级分割键
    const keys = key.split('.');
    let result = languagePacks[currentLanguage];
    
    // 如果当前语言包中没有找到对应语言包，则使用默认语言包
    if (!result) {
      result = languagePacks[languageConfig.defaultLanguage];
    }
    
    // 遍历层级结构找到对应的翻译文本
    for (const k of keys) {
      if (result && typeof result === 'object') {
        result = result[k];
      } else {
        result = undefined;
        break;
      }
    }
    
    // 如果找到了对应语言的翻译
    if (result && typeof result === 'object' && result[currentLanguage]) {
      let translation = result[currentLanguage];
      
      // 替换参数
      if (params && Object.keys(params).length > 0) {
        for (const [paramKey, paramValue] of Object.entries(params)) {
          translation = translation.replace(`{${paramKey}}`, paramValue);
        }
      }
      
      return translation;
    }
    
    // 如果找不到翻译，返回原始键名
    return key;
  } catch (error) {
    console.error(`[i18n] 翻译失败 - 键: ${key}`, error);
    return key;
  }
};

/**
 * 获取当前语言
 * @returns {string} 当前语言代码
 */
export const getCurrentLanguage = () => {
  return currentLanguage;
};

/**
 * 获取支持的语言列表
 * @returns {Array} 支持的语言列表
 */
export const getSupportedLanguages = () => {
  return [...languageConfig.supportedLanguages];
};

/**
 * 检查语言是否支持
 * @param {string} lang - 语言代码
 * @returns {boolean} 是否支持
 */
export const isLanguageSupported = (lang) => {
  return languageConfig.supportedLanguages.some(l => l.code === lang);
};

/**
 * 加载语言包
 * @param {string} lang - 语言代码
 */
export const loadLanguagePack = async (lang) => {
  try {
    console.log(`[i18n] 加载语言包: ${lang}`);
    
    // 检查是否已存在该语言包
    if (languagePacks[lang]) {
      return languagePacks[lang];
    }
    
    // 创建新的语言包，继承默认语言包的内容
    const basePack = JSON.parse(JSON.stringify(languagePacks[languageConfig.defaultLanguage] || defaultLanguagePack));
    
    // 这里可以扩展加载远程语言包的逻辑
    // 例如：从服务器下载特定语言的翻译文件
    // const response = await fetch(`${languageConfig.languagePath}${lang}.json`);
    // const remotePack = await response.json();
    
    // 合并远程语言包和基础语言包
    // languagePacks[lang] = { ...basePack, ...remotePack };
    
    // 对于现在，我们只使用基础语言包
    languagePacks[lang] = basePack;
    
    return languagePacks[lang];
  } catch (error) {
    console.error(`[i18n] 加载语言包失败: ${lang}`, error);
    
    // 如果加载失败，使用默认语言包作为备选
    if (!languagePacks[lang]) {
      languagePacks[lang] = languagePacks[languageConfig.defaultLanguage] || defaultLanguagePack;
    }
    
    return languagePacks[lang];
  }
};

/**
 * 语言包管理器类（供后续扩展使用）
 */
export class I18nManager {
  constructor(config = {}) {
    this.config = { ...languageConfig, ...config }
    this.currentLanguage = this.config.defaultLanguage
    this.languagePacks = {}
    this.listeners = new Set()
  }
  
  /**
   * 添加语言切换监听器
   */
  addListener(callback) {
    this.listeners.add(callback)
  }
  
  /**
   * 移除语言切换监听器
   */
  removeListener(callback) {
    this.listeners.delete(callback)
  }
  
  /**
   * 触发语言切换事件
   */
  emitLanguageChange(lang) {
    this.listeners.forEach(callback => {
      try {
        callback(lang)
      } catch (error) {
        console.error('[i18n] 监听器执行错误:', error)
      }
    })
  }
  
  /**
   * 获取语言包接口版本
   */
  getVersion() {
    return '1.0.0'
  }
}

// 默认导出实例
export default {
  initI18n,
  switchLanguage,
  t,
  getCurrentLanguage,
  getSupportedLanguages,
  isLanguageSupported,
  loadLanguagePack,
  I18nManager
}