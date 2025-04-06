"""
Text Processing Module.

Provides text tokenization, normalization, and preprocessing functionality.
"""

import re
import string
import unicodedata
from typing import List, Set, Tuple, Optional

import nltk
try:
    nltk.data.find('corpora/stopwords')
    STOPWORDS = set(nltk.corpus.stopwords.words('english'))
except LookupError:
    print("NLTK stopwords not found. Using built-in stopwords list.")
    STOPWORDS = {'a', 'an', 'the', 'in', 'on', 'at', 'of', 'and', 'or', 'to', 'for', 'with', 'by', 'about', 'as', 'into', 'like', 'through', 'after', 'over', 'between', 'out', 'in', 'on', 'off'}

try:
    from nltk.stem import PorterStemmer
    STEMMER = PorterStemmer()
except ImportError:
    STEMMER = None
    print("NLTK Porter Stemmer not available. Stemming will be skipped.")


def preprocess_text(text: str) -> str:
    """Preprocess text by normalizing, removing special characters, and converting to lowercase.
    
    Args:
        text: Input text
        
    Returns:
        Preprocessed text
    """
    if text is None:
        return ""
        
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    
    # Strip whitespace
    text = text.strip()
    
    # Stem if available
    if STEMMER:
        text = STEMMER.stem(text)
        
    return text


class Tokenizer:
    """Text tokenizer with support for document ID tracking."""
    
    def __init__(self, text: str, doc_id: str):
        """Initialize tokenizer.
        
        Args:
            text: Text to tokenize
            doc_id: Document ID associated with the text
        """
        self.text = text
        self.doc_id = doc_id
        self.used_stopwords = STOPWORDS
        
    def tokenize(self) -> List[Tuple[str, str]]:
        """Tokenize text and return token-document pairs.
        
        Returns:
            List of (token, doc_id) tuples
        """
        if not self.text:
            return []
            
        # Normalize text
        text = self.text.lower()
        
        # Remove punctuation and split by whitespace
        tokens = re.sub(r'[^\w\s]', ' ', text).split()
        
        # Generate token-doc pairs, apply processing
        token_doc_pairs = []
        for token in tokens:
            # Skip stopwords and numbers
            if token in self.used_stopwords or token.isdigit():
                continue
                
            # Apply stemming if available
            if STEMMER:
                token = STEMMER.stem(token)
                
            token_doc_pairs.append((token, self.doc_id))
            
        return token_doc_pairs 