import 'package:flutter/material.dart';

class AuthBackground extends StatelessWidget {
  final Widget child;
  final Widget? logo;
  final String? backgroundImage;
  final double overlayOpacity;

  const AuthBackground({
    Key? key,
    required this.child,
    this.logo,
    this.backgroundImage,
    this.overlayOpacity = 0.6,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        if (backgroundImage != null)
          Positioned.fill(
            child: Image.asset(backgroundImage!, fit: BoxFit.cover),
          ),
        Positioned.fill(
          child: Container(
              color: const Color(0xFF41b6e6).withOpacity(overlayOpacity)),
        ),
        // Add a white-to-transparent gradient for a 'smoke' effect
        Positioned.fill(
          child: IgnorePointer(
            child: Container(
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.white54,
                    Colors.transparent,
                  ],
                  stops: [0.0, 0.7],
                ),
              ),
            ),
          ),
        ),
        if (logo != null)
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.only(top: 16.0, left: 16.0),
              child: logo,
            ),
          ),
        child,
      ],
    );
  }
}
