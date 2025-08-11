module.exports = {
  extends: ['eslint:recommended', 'react-app', 'react-app/jest'],
  rules: {
    'jsx-a11y/no-redundant-roles': 'off', // Disable redundant roles rule
      'no-duplicate-imports': 'error', // Prevent duplicate imports
    'no-useless-return': 'error', // Prevent unnecessary return statements
    'no-else-return': 'error', // Disallow else blocks after return in if
    'prefer-template': 'error', // Prefer template literals over string concatenation
  },
};
