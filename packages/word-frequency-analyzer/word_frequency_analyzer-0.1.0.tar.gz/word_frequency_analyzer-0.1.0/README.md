# Word Frequency Analyzer - محلل تكرار الكلمات

حزمة Python بسيطة لتحليل تكرار الكلمات في النصوص.

A simple Python package to analyze word frequency in text.

## التثبيت - Installation

```bash
pip install word-frequency-analyzer
```

## الاستخدام - Usage

### استخدام الحزمة في كود Python

```python
from word_frequency_analyzer import word_frequency, analyze_text

# تحليل النص
text = "مرحبا بك في محلل تكرار الكلمات مرحبا"
result = word_frequency(text)
print(result)
# Output: [('مرحبا', 2), ('بك', 1), ('في', 1), ('محلل', 1), ('تكرار', 1), ('الكلمات', 1)]

# الحصول على نتائج منسقة
formatted_result = analyze_text(text)
print(formatted_result)
```

### استخدام الحزمة من سطر الأوامر

```bash
word-frequency
```

أو

```bash
python -m word_frequency_analyzer
```

## الميزات - Features

- تحليل تكرار الكلمات في النصوص
- دعم اللغة العربية والإنجليزية
- إزالة علامات الترقيم تلقائياً
- ترتيب النتائج حسب التكرار
- واجهة سطر أوامر سهلة الاستخدام
- قابلة للاستخدام كمكتبة في مشاريعك

## المتطلبات - Requirements

- Python 3.7 أو أحدث

## الترخيص - License

MIT License

## المساهمة - Contributing

المساهمات مرحب بها! يرجى فتح issue أو pull request.

Contributions are welcome! Please open an issue or pull request.

## الكاتب - Author

Your Name

## الدعم - Support

إذا واجهتك أي مشكلة، يرجى فتح issue على GitHub.

If you encounter any problems, please open an issue on GitHub.
