#!/usr/bin/env python
# coding: utf-8

"""
Word Frequency Analyzer Module
محلل تكرار الكلمات
"""


def word_frequency(text):
    """
    Analyze word frequency in a given text.
    
    Args:
        text (str): The input text to analyze
        
    Returns:
        list: A list of tuples (word, count) sorted by frequency in descending order
        
    Example:
        >>> text = "Hello world hello"
        >>> word_frequency(text)
        [('hello', 2), ('world', 1)]
    """
    words = text.split()
    word_count = {}

    for word in words:
        word = word.lower()
        word = word.strip('.,?!:"')
        
        if word in word_count:
            word_count[word] += 1
        else:
            word_count[word] = 1
    
    sorted_word_count = sorted(word_count.items(), key=lambda item: item[1], reverse=True)
    return sorted_word_count


def analyze_text(text):
    """
    Analyze text and return formatted results.
    
    Args:
        text (str): The input text to analyze
        
    Returns:
        str: Formatted string with word frequency analysis
    """
    result = word_frequency(text)
    
    output = "\nالكلمة\t\tعدد التكرار\n"
    output += "--------------------\n"
    
    for word, count in result:
        output += f"{word}\t\t{count}\n"
    
    return output


def main():
    """Main function for command-line usage."""
    input_text = input("الرجاء إدخال النص هنا: ")
    result = word_frequency(input_text)

    print("\nالكلمة\t\tعدد التكرار")
    print("--------------------")

    for word, count in result:
        print(f"{word}\t\t{count}")


if __name__ == "__main__":
    main()
