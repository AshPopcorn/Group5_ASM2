"""
Command line interface module.

Provides command line argument parsing and processing functionality.
"""

import argparse
import sys
import traceback
import os
import time
from typing import Dict, Any, List, Optional, Set

from ir_system.core.file_utils import FileListCollector, FileReader
from ir_system.core.text_processing import Tokenizer
from ir_system.core.indexing import SPIMIIndexer, load_inverted_index
from ir_system.core.compression import (
    DictionaryAsAStringCompressor, 
    BlockingCompressor, 
    FrontCodingCompressor
)
from ir_system.core.query_processing import process_query
from ir_system.utils.performance import PerformanceTracker, get_memory_usage, print_memory_stats

# Define data directory constants
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')
CORPUS_DIR = os.path.join(DATA_DIR, 'corpus')
INDICES_DIR = os.path.join(DATA_DIR, 'indices')

def setup_argument_parser() -> argparse.ArgumentParser:
    """Set up command line argument parser.

    Returns:
        argparse.ArgumentParser: Command line argument parser
    """
    parser = argparse.ArgumentParser(description='IR System - Information Retrieval System')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Index subcommand
    index_parser = subparsers.add_parser('index', help='Create an index')
    index_parser.add_argument('input_dir', help='Directory path to index')
    index_parser.add_argument('block_size', help='Maximum number of entries to process in memory')
    index_parser.add_argument('output_file', help='Index output file')
    index_parser.add_argument('--extensions', help='List of file extensions to process, comma separated, e.g. .txt,.html')
    index_parser.add_argument('--compress', choices=['block', 'front', 'string'], 
                             help='Compression technique to use')
    index_parser.add_argument('--skips', type=int, default=0,
                             help='Skip step size for creating skip lists, 0 means no skip lists')
    
    # Search subcommand
    search_parser = subparsers.add_parser('search', help='Search the index')
    search_parser.add_argument('query', help='Query to search for')
    search_parser.add_argument('index_file', help='Path to index file')
    search_parser.add_argument('--skips', type=int, default=0,
                              help='Skip step size to use, 0 means no skip lists')
    
    return parser

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments.

    Args:
        args: Command line argument list, defaults to None which uses sys.argv

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = setup_argument_parser()
    parsed_args = parser.parse_args(args)
    
    if not parsed_args.command:
        parser.print_help()
        sys.exit(1)
        
    return parsed_args

def resolve_path(path: str, default_dir: str = None) -> str:
    """Resolve path, supporting relative and absolute paths.

    Args:
        path: Input path
        default_dir: Default directory, if provided, relative paths will be relative to this directory

    Returns:
        str: Resolved path
    """
    # Check if path already includes data directory
    if path.startswith('data/'):
        # Convert to absolute path relative to working directory
        return os.path.abspath(path)
    elif os.path.isabs(path):
        return path
    elif default_dir and not path.startswith(default_dir):
        return os.path.join(default_dir, path)
    else:
        return os.path.abspath(path)

def index_command(args: argparse.Namespace) -> int:
    """Execute index command.

    Args:
        args: Command line arguments

    Returns:
        Exit code (0 means success)
    """
    try:
        # Resolve paths
        input_path = resolve_path(args.input_dir, CORPUS_DIR)
        output_file = resolve_path(args.output_file, INDICES_DIR)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        block_size = int(args.block_size)
        
        print(f"Starting to build index for {input_path}, block size: {block_size}, output: {output_file}")
        
        # Initialize performance tracker
        perf_tracker = PerformanceTracker()
        perf_tracker.take_memory_snapshot("Initial Memory")
        
        # Initialize file collector
        collector = FileListCollector(
            file_extensions=args.extensions.split(',') if args.extensions else None
        )
        
        # Collect files and assign document IDs
        perf_tracker.start_timer("File Collection")
        file_list = collector.collect_files(input_path)
        doc_id_mapping = collector.assign_doc_ids(file_list)
        collect_time = perf_tracker.stop_timer("File Collection")
        
        print(f"Collected {len(file_list)} files (took {collect_time:.4f} seconds)")
        
        # Initialize SPIMI indexer
        spimi_indexer = SPIMIIndexer(block_size, output_file)
        
        perf_tracker.take_memory_snapshot("Pre-indexing Memory")
        print_memory_stats("Pre-indexing")
        
        # Start indexing process
        perf_tracker.start_timer("Indexing")
        
        for file_path, doc_id in doc_id_mapping.items():
            print(f"Processing document {doc_id}/{len(doc_id_mapping)}: {os.path.basename(file_path)}")
            file_content = FileReader.read_file(file_path)
            tokenizer = Tokenizer(file_content, doc_id)
            
            for token, doc in tokenizer.tokenize():
                spimi_indexer.add_token(token, file_path)  # Use file path as docID
        
        index_duration = perf_tracker.stop_timer("Indexing")
        print(f"Indexing time: {index_duration:.4f} seconds")
        
        # Merge all blocks
        if spimi_indexer.token_count > 0:
            print("Flushing last memory block...")
            spimi_indexer.flush_block()
            
        perf_tracker.start_timer("Merging")
        merge_duration = spimi_indexer.merge_blocks()
        perf_tracker.stop_timer("Merging")
        
        # Apply dictionary compression (if specified)
        if args.compress:
            perf_tracker.start_timer("Compression")
            print(f"Applying {args.compress} compression...")
            
            # Load all terms
            with open(output_file, 'r', encoding='utf-8') as f:
                terms = set()
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) >= 1:
                        terms.add(parts[0])
            
            if args.compress == 'block':
                compressor = BlockingCompressor()
                compressor.compress(list(terms))
                compressor.save_to_file(f"{output_file}.block_dict")
                print(f"Block compression dictionary saved to {output_file}.block_dict")
            
            elif args.compress == 'front':
                compressor = FrontCodingCompressor()
                compressor.compress(list(terms))
                compressor.save_to_file(f"{output_file}.front_dict")
                print(f"Front coding compression dictionary saved to {output_file}.front_dict")
            
            elif args.compress == 'string':
                compressor = DictionaryAsAStringCompressor()
                compressor.build(list(terms))
                compressor.save_to_file(f"{output_file}.string_dict")
                print(f"String compression dictionary saved to {output_file}.string_dict")
            
            compress_duration = perf_tracker.stop_timer("Compression")
            print(f"Compression time: {compress_duration:.4f} seconds")
        
        # Report memory usage and statistics
        perf_tracker.take_memory_snapshot("Post-indexing Memory")
        print_memory_stats("Post-indexing")
        print(f"Total blocks flushed: {spimi_indexer.block_counter}")
        
        if spimi_indexer.flush_times:
            avg_flush = sum(spimi_indexer.flush_times) / len(spimi_indexer.flush_times)
            print(f"Average flush time: {avg_flush:.4f} seconds")
        
        total_time = index_duration + merge_duration
        print(f"Total time (indexing + merging): {total_time:.4f} seconds")
        print(f"Index file saved to: {output_file}")
        
        perf_tracker.print_report()
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unknown error occurred: {e}")
        traceback.print_exc()
        return 1


def search_command(args: argparse.Namespace) -> int:
    """Execute search command.

    Args:
        args: Command line arguments

    Returns:
        Exit code (0 means success)
    """
    try:
        # Parse index file path
        index_file = resolve_path(args.index_file, INDICES_DIR)
        query_string = args.query
        
        print(f"Executing query: {query_string}")
        
        # Load inverted index
        inverted_index = load_inverted_index(index_file, args.skips)
        
        # Get set of all document IDs
        all_docs = set()
        for doc_set in inverted_index.values():
            if hasattr(doc_set, 'posting_list'):
                all_docs.update(doc_set.posting_list)
            else:
                all_docs.update(doc_set)
                
        # Process query
        start_time = time.time()
        result_docs = process_query(query_string, inverted_index)
        query_time = time.time() - start_time
        
        # Print results
        print(f"Found {len(result_docs)} matching documents (took {query_time:.6f} seconds)")
        
        for i, doc in enumerate(sorted(result_docs), 1):
            print(f"{i}. {doc}")
            
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unknown error occurred: {e}")
        traceback.print_exc()
        return 1 