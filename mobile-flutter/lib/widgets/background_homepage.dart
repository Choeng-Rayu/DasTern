import 'package:flutter/material.dart';

class BackgroundHomepage extends StatelessWidget {
  final Widget child;
  final Color? headerColor;
  final Color? bodyColor;
  final double headerHeight;

  const BackgroundHomepage({
    Key? key,
    required this.child,
    this.headerColor,
    this.bodyColor,
    this.headerHeight = 200.0,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final defaultHeaderColor = Theme.of(context).primaryColor;
    final defaultBodyColor = Colors.grey[50] ?? Colors.white;

    // Get the status bar height (notch area)
    final statusBarHeight = MediaQuery.of(context).padding.top;
    final totalHeaderHeight = headerHeight + statusBarHeight;

    return Stack(
      children: [
        // Header Section (Top colored area including notch)
        Positioned(
          top: 0,
          left: 0,
          right: 0,
          child: Container(
            height: totalHeaderHeight,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  headerColor ?? defaultHeaderColor,
                  (headerColor ?? defaultHeaderColor).withOpacity(0.8),
                ],
              ),
            ),
          ),
        ),
        // Body Section (Bottom lighter area)
        Positioned(
          top: totalHeaderHeight,
          left: 0,
          right: 0,
          bottom: 0,
          child: Container(
            color: bodyColor ?? defaultBodyColor,
          ),
        ),
        // Content on top
        child,
      ],
    );
  }
}
