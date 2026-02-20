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
              color: const Color.fromARGB(255, 191, 238, 255)
                  .withOpacity(overlayOpacity)),
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
