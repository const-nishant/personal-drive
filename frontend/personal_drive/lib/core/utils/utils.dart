/// Utility functions and helpers for the Personal Drive application
library;
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
/// Validates if a string is a valid email format
bool isValidEmail(String email) {
  final emailRegex = RegExp(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
  );
  return emailRegex.hasMatch(email);
}

/// Formats file size from bytes to human readable format
String formatFileSize(int bytes) {
  if (bytes < 1024) return '$bytes B';
  if (bytes < 1024 * 1024) return '${(bytes / 1024).toStringAsFixed(1)} KB';
  if (bytes < 1024 * 1024 * 1024) return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
  return '${(bytes / (1024 * 1024 * 1024)).toStringAsFixed(1)} GB';
}

/// Gets file extension from file name
String getFileExtension(String fileName) {
  final parts = fileName.split('.');
  return parts.length > 1 ? parts.last.toLowerCase() : '';
}

/// Gets file icon based on file extension
String getFileIcon(String extension) {
  switch (extension) {
    case 'pdf':
      return '📄';
    case 'doc':
    case 'docx':
      return '📝';
    case 'xls':
    case 'xlsx':
      return '📊';
    case 'ppt':
    case 'pptx':
      return '📊';
    case 'jpg':
    case 'jpeg':
    case 'png':
    case 'gif':
      return '🖼️';
    case 'mp4':
    case 'avi':
    case 'mov':
      return '🎥';
    case 'mp3':
    case 'wav':
    case 'flac':
      return '🎵';
    case 'zip':
    case 'rar':
    case '7z':
      return '📦';
    default:
      return '📁';
  }
}

/// Shows a snackbar with the given message
void showSnackBar(BuildContext context, String message, {bool isError = false}) {
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      content: Text(message),
      backgroundColor: isError ? Colors.red : Colors.green,
      duration: const Duration(seconds: 3),
    ),
  );
}

/// Debounces a function call
Function debounce(Function func, Duration duration) {
  Timer? timer;
  return () {
    timer?.cancel();
    timer = Timer(duration, () => func());
  };
}

String getFormattedDate() {
    final now = DateTime.now();
    return DateFormat('EEEE, d MMM').format(now);
  }
/// Throttles a function call
Function throttle(Function func, Duration duration) {
  bool isThrottled = false;
  return () {
    if (!isThrottled) {
      func();
      isThrottled = true;
      Timer(duration, () => isThrottled = false);
    }
  };
}
