import 'package:flutter/material.dart';

class LoadingDialog extends StatelessWidget {
  final String message;
  final bool isDismissible;

  const LoadingDialog({
    Key? key,
    this.message = 'Processing...',
    this.isDismissible = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return WillPopScope(
      onWillPop: () async => isDismissible,
      child: Dialog(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const CircularProgressIndicator(),
              const SizedBox(height: 16),
              Text(
                message,
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 16),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class ErrorDialog extends StatelessWidget {
  final String title;
  final String message;
  final VoidCallback? onRetry;
  final VoidCallback? onDismiss;

  const ErrorDialog({
    Key? key,
    this.title = 'Error',
    required this.message,
    this.onRetry,
    this.onDismiss,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(title),
      content: SingleChildScrollView(
        child: Text(message),
      ),
      actions: [
        if (onRetry != null)
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              onRetry?.call();
            },
            child: const Text('Retry'),
          ),
        TextButton(
          onPressed: () {
            Navigator.pop(context);
            onDismiss?.call();
          },
          child: const Text('Dismiss'),
        ),
      ],
    );
  }
}

class SuccessDialog extends StatelessWidget {
  final String title;
  final String message;
  final VoidCallback? onConfirm;

  const SuccessDialog({
    Key? key,
    this.title = 'Success',
    required this.message,
    this.onConfirm,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Row(
        children: [
          Icon(Icons.check_circle, color: Colors.green, size: 28),
          const SizedBox(width: 12),
          Expanded(child: Text(title)),
        ],
      ),
      content: Text(message),
      actions: [
        TextButton(
          onPressed: () {
            Navigator.pop(context);
            onConfirm?.call();
          },
          child: const Text('OK'),
        ),
      ],
    );
  }
}
