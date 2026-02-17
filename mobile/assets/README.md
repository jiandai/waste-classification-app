# App Assets

This directory contains production-ready app assets for the Waste Sorter mobile application.

## Files

- **icon.png** (1024x1024px)
  - Main app icon for iOS and Android
  - Used on home screen, app store listings
  - Features three colored bins (blue, green, gray) representing the classification system
  - Includes "WS" logo in a recycling symbol

- **adaptive-icon.png** (1024x1024px)
  - Android adaptive icon foreground layer
  - Same design as icon.png
  - Works with Android's adaptive icon system (allows different shapes on different devices)
  - Background color defined in app.json: #ffffff

- **splash.png** (1284x2778px)
  - Splash screen displayed while app loads
  - Optimized for iPhone 14 Pro Max (portrait)
  - Features app icon, "Waste Sorter" title, and "AI-Powered Waste Classification" tagline
  - White background matching app theme

- **favicon.png** (48x48px)
  - Web favicon for progressive web app (PWA)
  - Scaled-down version of the main icon
  - Used in browser tabs and bookmarks

## Design Theme

The assets feature the app's waste classification color scheme:
- **Blue (#2196F3)**: Recycling bin
- **Green (#4CAF50)**: Organics/compost bin
- **Gray (#9E9E9E)**: Landfill/trash bin
- **White (#FFFFFF)**: Background
- **Dark (#212121)**: Outlines and text

## Regenerating Assets

Assets were generated programmatically using Python and Pillow. If you need to regenerate or modify them, use a similar script or design tools like Figma, Sketch, or Adobe Illustrator.

### Expo Asset Requirements
- Icon: 1024x1024px PNG (square)
- Splash: Typically 1284x2778px PNG (portrait orientation)
- Adaptive Icon: 1024x1024px PNG (Android)
- Favicon: 48x48px PNG (web)

For more information about Expo asset requirements, see:
https://docs.expo.dev/develop/user-interface/splash-screen/
https://docs.expo.dev/develop/user-interface/app-icons/
