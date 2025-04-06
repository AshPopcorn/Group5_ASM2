# IN6226 Information Retrieval & Analysis - Assignment 2: Search Engine
*Semester: Semester 2 2024-2025*

## 1. Instructions

In this course, there are a total of three team assignments. This is assignment 2 of 3.

A single PDF report is to be submitted by every team. Assign only one team member to submit the report.

Feel free to use any external materials but do not forget to reference your sources.

## 2. Report Requirements

**Read this section very carefully. Failure to adhere to the simple rules of reporting will result in lowered marks.**

- **Submission deadline**: Sunday, 06 April @ 2359h
- **Submission method**: Through NTULearn, one PDF file (and nothing else)

The report **should not** have a separate title page. At the top of the first page, please put the following mandatory information:

- Title: IN6226 Information Retrieval & Analysis / Assignment 2 / AY24-25
- Full names of team members
- Matric numbers of team members
- NTU email address of team members

The report should not exceed 4 pages excluding references. The report should cover what was done in each step of the assignment, provide reasoning for the chosen course of action, and demonstrate examples (where applicable). The report should be written as a coherent text. You can showcase portions of your code in the report.

**Do not** upload your code to NTULearn.

If you want to share your code as part of your submission, please do so via a private repo on GitHub. As students, you can apply for GitHub Education, which will enable private repos for you for free. Do not make your repos public as it may encourage copying of your work. After uploading your GitHub, add me (hamzahNTU) as a collaborator to your repo and add a link to the repo in your report.

The report must be neatly formatted. Reports that are hard to read due to formatting may be marked low or not marked at all.

## 3. Grading

The assignment will be graded overall on a scale of 0-100. This assignment comprises of 25% of the course grade. Team members will receive equal marks.

## 4. Dataset

You have been provided with the dataset for this assignment. You can use your own dataset if you prefer.

## 5. Assignment Tasks

In this assignment, you will continue to build an information retrieval system based on the results of Assignment 1, which is a system that can output a sorted list of term-document pairs (if BSBI was used) or an inverted index (if SPIMI was used).

The tasks in this assignment are:

### 5.1 Build an Inverted Index

**Input**: A file with sorted term-doc pairs  
**Output**: Inverted index

If in Assignment 1, BSBI was used, then in this part you will need to take the file containing the sorted list of term-doc pairs and transform it into a simple inverted index. In this assignment, do not worry about the list or inverted index being too big for main memory, however, take that into account.

If SPIMI was used in Assignment 1, you do not have to do anything for (5.1). In your report, indicate that the inverted index was built as part of Assignment 1.

**Bonus**: Persist the inverted index as a file so you do not need to rebuild it every time you launch the program.

### 5.2 Boolean Search

**Input**: A search query, an inverted index  
**Output**: A list of documents satisfying the query

Implement a simple AND-based Boolean search, e.g. a query "horse car phone" should be treated as "horse AND car AND phone" and return only documents that contain all three words.

**Bonus**: Implement OR and NOT in addition to AND.

### 5.3 Index Compression/Optimisation

Implement compression and optimisation techniques that were discussed in the lectures. Implement at least the Dictionary-as-a-String approach. Implementing other techniques such as blocking, front-coding, skip pointers, variable-length gap encoding are encouraged.

Compare your search engine performance and memory requirements before and after implementing compression and optimisation. Reflect the comparison in your report.

**Bonus**: If you implement many techniques and manage to achieve impressive savings in speed and/or memory.