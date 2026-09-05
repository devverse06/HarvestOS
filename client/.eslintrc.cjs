module.exports = {
    root: true,
    parser: '@typescript-eslint/parser',
    parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        ecmaFeatures: { jsx: true },
    },
    env: {
        browser: true,
        es2021: true,
        node: true,
    },
    plugins: ['@typescript-eslint'],
    rules: {
        'no-unreachable': 'error',
        'no-constant-condition': 'error',
        '@typescript-eslint/no-explicit-any': 'off',
        '@typescript-eslint/no-unused-vars': 'off',
    },
};
