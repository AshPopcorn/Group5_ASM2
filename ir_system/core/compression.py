"""
Dictionary Compression Module.

Provides various dictionary compression techniques for inverted indices.
"""

import os
from typing import List, Dict, Any, Optional, Tuple
import json


class DictionaryAsAStringCompressor:
    """Dictionary as a string compression technique.
    
    Concatenates all terms into a single string and stores term positions.
    """
    
    def __init__(self):
        """Initialize the dictionary as a string compressor."""
        self.dictionary_string = ""
        self.term_offsets = {}
        
    def build(self, terms: List[str]) -> None:
        """Build the compressed dictionary.
        
        Args:
            terms: List of terms to compress
        """
        # Sort terms to ensure deterministic compression
        sorted_terms = sorted(terms)
        
        # Build the dictionary string and term offsets
        offset = 0
        self.dictionary_string = ""
        self.term_offsets = {}
        
        for term in sorted_terms:
            self.term_offsets[term] = offset
            self.dictionary_string += term
            offset += len(term)
            
    def lookup(self, term: str) -> Optional[str]:
        """Look up a term in the compressed dictionary.
        
        Args:
            term: Term to look up
            
        Returns:
            Term if found, None otherwise
        """
        if term in self.term_offsets:
            offset = self.term_offsets[term]
            return self.dictionary_string[offset:offset+len(term)]
        return None
        
    def save_to_file(self, filename: str) -> None:
        """Save the compressed dictionary to a file.
        
        Args:
            filename: Path to save the dictionary
        """
        compression_data = {
            'dictionary_string': self.dictionary_string,
            'term_offsets': self.term_offsets
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(compression_data, f)
            
    def load_from_file(self, filename: str) -> None:
        """Load a compressed dictionary from a file.
        
        Args:
            filename: Path to the dictionary file
        """
        with open(filename, 'r', encoding='utf-8') as f:
            compression_data = json.load(f)
            
        self.dictionary_string = compression_data['dictionary_string']
        self.term_offsets = compression_data['term_offsets']


class BlockingCompressor:
    """Front coding/blocking compression technique.
    
    Groups terms into blocks and compresses by storing common prefixes once per block.
    """
    
    def __init__(self, block_size: int = 8):
        """Initialize the blocking compressor.
        
        Args:
            block_size: Number of terms per block
        """
        self.block_size = block_size
        self.compressed_blocks = []
        self.term_to_block = {}
        
    def compress(self, terms: List[str]) -> None:
        """Compress a list of terms.
        
        Args:
            terms: List of terms to compress
        """
        # Sort terms
        sorted_terms = sorted(terms)
        
        # Process terms in blocks
        for i in range(0, len(sorted_terms), self.block_size):
            block_terms = sorted_terms[i:i+self.block_size]
            
            # Find common prefix for the block
            if not block_terms:
                continue
                
            # First term in the block is stored in full
            compressed_block = [block_terms[0]]
            
            # For each subsequent term, store only the suffix after common prefix
            for j in range(1, len(block_terms)):
                prev_term = block_terms[j-1]
                curr_term = block_terms[j]
                
                # Calculate common prefix length
                prefix_len = 0
                for k in range(min(len(prev_term), len(curr_term))):
                    if prev_term[k] == curr_term[k]:
                        prefix_len += 1
                    else:
                        break
                        
                # Store (prefix_length, suffix)
                compressed_block.append((prefix_len, curr_term[prefix_len:]))
                
            # Add compressed block to the list
            self.compressed_blocks.append(compressed_block)
            
            # Map each term to its block for quick lookup
            for j, term in enumerate(block_terms):
                self.term_to_block[term] = (len(self.compressed_blocks) - 1, j)
                
    def decompress(self, block_idx: int, term_idx: int) -> str:
        """Decompress a term from its block and position.
        
        Args:
            block_idx: Block index
            term_idx: Term index within the block
            
        Returns:
            Decompressed term
        """
        if block_idx >= len(self.compressed_blocks) or term_idx >= len(self.compressed_blocks[block_idx]):
            return None
            
        block = self.compressed_blocks[block_idx]
        
        if term_idx == 0:
            # First term in block is stored in full
            return block[0]
        else:
            # Reconstruct term using prefix from previous term
            prefix_len, suffix = block[term_idx]
            prev_term = self.decompress(block_idx, term_idx - 1)
            return prev_term[:prefix_len] + suffix
            
    def lookup(self, term: str) -> str:
        """Look up a term in the compressed dictionary.
        
        Args:
            term: Term to look up
            
        Returns:
            Term if found, None otherwise
        """
        if term in self.term_to_block:
            block_idx, term_idx = self.term_to_block[term]
            return self.decompress(block_idx, term_idx)
        return None
        
    def save_to_file(self, filename: str) -> None:
        """Save the compressed dictionary to a file.
        
        Args:
            filename: Path to save the dictionary
        """
        compression_data = {
            'block_size': self.block_size,
            'compressed_blocks': self.compressed_blocks,
            'term_to_block': self.term_to_block
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(compression_data, f)
            
    def load_from_file(self, filename: str) -> None:
        """Load a compressed dictionary from a file.
        
        Args:
            filename: Path to the dictionary file
        """
        with open(filename, 'r', encoding='utf-8') as f:
            compression_data = json.load(f)
            
        self.block_size = compression_data['block_size']
        self.compressed_blocks = compression_data['compressed_blocks']
        self.term_to_block = compression_data['term_to_block']


class FrontCodingCompressor:
    """Front coding compression technique.
    
    Compresses by storing the difference from previous term.
    """
    
    def __init__(self):
        """Initialize the front coding compressor."""
        self.compressed_terms = []
        self.term_to_index = {}
        
    def compress(self, terms: List[str]) -> None:
        """Compress a list of terms.
        
        Args:
            terms: List of terms to compress
        """
        # Sort terms
        sorted_terms = sorted(terms)
        
        # First term is stored in full
        if not sorted_terms:
            return
            
        self.compressed_terms = [(0, sorted_terms[0])]
        self.term_to_index = {sorted_terms[0]: 0}
        
        for i in range(1, len(sorted_terms)):
            prev_term = sorted_terms[i-1]
            curr_term = sorted_terms[i]
            
            # Calculate common prefix length
            prefix_len = 0
            for j in range(min(len(prev_term), len(curr_term))):
                if prev_term[j] == curr_term[j]:
                    prefix_len += 1
                else:
                    break
                    
            # Store (prefix_length, suffix)
            self.compressed_terms.append((prefix_len, curr_term[prefix_len:]))
            self.term_to_index[curr_term] = i
            
    def decompress(self, index: int) -> str:
        """Decompress a term from its index.
        
        Args:
            index: Term index
            
        Returns:
            Decompressed term
        """
        if index >= len(self.compressed_terms):
            return None
            
        prefix_len, suffix = self.compressed_terms[index]
        
        if index == 0 or prefix_len == 0:
            # First term or term with no common prefix
            return suffix
        else:
            # Reconstruct term using prefix from previous term
            prev_term = self.decompress(index - 1)
            return prev_term[:prefix_len] + suffix
            
    def lookup(self, term: str) -> str:
        """Look up a term in the compressed dictionary.
        
        Args:
            term: Term to look up
            
        Returns:
            Term if found, None otherwise
        """
        if term in self.term_to_index:
            index = self.term_to_index[term]
            return self.decompress(index)
        return None
        
    def save_to_file(self, filename: str) -> None:
        """Save the compressed dictionary to a file.
        
        Args:
            filename: Path to save the dictionary
        """
        compression_data = {
            'compressed_terms': self.compressed_terms,
            'term_to_index': self.term_to_index
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(compression_data, f)
            
    def load_from_file(self, filename: str) -> None:
        """Load a compressed dictionary from a file.
        
        Args:
            filename: Path to the dictionary file
        """
        with open(filename, 'r', encoding='utf-8') as f:
            compression_data = json.load(f)
            
        self.compressed_terms = compression_data['compressed_terms']
        self.term_to_index = compression_data['term_to_index'] 


