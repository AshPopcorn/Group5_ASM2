# Information Retrieval System Quick Start Guide

This document provides basic examples for running the information retrieval system, allowing you to quickly get started.

## 1. Directory Structure

The system directory structure should be as follows:
```
IR-Assignment2-Group5/
├── ir_system/           # Main program package
├── data/                # Data directory
│   ├── corpus/          # Corpus storage
│   │   └── HillaryEmails/  # Sample corpus
│   └── indices/         # Generated indices
│       ├── temp/        # Temporary indices
│       └── examples/    # Example indices
├── run.py               # Main running script
└── requirements.txt     # Dependencies
```
IR-Assignment2-Group5/
├── ir_system/           # Main program
│   ├── cli/             # Command line handdle
│   │   └── commands.py
│   ├── utils/             # Compute the memory and search time, generate performance report
│   │   └── performance.py
│   └── core/            # System implemention
│       ├── compression.py        # Compression techniques (dictionary string, blocking, front coding)
│       ├── data_structures.py    # Generate skip pointers list for searching
│       ├── file_utils.py         # File parser (Asm 1)
│       ├── indexing.py           # Implement original SPIMI algorithm (Asm 1)
│       ├── query_processing.py   # Implement boolean search algorithm
│       └── text_processing.py    # Generate tokens and normalization (Asm 1)
└── main.py     # Main function
## 2. Building a Basic Index

First, let's build a basic index file:

```bash
python run.py index data/corpus/HillaryEmails 1000 data/indices/temp/test_index.txt
```

This command will:
- Process all documents in the `data/corpus/HillaryEmails` directory
- Use 1000 as the memory block size
- Save the index to `data/indices/temp/test_index.txt`

After execution, you will see the progress of document processing and a final performance report, including processing time and memory usage.

## 3. Building a Compressed Index

Next, let's build an index using string compression:

```bash
python run.py index data/corpus/HillaryEmails 1000 data/indices/temp/test_string_index.txt --compress string
```

This command uses the additional parameter `--compress string` to specify string compression. After execution, the system will apply compression and generate an additional dictionary file `test_string_index.txt.string_dict`.

## 4. Performing Basic Search

Now we can search using the built index:

```bash
python run.py search "information AND retrieval" data/indices/temp/test_index.txt
```

This command will:
- Search for documents containing both "information" and "retrieval"
- Display a list of matching document paths
- Show the time taken for the search

## 5. Searching with Compressed Index

Using a compressed index for searching:

```bash
python run.py search "information AND retrieval" data/indices/temp/test_string_index.txt
```

The system will automatically detect that this is a compressed index and load the corresponding compression dictionary.

## 6. Executing Complex Boolean Queries

The system supports complex boolean query expressions:

```bash
python run.py search "information OR (retrieval AND system)" data/indices/temp/test_index.txt
```

This query will find documents containing "information", or documents containing both "retrieval" and "system".

## 7. Optimizing Search with Skip Lists

Finally, let's try optimizing search performance with skip lists:

```bash
python run.py search "information AND retrieval" data/indices/temp/test_string_index.txt --skips 3
```

The parameter `--skips 3` specifies a skip list step size of 3, which can accelerate intersection operations on large indices.

## Summary

The examples above demonstrate the basic workflow of the information retrieval system, including:
1. Building a basic index
2. Building a compressed index
3. Performing simple searches
4. Executing boolean queries
5. Optimizing searches with skip lists

You can adjust parameters as needed, such as index block size, compression method, and skip list step size, to optimize system performance. 