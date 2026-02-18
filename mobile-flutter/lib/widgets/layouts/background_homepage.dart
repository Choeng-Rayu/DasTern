import 'package:flutter/material.dart';

class BackgroundHomepage extends StatelessWidget {
  final Widget child;
  final Color? bodyColor;

  const BackgroundHomepage({
    Key? key,
    required this.child,
    this.bodyColor,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final defaultBodyColor = Colors.grey[50] ?? Colors.white;

    return Container(
      width: double.infinity,
      height: double.infinity,
      color: bodyColor ?? defaultBodyColor,
      child: child,
    );
  }
}
