import 'package:freezed_annotation/freezed_annotation.dart';

part 'ocr_response_dto.freezed.dart';
part 'ocr_response_dto.g.dart';

@freezed
class OcrResponseDto with _$OcrResponseDto {
  const factory OcrResponseDto({
    @JsonKey(name: 'raw_text') String? rawText,
    @Default([]) List<OcrBlockDto> blocks,
    // Add other fields like quality if needed
  }) = _OcrResponseDto;

  factory OcrResponseDto.fromJson(Map<String, dynamic> json) =>
      _$OcrResponseDtoFromJson(json);
}

@freezed
class OcrBlockDto with _$OcrBlockDto {
  const factory OcrBlockDto({
    @Default('unknown') String type,
    OcrBoundingBoxDto? bbox,
    @Default([]) List<OcrLineDto> lines,
    @JsonKey(name: 'raw_text') String? rawText,
  }) = _OcrBlockDto;

  factory OcrBlockDto.fromJson(Map<String, dynamic> json) =>
      _$OcrBlockDtoFromJson(json);
}

@freezed
class OcrLineDto with _$OcrLineDto {
  const factory OcrLineDto({
    @Default('') String text,
    @Default(0.0) double confidence,
    OcrBoundingBoxDto? bbox,
  }) = _OcrLineDto;

  factory OcrLineDto.fromJson(Map<String, dynamic> json) =>
      _$OcrLineDtoFromJson(json);
}

@freezed
class OcrBoundingBoxDto with _$OcrBoundingBoxDto {
  const factory OcrBoundingBoxDto({
    required int x,
    required int y,
    required int width,
    required int height,
  }) = _OcrBoundingBoxDto;

  factory OcrBoundingBoxDto.fromJson(Map<String, dynamic> json) =>
      _$OcrBoundingBoxDtoFromJson(json);
}
