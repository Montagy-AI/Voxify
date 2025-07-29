import languageService from './language.service';
import api from './api';
import { DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES } from '../config/languages';

// Mock the api module
jest.mock('./api');

// Mock the languages config
jest.mock('../config/languages', () => ({
    DEFAULT_LANGUAGE: 'en',
    SUPPORTED_LANGUAGES: [
        { code: 'en', name: 'English', nativeName: 'English' },
        { code: 'es', name: 'Spanish', nativeName: 'Español' },
        { code: 'fr', name: 'French', nativeName: 'Français' },
        { code: 'de', name: 'German', nativeName: 'Deutsch' },
        { code: 'zh', name: 'Chinese', nativeName: '中文' }
    ]
}));

// Mock localStorage
const localStorageMock = (() => {
    let store = {};
    return {
        getItem: jest.fn((key) => store[key] || null),
        setItem: jest.fn((key, value) => {
            store[key] = value.toString();
        }),
        removeItem: jest.fn((key) => {
            delete store[key];
        }),
        clear: jest.fn(() => {
            store = {};
        })
    };
})();

Object.defineProperty(window, 'localStorage', {
    value: localStorageMock
});

// Mock navigator.language
Object.defineProperty(window, 'navigator', {
    value: {
        language: 'en-US',
        userLanguage: 'en-US'
    },
    writable: true
});

describe('LanguageService', () => {
    beforeEach(() => {
        // Clear all mocks before each test
        jest.clearAllMocks();
        localStorageMock.clear();
        // Reset navigator.language to default
        Object.defineProperty(window, 'navigator', {
            value: {
                language: 'en-US',
                userLanguage: 'en-US'
            },
            writable: true
        });
    });

    describe('getSupportedLanguages', () => {
        test('Return languages from API when successful', async () => {
            const mockApiResponse = {
                data: {
                    success: true,
                    data: {
                        languages: [
                            { code: 'en', name: 'English', native_name: 'English' },
                            { code: 'es', name: 'Spanish', native_name: 'Español' }
                        ],
                        total: 2
                    }
                }
            };
            api.get.mockResolvedValue(mockApiResponse);
            const result = await languageService.getSupportedLanguages();
            expect(api.get).toHaveBeenCalledWith('/voice/languages');
            expect(result).toEqual(mockApiResponse.data.data);
        });

        test('Fall back to local config when API fails', async () => {
            api.get.mockRejectedValue(new Error('Network error'));
            const result = await languageService.getSupportedLanguages();
            expect(result).toEqual({
                languages: SUPPORTED_LANGUAGES.map(lang => ({
                    code: lang.code,
                    name: lang.name,
                    native_name: lang.nativeName
                })),
                total: SUPPORTED_LANGUAGES.length
            });
        });

        test('Fall back to local config when API returns unsuccessful response', async () => {
            const mockApiResponse = {
                data: {
                    success: false
                }
            };
            api.get.mockResolvedValue(mockApiResponse);
            const result = await languageService.getSupportedLanguages();
            expect(result.languages).toHaveLength(SUPPORTED_LANGUAGES.length);
            expect(result.total).toBe(SUPPORTED_LANGUAGES.length);
        });

        test('Log warning when API fails', async () => {
            const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
            api.get.mockRejectedValue(new Error('Network error'));
            await languageService.getSupportedLanguages();
            expect(consoleSpy).toHaveBeenCalledWith(
                'Failed to fetch languages from server, using local config:',
                expect.any(Error)
            );
            consoleSpy.mockRestore();
        });
    });

    describe('validateLanguage', () => {
        test('Validate language via API when successful', async () => {
            const mockApiResponse = {
                data: {
                    success: true,
                    data: {
                        language: 'en',
                        is_valid: true
                    }
                }
            };
            api.post.mockResolvedValue(mockApiResponse);
            const result = await languageService.validateLanguage('en');
            expect(api.post).toHaveBeenCalledWith('/voice/languages/validate', {
                language: 'en'
            });
            expect(result).toEqual(mockApiResponse.data);
        });

        test('Fall back to local validation when API fails', async () => {
            api.post.mockRejectedValue(new Error('Network error'));
            const result = await languageService.validateLanguage('en');
            expect(result).toEqual({
                success: true,
                data: {
                    language: 'en',
                    is_valid: true,
                    supported_languages: null
                }
            });
        });

        test('Return invalid result with supported languages for invalid code', async () => {
            api.post.mockRejectedValue(new Error('Network error'));
            const result = await languageService.validateLanguage('invalid');
            expect(result.data.is_valid).toBe(false);
            expect(result.data.supported_languages).toEqual(['en', 'es', 'fr', 'de', 'zh']);
        });

        test('Log warning when API validation fails', async () => {
            const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
            api.post.mockRejectedValue(new Error('Network error'));
            await languageService.validateLanguage('en');
            expect(consoleSpy).toHaveBeenCalledWith(
                'Failed to validate language on server, using local validation:',
                expect.any(Error)
            );
            consoleSpy.mockRestore();
        });
    });

    describe('getDefaultLanguage', () => {
        test('Return the default language', () => {
            const result = languageService.getDefaultLanguage();
            expect(result).toBe(DEFAULT_LANGUAGE);
        });
    });

    describe('isValidLanguageLocal', () => {
        test('Return true for valid language codes', () => {
            expect(languageService.isValidLanguageLocal('en')).toBe(true);
            expect(languageService.isValidLanguageLocal('es')).toBe(true);
            expect(languageService.isValidLanguageLocal('fr')).toBe(true);
        });

        test('Return false for invalid language codes', () => {
            expect(languageService.isValidLanguageLocal('invalid')).toBe(false);
            expect(languageService.isValidLanguageLocal('xx')).toBe(false);
            expect(languageService.isValidLanguageLocal('')).toBe(false);
            expect(languageService.isValidLanguageLocal(null)).toBe(false);
        });
    });

    describe('getLanguageInfo', () => {
        test('Return language info for valid codes', () => {
            const result = languageService.getLanguageInfo('en');
            expect(result).toEqual({
                code: 'en',
                name: 'English',
                nativeName: 'English'
            });
        });

        test('Return undefined for invalid codes', () => {
            const result = languageService.getLanguageInfo('invalid');
            expect(result).toBeUndefined();
        });

        test('Return correct info for all supported languages', () => {
            SUPPORTED_LANGUAGES.forEach(lang => {
                const result = languageService.getLanguageInfo(lang.code);
                expect(result).toEqual(lang);
            });
        });
    });

    describe('getUserPreferredLanguage', () => {
        test('Return exact match when browser language is supported', () => {
            Object.defineProperty(window, 'navigator', {
                value: { language: 'es', userLanguage: 'es' },
                writable: true
            });
            const result = languageService.getUserPreferredLanguage();
            expect(result).toBe('es');
        });

        test('Return prefix match when exact match not found', () => {
            Object.defineProperty(window, 'navigator', {
                value: { language: 'en-GB', userLanguage: 'en-GB' },
                writable: true
            });
            const result = languageService.getUserPreferredLanguage();
            expect(result).toBe('en');
        });

        test('Return default language when no match found', () => {
            Object.defineProperty(window, 'navigator', {
                value: { language: 'ja-JP', userLanguage: 'ja-JP' },
                writable: true
            });
            const result = languageService.getUserPreferredLanguage();
            expect(result).toBe(DEFAULT_LANGUAGE);
        });

        test('Handle missing navigator.language gracefully', () => {
            Object.defineProperty(window, 'navigator', {
                value: { language: undefined, userLanguage: 'fr' },
                writable: true
            });
            const result = languageService.getUserPreferredLanguage();
            expect(result).toBe('fr');
        });

        test('Fall back to default when both language properties are missing', () => {
            Object.defineProperty(window, 'navigator', {
                value: { language: undefined, userLanguage: undefined },
                writable: true
            });
            const result = languageService.getUserPreferredLanguage();
            expect(result).toBe(DEFAULT_LANGUAGE);
        });
    });

    describe('saveUserLanguagePreference', () => {
        test('Save valid language preference to localStorage', () => {
            languageService.saveUserLanguagePreference('es');
            expect(localStorageMock.setItem).toHaveBeenCalledWith('user_preferred_language', 'es');
        });

        test('Do not save invalid language preference', () => {
            languageService.saveUserLanguagePreference('invalid');
            
            expect(localStorageMock.setItem).not.toHaveBeenCalled();
        });

        test('Save all supported languages correctly', () => {
            SUPPORTED_LANGUAGES.forEach(lang => {
                languageService.saveUserLanguagePreference(lang.code);
                expect(localStorageMock.setItem).toHaveBeenCalledWith('user_preferred_language', lang.code);
            });
        });
    });

    describe('getUserLanguagePreference', () => {
        test('Returns saved preference when valid', () => {
            // Set up localStorage to contain the preference
            localStorageMock.getItem.mockReturnValue('fr');
            const result = languageService.getUserLanguagePreference();
            expect(result).toBe('fr');
        });

        test('Fall back to browser preference when saved preference is invalid', () => {
            localStorageMock.getItem.mockReturnValue('invalid');
            Object.defineProperty(window, 'navigator', {
                value: { language: 'de', userLanguage: 'de' },
                writable: true
            });
            const result = languageService.getUserLanguagePreference();
            expect(result).toBe('de');
        });

        test('Fall back to browser preference when no saved preference', () => {
            localStorageMock.getItem.mockReturnValue(null);
            Object.defineProperty(window, 'navigator', {
                value: { language: 'zh', userLanguage: 'zh' },
                writable: true
            });
            const result = languageService.getUserLanguagePreference();
            expect(result).toBe('zh');
        });

        test('Return default when both saved and browser preferences are invalid', () => {
            localStorageMock.getItem.mockReturnValue('invalid');
            Object.defineProperty(window, 'navigator', {
                value: { language: 'ja-JP', userLanguage: 'ja-JP' },
                writable: true
            });
            const result = languageService.getUserLanguagePreference();
            expect(result).toBe(DEFAULT_LANGUAGE);
        });
    });

    describe('Integration Tests', () => {
        test('Complete workflow: validate, save, and retrieve preference', async () => {
            // Validate language
            api.post.mockResolvedValue({
                data: {
                    success: true,
                    data: { language: 'es', is_valid: true }
                }
            });
            const validation = await languageService.validateLanguage('es');
            expect(validation.data.is_valid).toBe(true);
            // Save preference
            languageService.saveUserLanguagePreference('es');
            expect(localStorageMock.setItem).toHaveBeenCalledWith('user_preferred_language', 'es');
            // Mock localStorage to return the saved preference
            localStorageMock.getItem.mockReturnValue('es');
            // Retrieve preference
            const preference = languageService.getUserLanguagePreference();
            expect(preference).toBe('es');
        });

        test('Handle API failures gracefully in workflow', async () => {
            // API validation fails, but local validation succeeds
            api.post.mockRejectedValue(new Error('Network error'));
            const validation = await languageService.validateLanguage('fr');
            expect(validation.data.is_valid).toBe(true);
            // Save and retrieve still work
            languageService.saveUserLanguagePreference('fr');
            localStorageMock.getItem.mockReturnValue('fr');
            const preference = languageService.getUserLanguagePreference();
            expect(preference).toBe('fr');
        });
    });

    describe('Error Handling', () => {
        test('Handle localStorage errors gracefully', () => {
            // Mock localStorage.setItem to throw an error
            localStorageMock.setItem.mockImplementation(() => {
                throw new Error('Storage quota exceeded');
            });
            // Add spy for console.warn to verify error handling
            const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
            // Should not throw
            expect(() => {
                languageService.saveUserLanguagePreference('en');
            }).not.toThrow();
            // Should log a warning
            expect(consoleSpy).toHaveBeenCalledWith(
                'Failed to save language preference to localStorage:',
                expect.any(Error)
            );
            consoleSpy.mockRestore();
        });

        test('Handle API timeout scenarios', async () => {
            const timeoutError = new Error('Timeout');
            timeoutError.code = 'ECONNABORTED';
            api.get.mockRejectedValue(timeoutError);
            const result = await languageService.getSupportedLanguages();
            expect(result.languages).toHaveLength(SUPPORTED_LANGUAGES.length);
        });
    });
});
