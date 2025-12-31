# Waste Sorter - Mobile App

A React Native (Expo) mobile application for waste classification using AI-powered computer vision.

## Features

- **Camera Integration**: Take photos of waste items directly from your device
- **Real-time Classification**: Get instant bin recommendations (BLUE/GREEN/GRAY/SPECIAL)
- **Interactive Clarification**: Answer follow-up questions for ambiguous items
- **Special Handling**: Get safety instructions for hazardous materials
- **Clean UI**: Native mobile experience with Material Design styling

## Prerequisites

- **Node.js** 16+ and npm
- **Expo Go** app installed on your mobile device:
  - iOS: Download from the App Store
  - Android: Download from Google Play Store

## Installation

1. Navigate to the mobile directory:
   ```bash
   cd mobile
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

## Running the App

1. Start the Expo development server:
   ```bash
   npx expo start
   ```

2. Scan the QR code displayed in your terminal:
   - **iPhone**: Open the Camera app and point it at the QR code. Tap the notification to open in Expo Go.
   - **Android**: Open the Expo Go app and use the built-in QR scanner.

3. The app will load on your device and you can start classifying waste items!

## Usage

1. **Take a Photo**: Tap the "Take Photo" button to launch your camera
2. **Grant Permissions**: Allow camera access when prompted
3. **Capture**: Take a clear photo of a single waste item in good lighting
4. **View Results**: See the recommended bin (color-coded) with confidence score
5. **Answer Questions**: If needed, respond to clarification questions
6. **Review Rationale**: Read the reasoning behind the classification
7. **Take Another**: Tap "Take Another Photo" to classify more items

## Bin Colors

- **BLUE** (#2196F3): Recycling - Clean recyclable materials
- **GREEN** (#4CAF50): Organics - Food waste and compostables
- **GRAY** (#9E9E9E): Landfill - Non-recyclable trash
- **SPECIAL** (#F44336): Special Handling - Batteries, e-waste, hazardous materials

## API Integration

The app connects to the hosted backend at:
```
https://waste-classification-app.onrender.com
```

### Endpoints Used

- `POST /v1/classify` - Upload image for classification
- `POST /v1/clarify` - Submit clarification answers

## Development

### Project Structure

```
mobile/
├── App.js              # Main application component
├── app.json            # Expo configuration
├── babel.config.js     # Babel configuration
├── package.json        # Dependencies and scripts
└── README.md          # This file
```

### Key Components

- **Camera Integration**: Uses `expo-image-picker` for camera access
- **API Client**: Fetch API with FormData for image uploads
- **State Management**: React hooks (useState) for app state
- **UI Components**: React Native core components (View, Text, TouchableOpacity, etc.)

### Modifying the API URL

To use a different backend, edit the `API_BASE_URL` constant in `App.js`:

```javascript
const API_BASE_URL = 'https://your-backend-url.com';
```

## Troubleshooting

### Camera Not Working

- Ensure you've granted camera permissions to the Expo Go app
- Check that your device has a working camera
- Try restarting the Expo Go app

### Network Errors

- Verify you have an active internet connection
- Check that the backend API is running and accessible
- Try accessing the API URL in your mobile browser

### QR Code Won't Scan

- Make sure you're using the Camera app on iOS or Expo Go app on Android
- Ensure the QR code is fully visible and well-lit
- Try the alternative method: Type the URL shown in terminal into Expo Go

### App Crashes on Launch

- Run `npm install` again to ensure all dependencies are installed
- Clear the Expo cache: `npx expo start -c`
- Check that you're using compatible versions of Node.js and npm

## Building for Production

To build standalone apps for iOS and Android:

1. Install EAS CLI:
   ```bash
   npm install -g eas-cli
   ```

2. Configure your project:
   ```bash
   eas build:configure
   ```

3. Build for your platform:
   ```bash
   # For iOS
   eas build --platform ios
   
   # For Android
   eas build --platform android
   ```

For detailed build instructions, see the [Expo documentation](https://docs.expo.dev/build/setup/).

## Technology Stack

- **Expo** ~52.0.0 - React Native framework
- **React Native** 0.76.5 - Mobile UI framework
- **expo-image-picker** - Camera and photo library access
- **expo-status-bar** - Status bar styling

## License

[Add your license here]

## Support

For issues with the mobile app, please open an issue in the main repository.
