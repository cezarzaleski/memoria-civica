import { describe, it, expect } from 'vitest';
import manifest from '@/app/manifest';

describe('app/manifest.ts', () => {
  it('should export a valid MetadataRoute.Manifest object', () => {
    const manifestData = manifest();
    expect(manifestData).toBeDefined();
    expect(typeof manifestData).toBe('object');
  });

  it('should contain required manifest fields', () => {
    const manifestData = manifest();
    
    expect(manifestData.name).toBe('Memória Cívica');
    expect(manifestData.short_name).toBe('Memória Cívica');
    expect(manifestData.description).toBe('Acompanhe votações e deputados do Congresso Nacional');
    expect(manifestData.start_url).toBe('/');
    expect(manifestData.display).toBe('standalone');
  });

  it('should have correct colors configuration', () => {
    const manifestData = manifest();
    
    expect(manifestData.background_color).toBe('#ffffff');
    expect(manifestData.theme_color).toBe('#1d4ed8');
  });

  it('should have proper scope configuration', () => {
    const manifestData = manifest();
    
    expect(manifestData.scope).toBe('/');
    expect(manifestData.orientation).toBe('portrait');
  });

  it('should contain icons with correct structure', () => {
    const manifestData = manifest();
    
    expect(manifestData.icons).toBeDefined();
    expect(Array.isArray(manifestData.icons)).toBe(true);
    expect(manifestData.icons!.length).toBeGreaterThanOrEqual(2);

    // Check for 192x192 and 512x512 icons
    const sizes = manifestData.icons!.map((icon) => icon.sizes);
    expect(sizes).toContain('192x192');
    expect(sizes).toContain('512x512');

    // Check for maskable icons
    const maskableIcons = manifestData.icons!.filter((icon) => icon.purpose?.includes('maskable'));
    expect(maskableIcons.length).toBeGreaterThan(0);
  });

  it('should have icon paths matching convention', () => {
    const manifestData = manifest();
    
    manifestData.icons!.forEach((icon) => {
      expect(icon.src).toMatch(/^\/icons\/icon-\d+(-maskable)?\.png$/);
      expect(icon.type).toBe('image/png');
    });
  });

  it('should have screenshots configured', () => {
    const manifestData = manifest();
    
    expect(manifestData.screenshots).toBeDefined();
    expect(Array.isArray(manifestData.screenshots)).toBe(true);
    expect(manifestData.screenshots!.length).toBeGreaterThan(0);

    const screenshot = manifestData.screenshots![0];
    expect(screenshot.src).toBe('/screenshots/mobile.png');
    expect(screenshot.sizes).toBe('540x720');
    expect(screenshot.form_factor).toBe('narrow');
    expect(screenshot.type).toBe('image/png');
  });

  it('should have shortcuts configured', () => {
    const manifestData = manifest();
    
    expect(manifestData.shortcuts).toBeDefined();
    expect(Array.isArray(manifestData.shortcuts)).toBe(true);
    expect(manifestData.shortcuts!.length).toBeGreaterThan(0);

    const shortcut = manifestData.shortcuts![0];
    expect(shortcut.name).toBe('Votações');
    expect(shortcut.url).toBe('/');
  });

  it('should have categories for app store classification', () => {
    const manifestData = manifest();
    
    expect(manifestData.categories).toBeDefined();
    expect(Array.isArray(manifestData.categories)).toBe(true);
    expect(manifestData.categories!.some((cat) => cat.includes('news') || cat.includes('politics'))).toBe(true);
  });
});
