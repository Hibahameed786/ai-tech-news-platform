from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk
import re  # Added for HTML stripping

# Download NLTK data if missing
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

summarizer = LsaSummarizer()

def summarize(text):
    if not text or len(text.split()) < 8:
        return text  # Return as-is if too short

    try:
        # Strip HTML tags from text
        clean_text = re.sub(r'<[^>]+>', '', text)
        parser = PlaintextParser.from_string(clean_text, Tokenizer("english"))
        summary = summarizer(parser.document, sentences_count=2)  # Summarize to 2 sentences for more detail
        summary_text = " ".join(str(sentence) for sentence in summary)
        return summary_text
    except Exception as e:
        # Fallback: Truncate to first 100 words if summarization fails, and strip HTML
        clean_text = re.sub(r'<[^>]+>', '', text)
        words = clean_text.split()[:100]
        return " ".join(words) + "..." if len(words) == 100 else clean_text