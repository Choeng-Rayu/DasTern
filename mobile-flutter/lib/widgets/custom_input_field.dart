import 'package:flutter/material.dart';

class CustomInputField extends StatelessWidget {
  final String hint;
  final int? maxLength;
  final TextInputType? keyboardType;
  final bool obscureText;
  final TextEditingController? controller;
  final double borderRadius;
  final EdgeInsetsGeometry? padding;
  final TextStyle? hintStyle;

  const CustomInputField({
    Key? key,
    required this.hint,
    this.maxLength,
    this.keyboardType,
    this.obscureText = false,
    this.controller,
    this.borderRadius = 12,
    this.padding,
    this.hintStyle,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: padding ?? const EdgeInsets.only(bottom: 12.0),
      child: TextField(
        controller: controller,
        maxLength: maxLength,
        keyboardType: keyboardType,
        obscureText: obscureText,
        style: const TextStyle(fontSize: 16, color: Colors.black),
        decoration: InputDecoration(
          counterText: '',
          hintText: hint,
          hintStyle:
              hintStyle ?? const TextStyle(fontSize: 15, color: Colors.black38),
          filled: true,
          fillColor: Colors.white,
          contentPadding: const EdgeInsets.symmetric(
            vertical: 14,
            horizontal: 16,
          ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(borderRadius),
            borderSide: BorderSide.none,
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(borderRadius),
            borderSide: BorderSide.none,
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(borderRadius),
            borderSide: BorderSide(color: Colors.blue.shade100, width: 2),
          ),
        ),
      ),
    );
  }
}
