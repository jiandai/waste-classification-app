# Web Frontend Assets

This directory contains the frontend assets for the Waste Classification App.

## Files

- `index.html` - Main application page
- `manifest.json` - PWA manifest for "Add to Home Screen" functionality
- `sw.js` - Service worker for offline support and caching
- `icon-*.png` - App icons (currently SVG placeholders)
- `icon-*.svg` - Source SVG icons

## Icon Files

**Note**: The icon-*.png files currently contain SVG markup as placeholders since image conversion tools are not available in the development environment. 

For production deployment, these should be replaced with actual PNG images. You can:
1. Use an online SVG to PNG converter
2. Use ImageMagick: `convert icon-192.svg icon-192.png`
3. Use any design tool (Figma, Photoshop, etc.) to export proper PNG files

The SVG icons are provided as `icon-192.svg` and `icon-512.svg` for easy conversion.
