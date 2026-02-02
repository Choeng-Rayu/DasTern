class OcrResponse {
  final bool success;
  final String rawText;
  final List<Map<String, dynamic>>? rawElements;
  final Map<String, dynamic>? stats;
  final String? languagesUsed;
  final String? error;

  OcrResponse({
    this.success = false,
    this.rawText = '',
    this.rawElements,
    this.stats,
    this.languagesUsed,
    this.error,
  });

  factory OcrResponse.fromJson(Map<String, dynamic> json) {
    // Extract text from raw array
    String extractedText = '';
    List<Map<String, dynamic>>? elements;

    if (json['raw'] != null && json['raw'] is List) {
      elements = List<Map<String, dynamic>>.from(json['raw']);
      // Join all text elements
      final texts = elements
          .where((e) =>
              e['text'] != null && e['text'].toString().trim().isNotEmpty)
          .map((e) => e['text'].toString())
          .toList();
      extractedText = texts.join(' ');
    }

    return OcrResponse(
      success: json['success'] ?? false,
      rawText: extractedText,
      rawElements: elements,
      stats: json['stats'] != null
          ? Map<String, dynamic>.from(json['stats'])
          : null,
      languagesUsed: json['languages_used']?.toString(),
      error: json['error']?.toString(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'success': success,
      'raw_text': rawText,
      'raw': rawElements,
      'stats': stats,
      'languages_used': languagesUsed,
      'error': error,
    };
  }

  Map<String, dynamic> toAiRequestJson() {
    // Format for AI service /extract-reminders endpoint
    return {
      'raw_ocr_json': {
        'raw': rawElements ?? [],
        'stats': stats ?? {},
        'languages_used': languagesUsed ?? 'khm+eng+fra',
        'extracted_text': rawText,
      }
    };
  }

  bool get hasError => error != null && error!.isNotEmpty;
  bool get hasData => rawText.isNotEmpty;

  int get totalElements => rawElements?.length ?? 0;
  double get avgConfidence => stats?['avg_confidence']?.toDouble() ?? 0.0;
  int get totalWords => stats?['total_words']?.toInt() ?? 0;

  // Backward compatibility getter
  double get confidence => avgConfidence;
}
