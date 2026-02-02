# Prescription OCR Scanner - Flutter App

A Flutter application for scanning prescription images using OCR technology, correcting the text with AI, and extracting medication reminders.

## Features

- 📷 **Image Capture**: Take photos or select from gallery
- 🔍 **OCR Processing**: Advanced multi-language OCR (English, Khmer, French)
- 🤖 **AI Correction**: Automatic text correction and medication extraction
- ⏰ **Smart Reminders**: Extract structured medication information
- 📊 **Quality Metrics**: Real-time image quality analysis
- 🎯 **Easy UI/UX**: Intuitive and user-friendly interface

## Project Structure

```
lib/
├── main.dart                           # App entry point
├── models/                             # Data models
│   ├── medication.dart                # Medication model
│   ├── ocr_response.dart              # OCR response model
│   └── ai_response.dart               # AI response model
├── services/                           # Business logic
│   ├── api_client.dart                # API communication
│   ├── ocr_service.dart               # OCR processing
│   └── ai_service.dart                # AI processing
├── providers/                          # State management (Provider)
│   └── processing_provider.dart       # OCR & AI providers
├── ui/
│   ├── screens/                       # App screens
│   │   ├── home_screen.dart           # Home/launcher screen
│   │   ├── ocr_result_screen.dart     # OCR results display
│   │   └── ai_result_screen.dart      # AI/Reminder results
│   └── components/                    # Reusable components
├── widgets/                            # Custom widgets
│   ├── dialogs.dart                   # Dialog widgets
│   ├── custom_widgets.dart            # Custom UI widgets
│   └── form_widgets.dart              # Form elements
└── utils/                              # Utilities
    ├── constants.dart                 # App constants
    └── helpers.dart                   # Helper functions
```

## Setup & Installation

### Prerequisites

- Flutter 3.0.0 or higher
- Dart 3.0.0 or higher
- OCR Service running (on localhost:8000 by default)
- AI LLM Service running (on same host)

### Installation Steps

1. **Clone or navigate to the project:**
   ```bash
   cd ocr_ai_for_reminder
   ```

2. **Get dependencies:**
   ```bash
   flutter pub get
   ```

3. **Run the app:**
   ```bash
   flutter run
   ```

### Configuration

Update the API base URL in `lib/utils/constants.dart`:

```dart
static const String apiBaseUrl = 'http://your-server:8000';
```

Or update in `lib/main.dart` when creating providers:

```dart
ChangeNotifierProvider(
  create: (_) => OCRProvider(baseUrl: 'http://your-server:8000'),
),
```

## Usage Flow

1. **Home Screen**: Select "Take Photo" or "Choose from Gallery"
2. **OCR Processing**: Image is sent to OCR service for text extraction
3. **OCR Results**: Review extracted text and quality metrics
4. **AI Processing**: Text is corrected and medications are extracted
5. **Medication View**: Display extracted medications with reminders

## Key Components

### Models

- **MedicationInfo**: Represents a single medication with dosage and timing
- **OCRResponse**: Contains OCR processing results with quality metrics
- **ReminderResponse**: Contains extracted medication reminders

### Services

- **APIClient**: Handles HTTP communication with backend services
- **OCRService**: Manages OCR image processing
- **AIService**: Manages AI correction and reminder extraction

### Providers

- **OCRProvider**: Manages OCR state and processing
- **AIProvider**: Manages AI processing and medication extraction

### Widgets

- **MedicationCard**: Display medication information
- **RoundedButton**: Styled button component
- **QualityMetricsWidget**: Display image quality analysis
- **Dialogs**: Loading, error, and success dialogs

## API Integration

### OCR Service Endpoints

- `POST /api/v1/ocr` - Process prescription image
- `GET /api/v1/health` - Health check

### AI Service Endpoints

- `POST /api/v1/correct` - Correct OCR text
- `POST /api/v1/extract-reminders` - Extract medication reminders

## State Management

Uses **Provider** pattern for state management:

- Clean separation of concerns
- Reactive UI updates
- Easy testing
- Scalable architecture

## Features Implemented

### Phase 1: Core Functionality ✅
- [x] Image picker integration
- [x] OCR processing pipeline
- [x] AI text correction
- [x] Medication extraction
- [x] Results display

### Phase 2: UI/UX ✅
- [x] Material Design 3
- [x] Responsive layouts
- [x] Loading indicators
- [x] Error handling dialogs
- [x] Quality metrics display

### Phase 3: Advanced Features (Future)
- [ ] Medication reminder notifications
- [ ] Local database storage
- [ ] Edit/manage medications
- [ ] Multi-language support
- [ ] Dark mode
- [ ] Offline mode

## Troubleshooting

### Service Connection Issues

**Problem**: "Service is offline" error
- Ensure OCR service is running on the configured port
- Check firewall settings
- Verify network connectivity

**Solution**:
```bash
# Start OCR service
cd ocr-service-anti
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start AI service
cd ai-llm-service
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Image Processing Errors

**Problem**: "OCR processing failed"
- Ensure image is clear and readable
- Try a different image
- Check image format (JPG, PNG supported)

### Build Issues

**Problem**: Dependency conflicts
- Clean Flutter cache:
  ```bash
  flutter clean
  flutter pub get
  ```

## Dependencies

- **provider**: ^6.1.1 - State management
- **image_picker**: ^1.0.7 - Image selection
- **http**: ^1.1.0 - HTTP requests
- **intl**: ^0.19.0 - Internationalization
- **logger**: ^2.1.0 - Logging
- **json_annotation**: ^4.8.1 - JSON serialization
- **cached_network_image**: ^3.3.0 - Image caching

## Development

### Running Tests

```bash
flutter test
```

### Build APK

```bash
flutter build apk --release
```

### Build for iOS

```bash
flutter build ios --release
```

## Code Generation

Generate model serialization code:

```bash
flutter pub run build_runner build
```

Watch for changes:

```bash
flutter pub run build_runner watch
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check existing documentation
2. Review error messages carefully
3. Check service connectivity
4. Review logs in debug console

## Future Improvements

- [ ] Advanced medication scheduling
- [ ] Integration with device calendar
- [ ] Push notifications for reminders
- [ ] Voice-based medication input
- [ ] Medication interaction warnings
- [ ] Export to PDF/CSV
- [ ] Cloud sync capability
