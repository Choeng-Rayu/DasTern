import 'package:flutter/material.dart';

class BottomRoundContainer extends StatelessWidget {
  final Widget child;
  final double borderRadius;
  final double elevation;
  final Color? backgroundColor;
  final EdgeInsetsGeometry? padding;

  const BottomRoundContainer({
    Key? key,
    required this.child,
    this.borderRadius = 32,
    this.elevation = 16,
    this.backgroundColor,
    this.padding,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.bottomCenter,
      child: Container(
        width: MediaQuery.of(context).size.width,
        // Height can be set by parent or via child
        decoration: BoxDecoration(
          // color: backgroundColor ?? Colors.white.withOpacity(0.7),
          color: backgroundColor ?? Colors.white,
          borderRadius: BorderRadius.only(
            topLeft: Radius.circular(borderRadius),
            topRight: Radius.circular(borderRadius),
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.08),
              blurRadius: elevation,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        padding:
            padding ?? const EdgeInsets.symmetric(vertical: 28, horizontal: 18),
        child: child,
      ),
    );
  }
}
