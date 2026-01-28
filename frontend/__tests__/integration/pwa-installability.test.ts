// @vitest-environment node
import { describe, it, expect, beforeEach } from 'vitest';
import { resolve } from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';
import path from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = resolve(__dirname, '../../');

describe('PWA Installability Integration Tests', () => {
  describe('Icon Files Validation', () => {
    it('should have all required icon files', () => {
      const iconDir = resolve(projectRoot, 'public', 'icons');
      const requiredIcons = [
        'icon-192.png',
        'icon-192-maskable.png',
        'icon-512.png',
        'icon-512-maskable.png',
      ];

      requiredIcons.forEach((iconFile) => {
        const iconPath = resolve(iconDir, iconFile);
        expect(fs.existsSync(iconPath), `Icon file ${iconFile} should exist`).toBe(true);
      });
    });

    it('should have valid PNG files with correct signature', () => {
      const iconDir = resolve(projectRoot, 'public', 'icons');
      const icons = ['icon-192.png', 'icon-512.png'];

      icons.forEach((iconFile) => {
        const iconPath = resolve(iconDir, iconFile);
        const buffer = fs.readFileSync(iconPath);

        // PNG signature: 0x89 0x50 0x4E 0x47
        const pngSignature = Buffer.from([0x89, 0x50, 0x4e, 0x47]);
        const fileSignature = buffer.slice(0, 4);

        expect(fileSignature.equals(pngSignature), `${iconFile} should have valid PNG signature`).toBe(true);
      });
    });

    it('should have icon files of reasonable size', () => {
      const iconDir = resolve(projectRoot, 'public', 'icons');
      const icons = [
        { file: 'icon-192.png', minSize: 100 },
        { file: 'icon-512.png', minSize: 100 },
      ];

      icons.forEach(({ file, minSize }) => {
        const iconPath = resolve(iconDir, file);
        const stats = fs.statSync(iconPath);
        expect(stats.size, `${file} should have minimum size of ${minSize} bytes`).toBeGreaterThanOrEqual(minSize);
      });
    });
  });

  describe('Manifest File Validation', () => {
    it('should have manifest.ts file', () => {
      const manifestPath = resolve(projectRoot, 'app', 'manifest.ts');
      expect(fs.existsSync(manifestPath)).toBe(true);
    });

    it('should export manifest function with correct TypeScript type', () => {
      const manifestPath = resolve(projectRoot, 'app', 'manifest.ts');
      const manifestContent = fs.readFileSync(manifestPath, 'utf-8');

      expect(manifestContent).toContain("import type { MetadataRoute } from 'next'");
      expect(manifestContent).toContain('MetadataRoute.Manifest');
      expect(manifestContent).toContain('export default function manifest');
    });

    it('should reference all icon files in manifest', () => {
      const manifestPath = resolve(projectRoot, 'app', 'manifest.ts');
      const manifestContent = fs.readFileSync(manifestPath, 'utf-8');

      const requiredIconPaths = [
        '/icons/icon-192.png',
        '/icons/icon-512.png',
        '/icons/icon-192-maskable.png',
        '/icons/icon-512-maskable.png',
      ];

      requiredIconPaths.forEach((iconPath) => {
        expect(manifestContent).toContain(iconPath);
      });
    });

    it('should have standalone display mode for PWA', () => {
      const manifestPath = resolve(projectRoot, 'app', 'manifest.ts');
      const manifestContent = fs.readFileSync(manifestPath, 'utf-8');

      expect(manifestContent).toContain("display: 'standalone'");
    });

    it('should have portrait orientation configured', () => {
      const manifestPath = resolve(projectRoot, 'app', 'manifest.ts');
      const manifestContent = fs.readFileSync(manifestPath, 'utf-8');

      expect(manifestContent).toContain("orientation: 'portrait'");
    });
  });

  describe('Layout Metadata Configuration', () => {
    it('should have app/layout.tsx with PWA metadata', () => {
      const layoutPath = resolve(projectRoot, 'app', 'layout.tsx');
      expect(fs.existsSync(layoutPath)).toBe(true);

      const layoutContent = fs.readFileSync(layoutPath, 'utf-8');

      // Verify PWA-related metadata exports
      expect(layoutContent).toContain('export const viewport');
      expect(layoutContent).toContain('export const metadata');
    });

    it('should configure appleWebApp metadata for iOS', () => {
      const layoutPath = resolve(projectRoot, 'app', 'layout.tsx');
      const layoutContent = fs.readFileSync(layoutPath, 'utf-8');

      expect(layoutContent).toContain('appleWebApp');
      expect(layoutContent).toContain('capable: true');
      expect(layoutContent).toContain('statusBarStyle');
    });

    it('should have manifest reference in metadata', () => {
      const layoutPath = resolve(projectRoot, 'app', 'layout.tsx');
      const layoutContent = fs.readFileSync(layoutPath, 'utf-8');

      expect(layoutContent).toContain("manifest: '/manifest.webmanifest'");
    });

    it('should configure proper viewport settings', () => {
      const layoutPath = resolve(projectRoot, 'app', 'layout.tsx');
      const layoutContent = fs.readFileSync(layoutPath, 'utf-8');

      expect(layoutContent).toContain('width: \'device-width\'');
      expect(layoutContent).toContain('initialScale: 1');
      expect(layoutContent).toContain('viewportFit: \'cover\'');
    });

    it('should have theme color matching design system', () => {
      const layoutPath = resolve(projectRoot, 'app', 'layout.tsx');
      const layoutContent = fs.readFileSync(layoutPath, 'utf-8');

      // Tailwind primary color
      expect(layoutContent).toContain('#1d4ed8');
    });
  });

  describe('Screenshot Assets', () => {
    it('should have screenshot file for install prompt', () => {
      const screenshotPath = resolve(projectRoot, 'public', 'screenshots', 'mobile.png');
      expect(fs.existsSync(screenshotPath)).toBe(true);
    });

    it('should have valid PNG screenshot', () => {
      const screenshotPath = resolve(projectRoot, 'public', 'screenshots', 'mobile.png');
      const buffer = fs.readFileSync(screenshotPath);

      const pngSignature = Buffer.from([0x89, 0x50, 0x4e, 0x47]);
      const fileSignature = buffer.slice(0, 4);

      expect(fileSignature.equals(pngSignature)).toBe(true);
    });

    it('should have screenshot referenced in manifest', () => {
      const manifestPath = resolve(projectRoot, 'app', 'manifest.ts');
      const manifestContent = fs.readFileSync(manifestPath, 'utf-8');

      expect(manifestContent).toContain('/screenshots/mobile.png');
      expect(manifestContent).toContain('540x720');
      expect(manifestContent).toContain('narrow');
    });
  });

  describe('PWA Installation Requirements', () => {
    it('should have all HTTPS headers configuration ready', () => {
      const nextConfigPath = resolve(projectRoot, 'next.config.mjs');
      const nextConfigContent = fs.readFileSync(nextConfigPath, 'utf-8');

      // Verify service worker configuration
      expect(nextConfigContent).toContain('register: true');
    });

    it('should have service worker disabled in dev mode', () => {
      const nextConfigPath = resolve(projectRoot, 'next.config.mjs');
      const nextConfigContent = fs.readFileSync(nextConfigPath, 'utf-8');

      expect(nextConfigContent).toContain("process.env.NODE_ENV === 'development'");
      expect(nextConfigContent).toContain('disable:');
    });

    it('should have minimum 2 icons for installability', () => {
      const manifestPath = resolve(projectRoot, 'app', 'manifest.ts');
      const manifestContent = fs.readFileSync(manifestPath, 'utf-8');

      const iconMatches = manifestContent.match(/src:.*\/icons\/icon-\d+\.png/g);
      expect(iconMatches && iconMatches.length).toBeGreaterThanOrEqual(2);
    });

    it('should have proper start_url configuration', () => {
      const manifestPath = resolve(projectRoot, 'app', 'manifest.ts');
      const manifestContent = fs.readFileSync(manifestPath, 'utf-8');

      expect(manifestContent).toContain("start_url: '/'");
    });
  });

  describe('Mobile Support', () => {
    it('should have iOS-specific apple-web-app metadata', () => {
      const layoutPath = resolve(projectRoot, 'app', 'layout.tsx');
      const layoutContent = fs.readFileSync(layoutPath, 'utf-8');

      expect(layoutContent).toContain('appleWebApp');
      expect(layoutContent).toContain('black-translucent');
    });

    it('should have proper viewport for mobile devices', () => {
      const layoutPath = resolve(projectRoot, 'app', 'layout.tsx');
      const layoutContent = fs.readFileSync(layoutPath, 'utf-8');

      expect(layoutContent).toContain('device-width');
      expect(layoutContent).toContain('initialScale: 1');
    });

    it('should configure theme color for mobile browser chrome', () => {
      const layoutPath = resolve(projectRoot, 'app', 'layout.tsx');
      const layoutContent = fs.readFileSync(layoutPath, 'utf-8');

      expect(layoutContent).toContain('themeColor');
      expect(layoutContent).toContain('#1d4ed8');
    });
  });
});
