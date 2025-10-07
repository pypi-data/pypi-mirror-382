# Alkuhlani Student - محلل تكرار الكلمات

حزمة Python بسيطة لتحليل تكرار الكلمات في النصوص.

A simple Python package to analyze word frequency in text.

## التثبيت - Installation

```bash
pip install alkuhlani-student
```

## الاستخدام - Usage

### استخدام الحزمة في كود Python

```python
from alkuhlani_student import word_frequency, analyze_text

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
alkuhlani-student
```

أو

```bash
python -m alkuhlani_student
```

## الميزات - Features

- تحليل تكرار الكلمات في النصوص
- دعم اللغة العربية والإنجليزية
- إزالة علامات الترقيم تلقائياً
- ترتيب النتائج حسب التكرار
- واجهة سطر أوامر سهلة الاستخدام
- قابلة للاستخدام كمكتبة في مشاريعك

## أمثلة - Examples

### مثال 1: تحليل نص عربي

```python
from alkuhlani_student import word_frequency

text = "Python هي لغة برمجة قوية. Python سهلة التعلم."
result = word_frequency(text)
print(result)
# Output: [('python', 2), ('هي', 1), ('لغة', 1), ('برمجة', 1), ('قوية', 1), ('سهلة', 1), ('التعلم', 1)]
```

### مثال 2: تحليل نص إنجليزي

```python
from alkuhlani_student import word_frequency

text = "Hello world! Hello Python. Python is great."
result = word_frequency(text)
print(result)
# Output: [('hello', 2), ('python', 2), ('world', 1), ('is', 1), ('great', 1)]
```

### مثال 3: استخدام analyze_text

```python
from alkuhlani_student import analyze_text

text = "مرحبا مرحبا بك"
print(analyze_text(text))
```

## المتطلبات - Requirements

- Python 3.7 أو أحدث

## الكاتب - Author

**Alkuhlani Student (CYS 2)**

---

**صُنع بـ ❤️ من قبل Alkuhlani Student (CYS 2)**
