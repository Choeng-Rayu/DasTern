// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'ocr_response_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

OcrResponseDto _$OcrResponseDtoFromJson(Map<String, dynamic> json) {
  return _OcrResponseDto.fromJson(json);
}

/// @nodoc
mixin _$OcrResponseDto {
  @JsonKey(name: 'raw_text')
  String? get rawText => throw _privateConstructorUsedError;
  List<OcrBlockDto> get blocks => throw _privateConstructorUsedError;

  /// Serializes this OcrResponseDto to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of OcrResponseDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $OcrResponseDtoCopyWith<OcrResponseDto> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $OcrResponseDtoCopyWith<$Res> {
  factory $OcrResponseDtoCopyWith(
          OcrResponseDto value, $Res Function(OcrResponseDto) then) =
      _$OcrResponseDtoCopyWithImpl<$Res, OcrResponseDto>;
  @useResult
  $Res call(
      {@JsonKey(name: 'raw_text') String? rawText, List<OcrBlockDto> blocks});
}

/// @nodoc
class _$OcrResponseDtoCopyWithImpl<$Res, $Val extends OcrResponseDto>
    implements $OcrResponseDtoCopyWith<$Res> {
  _$OcrResponseDtoCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of OcrResponseDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? rawText = freezed,
    Object? blocks = null,
  }) {
    return _then(_value.copyWith(
      rawText: freezed == rawText
          ? _value.rawText
          : rawText // ignore: cast_nullable_to_non_nullable
              as String?,
      blocks: null == blocks
          ? _value.blocks
          : blocks // ignore: cast_nullable_to_non_nullable
              as List<OcrBlockDto>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$OcrResponseDtoImplCopyWith<$Res>
    implements $OcrResponseDtoCopyWith<$Res> {
  factory _$$OcrResponseDtoImplCopyWith(_$OcrResponseDtoImpl value,
          $Res Function(_$OcrResponseDtoImpl) then) =
      __$$OcrResponseDtoImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'raw_text') String? rawText, List<OcrBlockDto> blocks});
}

/// @nodoc
class __$$OcrResponseDtoImplCopyWithImpl<$Res>
    extends _$OcrResponseDtoCopyWithImpl<$Res, _$OcrResponseDtoImpl>
    implements _$$OcrResponseDtoImplCopyWith<$Res> {
  __$$OcrResponseDtoImplCopyWithImpl(
      _$OcrResponseDtoImpl _value, $Res Function(_$OcrResponseDtoImpl) _then)
      : super(_value, _then);

  /// Create a copy of OcrResponseDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? rawText = freezed,
    Object? blocks = null,
  }) {
    return _then(_$OcrResponseDtoImpl(
      rawText: freezed == rawText
          ? _value.rawText
          : rawText // ignore: cast_nullable_to_non_nullable
              as String?,
      blocks: null == blocks
          ? _value._blocks
          : blocks // ignore: cast_nullable_to_non_nullable
              as List<OcrBlockDto>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$OcrResponseDtoImpl implements _OcrResponseDto {
  const _$OcrResponseDtoImpl(
      {@JsonKey(name: 'raw_text') this.rawText,
      final List<OcrBlockDto> blocks = const []})
      : _blocks = blocks;

  factory _$OcrResponseDtoImpl.fromJson(Map<String, dynamic> json) =>
      _$$OcrResponseDtoImplFromJson(json);

  @override
  @JsonKey(name: 'raw_text')
  final String? rawText;
  final List<OcrBlockDto> _blocks;
  @override
  @JsonKey()
  List<OcrBlockDto> get blocks {
    if (_blocks is EqualUnmodifiableListView) return _blocks;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_blocks);
  }

  @override
  String toString() {
    return 'OcrResponseDto(rawText: $rawText, blocks: $blocks)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$OcrResponseDtoImpl &&
            (identical(other.rawText, rawText) || other.rawText == rawText) &&
            const DeepCollectionEquality().equals(other._blocks, _blocks));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType, rawText, const DeepCollectionEquality().hash(_blocks));

  /// Create a copy of OcrResponseDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$OcrResponseDtoImplCopyWith<_$OcrResponseDtoImpl> get copyWith =>
      __$$OcrResponseDtoImplCopyWithImpl<_$OcrResponseDtoImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$OcrResponseDtoImplToJson(
      this,
    );
  }
}

abstract class _OcrResponseDto implements OcrResponseDto {
  const factory _OcrResponseDto(
      {@JsonKey(name: 'raw_text') final String? rawText,
      final List<OcrBlockDto> blocks}) = _$OcrResponseDtoImpl;

  factory _OcrResponseDto.fromJson(Map<String, dynamic> json) =
      _$OcrResponseDtoImpl.fromJson;

  @override
  @JsonKey(name: 'raw_text')
  String? get rawText;
  @override
  List<OcrBlockDto> get blocks;

  /// Create a copy of OcrResponseDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$OcrResponseDtoImplCopyWith<_$OcrResponseDtoImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

OcrBlockDto _$OcrBlockDtoFromJson(Map<String, dynamic> json) {
  return _OcrBlockDto.fromJson(json);
}

/// @nodoc
mixin _$OcrBlockDto {
  String get type => throw _privateConstructorUsedError;
  OcrBoundingBoxDto? get bbox => throw _privateConstructorUsedError;
  List<OcrLineDto> get lines => throw _privateConstructorUsedError;
  @JsonKey(name: 'raw_text')
  String? get rawText => throw _privateConstructorUsedError;

  /// Serializes this OcrBlockDto to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of OcrBlockDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $OcrBlockDtoCopyWith<OcrBlockDto> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $OcrBlockDtoCopyWith<$Res> {
  factory $OcrBlockDtoCopyWith(
          OcrBlockDto value, $Res Function(OcrBlockDto) then) =
      _$OcrBlockDtoCopyWithImpl<$Res, OcrBlockDto>;
  @useResult
  $Res call(
      {String type,
      OcrBoundingBoxDto? bbox,
      List<OcrLineDto> lines,
      @JsonKey(name: 'raw_text') String? rawText});

  $OcrBoundingBoxDtoCopyWith<$Res>? get bbox;
}

/// @nodoc
class _$OcrBlockDtoCopyWithImpl<$Res, $Val extends OcrBlockDto>
    implements $OcrBlockDtoCopyWith<$Res> {
  _$OcrBlockDtoCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of OcrBlockDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? type = null,
    Object? bbox = freezed,
    Object? lines = null,
    Object? rawText = freezed,
  }) {
    return _then(_value.copyWith(
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      bbox: freezed == bbox
          ? _value.bbox
          : bbox // ignore: cast_nullable_to_non_nullable
              as OcrBoundingBoxDto?,
      lines: null == lines
          ? _value.lines
          : lines // ignore: cast_nullable_to_non_nullable
              as List<OcrLineDto>,
      rawText: freezed == rawText
          ? _value.rawText
          : rawText // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }

  /// Create a copy of OcrBlockDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $OcrBoundingBoxDtoCopyWith<$Res>? get bbox {
    if (_value.bbox == null) {
      return null;
    }

    return $OcrBoundingBoxDtoCopyWith<$Res>(_value.bbox!, (value) {
      return _then(_value.copyWith(bbox: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$OcrBlockDtoImplCopyWith<$Res>
    implements $OcrBlockDtoCopyWith<$Res> {
  factory _$$OcrBlockDtoImplCopyWith(
          _$OcrBlockDtoImpl value, $Res Function(_$OcrBlockDtoImpl) then) =
      __$$OcrBlockDtoImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String type,
      OcrBoundingBoxDto? bbox,
      List<OcrLineDto> lines,
      @JsonKey(name: 'raw_text') String? rawText});

  @override
  $OcrBoundingBoxDtoCopyWith<$Res>? get bbox;
}

/// @nodoc
class __$$OcrBlockDtoImplCopyWithImpl<$Res>
    extends _$OcrBlockDtoCopyWithImpl<$Res, _$OcrBlockDtoImpl>
    implements _$$OcrBlockDtoImplCopyWith<$Res> {
  __$$OcrBlockDtoImplCopyWithImpl(
      _$OcrBlockDtoImpl _value, $Res Function(_$OcrBlockDtoImpl) _then)
      : super(_value, _then);

  /// Create a copy of OcrBlockDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? type = null,
    Object? bbox = freezed,
    Object? lines = null,
    Object? rawText = freezed,
  }) {
    return _then(_$OcrBlockDtoImpl(
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      bbox: freezed == bbox
          ? _value.bbox
          : bbox // ignore: cast_nullable_to_non_nullable
              as OcrBoundingBoxDto?,
      lines: null == lines
          ? _value._lines
          : lines // ignore: cast_nullable_to_non_nullable
              as List<OcrLineDto>,
      rawText: freezed == rawText
          ? _value.rawText
          : rawText // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$OcrBlockDtoImpl implements _OcrBlockDto {
  const _$OcrBlockDtoImpl(
      {this.type = 'unknown',
      this.bbox,
      final List<OcrLineDto> lines = const [],
      @JsonKey(name: 'raw_text') this.rawText})
      : _lines = lines;

  factory _$OcrBlockDtoImpl.fromJson(Map<String, dynamic> json) =>
      _$$OcrBlockDtoImplFromJson(json);

  @override
  @JsonKey()
  final String type;
  @override
  final OcrBoundingBoxDto? bbox;
  final List<OcrLineDto> _lines;
  @override
  @JsonKey()
  List<OcrLineDto> get lines {
    if (_lines is EqualUnmodifiableListView) return _lines;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_lines);
  }

  @override
  @JsonKey(name: 'raw_text')
  final String? rawText;

  @override
  String toString() {
    return 'OcrBlockDto(type: $type, bbox: $bbox, lines: $lines, rawText: $rawText)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$OcrBlockDtoImpl &&
            (identical(other.type, type) || other.type == type) &&
            (identical(other.bbox, bbox) || other.bbox == bbox) &&
            const DeepCollectionEquality().equals(other._lines, _lines) &&
            (identical(other.rawText, rawText) || other.rawText == rawText));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, type, bbox,
      const DeepCollectionEquality().hash(_lines), rawText);

  /// Create a copy of OcrBlockDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$OcrBlockDtoImplCopyWith<_$OcrBlockDtoImpl> get copyWith =>
      __$$OcrBlockDtoImplCopyWithImpl<_$OcrBlockDtoImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$OcrBlockDtoImplToJson(
      this,
    );
  }
}

abstract class _OcrBlockDto implements OcrBlockDto {
  const factory _OcrBlockDto(
      {final String type,
      final OcrBoundingBoxDto? bbox,
      final List<OcrLineDto> lines,
      @JsonKey(name: 'raw_text') final String? rawText}) = _$OcrBlockDtoImpl;

  factory _OcrBlockDto.fromJson(Map<String, dynamic> json) =
      _$OcrBlockDtoImpl.fromJson;

  @override
  String get type;
  @override
  OcrBoundingBoxDto? get bbox;
  @override
  List<OcrLineDto> get lines;
  @override
  @JsonKey(name: 'raw_text')
  String? get rawText;

  /// Create a copy of OcrBlockDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$OcrBlockDtoImplCopyWith<_$OcrBlockDtoImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

OcrLineDto _$OcrLineDtoFromJson(Map<String, dynamic> json) {
  return _OcrLineDto.fromJson(json);
}

/// @nodoc
mixin _$OcrLineDto {
  String get text => throw _privateConstructorUsedError;
  double get confidence => throw _privateConstructorUsedError;
  OcrBoundingBoxDto? get bbox => throw _privateConstructorUsedError;

  /// Serializes this OcrLineDto to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of OcrLineDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $OcrLineDtoCopyWith<OcrLineDto> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $OcrLineDtoCopyWith<$Res> {
  factory $OcrLineDtoCopyWith(
          OcrLineDto value, $Res Function(OcrLineDto) then) =
      _$OcrLineDtoCopyWithImpl<$Res, OcrLineDto>;
  @useResult
  $Res call({String text, double confidence, OcrBoundingBoxDto? bbox});

  $OcrBoundingBoxDtoCopyWith<$Res>? get bbox;
}

/// @nodoc
class _$OcrLineDtoCopyWithImpl<$Res, $Val extends OcrLineDto>
    implements $OcrLineDtoCopyWith<$Res> {
  _$OcrLineDtoCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of OcrLineDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? text = null,
    Object? confidence = null,
    Object? bbox = freezed,
  }) {
    return _then(_value.copyWith(
      text: null == text
          ? _value.text
          : text // ignore: cast_nullable_to_non_nullable
              as String,
      confidence: null == confidence
          ? _value.confidence
          : confidence // ignore: cast_nullable_to_non_nullable
              as double,
      bbox: freezed == bbox
          ? _value.bbox
          : bbox // ignore: cast_nullable_to_non_nullable
              as OcrBoundingBoxDto?,
    ) as $Val);
  }

  /// Create a copy of OcrLineDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $OcrBoundingBoxDtoCopyWith<$Res>? get bbox {
    if (_value.bbox == null) {
      return null;
    }

    return $OcrBoundingBoxDtoCopyWith<$Res>(_value.bbox!, (value) {
      return _then(_value.copyWith(bbox: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$OcrLineDtoImplCopyWith<$Res>
    implements $OcrLineDtoCopyWith<$Res> {
  factory _$$OcrLineDtoImplCopyWith(
          _$OcrLineDtoImpl value, $Res Function(_$OcrLineDtoImpl) then) =
      __$$OcrLineDtoImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String text, double confidence, OcrBoundingBoxDto? bbox});

  @override
  $OcrBoundingBoxDtoCopyWith<$Res>? get bbox;
}

/// @nodoc
class __$$OcrLineDtoImplCopyWithImpl<$Res>
    extends _$OcrLineDtoCopyWithImpl<$Res, _$OcrLineDtoImpl>
    implements _$$OcrLineDtoImplCopyWith<$Res> {
  __$$OcrLineDtoImplCopyWithImpl(
      _$OcrLineDtoImpl _value, $Res Function(_$OcrLineDtoImpl) _then)
      : super(_value, _then);

  /// Create a copy of OcrLineDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? text = null,
    Object? confidence = null,
    Object? bbox = freezed,
  }) {
    return _then(_$OcrLineDtoImpl(
      text: null == text
          ? _value.text
          : text // ignore: cast_nullable_to_non_nullable
              as String,
      confidence: null == confidence
          ? _value.confidence
          : confidence // ignore: cast_nullable_to_non_nullable
              as double,
      bbox: freezed == bbox
          ? _value.bbox
          : bbox // ignore: cast_nullable_to_non_nullable
              as OcrBoundingBoxDto?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$OcrLineDtoImpl implements _OcrLineDto {
  const _$OcrLineDtoImpl({this.text = '', this.confidence = 0.0, this.bbox});

  factory _$OcrLineDtoImpl.fromJson(Map<String, dynamic> json) =>
      _$$OcrLineDtoImplFromJson(json);

  @override
  @JsonKey()
  final String text;
  @override
  @JsonKey()
  final double confidence;
  @override
  final OcrBoundingBoxDto? bbox;

  @override
  String toString() {
    return 'OcrLineDto(text: $text, confidence: $confidence, bbox: $bbox)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$OcrLineDtoImpl &&
            (identical(other.text, text) || other.text == text) &&
            (identical(other.confidence, confidence) ||
                other.confidence == confidence) &&
            (identical(other.bbox, bbox) || other.bbox == bbox));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, text, confidence, bbox);

  /// Create a copy of OcrLineDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$OcrLineDtoImplCopyWith<_$OcrLineDtoImpl> get copyWith =>
      __$$OcrLineDtoImplCopyWithImpl<_$OcrLineDtoImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$OcrLineDtoImplToJson(
      this,
    );
  }
}

abstract class _OcrLineDto implements OcrLineDto {
  const factory _OcrLineDto(
      {final String text,
      final double confidence,
      final OcrBoundingBoxDto? bbox}) = _$OcrLineDtoImpl;

  factory _OcrLineDto.fromJson(Map<String, dynamic> json) =
      _$OcrLineDtoImpl.fromJson;

  @override
  String get text;
  @override
  double get confidence;
  @override
  OcrBoundingBoxDto? get bbox;

  /// Create a copy of OcrLineDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$OcrLineDtoImplCopyWith<_$OcrLineDtoImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

OcrBoundingBoxDto _$OcrBoundingBoxDtoFromJson(Map<String, dynamic> json) {
  return _OcrBoundingBoxDto.fromJson(json);
}

/// @nodoc
mixin _$OcrBoundingBoxDto {
  int get x => throw _privateConstructorUsedError;
  int get y => throw _privateConstructorUsedError;
  int get width => throw _privateConstructorUsedError;
  int get height => throw _privateConstructorUsedError;

  /// Serializes this OcrBoundingBoxDto to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of OcrBoundingBoxDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $OcrBoundingBoxDtoCopyWith<OcrBoundingBoxDto> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $OcrBoundingBoxDtoCopyWith<$Res> {
  factory $OcrBoundingBoxDtoCopyWith(
          OcrBoundingBoxDto value, $Res Function(OcrBoundingBoxDto) then) =
      _$OcrBoundingBoxDtoCopyWithImpl<$Res, OcrBoundingBoxDto>;
  @useResult
  $Res call({int x, int y, int width, int height});
}

/// @nodoc
class _$OcrBoundingBoxDtoCopyWithImpl<$Res, $Val extends OcrBoundingBoxDto>
    implements $OcrBoundingBoxDtoCopyWith<$Res> {
  _$OcrBoundingBoxDtoCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of OcrBoundingBoxDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? x = null,
    Object? y = null,
    Object? width = null,
    Object? height = null,
  }) {
    return _then(_value.copyWith(
      x: null == x
          ? _value.x
          : x // ignore: cast_nullable_to_non_nullable
              as int,
      y: null == y
          ? _value.y
          : y // ignore: cast_nullable_to_non_nullable
              as int,
      width: null == width
          ? _value.width
          : width // ignore: cast_nullable_to_non_nullable
              as int,
      height: null == height
          ? _value.height
          : height // ignore: cast_nullable_to_non_nullable
              as int,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$OcrBoundingBoxDtoImplCopyWith<$Res>
    implements $OcrBoundingBoxDtoCopyWith<$Res> {
  factory _$$OcrBoundingBoxDtoImplCopyWith(_$OcrBoundingBoxDtoImpl value,
          $Res Function(_$OcrBoundingBoxDtoImpl) then) =
      __$$OcrBoundingBoxDtoImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({int x, int y, int width, int height});
}

/// @nodoc
class __$$OcrBoundingBoxDtoImplCopyWithImpl<$Res>
    extends _$OcrBoundingBoxDtoCopyWithImpl<$Res, _$OcrBoundingBoxDtoImpl>
    implements _$$OcrBoundingBoxDtoImplCopyWith<$Res> {
  __$$OcrBoundingBoxDtoImplCopyWithImpl(_$OcrBoundingBoxDtoImpl _value,
      $Res Function(_$OcrBoundingBoxDtoImpl) _then)
      : super(_value, _then);

  /// Create a copy of OcrBoundingBoxDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? x = null,
    Object? y = null,
    Object? width = null,
    Object? height = null,
  }) {
    return _then(_$OcrBoundingBoxDtoImpl(
      x: null == x
          ? _value.x
          : x // ignore: cast_nullable_to_non_nullable
              as int,
      y: null == y
          ? _value.y
          : y // ignore: cast_nullable_to_non_nullable
              as int,
      width: null == width
          ? _value.width
          : width // ignore: cast_nullable_to_non_nullable
              as int,
      height: null == height
          ? _value.height
          : height // ignore: cast_nullable_to_non_nullable
              as int,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$OcrBoundingBoxDtoImpl implements _OcrBoundingBoxDto {
  const _$OcrBoundingBoxDtoImpl(
      {required this.x,
      required this.y,
      required this.width,
      required this.height});

  factory _$OcrBoundingBoxDtoImpl.fromJson(Map<String, dynamic> json) =>
      _$$OcrBoundingBoxDtoImplFromJson(json);

  @override
  final int x;
  @override
  final int y;
  @override
  final int width;
  @override
  final int height;

  @override
  String toString() {
    return 'OcrBoundingBoxDto(x: $x, y: $y, width: $width, height: $height)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$OcrBoundingBoxDtoImpl &&
            (identical(other.x, x) || other.x == x) &&
            (identical(other.y, y) || other.y == y) &&
            (identical(other.width, width) || other.width == width) &&
            (identical(other.height, height) || other.height == height));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, x, y, width, height);

  /// Create a copy of OcrBoundingBoxDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$OcrBoundingBoxDtoImplCopyWith<_$OcrBoundingBoxDtoImpl> get copyWith =>
      __$$OcrBoundingBoxDtoImplCopyWithImpl<_$OcrBoundingBoxDtoImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$OcrBoundingBoxDtoImplToJson(
      this,
    );
  }
}

abstract class _OcrBoundingBoxDto implements OcrBoundingBoxDto {
  const factory _OcrBoundingBoxDto(
      {required final int x,
      required final int y,
      required final int width,
      required final int height}) = _$OcrBoundingBoxDtoImpl;

  factory _OcrBoundingBoxDto.fromJson(Map<String, dynamic> json) =
      _$OcrBoundingBoxDtoImpl.fromJson;

  @override
  int get x;
  @override
  int get y;
  @override
  int get width;
  @override
  int get height;

  /// Create a copy of OcrBoundingBoxDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$OcrBoundingBoxDtoImplCopyWith<_$OcrBoundingBoxDtoImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
