# Information Retrieval System Implementation Report

## 1. Project Overview

This project implements an information retrieval system based on the SPIMI (Single-Pass In-Memory Indexing) algorithm, supporting text indexing, inverted index compression, and Boolean query functionalities. The system employs a modular design, capable of handling large document collections and comparing indexing efficiency across different compression methods. The optimized system structure is clearer and the file organization more logical, making it easier to maintain and use.

## 2. System Architecture

The system consists of the following main modules:

1. **File Processing Module**: Responsible for file collection and reading
2. **Text Processing Module**: Implements text tokenization
3. **Indexing Module**: Implements the SPIMI indexing algorithm
4. **Dictionary Compression Module**: Implements three compression methods
5. **Query Processing Module**: Handles Boolean query expressions
6. **Main Control Module**: Integrates all components and provides a command-line interface

### Directory Structure

The system adopts an optimized directory structure that separates code and data, improving maintainability:

```
IR-Assignment2/
├── ir_system/             # Core code package
│   ├── cli/               # Command-line interface
│   ├── core/              # Core functional modules
│   └── utils/             # Utility functions
├── data/                  # Data directory
│   ├── corpus/            # Document collection
│   │   └── HillaryEmails/ # Hillary Emails dataset
│   └── indices/           # Index files
│       ├── current/       # Current working indices
│       └── examples/      # Example index files
├── run.py                 # Program entry point
└── README.md              # Project documentation
```

## 3. Core Functionality Implementation

### 3.1 SPIMI Indexing Algorithm

SPIMI is a memory-constrained single-pass inverted index construction algorithm suitable for large-scale document collection indexing.

```python
class SPIMIIndexer:
    def __init__(self, block_size: int, output_file: str):
        self.block_size = block_size      # Memory size limit
        self.output_file = output_file    # Final output file
        self.index = defaultdict(list)    # Index: {term: [doc1, doc2, ...]}
        self.token_count = 0              # Current number of stored tokens
        self.block_files = []             # Temporary block files list
        self.block_counter = 0            # Block counter
```

The core process of the SPIMI algorithm includes:

1. **Token Addition**: Adding each token from documents to the in-memory index
2. **Block Flushing**: When the in-memory index reaches the preset size limit, it's written to a temporary file
3. **Block Merging**: After all documents are processed, all temporary block files are merged into the final inverted index

### 3.2 Index Compression Methods

The system implements three dictionary compression methods:

#### 3.2.1 Blocking Compression

The dictionary is divided into fixed-size blocks, with only the first term in each block stored in its complete form. Other terms are derived through their relationship with the first term.

```python
class BlockingCompressor:
    def __init__(self, block_size=8):
        self.block_size = block_size
        self.blocks = []  # Storage format: [(prefix, [complete term list])]
```

#### 3.2.2 Front Coding Compression

This method utilizes common prefixes between adjacent terms for compression. The first term in each block is stored completely, while subsequent terms only store the parts that differ from the previous term.

```python
class FrontCodingCompressor:
    def __init__(self, block_size=8):
        self.block_size = block_size
        self.blocks = []  # Storage format: [(prefix, [(shared prefix length, suffix)])]
```

#### 3.2.3 Dictionary as a String Compression

The entire dictionary is stored as a long string, with each term represented by its offset and length in the string.

```python
class DictionaryAsAStringCompressor:
    def __init__(self):
        self.dictionary_string = ""  # String storing all terms
        self.term_offsets = {}       # {term: (start_position, length)}
```

### 3.3 Skip List Query Optimization

To improve the efficiency of intersection operations in Boolean queries, the system implements posting lists with skip pointers:

```python
class PostingListWithSkips:
    def __init__(self, posting_list=None, skip_distance=None):
        self.posting_list = sorted(posting_list) if posting_list else []
        self.skip_distance = skip_distance
        self.skip_pointers = []
        
        if self.posting_list:
            self._build_skip_pointers()
```

Skip lists theoretically accelerate the computation of intersection operations by adding skip pointers to the posting lists.

### 3.4 Boolean Query Processing

The system supports complex Boolean queries, including combinations of AND, OR, NOT operators and parentheses:

```python
def evaluate_query_tree(tree, inverted_index, all_docs):
    if tree is None:
        return set()
        
    if isinstance(tree, str):
        # Process individual query term
        processor = LinguisticProcessor()
        normalized_term = processor.normalize(tree)
        if normalized_term is not None:
            term = normalized_term
        else:
            term = tree
        return inverted_index.get(term, set())
        
    op, operands = tree
    
    if op == 'AND':
        # AND operation optimization
        results = [evaluate_query_tree(o, inverted_index, all_docs) for o in operands]
        # Sort by set size, starting with the smallest
        results.sort(key=len)
        result = results[0]
        for other_result in results[1:]:
            result = result.intersection(other_result)
            if not result:
                return set()
        return result
        
    elif op == 'OR':
        # OR operation
        return set.union(*(evaluate_query_tree(o, inverted_index, all_docs) for o in operands))
```

## 4. Optimization Measures

### 4.1 File Structure Optimization

To improve system maintainability and user experience, we implemented the following file structure optimizations:

1. **Separation of Code and Data**: Created a dedicated `data` directory to separate all data files from code
2. **Centralized Corpus Management**: Placed corpus files centrally in the `data/corpus` directory
3. **Categorized Index File Storage**:
   - `data/indices/current`: Stores currently used working index files
   - `data/indices/examples`: Stores example index files for different compression methods

### 4.2 Storage Space Optimization

By optimizing file organization, we significantly reduced redundant files, saving storage space:

| Before Optimization | After Optimization | Reduction Percentage |
|--------------------|-------------------|---------------------|
| 1.24GB             | 457MB             | ~63%                |

Specific index file size information:

| Index Type | Index File Size | Dictionary File Size | Total |
|------------|----------------|---------------------|-------|
| No Compression Index | 76MB | - | 76MB |
| Blocking Compression Index | 76MB | 372KB | 76.4MB |
| Front Coding Compression Index | 76MB | 272KB | 76.3MB |
| Dictionary as String Index | 76MB | 936KB | 76.9MB |
| Current Working Index | 112MB | 936KB | 112.9MB |

## 5. Experimental Results and Comparison

### 5.1 Index Compression Effectiveness

Comparison of dictionary file sizes across different compression methods:

| Compression Method | Dictionary File Size | Compression Ratio (Relative Size) |
|-------------------|---------------------|----------------------------------|
| Front Coding      | 272KB               | 100% (Best)                      |
| Blocking          | 372KB               | 137%                             |
| Dictionary as String | 936KB            | 344%                             |

![Dictionary Compression Comparison](https://mermaid.ink/img/pako:eNpNkM1OwzAQhF9l5QMcSIPxXyzlVmijWjSUQw8IbJIlsVLHke0AFeqzy491EZ6PjEajaX8pKkXUUBGIWuOAGm7OsR9cKG1yw2gfQtf4jTwsXMGGIXHwHXnBXxhCJO6bE0Zo5JkzXXhDxq39fxXFsYKS3KL-TNKCXDhvYXHgUxKcUPbcTjkXwbNP0RHTlHjBZpQ7s0wSsxs3RWaS5fNuQ0VZlMnECbUzuZw_sgUdDmmrjt-DUK9QvHTWB43OUJGhhG4Zs2pqeKJjDlmVZaUoZ9LD7gf78S-U0WiXqRJsKH2EbGwX1x38AU6QXsc?type=png)

### 5.2 Boolean Query Performance

Testing performance with different index files and query types:

| Query | Index Type | Query Time (s) | Matching Documents |
|-------|------------|----------------|-------------------|
| information AND retrieval | Current Working Index | 0.000273 | 2 |
| information AND (retrieval OR system) | No Compression Index | 0.000414 | 182 |
| information AND (retrieval OR system) | Dictionary as String Index | 0.000427 | 182 |

The query performance indicates that even for complex Boolean queries, the system can complete processing in milliseconds. The query time for Dictionary as String compression is very close to the uncompressed index, showing that compression has minimal impact on query performance.

### 5.3 System Usability Evaluation

The optimized system offers the following advantages:

1. **Clear File Organization**: Functionally categorized directory structure makes it easy for users to find needed files
2. **Easy Index Management**: Separating current indices from example indices reduces confusion
3. **Efficient Storage Utilization**: Reducing redundant files saves significant storage space
4. **Stable Query Performance**: The restructured system maintains the original efficient query performance

## 6. Conclusions and Findings

1. **Importance of File Organization**: A rational file organization structure is crucial for the maintainability and usability of large projects. The optimized directory structure makes the system clearer.

2. **Compression Method Comparison**:
   - Front coding compression provides the best dictionary compression ratio
   - Dictionary as a string compression, though having a lower compression ratio, is simple to implement and has minimal impact on query speed

3. **System Performance**: The optimized system performs well when processing medium-sized document collections (Hillary Emails, approximately 7,946 emails), with efficient index construction and quick query response.

4. **Practical Implications**: Through exploration of index compression methods and file organization, we discovered methods that can significantly improve system efficiency and user experience in practical applications.

## 7. Future Work

1. **Resolve Front Coding and Blocking Compression Compatibility Issues**: The current system has some compatibility issues when using front coding and blocking compression indices that need further refinement.

2. **Implement Incremental Index Updates**: Add support for incremental index updates to avoid reindexing the entire corpus.

3. **Further Optimize Skip List Implementation**: Make skip lists demonstrate performance advantages on larger datasets.

4. **Extend Query Functionality**: Support phrase queries, approximate queries, and ranking functionality.

5. **Provide a Graphical User Interface**: Develop a GUI interface to allow non-technical users to easily use the system. 