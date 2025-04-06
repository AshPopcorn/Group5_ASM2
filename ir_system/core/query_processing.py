"""
Query Processing Module.

Contains functionality for parsing and evaluating boolean queries.
"""

import re
from typing import Dict, Set, List, Any, Optional, Union
import nltk
from ir_system.core.text_processing import preprocess_text


class BooleanQueryParser:
    """A parser for boolean queries with support for AND, OR, NOT operations and grouping with parentheses."""
    
    def __init__(self):
        """Initialize the boolean query parser."""
        # Define operators and special characters
        self.operators = {
            'AND': 2,     # Precedence 2 (higher than OR)
            'OR': 1,      # Precedence 1 (lower than AND)
            'NOT': 3      # Precedence 3 (highest)
        }
        
        # Initialize stopwords list if nltk data is available
        try:
            nltk.data.find('corpora/stopwords')
            self.stopwords = set(nltk.corpus.stopwords.words('english'))
        except LookupError:
            print("NLTK stopwords not found. Using a minimal built-in stopwords list.")
            self.stopwords = {'a', 'an', 'the', 'in', 'on', 'at', 'of', 'and', 'or', 'to', 'for', 'with', 'by'}
        
    def tokenize_query(self, query: str) -> List[str]:
        """Tokenize a query string into terms and operators.
        
        Args:
            query: The query string to tokenize
            
        Returns:
            List of tokens (terms and operators)
        """
        # Replace operators with spaces around them
        query = query.replace("(", " ( ")
        query = query.replace(")", " ) ")
        
        # Convert to uppercase for operator recognition
        tokens = query.split()
        result = []
        
        for token in tokens:
            if token.upper() in ['AND', 'OR', 'NOT', '(', ')']:
                result.append(token.upper())
            else:
                # Preprocess term
                preprocessed = preprocess_text(token)
                if preprocessed and preprocessed not in self.stopwords:
                    result.append(preprocessed)
        
        return result
    
    def to_postfix(self, tokens: List[str]) -> List[str]:
        """Convert infix tokens to postfix notation.
        
        Args:
            tokens: Tokenized query in infix notation
            
        Returns:
            Query in postfix notation
        """
        output = []
        stack = []
        
        for token in tokens:
            if token.upper() in self.operators:
                while (stack and stack[-1] != '(' and 
                       ((token.upper() != 'NOT' and self.operators.get(stack[-1], 0) >= self.operators.get(token.upper(), 0)) or
                        (token.upper() == 'NOT' and self.operators.get(stack[-1], 0) > self.operators.get(token.upper(), 0)))):
                    output.append(stack.pop())
                stack.append(token.upper())
            elif token == '(':
                stack.append(token)
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if stack and stack[-1] == '(':
                    stack.pop()
            else:
                output.append(token)
                
        while stack:
            output.append(stack.pop())
            
        return output
    
    def evaluate_postfix(self, postfix: List[str], index: Dict[str, Any]) -> Set[str]:
        """Evaluate a postfix query using the provided index.
        
        Args:
            postfix: Query in postfix notation
            index: The inverted index
            
        Returns:
            Set of document IDs matching the query
        """
        stack = []
        all_docs = set()
        
        # Collect all document IDs from the index
        for term, docs in index.items():
            if hasattr(docs, 'posting_list'):
                all_docs.update(docs.posting_list)
            else:
                all_docs.update(docs)
        
        for token in postfix:
            if token == 'AND':
                if len(stack) >= 2:
                    right = stack.pop()
                    left = stack.pop()
                    
                    # Handle different types of posting lists
                    if hasattr(left, 'intersection') and callable(getattr(left, 'intersection')):
                        result = left.intersection(right)
                    elif hasattr(right, 'intersection') and callable(getattr(right, 'intersection')):
                        result = right.intersection(left)
                    else:
                        result = set(left).intersection(set(right))
                        
                    stack.append(result)
            elif token == 'OR':
                if len(stack) >= 2:
                    right = stack.pop()
                    left = stack.pop()
                    
                    # Handle different types of posting lists
                    if hasattr(left, 'union') and callable(getattr(left, 'union')):
                        result = left.union(right)
                    elif hasattr(right, 'union') and callable(getattr(right, 'union')):
                        result = right.union(left)
                    else:
                        result = set(left).union(set(right))
                        
                    stack.append(result)
            elif token == 'NOT':
                if stack:
                    operand = stack.pop()
                    
                    # Handle different types of posting lists
                    if hasattr(operand, 'difference') and callable(getattr(operand, 'difference')):
                        result = all_docs.difference(operand)
                    else:
                        result = all_docs - set(operand)
                        
                    stack.append(result)
            else:
                # Term lookup
                if token in index:
                    stack.append(index[token])
                else:
                    # Term not in index, push empty set
                    stack.append(set())
        
        if stack:
            result = stack[0]
            # Convert any special posting list to set
            if hasattr(result, 'posting_list'):
                return set(result.posting_list)
            elif not isinstance(result, set):
                return set(result)
            return result
        return set()


def process_query(query: str, index: Dict[str, Any]) -> Set[str]:
    """Process a boolean query and return matching documents.
    
    Args:
        query: Boolean query string
        index: Inverted index dictionary
        
    Returns:
        Set of matching document IDs
    """
    parser = BooleanQueryParser()
    
    # Print information about the query processing
    print(f"Processing query: {query}")
    print(f"Using built-in stopwords list: {', '.join(sorted(list(parser.stopwords)[:10]))}...")
    
    # Tokenize and convert to postfix
    tokens = parser.tokenize_query(query)
    postfix = parser.to_postfix(tokens)
    
    # Evaluate query
    return parser.evaluate_postfix(postfix, index) 