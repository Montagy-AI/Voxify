import api from './api';
import { DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES } from '../config/languages';

class LanguageService {
  // 从后端获取支持的语言列表
  async getSupportedLanguages() {
    try {
      const response = await api.get('/voice/languages');
      if (response.data.success) {
        return response.data.data;
      }
      throw new Error('Failed to fetch languages');
    } catch (error) {
      console.warn(
        'Failed to fetch languages from server, using local config:',
        error
      );
      // 回退到本地配置
      return {
        languages: SUPPORTED_LANGUAGES.map((lang) => ({
          code: lang.code,
          name: lang.name,
          native_name: lang.nativeName,
        })),
        total: SUPPORTED_LANGUAGES.length,
      };
    }
  }

  // 验证语言代码
  async validateLanguage(languageCode) {
    try {
      const response = await api.post('/voice/languages/validate', {
        language: languageCode,
      });
      return response.data;
    } catch (error) {
      console.warn(
        'Failed to validate language on server, using local validation:',
        error
      );
      // 回退到本地验证
      const isValid = SUPPORTED_LANGUAGES.some(
        (lang) => lang.code === languageCode
      );
      return {
        success: true,
        data: {
          language: languageCode,
          is_valid: isValid,
          supported_languages: !isValid
            ? SUPPORTED_LANGUAGES.map((l) => l.code)
            : null,
        },
      };
    }
  }

  // 获取默认语言
  getDefaultLanguage() {
    return DEFAULT_LANGUAGE;
  }

  // 本地语言验证（不需要网络请求）
  isValidLanguageLocal(languageCode) {
    return SUPPORTED_LANGUAGES.some((lang) => lang.code === languageCode);
  }

  // 获取语言信息
  getLanguageInfo(languageCode) {
    return SUPPORTED_LANGUAGES.find((lang) => lang.code === languageCode);
  }

  // 获取用户首选语言（基于浏览器设置）
  getUserPreferredLanguage() {
    const browserLang = navigator.language || navigator.userLanguage;

    // 尝试完全匹配
    let match = SUPPORTED_LANGUAGES.find((lang) => lang.code === browserLang);
    if (match) return match.code;

    // 尝试语言前缀匹配（如 'en' 匹配 'en-US'）
    const langPrefix = browserLang.split('-')[0];
    match = SUPPORTED_LANGUAGES.find((lang) =>
      lang.code.startsWith(langPrefix)
    );
    if (match) return match.code;

    // 回退到默认语言
    return DEFAULT_LANGUAGE;
  }

  // 保存用户语言偏好到本地存储
  saveUserLanguagePreference(languageCode) {
    if (this.isValidLanguageLocal(languageCode)) {
      localStorage.setItem('user_preferred_language', languageCode);
    }
  }

  // 从本地存储获取用户语言偏好
  getUserLanguagePreference() {
    const saved = localStorage.getItem('user_preferred_language');
    if (saved && this.isValidLanguageLocal(saved)) {
      return saved;
    }
    return this.getUserPreferredLanguage();
  }
}

const languageService = new LanguageService();
export default languageService;
