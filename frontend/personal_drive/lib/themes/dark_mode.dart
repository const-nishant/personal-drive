import 'package:flutter/material.dart';

ThemeData darkTheme = ThemeData(
  colorScheme: ColorScheme.dark(
    surface: Colors.grey.shade900,
    primary: Colors.grey.shade600,
    secondary: Colors.grey.shade700,
    tertiary: const Color.fromARGB(255, 57, 57, 57),
    inversePrimary: Colors.grey.shade300,
  ),
  dialogTheme: DialogThemeData(
    titleTextStyle: TextStyle(color: Colors.grey.shade600),
    contentTextStyle: TextStyle(color: Colors.grey.shade600),
    backgroundColor: Colors.grey.shade900,
  ),
  iconTheme: IconThemeData(color: Colors.grey.shade200),
);
