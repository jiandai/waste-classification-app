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
   npm start
   ```
   
   This will start Expo with the `--host lan` flag, making the development server accessible on your local network (e.g., `exp://10.0.0.132:8081`) instead of just localhost (`exp://127.0.0.1:8081`).
   
   **If you're still seeing `exp://127.0.0.1:8081`**, try these solutions:
   
   a. **Clear the cache**:
   ```bash
   npm run start:clear
   ```
   
   b. **Set your IP address manually** (if Expo can't detect it):
   - Copy `.env.example` to `.env`
   - Find your computer's IP address:
     - **Mac/Linux**: Run `ifconfig | grep "inet " | grep -v 127.0.0.1`
     - **Windows**: Run `ipconfig` and look for IPv4 Address
   - Edit `.env` and set: `REACT_NATIVE_PACKAGER_HOSTNAME=YOUR_IP_ADDRESS`
   - Restart the Expo server
   
   c. **Use tunnel mode** (works across any network):
   ```bash
   npm run start:tunnel
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

The app connects to the backend API. By default, it uses:
```
https://waste-classification-app.onrender.com
```

### Configuring the API URL

The API URL can be configured via environment variables, making it easy to point to different backends for development, staging, and production:

1. **Create a `.env` file** (if it doesn't exist):
   ```bash
   cp .env.example .env
   ```

2. **Set the API URL** in your `.env` file:
   ```bash
   EXPO_PUBLIC_API_URL=https://your-backend-url.com
   ```

3. **Restart the Expo development server** for changes to take effect:
   ```bash
   npm start
   ```

**Examples:**
- Local development: `EXPO_PUBLIC_API_URL=http://192.168.1.100:8000`
- Staging: `EXPO_PUBLIC_API_URL=https://staging-api.example.com`
- Production: `EXPO_PUBLIC_API_URL=https://waste-classification-app.onrender.com` (default)

**Note:** If `EXPO_PUBLIC_API_URL` is not set, the app defaults to the production URL.

### Endpoints Used

- `POST /v1/classify` - Upload image for classification
- `POST /v1/clarify` - Submit clarification answers

## Development

```
mobile/
├── App.js              # Main application component
├── app.config.js       # Expo configuration (supports env vars)
├── .env.example        # Environment variable template
├── assets/             # Production app assets (icon, splash, etc.)
├── babel.config.js     # Babel configuration
├── package.json        # Dependencies and scripts
└── README.md           # This file
```

### Key Components

- **Camera Integration**: Uses `expo-image-picker` for camera access
- **API Client**: Fetch API with FormData for image uploads
- **Configuration**: Environment-based API URL configuration via `expo-constants`
- **State Management**: React hooks (useState) for app state
- **UI Components**: React Native core components (View, Text, TouchableOpacity, etc.)

## Troubleshooting

### Connection Error: "Could not connect to the server"

If you see an error like "Could not connect to the server" with URL `exp://127.0.0.1:8081`:

1. **Clear the Expo cache and restart**:
   ```bash
   npm run start:clear
   ```
   This clears any cached configuration that might be forcing localhost.

2. **Verify your network**:
   - Make sure your computer and mobile device are on the same Wi-Fi network
   - Check that your firewall isn't blocking port 8081

3. **Use tunnel mode** (if LAN doesn't work):
   ```bash
   npm run start:tunnel
   ```
   This creates a tunnel that works across any network, though it may be slower.

4. **Manually specify the connection**:
   - In Expo Go, you can manually enter the connection URL
   - Look for your computer's IP address in the terminal output
   - Enter `exp://YOUR_IP:8081` in Expo Go

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

### "Waste Sorter Beta Has Expired"

The TestFlight build passed its 90-day expiry. Nothing is broken — a new build has to be
uploaded. See [TestFlight Builds Expire After 90 Days](#testflight-builds-expire-after-90-days).

### EAS Build Configuration (Production/Preview)

For production builds using EAS (Expo Application Services), you can configure different API URLs for different build profiles:

1. **Create or update `eas.json`**:
   ```json
   {
     "build": {
       "production": {
         "env": {
           "EXPO_PUBLIC_API_URL": "https://waste-classification-app.onrender.com"
         }
       },
       "preview": {
         "env": {
           "EXPO_PUBLIC_API_URL": "https://staging-api.example.com"
         }
       }
     }
   }
   ```

2. **Build with a specific profile**:
   ```bash
   # Production build with production API
   eas build --platform ios --profile production
   
   # Preview build with staging API
   eas build --platform ios --profile preview
   ```

This approach ensures production builds always point to the correct backend without code changes.

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

## TestFlight Builds Expire After 90 Days

If the app on your iPhone shows **"Waste Sorter Beta Has Expired"**, nothing is broken.
Every TestFlight build stops launching 90 days after it is uploaded to App Store Connect.
There is no way to extend or reactivate an expired build — the only fix is to upload a new one.

Expect this roughly quarterly for as long as the app is distributed through TestFlight.

### Reactivating

Run both commands from the `mobile/` directory:

```bash
eas build --platform ios --profile production
eas submit --platform ios --latest
```

- `--latest` submits the build you just made, so there is no build ID to copy.
- `eas submit` defaults to the `production` submit profile, so `--profile` can be omitted.
- Both commands need interactive Apple authentication (Apple ID + 2FA), so they must be
  run locally — they cannot be automated without stored credentials.

Then, on the iPhone:

1. Wait ~5-30 minutes for App Store Connect to finish processing the build.
2. Delete the expired app icon from the home screen — it stays dead.
3. Open TestFlight and install Waste Sorter again.

Internal testers (your own team, up to 100) get the build with **no App Review**.
External testers require a Beta App Review round for the first build of a version.

### Before rebuilding, check the backend

The build bakes in the API URL (`EXPO_PUBLIC_API_URL`, defaulting to the Render
deployment). Render free-tier services sleep when idle and can be suspended after long
inactivity, so confirm the backend is alive first — otherwise you rebuild into an app
that fails on every classification:

```bash
curl -i https://waste-classification-app.onrender.com/health
```

Expect `200`. Allow 30-60 seconds for a cold start. A connection failure means the
Render service needs redeploying (see `DEPLOYMENT.md`) before the rebuild is worthwhile.

### Notes on the other build profiles

- **`--profile preview` will not install on a phone.** It sets `ios.simulator: true`,
  which produces a `.app` for the Xcode simulator only.
- **Ad-hoc internal distribution** (a `distribution: "internal"` profile without the
  simulator flag, plus `eas device:create` to register device UDIDs) lasts about a year
  instead of 90 days, but is capped at 100 registered devices per membership year.
- **A full App Store release** removes the expiry entirely, at the cost of App Review.

## Technology Stack

- **Expo** ~52.0.0 - React Native framework
- **React Native** 0.76.5 - Mobile UI framework
- **expo-image-picker** - Camera and photo library access
- **expo-status-bar** - Status bar styling

## License

[Add your license here]

## Support

For issues with the mobile app, please open an issue in the main repository.
