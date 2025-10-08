"""
Example of using the Kurdish Text Handler Library
نموونەی بەکارهێنانی کتێبخانەی نامەی کوردی
"""

import tkinter as tk
from Kurdish_Characters import KurdishTextHandler, create_kurdish_window

def main():
    # Create the main window with Kurdish font support
    # دروستکردنی پەنجەرەی سەرەکی بە پشتگیری فۆنتی کوردی
    root = create_kurdish_window("نموونەی کوردی - Kurdish Example")
    handler = KurdishTextHandler()
    
    # Set window size
    # دانانی قەبارەی پەنجەرە
    root.geometry("500x500")
    
    # Kurdish sample text
    # نموونەی نامەی کوردی
    kurdish_text = "د ج ح ھ ه ع إ غ ڤ ف ق پ ص ض چ گ ک م ت ا أ ل ڵ ب ێ ی س ش ز و ە ى لا ر ڕ ۆ وو ئـ ژ ڵا ن y پیش پێک ئ آ ة ك y"
    sample_sentence = "سڵاو، ئەم نموونەیەکە بۆ نیشاندانی نامەی کوردییە."
    
    # Title label
    # لەیبڵی ناونیشان
    title_label = handler.create_kurdish_label(
        root, 
        "نموونەی بەکارهێنانی کتێبخانەی نامەی کوردی", 
        font=("Arial", 14, "bold")
    )
    title_label.pack(pady=10)
    
    # Label with Kurdish characters
    # لەیبڵ بە نامەی کوردی
    kurdish_label = handler.create_kurdish_label(
        root,
        f"ئەلفوبێی کوردی: {kurdish_text}",
        wraplength=450,
        justify='right'
    )
    kurdish_label.pack(pady=5)
    
    # Sample sentence label
    # لەیبڵی ڕستەی نموونە
    sentence_label = handler.create_kurdish_label(
        root,
        f"نموونەی نامە: {sample_sentence}",
        wraplength=450,
        justify='right'
    )
    sentence_label.pack(pady=5)
    
    # Demonstration of positional forms
    # پیشاندانی فۆرمەکانی جیاواز
    positional_demo_label = handler.create_kurdish_label(
        root,
        "نموونەی فۆرمەکانی جیاواز:",
        font=("Arial", 12, "bold"),
        wraplength=450,
        justify='right'
    )
    positional_demo_label.pack(pady=(15, 5))
    
    # Positional forms examples
    forms_examples = [
        "فۆرمی تەنیا: د ج ح ه ع",
        "فۆرمی سەرەتا: دـ جـ حـ هـ عـ",
        "فۆرمی ناوەڕاست: ـدـ ـجـ ـحـ ـهـ ـعـ",
        "فۆرمی کۆتایی: ـد ـج ـح ـه ـع"
    ]
    
    for example in forms_examples:
        example_label = handler.create_kurdish_label(
            root,
            example,
            wraplength=450,
            justify='right'
        )
        example_label.pack(pady=2)
    
    # Complete words examples
    # نموونەی وشە تەواو
    words_label = handler.create_kurdish_label(
        root,
        "نموونەی وشە تەواو:",
        font=("Arial", 12, "bold"),
        wraplength=450,
        justify='right'
    )
    words_label.pack(pady=(15, 5))
    
    words_examples = [
        "پێک = پـ + ـێـ + ـک",
        "سـلام = سـ + ـلـ + ـا + م",
        "دـانـشـکـدە = دـ + ـا + نـ + ـشـ + ـکـ + ـدـ + ـە"
    ]
    
    for word_example in words_examples:
        word_label = handler.create_kurdish_label(
            root,
            word_example,
            wraplength=450,
            justify='right'
        )
        word_label.pack(pady=2)
    
    # Entry widget for Kurdish text
    # ویجتی ئینتری بۆ نامەی کوردی
    entry_label = handler.create_kurdish_label(root, "دانەیەک بنوسە:")
    entry_label.pack(pady=(20, 5))
    
    kurdish_entry = handler.create_kurdish_entry(root, width=40)
    kurdish_entry.pack(pady=5)
    kurdish_entry.insert(0, "نموونە: پێک")
    
    # Run the application
    # کارپێکردنی بەرنامەکە
    root.mainloop()

if __name__ == "__main__":
    main()