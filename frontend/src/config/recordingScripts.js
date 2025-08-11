// Recording scripts configuration - currently supports Chinese and English only
export const recordingScripts = {
  'zh-CN': [
    '今天天气真不错，适合出去散步。',
    '我很喜欢听音乐，特别是古典音乐。', 
    '学习新技能让我感到很充实和快乐。',
    '阅读是我最喜欢的休闲活动之一。',
    '每天早晨的咖啡时光总是让我感到放松。',
    '与朋友聊天是一件非常愉快的事情。',
    '我喜欢在安静的环境中思考问题。',
    '运动让我保持健康和积极的心态。'
  ],
  'en-US': [
    'The weather is beautiful today, perfect for a walk.',
    'I love listening to music, especially classical pieces.',
    'Learning new skills makes me feel fulfilled and happy.',
    'Reading is one of my favorite leisure activities.',
    'My morning coffee time always helps me feel relaxed.',
    'Chatting with friends is always a delightful experience.',
    'I enjoy thinking quietly in a peaceful environment.',
    'Exercise helps me maintain a healthy and positive mindset.'
  ],
  'en-GB': [
    'The weather is lovely today, brilliant for a stroll.',
    'I adore listening to music, particularly classical compositions.',
    'Learning new skills makes me feel quite fulfilled and cheerful.',
    'Reading is amongst my favourite pastimes.',
    'My morning tea time always helps me feel rather relaxed.',
    'Having a chat with mates is always a wonderful experience.',
    'I quite enjoy pondering quietly in a tranquil setting.',
    'Exercise helps me maintain a healthy and optimistic outlook.'
  ]
};

// Function to get random script
export const getRandomScript = (language) => {
  const scripts = recordingScripts[language];
  if (!scripts || scripts.length === 0) {
    // If language not supported, return English default
    return recordingScripts['en-US'][0];
  }
  
  const randomIndex = Math.floor(Math.random() * scripts.length);
  return scripts[randomIndex];
};

// Check if language supports recording feature
export const isRecordingSupported = (language) => {
  return language in recordingScripts;
};