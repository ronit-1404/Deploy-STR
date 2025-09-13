# context.py

# Expanded keywords for more accurate classification
CONTEXT_RULES = {
    "programming": {
        "function", "class", "import", "def", "{", "console", "return",
        "useState", "int", "main", "print", "const", "let", "var", "code", "debug"
    },
    "video_lecture": {
        "slide", "lecture", "topic", "chapter", "duration", "ppt", "video",
        "timestamp", "subscribe", "channel", "lesson", "watch"
    },
    "article": {
        "introduction", "conclusion", "abstract", "keywords", "references",
        "journal", "author", "doi", "publication", "study", "methodology"
    },
    "document": {
        "page", "section", "chapter", "appendix", "index", "figure", "table",
        "contents", "heading", "paragraph", "notes"
    },
    "browsing": {
        "search", "login", "subscribe", "youtube", "results", "signup",
        "homepage", "watch", "history", "tab", "url", "website"
    }
}

def detect_context(text):
    text_lower = text.lower()
    scores = {context: 0 for context in CONTEXT_RULES}

    for context, keywords in CONTEXT_RULES.items():
        for keyword in keywords:
            if keyword in text_lower:
                scores[context] += 1

    best_context = max(scores, key=scores.get)
    return best_context if scores[best_context] > 0 else "unknown"
