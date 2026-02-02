# Flutter OCR AI Reminder App - Complete Setup Guide

## Quick Start

### 1. System Requirements

```bash
# Check Flutter installation
flutter --version

# Ensure you have these:
- Flutter 3.0.0+
- Dart 3.0.0+
- Android SDK / Xcode (for iOS)
```

### 2. Backend Services Setup

Before running the Flutter app, ensure backend services are running:

#### OCR Service (ocr-service-anti)
```bash
cd /home/rayu/DasTern/ocr-service-anti
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### AI/LLM Service (ai-llm-service)
```bash
cd /home/rayu/DasTern/ai-llm-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# For Ollama support:
# pip install -r requirements_ollama.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### 3. Flutter App Setup

```bash
cd /home/rayu/DasTern/ocr_ai_for_reminder

# Get dependencies
flutter pub get

# Generate model serialization code
flutter pub run build_runner build

# Run the app
flutter run
```

## Architecture Overview

### Three-Layer Architecture

```
┌─────────────────────────────────────┐
│      Flutter UI Layer               │
│  (Screens, Widgets, Components)     │
└──────────────┬──────────────────────┘
               │
┌──────────────┴──────────────────────┐
│    Business Logic Layer             │
│  (Providers, Services)              │
└──────────────┬──────────────────────┘
               │
┌──────────────┴──────────────────────┐
│    Backend Services Layer           │
│  (OCR Service, AI Service)          │
└─────────────────────────────────────┘
```

### Data Flow

```
User selects image
        ↓
ImagePicker (Camera/Gallery)
        ↓
OCRProvider.processImage()
        ↓
APIClient.uploadImageForOCR()
        ↓
OCRService backend (/api/v1/ocr)
        ↓
OCRResponse with extracted text
        ↓
AIProvider.processFullPipeline()
        ↓
APIClient.correctOCRText()
        ↓
AIService backend (/api/v1/correct)
        ↓
AIService backend (/api/v1/extract-reminders)
        ↓
MedicationInfo list
        ↓
Display in UI
```

## Folder Structure Explained

```
lib/
├── main.dart
│   └── App entry point, routing setup, provider configuration
│
├── models/                    [Data Layer]
│   ├── medication.dart        - Medication data model
│   ├── ocr_response.dart      - OCR API response model
│   └── ai_response.dart       - AI API response model
│
├── services/                  [API & Business Logic Layer]
│   ├── api_client.dart        - HTTP client for backend communication
│   ├── ocr_service.dart       - OCR processing logic
│   └── ai_service.dart        - AI processing logic
│
├── providers/                 [State Management Layer]
│   └── processing_provider.dart
│       - OCRProvider: manages OCR state
│       - AIProvider: manages AI state
│       - ProcessingState: tracks processing progress
│
├── ui/                        [Presentation Layer]
│   ├── screens/
│   │   ├── home_screen.dart       - Main/launcher screen
│   │   ├── ocr_result_screen.dart - OCR results & metrics
│   │   └── ai_result_screen.dart  - Medication reminders
│   │
│   └── components/
│       └── common.dart        - Reusable UI components
│
├── widgets/                   [Reusable UI Components]
│   ├── dialogs.dart           - Loading, error, success dialogs
│   ├── custom_widgets.dart    - MedicationCard, QualityMetrics
│   └── form_widgets.dart      - Buttons, inputs, empty states
│
└── utils/                     [Utility Layer]
    ├── constants.dart         - App constants & config
    ├── environment.dart       - Environment variables
    └── helpers.dart           - Utility functions
```

## State Management (Provider Pattern)

### OCRProvider

```dart
// State
- imagePath: String?              // Selected image path
- ocrResponse: OCRResponse?       // OCR result
- processingState: ProcessingState // Current processing status
- isServiceHealthy: bool          // Service connectivity

// Methods
- checkServiceHealth(): Future<void>
- setImagePath(path: String): void
- processImage(): Future<bool>
- getQualityMetrics(): Map?
- reset(): void
```

### AIProvider

```dart
// State
- rawOCRText: String?                    // Original OCR text
- ocrMetadata: Map<String, dynamic>?     // OCR metadata
- correctionResult: AIProcessingResult?  // Text correction result
- reminderResponse: ReminderResponse?    // Extracted reminders
- medications: List<MedicationInfo>      // Parsed medications
- processingState: ProcessingState       // Current status

// Methods
- setRawOCRData(text, metadata): void
- correctOCRText(language?): Future<bool>
- extractReminders(): Future<bool>
- processFullPipeline(language?): Future<bool>
- reset(): void
```

## API Endpoints Integration

### OCR Service Endpoints

**POST /api/v1/ocr**
```
Request:
- file: binary image
- languages?: "eng+khm+fra"
- skip_enhancement?: boolean

Response: OCRResponse
{
  meta: ProcessingMeta
  quality: QualityMetrics
  blocks: [Block, ...]
  full_text: string
  success: boolean
}
```

**GET /health**
- Health check endpoint

### AI Service Endpoints

**POST /api/v1/correct**
```
Request:
{
  raw_text: string
  language: "en" | "km" | "fr"
  context?: object
}

Response: AIProcessingResult
{
  corrected_text: string
  confidence: 0.0-1.0
  changes_made?: [{original, corrected}, ...]
  language: string
}
```

**POST /api/v1/extract-reminders**
```
Request:
{
  raw_ocr_json: object (full OCR response)
}

Response: ReminderResponse
{
  medications: [MedicationInfo, ...]
  success: boolean
  error?: string
}
```

## UI/UX Components

### Screens

1. **HomeScreen**
   - Image picker buttons
   - Feature highlights
   - Service status indicator

2. **OCRResultScreen**
   - Image preview
   - Extracted text display
   - Quality metrics visualization
   - Proceed to AI button

3. **AIResultScreen**
   - Processing progress
   - Medication cards list
   - Success summary
   - Action buttons

### Widgets

- **MedicationCard**: Display medication with times, dosage, repeat
- **QualityMetricsWidget**: Show blur, contrast, skew metrics
- **RoundedButton**: Styled action button
- **LoadingDialog**: Processing indicator
- **ErrorDialog**: Error message with retry
- **SuccessDialog**: Success confirmation
- **EmptyStateWidget**: No data placeholder

## Configuration

### Update API Base URL

**Option 1: In constants.dart**
```dart
static const String apiBaseUrl = 'http://your-server:8000';
```

**Option 2: In main.dart**
```dart
ChangeNotifierProvider(
  create: (_) => OCRProvider(baseUrl: 'http://your-server:8000'),
),
```

**Option 3: Runtime with --dart-define**
```bash
flutter run --dart-define=API_BASE_URL=http://your-server:8000
```

### Configure Supported Languages

In `utils/environment.dart`:
```dart
static const List<String> supportedLanguages = ['eng', 'khm', 'fra'];
static const String defaultLanguages = 'eng+khm+fra';
```

## Development Workflow

### 1. Add New Screen

```dart
// lib/ui/screens/new_screen.dart
import 'package:flutter/material.dart';

class NewScreen extends StatefulWidget {
  const NewScreen({Key? key}) : super(key: key);

  @override
  State<NewScreen> createState() => _NewScreenState();
}

class _NewScreenState extends State<NewScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('New Screen')),
      body: Container(),
    );
  }
}
```

### 2. Register Route

```dart
// In main.dart
routes: {
  '/new-screen': (context) => const NewScreen(),
}

// Navigate
Navigator.pushNamed(context, '/new-screen');
```

### 3. Add State Management

```dart
// In providers/processing_provider.dart
class NewProvider extends ChangeNotifier {
  // State
  
  // Methods
}

// In main.dart
ChangeNotifierProvider(create: (_) => NewProvider()),

// Use in widget
Consumer<NewProvider>(
  builder: (context, provider, _) {
    // Build with provider state
  },
)
```

## Testing

### Run All Tests

```bash
flutter test
```

### Run Specific Test

```bash
flutter test test/services/ocr_service_test.dart
```

### Build & Release

```bash
# Android APK
flutter build apk --release

# Android App Bundle
flutter build appbundle --release

# iOS
flutter build ios --release

# Web
flutter build web --release
```

## Troubleshooting

### Issue: "Service is offline"

**Check:**
1. Backend services are running
2. Correct API base URL configured
3. Network connectivity
4. Firewall rules

**Solution:**
```bash
# Verify services
curl http://localhost:8000/
curl http://localhost:8001/

# Check logs
# OCR service logs
# AI service logs
```

### Issue: Image processing fails

**Check:**
1. Image is clear and readable
2. Image format supported (JPG, PNG)
3. Image size reasonable (<10MB)

### Issue: Dependency conflicts

**Solution:**
```bash
flutter clean
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs
```

### Issue: Build errors

**Solution:**
```bash
# Clear Flutter cache
flutter clean

# Regenerate model code
flutter pub run build_runner build --delete-conflicting-outputs

# Rebuild
flutter run
```

## Performance Tips

1. **Image Optimization**: Compress images before upload
2. **Caching**: Use cached_network_image for repeat requests
3. **Pagination**: Implement lazy loading for large lists
4. **Code Splitting**: Separate business logic from UI
5. **Memory Management**: Dispose resources properly

## Security Best Practices

1. **API Keys**: Use environment variables
2. **HTTPS**: Use in production
3. **Input Validation**: Validate all user inputs
4. **Data Privacy**: Handle sensitive data carefully
5. **Error Handling**: Don't expose sensitive errors to UI

## Next Steps

1. Implement local database (Hive/SQLite)
2. Add push notifications for reminders
3. Implement offline mode
4. Add medication interaction warnings
5. Implement cloud sync
6. Add user authentication
7. Implement dark theme

## Support

For issues:
1. Check Flutter documentation
2. Review backend service logs
3. Check network connectivity
4. Verify API endpoints responding correctly
5. Check device permissions (camera, gallery)

## Resources

- [Flutter Documentation](https://flutter.dev)
- [Provider Package](https://pub.dev/packages/provider)
- [Image Picker](https://pub.dev/packages/image_picker)
- [HTTP Package](https://pub.dev/packages/http)
