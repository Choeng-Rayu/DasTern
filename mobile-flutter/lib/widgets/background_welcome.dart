import 'package:flutter/material.dart';

class BackgroundWelcome extends StatelessWidget {
  final Widget? child;
  const BackgroundWelcome({Key? key, this.child}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        image: DecorationImage(
          image: AssetImage('assets/images/background-welcome.jpg'),
          fit: BoxFit.cover,
        ),
      ),
      child: child,
    );
  }
}
