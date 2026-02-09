/// AI response models with manual JSON serialization
/// Matches the AI Service API structure from schemas.py

import 'medication.dart';

/// Request for structured reminder extraction
class ReminderRequest {
  final Map<String, dynamic> rawOcrJson;

  ReminderRequest({required this.rawOcrJson});

  factory ReminderRequest.fromJson(Map<String, dynamic> json) {
    return ReminderRequest(
      rawOcrJson: json['raw_ocr_json'] ?? {},
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'raw_ocr_json': rawOcrJson,
    };
  }
}

/// Structured reminder response from AI Service
class ReminderResponse {
  final List<MedicationInfo> medications;
  final bool success;
  final String? error;
  final Map<String, dynamic>? metadata;

  ReminderResponse({
    required this.medications,
    required this.success,
    this.error,
    this.metadata,
  });

  factory ReminderResponse.fromJson(Map<String, dynamic> json) {
    return ReminderResponse(
      medications: json['medications'] != null
          ? (json['medications'] as List)
              .map((e) => MedicationInfo.fromJson(e))
              .toList()
          : [],
      success: json['success'] ?? false,
      error: json['error'],
      metadata: json['metadata'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'medications': medications.map((e) => e.toJson()).toList(),
      'success': success,
      'error': error,
      'metadata': metadata,
    };
  }
}

/// Request for OCR text correction
class OCRCorrectionRequest {
  final String rawText;
  final String language;
  final Map<String, dynamic>? context;

  OCRCorrectionRequest({
    required this.rawText,
    this.language = 'en',
    this.context,
  });

  factory OCRCorrectionRequest.fromJson(Map<String, dynamic> json) {
    return OCRCorrectionRequest(
      rawText: json['raw_text'] ?? '',
      language: json['language'] ?? 'en',
      context: json['context'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'raw_text': rawText,
      'language': language,
      'context': context,
    };
  }
}

/// Response after OCR correction
class OCRCorrectionResponse {
  final String correctedText;
  final double confidence;
  final List<Map<String, String>>? changesMade;
  final String language;
  final Map<String, dynamic>? metadata;

  OCRCorrectionResponse({
    required this.correctedText,
    required this.confidence,
    this.changesMade,
    required this.language,
    this.metadata,
  });

  factory OCRCorrectionResponse.fromJson(Map<String, dynamic> json) {
    return OCRCorrectionResponse(
      correctedText: json['corrected_text'] ?? '',
      confidence: (json['confidence'] ?? 0.0).toDouble(),
      changesMade: json['changes_made'] != null
          ? (json['changes_made'] as List)
              .map((e) => Map<String, String>.from(e as Map))
              .toList()
          : null,
      language: json['language'] ?? 'en',
      metadata: json['metadata'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'corrected_text': correctedText,
      'confidence': confidence,
      'changes_made': changesMade,
      'language': language,
      'metadata': metadata,
    };
  }
}

/// AI processing result - combines correction response with medication data
class AIProcessingResult {
  final String correctedText;
  final double confidence;
  final List<Map<String, String>>? changesMade;
  final String language;
  final Map<String, dynamic>? metadata;
  final List<MedicationInfo>? medications;

  AIProcessingResult({
    required this.correctedText,
    required this.confidence,
    this.changesMade,
    required this.language,
    this.metadata,
    this.medications,
  });

  factory AIProcessingResult.fromJson(Map<String, dynamic> json) {
    return AIProcessingResult(
      correctedText: json['corrected_text'] ?? '',
      confidence: (json['confidence'] ?? 0.0).toDouble(),
      changesMade: json['changes_made'] != null
          ? (json['changes_made'] as List)
              .map((e) => Map<String, String>.from(e as Map))
              .toList()
          : null,
      language: json['language'] ?? 'en',
      metadata: json['metadata'],
      medications: json['medications'] != null
          ? (json['medications'] as List)
              .map((e) => MedicationInfo.fromJson(e))
              .toList()
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'corrected_text': correctedText,
      'confidence': confidence,
      'changes_made': changesMade,
      'language': language,
      'metadata': metadata,
      'medications': medications?.map((e) => e.toJson()).toList(),
    };
  }
}

/// Chat request for chatbot interaction
class ChatRequest {
  final String message;
  final String language;
  final Map<String, dynamic>? context;
  final String? sessionId;

  ChatRequest({
    required this.message,
    this.language = 'en',
    this.context,
    this.sessionId,
  });

  factory ChatRequest.fromJson(Map<String, dynamic> json) {
    return ChatRequest(
      message: json['message'] ?? '',
      language: json['language'] ?? 'en',
      context: json['context'],
      sessionId: json['session_id'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'message': message,
      'language': language,
      'context': context,
      'session_id': sessionId,
    };
  }
}

/// Chat response from chatbot
class ChatResponse {
  final String response;
  final String language;
  final double confidence;
  final Map<String, dynamic>? metadata;

  ChatResponse({
    required this.response,
    required this.language,
    required this.confidence,
    this.metadata,
  });

  factory ChatResponse.fromJson(Map<String, dynamic> json) {
    return ChatResponse(
      response: json['response'] ?? '',
      language: json['language'] ?? 'en',
      confidence: (json['confidence'] ?? 0.0).toDouble(),
      metadata: json['metadata'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'response': response,
      'language': language,
      'confidence': confidence,
      'metadata': metadata,
    };
  }
}
