"""
SPIMI Indexer Module.

This module implements the Single-Pass In-Memory Indexing algorithm for creating inverted indices.
"""

import os
import json
import time
import heapq
from typing import Dict, List, Set, Tuple, Any, Optional
from collections import defaultdict
import pickle

from ir_system.core.data_structures import PostingList


class SPIMIIndexer:
    """SPIMI Indexer implementation for creating inverted indices."""
    
    def __init__(self, block_size: int, output_file: str):
        """Initialize SPIMI indexer.

        Args:
            block_size: Maximum number of tokens to process in memory before flushing to disk
            output_file: Path to the output index file
        """
        self.block_size = block_size
        self.output_file = output_file
        self.temp_dir = os.path.join(os.path.dirname(output_file), 'temp_blocks')
        
        # Ensure the temporary directory exists
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Initialize in-memory dictionary
        self.dictionary = defaultdict(set)
        self.token_count = 0
        self.block_counter = 0
        self.flush_times = []
        
    def add_token(self, token: str, doc_id: str) -> None:
        """Add token to the in-memory dictionary.

        Args:
            token: Token to add
            doc_id: Document ID containing the token
        """
        # Add docID to the postings list for this token
        self.dictionary[token].add(doc_id)
        self.token_count += 1
        
        # If we've reached the block size, flush to disk
        if self.token_count >= self.block_size:
            self.flush_block()
            
    def flush_block(self) -> None:
        """Flush current in-memory block to disk."""
        if not self.dictionary:
            return
            
        start_time = time.time()
        
        # Sort dictionary terms
        sorted_terms = sorted(self.dictionary.keys())
        
        # Create block file path
        block_path = os.path.join(self.temp_dir, f'block_{self.block_counter}.txt')
        
        # Write sorted dictionary to disk
        with open(block_path, 'w', encoding='utf-8') as f:
            for term in sorted_terms:
                postings = sorted(self.dictionary[term])
                postings_str = ','.join(postings)
                f.write(f"{term}\t{postings_str}\n")
        
        # Clear the in-memory dictionary and update counters
        self.dictionary.clear()
        self.token_count = 0
        self.block_counter += 1
        
        elapsed = time.time() - start_time
        self.flush_times.append(elapsed)
        
    def merge_blocks(self) -> float:
        """Merge all blocks into a final inverted index.

        Returns:
            float: Time taken to merge blocks in seconds
        """
        start_time = time.time()
        
        # No blocks to merge
        if self.block_counter == 0:
            print("No blocks to merge.")
            return 0
            
        # Get all block files
        block_files = []
        for i in range(self.block_counter):
            block_path = os.path.join(self.temp_dir, f'block_{i}.txt')
            if os.path.exists(block_path):
                block_files.append(block_path)
        
        if not block_files:
            print("No block files found.")
            return 0
            
        print(f"Merging {len(block_files)} blocks...")
        
        # Open all block files
        file_handles = []
        for block_file in block_files:
            file_handles.append(open(block_file, 'r', encoding='utf-8'))
            
        # Create a min-heap for k-way merge
        heap = []
        
        # Initialize heap with first line from each block
        for i, f in enumerate(file_handles):
            line = f.readline().strip()
            if line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    term, postings = parts[0], parts[1]
                    # Add to heap: (term, postings, block_index)
                    heapq.heappush(heap, (term, postings, i))
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        # Open output file
        with open(self.output_file, 'w', encoding='utf-8') as out_file:
            # Merge blocks
            current_term = None
            current_postings = set()
            
            while heap:
                term, postings, block_idx = heapq.heappop(heap)
                
                # If this is a new term, write the previous term's postings
                if current_term is not None and current_term != term:
                    # Write current term and postings
                    sorted_postings = sorted(current_postings)
                    postings_str = ','.join(sorted_postings)
                    out_file.write(f"{current_term}\t{postings_str}\n")
                    
                    # Reset for new term
                    current_postings = set()
                
                # Update current term
                current_term = term
                
                # Add postings to current term
                for doc_id in postings.split(','):
                    current_postings.add(doc_id)
                
                # Get next line from the same block
                line = file_handles[block_idx].readline().strip()
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        next_term, next_postings = parts[0], parts[1]
                        heapq.heappush(heap, (next_term, next_postings, block_idx))
            
            # Write the last term
            if current_term is not None:
                sorted_postings = sorted(current_postings)
                postings_str = ','.join(sorted_postings)
                out_file.write(f"{current_term}\t{postings_str}\n")
        
        # Close all file handles
        for f in file_handles:
            f.close()
            
        # Clean up temporary files
        for block_file in block_files:
            try:
                os.remove(block_file)
            except:
                print(f"Warning: Could not remove temporary file {block_file}")
                
        # Try to remove the temporary directory
        try:
            os.rmdir(self.temp_dir)
        except:
            print(f"Warning: Could not remove temporary directory {self.temp_dir}")
            
        elapsed_time = time.time() - start_time
        print(f"Merged {len(block_files)} blocks in {elapsed_time:.4f} seconds")
        
        # Calculate and print index statistics
        term_count = 0
        with open(self.output_file, 'r', encoding='utf-8') as f:
            for line in f:
                term_count += 1
                
        print(f"Final index contains {term_count} unique terms")
        
        return elapsed_time


def load_inverted_index(index_file: str, skip_size: int = 0) -> Dict[str, Any]:
    """Load inverted index from file.

    Args:
        index_file: Path to the index file
        skip_size: Skip list step size (0 means no skip lists)

    Returns:
        Dictionary mapping terms to posting lists
    """
    inverted_index = {}
    
    try:
        print(f"Loading index from {index_file}...")
        
        # Check if the index has skip lists
        skip_index_file = f"{index_file}.skips"
        if skip_size > 0 and os.path.exists(skip_index_file):
            print(f"Using pre-computed skip lists with step size {skip_size}")
            with open(skip_index_file, 'rb') as f:
                return pickle.load(f)
                
        with open(index_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) < 2:
                    continue
                    
                term, postings_str = parts[0], parts[1]
                
                # Parse posting list
                posting_list = postings_str.split(',')
                
                # Construct PostingList object with skip lists if requested
                if skip_size > 0:
                    inverted_index[term] = PostingList(posting_list, skip_size)
                else:
                    inverted_index[term] = set(posting_list)
        
        print(f"Loaded index with {len(inverted_index)} terms")
        
        # Save with skip lists if they were generated
        if skip_size > 0 and not os.path.exists(skip_index_file):
            print(f"Saving index with skip lists (step size: {skip_size}) to {skip_index_file}")
            with open(skip_index_file, 'wb') as f:
                pickle.dump(inverted_index, f)
                
        return inverted_index
        
    except Exception as e:
        print(f"Error loading index: {e}")
        raise 