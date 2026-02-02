# Flutter App Testing Guide

## Unit Testing

### Test Structure

```
test/
├── services/
│   ├── ocr_service_test.dart
│   ├── ai_service_test.dart
│   └── api_client_test.dart
├── models/
│   ├── medication_model_test.dart
│   └── ocr_response_model_test.dart
└── providers/
    └── processing_provider_test.dart
```

### Run Tests

```bash
# Run all tests
flutter test

# Run specific test file
flutter test test/services/ocr_service_test.dart

# Run tests with coverage
flutter test --coverage
```

## Widget Testing

### Example Widget Test

```dart
testWidgets('Home screen displays correctly', (WidgetTester tester) async {
  await tester.pumpWidget(const MyApp());
  
  expect(find.byType(HomeScreen), findsOneWidget);
  expect(find.byText('Scan Your Prescription'), findsOneWidget);
  
  await tester.tap(find.byIcon(Icons.camera_alt));
  await tester.pumpAndSettle();
});
```

## Integration Testing

### Test Flow

1. **Image Selection**
   - Take photo from camera
   - Select from gallery
   - Verify image is set

2. **OCR Processing**
   - Send image to OCR service
   - Verify response received
   - Check OCR results display

3. **AI Processing**
   - Send text to AI service
   - Verify corrections applied
   - Check medication extraction

4. **Medication Display**
   - Verify medications displayed
   - Check medication details
   - Verify UI elements

### Run Integration Tests

```bash
# Run integration tests
flutter drive --target=test_driver/app.dart
```

## Manual Testing Checklist

### Pre-Launch Checks

- [ ] Flutter version >= 3.0.0
- [ ] All dependencies installed (`flutter pub get`)
- [ ] Model code generated (`flutter pub run build_runner build`)
- [ ] No lint errors (`flutter analyze`)
- [ ] Backend services running

### Functionality Testing

#### Home Screen
- [ ] App launches without errors
- [ ] Service health indicator shows correct status
- [ ] "Take Photo" button works
- [ ] "Choose from Gallery" button works
- [ ] Feature highlights display correctly

#### OCR Processing
- [ ] Image is uploaded correctly
- [ ] Processing indicator shows
- [ ] Processing completes within reasonable time
- [ ] Extracted text displays
- [ ] Quality metrics are accurate
- [ ] "Proceed to AI" button works

#### AI Processing
- [ ] AI processing starts automatically
- [ ] Progress bar updates
- [ ] Medications are extracted
- [ ] Medication cards display correctly
- [ ] All medication details shown (name, dosage, times, duration, notes)

#### UI/UX
- [ ] All screens are responsive
- [ ] Text is readable on all screen sizes
- [ ] Buttons are easily tappable (min 48x48 dp)
- [ ] Colors are consistent
- [ ] Navigation works correctly
- [ ] Back button works on all screens
- [ ] No layout overflow

#### Error Handling
- [ ] Service offline error shown gracefully
- [ ] Image processing failures handled
- [ ] Network timeout handled
- [ ] Invalid image shown appropriate error
- [ ] Retry functionality works

### Performance Testing

#### Response Times

- Image upload: < 10 seconds
- OCR processing: < 30 seconds
- AI correction: < 5 seconds
- Medication extraction: < 3 seconds
- UI rendering: < 100ms

#### Memory Usage

- App startup: < 100 MB
- After image load: < 200 MB
- During processing: < 300 MB

### Device Testing

Test on multiple devices:
- [ ] Phone (small screen - 5.5")
- [ ] Tablet (large screen - 10")
- [ ] Different Android versions (API 21-31+)
- [ ] Different iOS versions (12, 14, 15+)
- [ ] Portrait orientation
- [ ] Landscape orientation
- [ ] After screen rotation

### Network Conditions

- [ ] WiFi connection
- [ ] Mobile 4G/LTE
- [ ] Slow network (throttle in DevTools)
- [ ] Network disconnect/reconnect

## Performance Testing

### Using DevTools

```bash
# Start DevTools
flutter pub global activate devtools

# Run app with DevTools
flutter run
devtools
```

### Profile Build

```bash
# Build profile version for testing
flutter run --profile

# Check memory usage
flutter logs | grep "GC:"
```

### Release Build

```bash
# Build release version
flutter build apk --release

# Test release APK
adb install build/app/outputs/flutter-apk/app-release.apk
```

## Common Test Scenarios

### Scenario 1: Clear Prescription Image

**Steps:**
1. Take photo of clear prescription
2. Review extracted text
3. Verify all medications extracted
4. Check confidence score > 80%

**Expected Result:** All medications correctly extracted with high confidence

### Scenario 2: Blurry Image

**Steps:**
1. Take blurry photo
2. Check quality metrics
3. Review blur score
4. Try processing

**Expected Result:** Quality warning shown, user can retry

### Scenario 3: Multi-language Prescription

**Steps:**
1. Use prescription with English + Khmer text
2. Select both languages
3. Process OCR
4. Check extracted text includes both languages

**Expected Result:** Both languages recognized and extracted

### Scenario 4: Service Offline

**Steps:**
1. Stop backend services
2. Launch app
3. Attempt to process image

**Expected Result:** Clear error message about offline service

### Scenario 5: Network Timeout

**Steps:**
1. Enable airplane mode
2. Attempt image processing
3. Wait for timeout
4. Re-enable network

**Expected Result:** Timeout handled gracefully, retry available

## Debugging

### Enable Debug Logging

```dart
// In utils/environment.dart
static const bool enableDebugMode = true;
static const bool enableLogging = true;
```

### View Logs

```bash
# View all logs
flutter logs

# View logs for specific package
flutter logs | grep ocr_ai_for_reminder

# Save logs to file
flutter logs > app.log
```

### Use Dart DevTools

```bash
# Open DevTools in browser
devtools

# Set breakpoints in VS Code
# F5 to start debugging
```

### Network Debugging

```bash
# Monitor network requests
# Charles Proxy or Fiddler for HTTPS
# Android Studio Profiler for network

# Check API responses
curl -v http://localhost:8000/api/v1/ocr
```

## CI/CD Testing

### GitHub Actions Example

```yaml
name: Flutter Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: subosito/flutter-action@v2
      - run: flutter pub get
      - run: flutter test
```

## Test Results

### Generate Coverage Report

```bash
# Generate coverage
flutter test --coverage

# View coverage report
lcov --list coverage/lcov.info

# Generate HTML report
genhtml coverage/lcov.info -o coverage/
open coverage/index.html
```

## Known Issues & Workarounds

### Issue: Build fails with dependency conflict

**Workaround:**
```bash
flutter clean
flutter pub get --no-offline
flutter pub run build_runner build --delete-conflicting-outputs
```

### Issue: DevTools not loading

**Workaround:**
```bash
flutter clean
flutter pub global deactivate devtools
flutter pub global activate devtools
devtools
```

### Issue: Image picker not working on iOS

**Workaround:**
Check Info.plist permissions:
```xml
<key>NSCameraUsageDescription</key>
<string>We need camera access to take photos</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>We need library access to select photos</string>
```

## Resources

- [Flutter Testing Documentation](https://flutter.dev/docs/testing)
- [DevTools Documentation](https://dart.dev/tools/dart-devtools)
- [Provider Package Testing](https://pub.dev/packages/provider#testing)
- [Image Picker Testing](https://pub.dev/packages/image_picker#testing)
