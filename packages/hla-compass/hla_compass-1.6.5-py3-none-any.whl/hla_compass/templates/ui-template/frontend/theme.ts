/**
 * Theme utilities for SDK UI template
 * Mirrors platform frontend/src/design-system/theme.ts (simplified)
 */

import { theme as antdTheme } from 'antd';

export type ThemeMode = 'light' | 'dark' | 'high-contrast' | 'system';

export const getSystemTheme = (): 'light' | 'dark' => {
  if (typeof window === 'undefined') return 'light';
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
};

export const applyTheme = (mode: ThemeMode) => {
  if (typeof document === 'undefined') return;
  const actualMode = mode === 'system' ? getSystemTheme() : mode;
  // set class on body to leverage variables.css theme sections
  document.body.classList.remove('light-theme', 'dark-theme', 'high-contrast-theme');
  document.body.classList.add(`${actualMode}-theme`);
  // Smooth transition helper
  document.body.classList.add('theme-transition');
  setTimeout(() => document.body.classList.remove('theme-transition'), 300);
};

export const createAntdTheme = (mode: ThemeMode) => {
  const actualMode = mode === 'system' ? getSystemTheme() : mode;
  const isDark = actualMode === 'dark' || actualMode === 'high-contrast';
  return {
    algorithm: isDark ? antdTheme.darkAlgorithm : antdTheme.defaultAlgorithm,
    cssVar: true,
    token: {
      // Keep token values minimal; host platform overrides when embedded
      colorPrimary: getComputedStyle(document.documentElement)
        .getPropertyValue('--color-primary') || '#0052cc',
      borderRadius: 8,
      fontFamily: getComputedStyle(document.documentElement)
        .getPropertyValue('--font-sans') || '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    },
  } as any;
};
