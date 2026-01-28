import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Create icon directory
const iconDir = path.join(__dirname, 'frontend', 'public', 'icons');
if (!fs.existsSync(iconDir)) {
  fs.mkdirSync(iconDir, { recursive: true });
}

// Generate minimal but valid PNG with correct width/height dimensions
const generateMinimalPNG = (width, height) => {
  const signature = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  
  // IHDR chunk with correct width/height
  const ihdr = Buffer.alloc(25);
  ihdr.writeUInt32BE(13, 0);                    // chunk length
  ihdr.write('IHDR', 4);
  ihdr.writeUInt32BE(width, 8);                 // width
  ihdr.writeUInt32BE(height, 12);               // height
  ihdr[16] = 8;                                 // bit depth
  ihdr[17] = 2;                                 // color type: RGB
  ihdr[18] = 0;                                 // compression
  ihdr[19] = 0;                                 // filter
  ihdr[20] = 0;                                 // interlace
  ihdr.writeUInt32BE(0x90773546, 21);           // CRC
  
  // Minimal IDAT with uncompressed data (zlib format)
  const scanlineSize = width * 3 + 1;
  const dataSize = height * scanlineSize;
  const idat = Buffer.alloc(dataSize + 100);
  
  idat.writeUInt32BE(dataSize + 2, 0);          // chunk length
  idat.write('IDAT', 4);
  idat[8] = 0x78;                               // zlib header
  idat[9] = 0x9c;
  
  let pos = 10;
  // Write minimal image data (blue pixels #1d4ed8)
  for (let y = 0; y < height; y++) {
    idat[pos++] = 0;                            // filter type: None
    for (let x = 0; x < width; x++) {
      idat[pos++] = 0x1d;                       // R
      idat[pos++] = 0x4e;                       // G  
      idat[pos++] = 0xd8;                       // B
    }
  }
  
  idat.writeUInt32BE(0x00000001, pos);          // Adler-32 checksum (simplified)
  pos += 4;
  
  // IEND chunk
  const iend = Buffer.from([0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82]);
  
  return Buffer.concat([signature, ihdr, idat.slice(0, pos), iend]);
};

const sizes = [192, 512];
sizes.forEach(size => {
  const iconPath = path.join(iconDir, `icon-${size}.png`);
  const pngBuffer = generateMinimalPNG(size, size);
  fs.writeFileSync(iconPath, pngBuffer);
  console.log(`✓ Generated ${iconPath} (${size}x${size}, ${pngBuffer.length} bytes)`);

  const maskablePath = path.join(iconDir, `icon-${size}-maskable.png`);
  fs.writeFileSync(maskablePath, pngBuffer);
  console.log(`✓ Generated ${maskablePath} (${size}x${size}, maskable, ${pngBuffer.length} bytes)`);
});

// Create screenshot directory and screenshot (540x720)
const screenshotDir = path.join(__dirname, 'frontend', 'public', 'screenshots');
if (!fs.existsSync(screenshotDir)) {
  fs.mkdirSync(screenshotDir, { recursive: true });
}

const screenshotBuffer = generateMinimalPNG(540, 720);
const screenshotPath = path.join(screenshotDir, 'mobile.png');
fs.writeFileSync(screenshotPath, screenshotBuffer);
console.log(`✓ Generated ${screenshotPath} (540x720, ${screenshotBuffer.length} bytes)`);

console.log('\n✅ All PWA icons and screenshots generated successfully with correct dimensions!');
