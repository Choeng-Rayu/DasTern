import 'package:flutter/material.dart';

class HospitalLogo extends StatelessWidget {
  final double radius;
  final String name;
  final TextStyle? textStyle;
  final double spacing;

  const HospitalLogo({
    Key? key,
    this.radius = 28,
    this.name = 'DasTern',
    this.textStyle,
    this.spacing = 8,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        CircleAvatar(
          radius: radius,
          backgroundColor: Colors.blue.shade100,
          child: Icon(Icons.local_hospital, color: Colors.blue, size: radius),
        ),
        SizedBox(width: spacing),
        Text(
          name,
          style:
              textStyle ??
              const TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
                color: Colors.black,
              ),
        ),
      ],
    );
  }
}
