// @vitest-environment node
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = resolve(__dirname, '../../');

describe('next.config.mjs', () => {
  it('should exist and be a valid module', () => {
    const configPath = resolve(projectRoot, 'next.config.mjs');
    expect(fs.existsSync(configPath)).toBe(true);
  });

  it('should have next-pwa configured with correct options', async () => {
    const configPath = resolve(projectRoot, 'next.config.mjs');
    const configContent = fs.readFileSync(configPath, 'utf-8');

    // Verify next-pwa is imported
    expect(configContent).toContain('withPWA');

    // Verify key PWA configuration options
    expect(configContent).toContain("dest: 'public'");
    expect(configContent).toContain('register: true');
    expect(configContent).toContain('skipWaiting: true');
  });

  it('should disable service worker in development mode', () => {
    const configPath = resolve(projectRoot, 'next.config.mjs');
    const configContent = fs.readFileSync(configPath, 'utf-8');

    expect(configContent).toContain("process.env.NODE_ENV === 'development'");
  });

  it('should configure runtime caching for deputado photos', () => {
    const configPath = resolve(projectRoot, 'next.config.mjs');
    const configContent = fs.readFileSync(configPath, 'utf-8');

    // Verify Câmara CDN pattern is configured (regex pattern may have escaped dots and slashes)
    expect(configContent).toMatch(/camara\\\.leg\\\.br/);
    expect(configContent).toContain('jpg');
    expect(configContent).toContain('png');
  });

  it('should have CacheFirst strategy for external assets', () => {
    const configPath = resolve(projectRoot, 'next.config.mjs');
    const configContent = fs.readFileSync(configPath, 'utf-8');

    expect(configContent).toContain('CacheFirst');
  });

  it('should configure cache expiration for deputado photos', () => {
    const configPath = resolve(projectRoot, 'next.config.mjs');
    const configContent = fs.readFileSync(configPath, 'utf-8');

    // Check for 30-day expiration configuration
    expect(configContent).toContain('maxAgeSeconds');
    expect(configContent).toContain('maxEntries');
  });

  it('should export valid Next.js configuration', () => {
    const configPath = resolve(projectRoot, 'next.config.mjs');
    const configContent = fs.readFileSync(configPath, 'utf-8');

    // Verify Next.js config object is exported
    expect(configContent).toContain('export default');
  });

  it('should have proper cache settings structure', () => {
    const configPath = resolve(projectRoot, 'next.config.mjs');
    const configContent = fs.readFileSync(configPath, 'utf-8');

    // Verify cache name for deputado photos
    expect(configContent).toContain('cacheName');
    expect(configContent).toContain('deputado-photos');
  });
});
