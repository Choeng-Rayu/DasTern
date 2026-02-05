import 'package:flutter/material.dart';

class RoundedButton extends StatelessWidget {
  final String label;
  final VoidCallback onPressed;
  final Color backgroundColor;
  final Color textColor;
  final double borderRadius;
  final bool isLoading;
  final bool isEnabled;
  final IconData? icon;
  final Size minimumSize;

  const RoundedButton({
    Key? key,
    required this.label,
    required this.onPressed,
    this.backgroundColor = Colors.blue,
    this.textColor = Colors.white,
    this.borderRadius = 8,
    this.isLoading = false,
    this.isEnabled = true,
    this.icon,
    this.minimumSize = const Size(double.infinity, 50),
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: (isEnabled && !isLoading) ? onPressed : null,
      style: ElevatedButton.styleFrom(
        backgroundColor: backgroundColor,
        foregroundColor: textColor,
        minimumSize: minimumSize,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(borderRadius),
        ),
      ),
      child: isLoading
          ? const SizedBox(
              height: 20,
              width: 20,
              child: CircularProgressIndicator(strokeWidth: 2),
            )
          : Row(
              mainAxisAlignment: MainAxisAlignment.center,
              mainAxisSize: MainAxisSize.min,
              children: [
                if (icon != null) ...[
                  Icon(icon),
                  const SizedBox(width: 8),
                ],
                Text(label),
              ],
            ),
    );
  }
}

class TextInputField extends StatefulWidget {
  final String label;
  final String? hint;
  final TextEditingController controller;
  final TextInputType keyboardType;
  final int maxLines;
  final bool obscureText;
  final String? Function(String?)? validator;
  final IconData? prefixIcon;
  final IconData? suffixIcon;
  final VoidCallback? onSuffixIconPressed;

  const TextInputField({
    Key? key,
    required this.label,
    this.hint,
    required this.controller,
    this.keyboardType = TextInputType.text,
    this.maxLines = 1,
    this.obscureText = false,
    this.validator,
    this.prefixIcon,
    this.suffixIcon,
    this.onSuffixIconPressed,
  }) : super(key: key);

  @override
  State<TextInputField> createState() => _TextInputFieldState();
}

class _TextInputFieldState extends State<TextInputField> {
  late bool _showPassword;

  @override
  void initState() {
    super.initState();
    _showPassword = widget.obscureText;
  }

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: widget.controller,
      keyboardType: widget.keyboardType,
      maxLines: widget.maxLines,
      obscureText: _showPassword,
      validator: widget.validator,
      decoration: InputDecoration(
        labelText: widget.label,
        hintText: widget.hint,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: Colors.grey[300]!),
        ),
        prefixIcon: widget.prefixIcon != null ? Icon(widget.prefixIcon) : null,
        suffixIcon: widget.suffixIcon != null
            ? IconButton(
                icon: Icon(widget.suffixIcon),
                onPressed: () {
                  if (widget.obscureText) {
                    setState(() => _showPassword = !_showPassword);
                  }
                  widget.onSuffixIconPressed?.call();
                },
              )
            : null,
      ),
    );
  }
}

class EmptyStateWidget extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;
  final VoidCallback? onActionPressed;
  final String? actionLabel;

  const EmptyStateWidget({
    Key? key,
    required this.icon,
    required this.title,
    required this.description,
    this.onActionPressed,
    this.actionLabel,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 80, color: Colors.grey[400]),
          const SizedBox(height: 16),
          Text(
            title,
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Text(
            description,
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 14, color: Colors.grey[600]),
          ),
          if (actionLabel != null && onActionPressed != null) ...[
            const SizedBox(height: 24),
            RoundedButton(
              label: actionLabel!,
              onPressed: onActionPressed!,
              minimumSize: const Size(150, 40),
            ),
          ],
        ],
      ),
    );
  }
}
