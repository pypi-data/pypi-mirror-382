# Kurdish Characters Library
# کتێبخانەی نامەی کوردی

A Python library to properly display Kurdish characters in tkinter and other interfaces.
کتێبخانەیەکی پایتۆن بۆ پیشاندانی دروستی نامەی کوردی لە تکینتەر و ڕووکارەکانی دیکە.

## Problem
## کێشە

When using Kurdish characters in tkinter or other Python GUI libraries, the characters may appear as question marks or strange symbols due to font and encoding issues.
کاتێک نامەی کوردی بەکاردەهێنرێت لە تکینتەر یان کتێبخانەکانی دیکەی پایتۆن، نامەکان دەتوانن وەکو نیشانەی پرسیار یان هێمایەکی نادیاری دیکە دەربچن بەهۆی کێشەی فۆنت و کۆدکردن.

## Solution
## چارەسەر

This library provides utilities to:
1. Automatically detect and use fonts that support Kurdish characters
2. Create tkinter widgets properly configured for Kurdish text
3. Validate Kurdish text content

ئەم کتێبخانەیە ئامرازەکان دابین دەکات بۆ:
٢. دۆزینەوەی خۆکارانە و بەکارهێنانی فۆنتەکان کە پشتگیری نامەی کوردی دەکەن
٢. دروستکردنی ویجتەکانی تکینتەر بەشێوەیەکی دروست بۆ نامەی کوردی
٣. پشتڕاستکردنەوەی ناوەڕۆکی نامەی کوردی

## Installation
## دامەزراندن

### Using pip
### بەکارهێنانی pip

```bash
pip install Kurdish_Characters
```

### Manual installation
### دامەزراندنی دەستی

1. Download the library files
2. Place them in your project directory

٢. دابەزاندنی فایلەکانی کتێبخانە
٢. جێگیرکردنیان لە بوخچەی پڕۆژەکەت

## Usage
## بەکارهێنان

### Basic Usage
### بەکارهێنانی سادە

```python
from Kurdish_Characters import KurdishTextHandler, create_kurdish_window

# Create a window with Kurdish font support
# دروستکردنی پەنجەرەیەک بە پشتگیری فۆنتی کوردی
root = create_kurdish_window("My Kurdish App")

# Create a handler instance
# دروستکردنی نموونەیەک لە هەندلەر
handler = KurdishTextHandler()

# Create widgets with proper Kurdish font support
# دروستکردنی ویجتەکان بە پشتگیری فۆنتی کوردی
label = handler.create_kurdish_label(root, "سڵاو جیهان")
label.pack()

entry = handler.create_kurdish_entry(root)
entry.pack()

text_widget = handler.create_kurdish_text(root)
text_widget.pack()
```

### Advanced Usage
### بەکارهێنانی پێشکەوتوو

```python
from Kurdish_Characters import display_kurdish_message

# Display a simple message box with Kurdish text
# پیشاندانی سندوقی پەیامێکی سادە بە نامەی کوردی
display_kurdish_message("سڵاو، ئەم پەیامە کوردییە", "پەیامی کوردی")
```

## Features
## تایبەتمەندییەکان

- Automatic font detection for Kurdish character support
- Helper functions for common tkinter widgets (Label, Entry, Text)
- Text validation for Kurdish characters
- Proper text direction handling
- Easy to integrate with existing tkinter applications

- دۆزینەوەی خۆکارانەی فۆنت بۆ پشتگیری نامەی کوردی
- فرمانە یارمەتیدەرەکان بۆ ویجتە باوەکانی تکینتەر (Label, Entry, Text)
- پشتڕاستکردنەوەی نامە بۆ نامەی کوردی
- مامەڵەکردنی دروستی ئاڕاستەی نامە
- ئاسانە بۆ تێکەڵکردن لەگەڵ بەرنامەکانی تکینتەری هەبوو

## Supported Characters
## نامە پشتگیریکراوەکان

The library supports all common Kurdish characters including:
کتێبخانەکە پشتگیری هەموو نامە کوردیە باوەکان دەکات لەوانە:

Basic isolated forms:
د ج ح ھ ه ع إ غ ڤ ف ق پ ص ض چ گ ک م ت ا أ ل ڵ ب ێ ی س ش ز و ە ى لا ر ڕ ۆ وو ئـ ژ ڵا ن y پیش پێک ئ آ ة ك y

Positional forms (initial, medial, final):
دـ ـدـ ـد   جـ ـجـ ـج   حـ ـحـ ـح   هـ ـهـ ـه   عـ ـعـ ـع   etc.

The library now includes complete positional forms for all characters, ensuring proper display of Kurdish text in all positions within words.

## Requirements
## پێویستییەکان

- Python 3.6 or higher
- tkinter (usually included with Python)

- پایتۆن ٣.٦ یان بەرزتر
- تکینتەر (بەشێوەیەکی ئاسایی لەگەڵ پایتۆن دابەزێنراوە)

## License
## مۆڵەت

This library is provided as-is for the Kurdish developer community. Feel free to use and modify it as needed.
ئەم کتێبخانەیە بە شێوەیەکی هەیە بۆ کۆمەڵگەی پەرەپێدەرە کوردەکان. بە دڵخوازی بەکاری بهێنە و دەستکاری بکە.

## Contributing
## بەشداربوون

Contributions are welcome! Please feel free to submit issues and pull requests.
بەشداربوون پێشوازی لێدەکرێت! تکایە بە دڵخوازی کێشەکان بنێرە و داواکاری ڕەنگەکان.

## Support
## پشتگیری

If you encounter any issues, please file an issue on the GitHub repository.
ئەگەر هەر کێشەیەکت هەبوو، تکایە کێشەکە بنێرە لەسەر بەخچەی گیت هەب.

GitHub: https://github.com/neshwantaha/Kurdish_Characters