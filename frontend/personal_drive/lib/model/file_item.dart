import 'package:flutter/widgets.dart';

class FileItem {
  final String name;
  final String type;
  final IconData icon;
  final Color iconColor;
  final Color backgroundColor;
  final Color darkBackgroundColor;
  final String timeAgo;

  FileItem({
    required this.name,
    required this.type,
    required this.icon,
    required this.iconColor,
    required this.backgroundColor,
    required this.darkBackgroundColor,
    required this.timeAgo,
  });
}
