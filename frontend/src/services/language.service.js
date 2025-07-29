import api from './api';
import { DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES } from '../config/languages';

class LanguageService {
    // Get list of supported languages
    async getSupportedLanguages() {
        try {
            const response = await api.get('/voice/languages');
            if (response.data.success) {
                return response.data.data;
            }
            throw new Error('Failed to fetch languages');
        } catch (error) {
            console.warn('Failed to fetch languages from server, using local config:', error);
            // Fallback to local configuration
            return {
                languages: SUPPORTED_LANGUAGES.map(lang => ({
                    code: lang.code,
                    name: lang.name,
                    native_name: lang.nativeName
                })),
                total: SUPPORTED_LANGUAGES.length
            };
        }
    }

    // Verify language code against server
    async validateLanguage(languageCode) {
        try {
            const response = await api.post('/voice/languages/validate', {
                language: languageCode
            });
            return response.data;
        } catch (error) {
            console.warn('Failed to validate language on server, using local validation:', error);
            // Fallback to local validation
            const isValid = SUPPORTED_LANGUAGES.some(lang => lang.code === languageCode);
            return {
                success: true,
                data: {
                    language: languageCode,
                    is_valid: isValid,
                    supported_languages: !isValid ? SUPPORTED_LANGUAGES.map(l => l.code) : null
                }
            };
        }
    }

    getDefaultLanguage() {
        return DEFAULT_LANGUAGE;
    }

    isValidLanguageLocal(languageCode) {
        return SUPPORTED_LANGUAGES.some(lang => lang.code === languageCode);
    }

    getLanguageInfo(languageCode) {
        return SUPPORTED_LANGUAGES.find(lang => lang.code === languageCode);
    }

    getUserPreferredLanguage() {
        const browserLang = navigator.language || navigator.userLanguage;
        
        // If no browser language is available, return default
        if (!browserLang) {
            return DEFAULT_LANGUAGE;
        }
        
        // Try an exact match first
        let match = SUPPORTED_LANGUAGES.find(lang => lang.code === browserLang);
        if (match) return match.code;

        // Try language prefix matching (e.g. 'en' matches 'en-US')
        const langPrefix = browserLang.split('-')[0];
        match = SUPPORTED_LANGUAGES.find(lang => lang.code.startsWith(langPrefix));
        if (match) return match.code;

        // Fallback to default language
        return DEFAULT_LANGUAGE;
    }

    saveUserLanguagePreference(languageCode) {
        if (this.isValidLanguageLocal(languageCode)) {
            try {
                localStorage.setItem('user_preferred_language', languageCode);
            } catch (error) {
                console.warn('Failed to save language preference to localStorage:', error);
            }
        }
    }

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