# NTU Information Retrieval - Assignment 2

## Directory Structure

The project has been refactored into a more modular package structure:

- `ir_system/` - Main program package
  - `cli/` - Command-line interface
    - `commands.py` - Command-line command implementations
  - `core/` - Core functionality
    - `file_utils.py` - File operations
    - `text_processing.py` - Text processing and tokenization
    - `indexing.py` - SPIMI indexing and inverted index operations
    - `compression.py` - Dictionary compression techniques
    - `query_processing.py` - Query parsing and evaluation
  - `utils/` - Utility functions
    - `performance.py` - Performance monitoring
  - `main.py` - Main program entry
- `data/` - Data directory
  - `corpus/` - Corpus files
  - `indices/` - Index files
    - `compression_samples/` - Index samples with different compression techniques
- `run.py` - Simple run script

## Installation

1. Ensure you have Python 3.6+ installed
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

3. If you want to use NLTK stopwords (optional), download them:

```python
import nltk
nltk.download('stopwords')
```

## Usage

### Running the Program

You can use the run.py script to execute the program:

```bash
# Make sure the script is executable
chmod +x run.py

# Run the program
./run.py [arguments]
```

Or run directly with python:

```bash
python run.py [arguments]
```

### Building an Index

```bash
./run.py index <input_directory> <block_size> <output_file> [--extensions EXT1,EXT2] [--compress {block,front,string}] [--skips skip_size]
```

Examples:
```bash
# Create an index with string compression
./run.py index data/corpus/HillaryEmails 10000 data/indices/my_index.txt --compress string

# Create an index without compression
./run.py index data/corpus/HillaryEmails 1000 data/indices/simple_index.txt

# Create an index with block compression and skip lists
./run.py index data/corpus/HillaryEmails 5000 data/indices/block_index.txt --compress block --skips 4
```

### Searching

```bash
./run.py search "<query>" <index_file> [--skips skip_size]
```

Examples:
```bash
# Simple search
./run.py search "information AND retrieval" data/indices/my_index.txt

# Search with skip lists
./run.py search "information AND retrieval" data/indices/my_index.txt --skips 3
```

## Advanced Boolean Queries

The system supports the following Boolean operators:
- AND (default if no operator is specified)
- OR
- NOT

Complex query examples:
```bash
./run.py search "(information OR data) AND (retrieval NOT ranking)" data/indices/my_index.txt
```

## Data Directory Structure

The project uses the following directory structure to organize data files:

- `data/corpus/` - Storage for corpus files (e.g., Hillary Emails dataset)
- `data/indices/` - Storage for index files
  - `current/` - Currently used working indices
  - `examples/` - Example indices with different compression techniques

Index file naming conventions:
- Basic index files: `*.txt`
- Block compression dictionaries: `*.txt.block_dict`
- Front coding dictionaries: `*.txt.front_dict`
- String compression dictionaries: `*.txt.string_dict`

## Compression Methods

The system implements three dictionary compression methods:

1. **Block Compression** - Divides the dictionary into fixed-size blocks, with only the first term in each block stored in its complete form.
2. **Front Coding Compression** - Utilizes common prefixes between adjacent terms. The first term in each block is stored completely, while subsequent terms only store the parts that differ.
3. **Dictionary as String Compression** - Stores the entire dictionary as a long string, with each term represented by its offset and length.

## Performance

Our optimization efforts have led to significant improvements in storage efficiency:

- Storage space reduction: ~63% (from 1.24GB to 457MB)
- Query performance remains efficient even with compression (sub-millisecond response times)
- Front coding provides the best compression ratio, while dictionary-as-string offers the simplest implementation

## Future Work

1. Resolve compatibility issues with front coding and blocking compression indices
2. Implement incremental index updates
3. Further optimize skip list implementation for larger datasets
4. Extend query functionality (phrase queries, approximate queries, ranking)
5. Develop a graphical user interface for non-technical users 