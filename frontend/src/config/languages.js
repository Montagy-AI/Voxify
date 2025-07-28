export const SUPPORTED_LANGUAGES = [
  // 原生多语言支持 (F5TTS_v1_Base) - 最佳质量
  {
    code: 'zh-CN',
    name: 'Chinese (Simplified)',
    nativeName: '中文 (简体)',
    flag: '🇨🇳',
    supportLevel: 'native',
  },
  {
    code: 'zh-TW',
    name: 'Chinese (Traditional)',
    nativeName: '中文 (繁體)',
    flag: '🇹🇼',
    supportLevel: 'native',
  },
  {
    code: 'en-US',
    name: 'English (US)',
    nativeName: 'English (United States)',
    flag: '🇺🇸',
    supportLevel: 'native',
  },
  {
    code: 'en-GB',
    name: 'English (UK)',
    nativeName: 'English (United Kingdom)',
    flag: '🇬🇧',
    supportLevel: 'native',
  },

  // 专用模型支持 - 高质量但需要特定模型
  {
    code: 'ja-JP',
    name: 'Japanese',
    nativeName: '日本語',
    flag: '🇯🇵',
    supportLevel: 'specialized',
  },
  {
    code: 'fr-FR',
    name: 'French',
    nativeName: 'Français',
    flag: '🇫🇷',
    supportLevel: 'specialized',
  },
  {
    code: 'de-DE',
    name: 'German',
    nativeName: 'Deutsch',
    flag: '🇩🇪',
    supportLevel: 'specialized',
  },
  {
    code: 'es-ES',
    name: 'Spanish',
    nativeName: 'Español',
    flag: '🇪🇸',
    supportLevel: 'specialized',
  },
  {
    code: 'it-IT',
    name: 'Italian',
    nativeName: 'Italiano',
    flag: '🇮🇹',
    supportLevel: 'specialized',
  },
  {
    code: 'ru-RU',
    name: 'Russian',
    nativeName: 'Русский',
    flag: '🇷🇺',
    supportLevel: 'specialized',
  },
  {
    code: 'hi-IN',
    name: 'Hindi',
    nativeName: 'हिन्दी',
    flag: '🇮🇳',
    supportLevel: 'specialized',
  },

  // Fallback支持 - 基础支持，效果可能有限
  {
    code: 'ko-KR',
    name: 'Korean',
    nativeName: '한국어',
    flag: '🇰🇷',
    supportLevel: 'fallback',
  },
  {
    code: 'pt-BR',
    name: 'Portuguese (Brazil)',
    nativeName: 'Português (Brasil)',
    flag: '🇧🇷',
    supportLevel: 'fallback',
  },
  {
    code: 'ar-SA',
    name: 'Arabic',
    nativeName: 'العربية',
    flag: '🇸🇦',
    supportLevel: 'fallback',
  },
  {
    code: 'th-TH',
    name: 'Thai',
    nativeName: 'ไทย',
    flag: '🇹🇭',
    supportLevel: 'fallback',
  },
  {
    code: 'vi-VN',
    name: 'Vietnamese',
    nativeName: 'Tiếng Việt',
    flag: '🇻🇳',
    supportLevel: 'fallback',
  },
];

export const DEFAULT_LANGUAGE = 'zh-CN';

export const LANGUAGE_GROUPS = {
  '原生支持 (最佳质量)': ['zh-CN', 'zh-TW', 'en-US', 'en-GB'],
  '专用模型支持 (高质量)': [
    'ja-JP',
    'fr-FR',
    'de-DE',
    'es-ES',
    'it-IT',
    'ru-RU',
    'hi-IN',
  ],
  '基础支持 (有限效果)': ['ko-KR', 'pt-BR', 'ar-SA', 'th-TH', 'vi-VN'],
};

// 支持级别映射
export const SUPPORT_LEVEL_INFO = {
  native: {
    label: '原生支持',
    description: '使用F5-TTS多语言基础模型，质量最佳',
    emoji: '🔵',
    color: 'text-blue-400',
  },
  specialized: {
    label: '专用模型',
    description: '使用特定语言的专用模型，高质量合成',
    emoji: '🟡',
    color: 'text-yellow-400',
  },
  fallback: {
    label: '基础支持',
    description: '使用基础模型进行合成，效果可能有限',
    emoji: '🟠',
    color: 'text-orange-400',
  },
};

export const getLanguageInfo = (code) => {
  return (
    SUPPORTED_LANGUAGES.find((lang) => lang.code === code) ||
    SUPPORTED_LANGUAGES.find((lang) => lang.code === DEFAULT_LANGUAGE)
  );
};

export const isValidLanguage = (code) => {
  return SUPPORTED_LANGUAGES.some((lang) => lang.code === code);
};

export const getLanguageOptions = (
  includeGroups = false,
  showSupportLevel = true
) => {
  if (!includeGroups) {
    return SUPPORTED_LANGUAGES.map((lang) => {
      const supportInfo = SUPPORT_LEVEL_INFO[lang.supportLevel];
      const levelIndicator = showSupportLevel ? ` ${supportInfo.emoji}` : '';

      return {
        value: lang.code,
        label: `${lang.flag} ${lang.nativeName}${levelIndicator}`,
        searchLabel: `${lang.name} ${lang.nativeName}`,
        supportLevel: lang.supportLevel,
        supportInfo: supportInfo,
      };
    });
  }

  const groupedOptions = [];
  Object.entries(LANGUAGE_GROUPS).forEach(([groupName, codes]) => {
    groupedOptions.push({
      label: groupName,
      options: codes.map((code) => {
        const lang = getLanguageInfo(code);
        const supportInfo = SUPPORT_LEVEL_INFO[lang.supportLevel];
        const levelIndicator = showSupportLevel ? ` ${supportInfo.emoji}` : '';

        return {
          value: lang.code,
          label: `${lang.flag} ${lang.nativeName}${levelIndicator}`,
          searchLabel: `${lang.name} ${lang.nativeName}`,
          supportLevel: lang.supportLevel,
          supportInfo: supportInfo,
        };
      }),
    });
  });

  return groupedOptions;
};

export const SAMPLE_TEXTS = {
  'en-US':
    'Hello, this is a test of English speech synthesis. The weather is beautiful today.',
  'en-GB':
    'Good day! This is a demonstration of British English voice synthesis technology.',
  'zh-CN': '你好，这是中文语音合成的测试。今天天气很好。',
  'zh-TW': '您好，這是繁體中文語音合成的測試。今天天氣很好。',
  'ja-JP':
    'こんにちは。これは日本語の音声合成テストです。今日はとても良い天気ですね。',
  'ko-KR':
    '안녕하세요. 이것은 한국어 음성 합성 테스트입니다. 오늘 날씨가 정말 좋네요.',
  'fr-FR':
    "Bonjour, ceci est un test de synthèse vocale française. Il fait très beau aujourd'hui.",
  'de-DE':
    'Hallo, das ist ein Test der deutschen Sprachsynthese. Das Wetter ist heute wunderschön.',
  'es-ES':
    'Hola, esta es una prueba de síntesis de voz en español. Hace muy buen tiempo hoy.',
  'it-IT':
    "Ciao, questo è un test di sintesi vocale italiana. Oggi c'è un tempo bellissimo.",
  'pt-BR':
    'Olá, este é um teste de síntese de voz em português brasileiro. O tempo está lindo hoje.',
  'ru-RU': 'Привет, это тест русского синтеза речи. Сегодня прекрасная погода.',
  'ar-SA': 'مرحبا، هذا اختبار لتخليق الكلام العربي. الطقس جميل اليوم.',
  'hi-IN':
    'नमस्ते, यह हिंदी भाषा संश्लेषण का परीक्षण है। आज मौसम बहुत अच्छा है।',
  'th-TH': 'สวัสดี นี่คือการทดสอบการสังเคราะห์เสียงภาษาไทย วันนี้อากาศดีมากเลย',
  'vi-VN':
    'Xin chào, đây là bài kiểm tra tổng hợp giọng nói tiếng Việt. Hôm nay thời tiết rất đẹp.',
};

// 获取语言支持级别
export const getLanguageSupportLevel = (code) => {
  const lang = getLanguageInfo(code);
  return lang ? lang.supportLevel : 'unknown';
};

// 检查是否为原生支持的语言
export const isNativeSupported = (code) => {
  return getLanguageSupportLevel(code) === 'native';
};

// 检查是否为专用模型支持的语言
export const isSpecializedSupported = (code) => {
  return getLanguageSupportLevel(code) === 'specialized';
};

// 检查是否为fallback支持的语言
export const isFallbackSupported = (code) => {
  return getLanguageSupportLevel(code) === 'fallback';
};

// 获取支持级别信息
export const getSupportLevelInfo = (code) => {
  const level = getLanguageSupportLevel(code);
  return SUPPORT_LEVEL_INFO[level] || null;
};

// 按支持级别分组语言
export const getLanguagesByLevel = () => {
  const grouped = {
    native: [],
    specialized: [],
    fallback: [],
  };

  SUPPORTED_LANGUAGES.forEach((lang) => {
    const level = lang.supportLevel;
    if (grouped[level]) {
      grouped[level].push(lang);
    }
  });

  return grouped;
};

const languagesConfig = {
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
};

export default languagesConfig;
