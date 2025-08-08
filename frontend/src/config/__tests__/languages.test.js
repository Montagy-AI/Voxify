import '@testing-library/jest-dom';
import languagesConfig, {
  SUPPORTED_LANGUAGES,
  DEFAULT_LANGUAGE,
  LANGUAGE_GROUPS,
  SUPPORT_LEVEL_INFO,
  getLanguageInfo,
  isValidLanguage,
  getLanguageOptions,
  getLanguageSupportLevel,
  isNativeSupported,
  isSpecializedSupported,
  isFallbackSupported,
  getSupportLevelInfo,
  getLanguagesByLevel,
  SAMPLE_TEXTS,
} from '../languages';

describe('Languages Configuration', () => {
  /*
   * Constants Tests
   */
  describe('Constants', () => {
    test('SUPPORTED_LANGUAGES contains expected languages', () => {
      expect(SUPPORTED_LANGUAGES).toBeDefined();
      expect(Array.isArray(SUPPORTED_LANGUAGES)).toBe(true);
      expect(SUPPORTED_LANGUAGES.length).toBeGreaterThan(0);
      
      // Check for key languages
      const languageCodes = SUPPORTED_LANGUAGES.map(lang => lang.code);
      expect(languageCodes).toContain('en-US');
      expect(languageCodes).toContain('zh-CN');
      expect(languageCodes).toContain('ja-JP');
      expect(languageCodes).toContain('fr-FR');
    });

    test('DEFAULT_LANGUAGE is set correctly', () => {
      expect(DEFAULT_LANGUAGE).toBe('zh-CN');
      expect(SUPPORTED_LANGUAGES.some(lang => lang.code === DEFAULT_LANGUAGE)).toBe(true);
    });

    test('LANGUAGE_GROUPS contains all supported languages', () => {
      const allGroupedLanguages = Object.values(LANGUAGE_GROUPS).flat();
      const supportedLanguageCodes = SUPPORTED_LANGUAGES.map(lang => lang.code);
      
      expect(allGroupedLanguages.sort()).toEqual(supportedLanguageCodes.sort());
    });

    test('SUPPORT_LEVEL_INFO contains all support levels', () => {
      expect(SUPPORT_LEVEL_INFO).toHaveProperty('native');
      expect(SUPPORT_LEVEL_INFO).toHaveProperty('specialized');
      expect(SUPPORT_LEVEL_INFO).toHaveProperty('fallback');
      
      // Check structure of support level info
      Object.values(SUPPORT_LEVEL_INFO).forEach(info => {
        expect(info).toHaveProperty('label');
        expect(info).toHaveProperty('description');
        expect(info).toHaveProperty('emoji');
        expect(info).toHaveProperty('color');
      });
    });

    test('SAMPLE_TEXTS contains sample text for all languages', () => {
      const languageCodes = SUPPORTED_LANGUAGES.map(lang => lang.code);
      languageCodes.forEach(code => {
        expect(SAMPLE_TEXTS).toHaveProperty(code);
        expect(typeof SAMPLE_TEXTS[code]).toBe('string');
        expect(SAMPLE_TEXTS[code].length).toBeGreaterThan(0);
      });
    });
  });

  /*
   * Language Structure Tests
   */
  describe('Language Structure', () => {
    test('each language has required properties', () => {
      SUPPORTED_LANGUAGES.forEach(lang => {
        expect(lang).toHaveProperty('code');
        expect(lang).toHaveProperty('name');
        expect(lang).toHaveProperty('nativeName');
        expect(lang).toHaveProperty('flag');
        expect(lang).toHaveProperty('supportLevel');
        
        expect(typeof lang.code).toBe('string');
        expect(typeof lang.name).toBe('string');
        expect(typeof lang.nativeName).toBe('string');
        expect(typeof lang.flag).toBe('string');
        expect(['native', 'specialized', 'fallback']).toContain(lang.supportLevel);
      });
    });

    test('language codes are unique', () => {
      const codes = SUPPORTED_LANGUAGES.map(lang => lang.code);
      const uniqueCodes = [...new Set(codes)];
      expect(codes.length).toBe(uniqueCodes.length);
    });

    test('language codes follow expected format', () => {
      SUPPORTED_LANGUAGES.forEach(lang => {
        expect(lang.code).toMatch(/^[a-z]{2}-[A-Z]{2}$/);
      });
    });
  });

  /*
   * getLanguageInfo Tests
   */
  describe('getLanguageInfo', () => {
    test('returns correct language info for valid code', () => {
      const englishInfo = getLanguageInfo('en-US');
      expect(englishInfo).toBeDefined();
      expect(englishInfo.code).toBe('en-US');
      expect(englishInfo.name).toBe('English (US)');
      expect(englishInfo.supportLevel).toBe('native');
    });

    test('returns default language for invalid code', () => {
      const invalidInfo = getLanguageInfo('invalid-code');
      expect(invalidInfo).toBeDefined();
      expect(invalidInfo.code).toBe(DEFAULT_LANGUAGE);
    });

    test('handles null and undefined input', () => {
      const nullInfo = getLanguageInfo(null);
      expect(nullInfo.code).toBe(DEFAULT_LANGUAGE);
      
      const undefinedInfo = getLanguageInfo(undefined);
      expect(undefinedInfo.code).toBe(DEFAULT_LANGUAGE);
    });

    test('returns correct info for all supported languages', () => {
      SUPPORTED_LANGUAGES.forEach(expectedLang => {
        const info = getLanguageInfo(expectedLang.code);
        expect(info).toEqual(expectedLang);
      });
    });
  });

  /*
   * isValidLanguage Tests
   */
  describe('isValidLanguage', () => {
    test('returns true for valid language codes', () => {
      expect(isValidLanguage('en-US')).toBe(true);
      expect(isValidLanguage('zh-CN')).toBe(true);
      expect(isValidLanguage('ja-JP')).toBe(true);
    });

    test('returns false for invalid language codes', () => {
      expect(isValidLanguage('invalid-code')).toBe(false);
      expect(isValidLanguage('en')).toBe(false);
      expect(isValidLanguage('EN-US')).toBe(false);
    });

    test('handles null and undefined input', () => {
      expect(isValidLanguage(null)).toBe(false);
      expect(isValidLanguage(undefined)).toBe(false);
      expect(isValidLanguage('')).toBe(false);
    });

    test('validates all supported languages', () => {
      SUPPORTED_LANGUAGES.forEach(lang => {
        expect(isValidLanguage(lang.code)).toBe(true);
      });
    });
  });

  /*
   * getLanguageOptions Tests
   */
  describe('getLanguageOptions', () => {
    test('returns flat array when includeGroups is false', () => {
      const options = getLanguageOptions(false, true);
      expect(Array.isArray(options)).toBe(true);
      expect(options.length).toBe(SUPPORTED_LANGUAGES.length);
      
      options.forEach(option => {
        expect(option).toHaveProperty('value');
        expect(option).toHaveProperty('label');
        expect(option).toHaveProperty('searchLabel');
        expect(option).toHaveProperty('supportLevel');
        expect(option).toHaveProperty('supportInfo');
      });
    });

    test('returns grouped array when includeGroups is true', () => {
      const groupedOptions = getLanguageOptions(true, true);
      expect(Array.isArray(groupedOptions)).toBe(true);
      expect(groupedOptions.length).toBe(Object.keys(LANGUAGE_GROUPS).length);
      
      groupedOptions.forEach(group => {
        expect(group).toHaveProperty('label');
        expect(group).toHaveProperty('options');
        expect(Array.isArray(group.options)).toBe(true);
      });
    });

    test('includes support level indicators when showSupportLevel is true', () => {
      const options = getLanguageOptions(false, true);
      options.forEach(option => {
        expect(option.label).toMatch(/[🔵🟡🟠]/); // Should contain emoji
      });
    });

    test('excludes support level indicators when showSupportLevel is false', () => {
      const options = getLanguageOptions(false, false);
      options.forEach(option => {
        expect(option.label).not.toMatch(/[🔵🟡🟠]/); // Should not contain emoji
      });
    });

    test('maintains correct language data in options', () => {
      const options = getLanguageOptions(false, true);
      const englishOption = options.find(opt => opt.value === 'en-US');
      
      expect(englishOption).toBeDefined();
      expect(englishOption.value).toBe('en-US');
      expect(englishOption.supportLevel).toBe('native');
      expect(englishOption.label).toContain('🇺🇸');
      expect(englishOption.label).toContain('English (United States)');
    });
  });

  /*
   * Support Level Tests
   */
  describe('Support Level Functions', () => {
    test('getLanguageSupportLevel returns correct support levels', () => {
      expect(getLanguageSupportLevel('en-US')).toBe('native');
      expect(getLanguageSupportLevel('zh-CN')).toBe('native');
      expect(getLanguageSupportLevel('ja-JP')).toBe('specialized');
      expect(getLanguageSupportLevel('ko-KR')).toBe('fallback');
      expect(getLanguageSupportLevel('invalid')).toBe('native'); // Returns default language level
    });

    test('isNativeSupported correctly identifies native languages', () => {
      expect(isNativeSupported('en-US')).toBe(true);
      expect(isNativeSupported('zh-CN')).toBe(true);
      expect(isNativeSupported('en-GB')).toBe(true);
      expect(isNativeSupported('zh-TW')).toBe(true);
      
      expect(isNativeSupported('ja-JP')).toBe(false);
      expect(isNativeSupported('ko-KR')).toBe(false);
    });

    test('isSpecializedSupported correctly identifies specialized languages', () => {
      expect(isSpecializedSupported('ja-JP')).toBe(true);
      expect(isSpecializedSupported('fr-FR')).toBe(true);
      expect(isSpecializedSupported('de-DE')).toBe(true);
      expect(isSpecializedSupported('es-ES')).toBe(true);
      
      expect(isSpecializedSupported('en-US')).toBe(false);
      expect(isSpecializedSupported('ko-KR')).toBe(false);
    });

    test('isFallbackSupported correctly identifies fallback languages', () => {
      expect(isFallbackSupported('ko-KR')).toBe(true);
      expect(isFallbackSupported('pt-BR')).toBe(true);
      expect(isFallbackSupported('ar-SA')).toBe(true);
      expect(isFallbackSupported('th-TH')).toBe(true);
      
      expect(isFallbackSupported('en-US')).toBe(false);
      expect(isFallbackSupported('ja-JP')).toBe(false);
    });

    test('getSupportLevelInfo returns correct info object', () => {
      const nativeInfo = getSupportLevelInfo('en-US');
      expect(nativeInfo).toEqual(SUPPORT_LEVEL_INFO.native);
      
      const specializedInfo = getSupportLevelInfo('ja-JP');
      expect(specializedInfo).toEqual(SUPPORT_LEVEL_INFO.specialized);
      
      const fallbackInfo = getSupportLevelInfo('ko-KR');
      expect(fallbackInfo).toEqual(SUPPORT_LEVEL_INFO.fallback);
    });

    test('getSupportLevelInfo handles invalid language codes', () => {
      const invalidInfo = getSupportLevelInfo('invalid');
      expect(invalidInfo).toEqual(SUPPORT_LEVEL_INFO.native); // Should return default language info
    });
  });

  /*
   * getLanguagesByLevel Tests
   */
  describe('getLanguagesByLevel', () => {
    test('returns correctly grouped languages by support level', () => {
      const groupedByLevel = getLanguagesByLevel();
      
      expect(groupedByLevel).toHaveProperty('native');
      expect(groupedByLevel).toHaveProperty('specialized');
      expect(groupedByLevel).toHaveProperty('fallback');
      
      expect(Array.isArray(groupedByLevel.native)).toBe(true);
      expect(Array.isArray(groupedByLevel.specialized)).toBe(true);
      expect(Array.isArray(groupedByLevel.fallback)).toBe(true);
    });

    test('all languages are categorized correctly', () => {
      const groupedByLevel = getLanguagesByLevel();
      const totalGroupedLanguages = 
        groupedByLevel.native.length + 
        groupedByLevel.specialized.length + 
        groupedByLevel.fallback.length;
      
      expect(totalGroupedLanguages).toBe(SUPPORTED_LANGUAGES.length);
    });

    test('languages are in correct support level groups', () => {
      const groupedByLevel = getLanguagesByLevel();
      
      // Check native languages
      groupedByLevel.native.forEach(lang => {
        expect(lang.supportLevel).toBe('native');
      });
      
      // Check specialized languages
      groupedByLevel.specialized.forEach(lang => {
        expect(lang.supportLevel).toBe('specialized');
      });
      
      // Check fallback languages
      groupedByLevel.fallback.forEach(lang => {
        expect(lang.supportLevel).toBe('fallback');
      });
    });

    test('expected languages are in correct groups', () => {
      const groupedByLevel = getLanguagesByLevel();
      
      const nativeCodes = groupedByLevel.native.map(lang => lang.code);
      expect(nativeCodes).toContain('en-US');
      expect(nativeCodes).toContain('zh-CN');
      
      const specializedCodes = groupedByLevel.specialized.map(lang => lang.code);
      expect(specializedCodes).toContain('ja-JP');
      expect(specializedCodes).toContain('fr-FR');
      
      const fallbackCodes = groupedByLevel.fallback.map(lang => lang.code);
      expect(fallbackCodes).toContain('ko-KR');
      expect(fallbackCodes).toContain('pt-BR');
    });
  });

  /*
   * Sample Texts Tests
   */
  describe('Sample Texts', () => {
    test('sample texts exist for all supported languages', () => {
      SUPPORTED_LANGUAGES.forEach(lang => {
        expect(SAMPLE_TEXTS).toHaveProperty(lang.code);
        expect(typeof SAMPLE_TEXTS[lang.code]).toBe('string');
        expect(SAMPLE_TEXTS[lang.code].trim().length).toBeGreaterThan(0);
      });
    });

    test('sample texts contain meaningful content', () => {
      // Test a few specific languages for meaningful content
      expect(SAMPLE_TEXTS['en-US']).toContain('English');
      expect(SAMPLE_TEXTS['zh-CN']).toContain('中文');
      expect(SAMPLE_TEXTS['ja-JP']).toContain('日本語');
      expect(SAMPLE_TEXTS['fr-FR']).toContain('française');
    });

    test('sample texts are reasonable length', () => {
      Object.values(SAMPLE_TEXTS).forEach(text => {
        expect(text.length).toBeGreaterThan(20); // Not too short
        expect(text.length).toBeLessThan(200); // Not too long
      });
    });
  });

  /*
   * Language Groups Consistency Tests
   */
  describe('Language Groups Consistency', () => {
    test('LANGUAGE_GROUPS matches support levels', () => {
      const nativeGroup = LANGUAGE_GROUPS['原生支持 (最佳质量)'];
      nativeGroup.forEach(code => {
        const lang = getLanguageInfo(code);
        expect(lang.supportLevel).toBe('native');
      });

      const specializedGroup = LANGUAGE_GROUPS['专用模型支持 (高质量)'];
      specializedGroup.forEach(code => {
        const lang = getLanguageInfo(code);
        expect(lang.supportLevel).toBe('specialized');
      });

      const fallbackGroup = LANGUAGE_GROUPS['基础支持 (有限效果)'];
      fallbackGroup.forEach(code => {
        const lang = getLanguageInfo(code);
        expect(lang.supportLevel).toBe('fallback');
      });
    });

    test('no duplicate languages across groups', () => {
      const allGroupedLanguages = Object.values(LANGUAGE_GROUPS).flat();
      const uniqueLanguages = [...new Set(allGroupedLanguages)];
      expect(allGroupedLanguages.length).toBe(uniqueLanguages.length);
    });
  });

  /*
   * Default Export Tests
   */
  describe('Default Export', () => {
    test('default export contains all expected properties', () => {
      expect(languagesConfig).toHaveProperty('SUPPORTED_LANGUAGES');
      expect(languagesConfig).toHaveProperty('DEFAULT_LANGUAGE');
      expect(languagesConfig).toHaveProperty('LANGUAGE_GROUPS');
      expect(languagesConfig).toHaveProperty('SUPPORT_LEVEL_INFO');
      expect(languagesConfig).toHaveProperty('getLanguageInfo');
      expect(languagesConfig).toHaveProperty('isValidLanguage');
      expect(languagesConfig).toHaveProperty('getLanguageOptions');
      expect(languagesConfig).toHaveProperty('getLanguageSupportLevel');
      expect(languagesConfig).toHaveProperty('isNativeSupported');
      expect(languagesConfig).toHaveProperty('isSpecializedSupported');
      expect(languagesConfig).toHaveProperty('isFallbackSupported');
      expect(languagesConfig).toHaveProperty('getSupportLevelInfo');
      expect(languagesConfig).toHaveProperty('getLanguagesByLevel');
      expect(languagesConfig).toHaveProperty('SAMPLE_TEXTS');
    });

    test('default export functions work correctly', () => {
      expect(languagesConfig.isValidLanguage('en-US')).toBe(true);
      expect(languagesConfig.getLanguageInfo('zh-CN').name).toBe('Chinese (Simplified)');
      expect(languagesConfig.isNativeSupported('en-US')).toBe(true);
    });
  });

  /*
   * Edge Cases and Error Handling Tests
   */
  describe('Edge Cases and Error Handling', () => {
    test('functions handle empty string input', () => {
      expect(isValidLanguage('')).toBe(false);
      expect(getLanguageInfo('')).toEqual(getLanguageInfo(DEFAULT_LANGUAGE));
      expect(getLanguageSupportLevel('')).toBe('native'); // Default language level
    });

    test('functions handle malformed language codes', () => {
      const malformedCodes = ['en', 'EN-US', 'en-us', 'english', '123-456'];
      
      malformedCodes.forEach(code => {
        expect(isValidLanguage(code)).toBe(false);
        expect(getLanguageInfo(code)).toEqual(getLanguageInfo(DEFAULT_LANGUAGE));
      });
    });

    test('functions are consistent with each other', () => {
      SUPPORTED_LANGUAGES.forEach(lang => {
        expect(isValidLanguage(lang.code)).toBe(true);
        expect(getLanguageInfo(lang.code)).toEqual(lang);
        expect(getLanguageSupportLevel(lang.code)).toBe(lang.supportLevel);
      });
    });
  });

  /*
   * Performance and Memory Tests
   */
  describe('Performance and Memory', () => {
    test('functions do not mutate original data', () => {
      const originalLanguages = [...SUPPORTED_LANGUAGES];
      const originalGroups = { ...LANGUAGE_GROUPS };
      
      // Call various functions
      getLanguageOptions(true, true);
      getLanguagesByLevel();
      getLanguageInfo('en-US');
      
      // Check data hasn't been mutated
      expect(SUPPORTED_LANGUAGES).toEqual(originalLanguages);
      expect(LANGUAGE_GROUPS).toEqual(originalGroups);
    });

    test('repeated function calls return consistent results', () => {
      const code = 'en-US';
      const result1 = getLanguageInfo(code);
      const result2 = getLanguageInfo(code);
      const result3 = getLanguageInfo(code);
      
      expect(result1).toEqual(result2);
      expect(result2).toEqual(result3);
    });
  });
});
