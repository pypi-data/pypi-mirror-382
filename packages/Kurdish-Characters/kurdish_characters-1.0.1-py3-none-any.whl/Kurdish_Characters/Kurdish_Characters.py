"""
Kurdish Text Handler Library
A Python library to properly display Kurdish characters in tkinter and other interfaces.
کتێبخانەی نامەی کوردی
کتێبخانەیەکی پایتۆن بۆ پیشاندانی دروستی نامەی کوردی لە تکینتەر و ڕووکارەکانی دیکە.
"""

import tkinter as tk
from tkinter import font
import sys

# List of Kurdish characters for reference
# لیستی نامە کوردیەکان بۆ سەرچاوە
KURDISH_CHARS = [
    'د', 'ج', 'ح', 'ھ', 'ه', 'ع', 'إ', 'غ', 'ڤ', 'ف', 'ق', 'پ', 'ص', 'ض', 
    'چ', 'گ', 'ک', 'م', 'ت', 'ا', 'أ', 'ل', 'ڵ', 'ب', 'ێ', 'ی', 'س', 'ش', 
    'ز', 'و', 'ە', 'ى', 'لا', 'ر', 'ڕ', 'ۆ', 'وو', 'ئـ', 'ژ', 'ڵا', 'ن', 'ي',
    'پیش', 'پێک',
    # Additional characters for beginning, middle, and end of words
    # زیادکردنی نامەکان بۆ سەرەتای، ناوەڕاست، و کۆتایی وشەکان
    'ئ', 'آ', 'ة', 'ك', 'ي', 'ـد', 'ـج', 'ـح', 'ـه', 'ـع', 'ـغ', 'ـڤ', 'ـف', 'ـق', 'ـپ', 
    'ـص', 'ـض', 'ـچ', 'ـگ', 'ـک', 'ـم', 'ـت', 'ـا', 'ـل', 'ـڵ', 'ـب', 'ـێ', 'ـی', 'ـس', 
    'ـش', 'ـز', 'ـو', 'ـە', 'ـى', 'ـر', 'ـڕ', 'ـۆ', 'ـوو', 'ـژ', 'ـن', 'ـي',
    'دـ', 'جـ', 'حـ', 'هـ', 'عـ', 'غـ', 'ڤـ', 'فـ', 'قـ', 'پـ', 'صـ', 'ضـ', 'چـ', 'گـ',
    'کـ', 'مـ', 'تـ', 'لـ', 'ڵـ', 'بـ', 'سـ', 'شـ', 'زـ', 'وـ', 'رـ', 'ڕـ', 'ژـ', 'نـ',
    # Proper medial forms (middle of words)
    'ـدـ', 'ـجـ', 'ـحـ', 'ـهـ', 'ـعـ', 'ـغـ', 'ـڤـ', 'ـفـ', 'ـقـ', 'ـپـ', 'ـصـ', 'ـضـ', 
    'ـچـ', 'ـگـ', 'ـکـ', 'ـمـ', 'ـتـ', 'ـلـ', 'ـڵـ', 'ـبـ', 'ـسـ', 'ـشـ', 'ـزـ', 'ـوـ', 
    'ـرـ', 'ـنـ', 'ـژـ', 'ـێـ',
    # Additional missing positional forms
    'آـ', 'ـآـ', 'ـآ', 'أـ', 'ـأـ', 'ـأ', 'إـ', 'ـإـ', 'ـإ', 'ـئـ', 'ـئ',
    'اـ', 'ـاـ', 'ةـ', 'ـةـ', 'ـة', 'كـ', 'ـكـ', 'ـك', 'ىـ', 'ـىـ', 'يـ', 'ـيـ',
    'ـڕـ', 'ھـ', 'ـھـ', 'ـھ', 'ۆـ', 'ـۆـ', 'یـ', 'ـیـ', 'ێـ', 'ەـ', 'ـەـ',
    # Double character forms
    'دـد', 'جـج', 'حـح', 'هـه', 'عـع', 'غـغ', 'ڤـڤ', 'فـف', 'قـق', 'پـپ', 'صـص', 'ضـض',
    'چـچ', 'گـگ', 'کـک', 'مـم', 'تـت', 'لـل', 'ڵـڵ', 'بـب', 'سـس', 'شـش', 'زـز', 'وـو',
    'رـر', 'ڕـڕ', 'ژـژ', 'نـن'
]

class KurdishTextHandler:
    """A class to handle Kurdish text display in various Python interfaces.
    کڵاسێک بۆ مامەڵەکردن لەگەڵ پیشاندانی نامەی کوردی لە ڕووکارە جۆراوجۆرەکانی پایتۆن.
    """
    
    def __init__(self):
        """Initialize the Kurdish text handler.
        دەستپێکردنی هەندلەری نامەی کوردی.
        """
        # لیستی فۆنتەکانی کوردی
        self.kurdish_fonts = [
            "Arial Unicode MS",
            "Tahoma",
            "Times New Roman",
            "Microsoft Sans Serif",
            "Segoe UI",
            "DejaVu Sans",
            "Noto Sans Arabic",
            "Noto Sans Kurdish"
        ]
    
    def get_available_kurdish_font(self):
        """
        Find and return the first available font that supports Kurdish characters.
        دۆزینەوە و گەڕاندنەوەی یەکەم فۆنتی بەردەست کە پشتگیری نامەی کوردی دەکات.
        
        Returns:
            str: Name of the first available Kurdish-supporting font
            str: ناوی یەکەم فۆنتی بەردەست کە پشتگیری نامەی کوردی دەکات
        """
        try:
            # Get all available fonts
            # وەرگرتنی هەموو فۆنتە بەردەستەکان
            available_fonts = list(font.families())
            
            # Check for Kurdish-specific fonts first
            # پشکنین بۆ فۆنتە تایبەتەکانی کوردی سەرەتا
            for kurdish_font in self.kurdish_fonts:
                if kurdish_font in available_fonts:
                    return kurdish_font
            
            # If no specific Kurdish font found, try common unicode fonts
            # ئەگەر هیچ فۆنتێکی تایبەتی کوردی نەدۆزرایەوە، هەوڵدان بۆ فۆنتە یونیکۆدییەکان
            unicode_fonts = ["Arial Unicode MS", "DejaVu Sans", "Noto Sans"]
            for unicode_font in unicode_fonts:
                if unicode_font in available_fonts:
                    return unicode_font
                    
            # Fallback to any available font
            # گەڕانەوە بۆ هەر فۆنتێکی بەردەست
            return available_fonts[0] if available_fonts else "Arial"
        except Exception:
            # Fallback if there's any issue with font detection
            # گەڕانەوە ئەگەر هەر کێشەیەک هەبوو لە دۆزینەوەی فۆنت
            return "Arial"
    
    def create_kurdish_label(self, parent, text="", **kwargs):
        """
        Create a tkinter Label with proper font for Kurdish text.
        دروستکردنی لەیبڵی تکینتەر بە فۆنتی دروست بۆ نامەی کوردی.
        
        Args:
            parent: Parent widget
            parent: ویجتی باوان
            text (str): Kurdish text to display
            text (str): نامەی کوردی بۆ پیشاندان
            **kwargs: Additional arguments for Label
            **kwargs: ئارگومێنتە زیادەکان بۆ لەیبڵ
            
        Returns:
            tk.Label: Label widget configured for Kurdish text
            tk.Label: ویجتی لەیبڵ کە بۆ نامەی کوردی شێوەدراوە
        """
        kurdish_font = self.get_available_kurdish_font()
        kwargs.setdefault('font', (kurdish_font, 12))
        return tk.Label(parent, text=text, **kwargs)
    
    def create_kurdish_entry(self, parent, **kwargs):
        """
        Create a tkinter Entry with proper font for Kurdish text.
        دروستکردنی ئینتری تکینتەر بە فۆنتی دروست بۆ نامەی کوردی.
        
        Args:
            parent: Parent widget
            parent: ویجتی باوان
            **kwargs: Additional arguments for Entry
            **kwargs: ئارگومێنتە زیادەکان بۆ ئینتری
            
        Returns:
            tk.Entry: Entry widget configured for Kurdish text
            tk.Entry: ویجتی ئینتری کە بۆ نامەی کوردی شێوەدراوە
        """
        kurdish_font = self.get_available_kurdish_font()
        kwargs.setdefault('font', (kurdish_font, 12))
        return tk.Entry(parent, **kwargs)
    
    def create_kurdish_text(self, parent, **kwargs):
        """
        Create a tkinter Text widget with proper font for Kurdish text.
        دروستکردنی ویجتی تێکستی تکینتەر بە فۆنتی دروست بۆ نامەی کوردی.
        
        Args:
            parent: Parent widget
            parent: ویجتی باوان
            **kwargs: Additional arguments for Text widget
            **kwargs: ئارگومێنتە زیادەکان بۆ ویجتی تێکست
            
        Returns:
            tk.Text: Text widget configured for Kurdish text
            tk.Text: ویجتی تێکست کە بۆ نامەی کوردی شێوەدراوە
        """
        kurdish_font = self.get_available_kurdish_font()
        kwargs.setdefault('font', (kurdish_font, 12))
        return tk.Text(parent, **kwargs)
    
    def fix_text_direction(self, text):
        """
        Fix text direction for proper Kurdish text display.
        چاککردنەوەی ئاڕاستەی نامە بۆ پیشاندانی دروستی نامەی کوردی.
        
        Args:
            text (str): Text to fix direction for
            text (str): نامە بۆ چاککردنەوەی ئاڕاستە
            
        Returns:
            str: Text with proper direction
            str: نامە لەگەڵ ئاڕاستەی دروست
        """
        # For Kurdish, we generally don't need special direction handling
        # But this method is here for future enhancements
        # بۆ کوردی، بەشێوەیەکی گشتی پێویستی نابێت بە مامەڵەی تایبەتی ئاڕاستە
        # بەڵام ئەم ڕێگایە لێرەیە بۆ پێشخستنەکانی داهاتوو
        return text
    
    def validate_kurdish_text(self, text):
        """
        Validate if text contains Kurdish characters.
        پشتڕاستکردنەوە ئەگەر نامەکە نامەی کوردی لەخۆبگرێت.
        
        Args:
            text (str): Text to validate
            text (str): نامە بۆ پشتڕاستکردنەوە
            
        Returns:
            bool: True if text contains Kurdish characters, False otherwise
            bool: ڕاست ئەگەر نامەکە نامەی کوردی لەخۆبگرێت، هەڵە بەپێچەوانە
        """
        kurdish_char_set = set(KURDISH_CHARS)
        text_char_set = set(text)
        return bool(kurdish_char_set.intersection(text_char_set))

def create_kurdish_window(title="Kurdish Text Window"):
    """
    Create a tkinter window configured for Kurdish text.
    دروستکردنی پەنجەرەیەکی تکینتەر کە بۆ نامەی کوردی شێوەدراوە.
    
    Args:
        title (str): Window title
        title (str): ناونیشانی پەنجەرە
        
    Returns:
        tk.Tk: Configured tkinter window
        tk.Tk: پەنجەرەی تکینتەر کە شێوەدراوە
    """
    root = tk.Tk()
    root.title(title)
    
    # Try to set a proper font for the entire window
    # هەوڵدان بۆ دانانی فۆنتێکی دروست بۆ هەموو پەنجەرەکە
    try:
        kurdish_font = KurdishTextHandler().get_available_kurdish_font()
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family=kurdish_font, size=12)
    except Exception:
        pass  # If we can't set the font, continue with default
        # ئەگەر نەتوانین فۆنت دابنێین، بەردەوام بوون لەگەڵ فۆنتی سەرەکی
    
    return root

def display_kurdish_message(message, title="Kurdish Message"):
    """
    Display a message box with Kurdish text.
    پیشاندانی سندوقێکی پەیام بە نامەی کوردی.
    
    Args:
        message (str): Kurdish message to display
        message (str): پەیامی کوردی بۆ پیشاندان
        title (str): Title of the message box
        title (str): ناونیشانی سندوقی پەیام
    """
    root = create_kurdish_window(title)
    handler = KurdishTextHandler()
    
    label = handler.create_kurdish_label(root, message, wraplength=400, justify='right')
    label.pack(padx=20, pady=20)
    
    button = tk.Button(root, text="OK", command=root.destroy)
    button.pack(pady=10)
    
    root.mainloop()

# Example usage
# نموونەی بەکارهێنان
if __name__ == "__main__":
    # Example of how to use the library
    # نموونەی چۆنیەتی بەکارهێنانی کتێبخانەکە
    sample_kurdish_text = "د ج ح ھ ه ع إ غ ڤ ف ق پ ص ض چ گ ک م ت ا أ ل ڵ ب ێ ی س ش ز و ە ى لا ر ڕ ۆ وو ئـ ژ ڵا ن y پیش پێک ئ آ ة ك y"
    
    # Display in a message box
    # پیشاندان لە سندوقێکی پەیام
    display_kurdish_message(sample_kurdish_text, "نمونەی نامەی کوردی")