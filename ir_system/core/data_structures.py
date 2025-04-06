"""
Data Structures Module.

Provides specialized data structures for information retrieval, including skip lists.
"""

import math
from typing import List, Set, Tuple, Dict, Any, Iterator, Union


class PostingList:
    """Posting list implementation with skip pointers for fast list intersection."""
    
    def __init__(self, posting_list: List[str], skip_size: int = None):
        """Initialize a posting list with skip pointers.
        
        Args:
            posting_list: List of document IDs
            skip_size: Skip distance (if None, sqrt(n) is used)
        """
        self.posting_list = sorted(posting_list) if posting_list else []
        self.skip_size = skip_size
        self.skip_pointers = []
        
        if posting_list:
            self._build_skip_pointers()
            
    def __len__(self) -> int:
        """Get the length of the posting list.
        
        Returns:
            Number of documents in the posting list
        """
        return len(self.posting_list)
        
    def __iter__(self) -> Iterator[str]:
        """Iterator for the posting list.
        
        Returns:
            Iterator over document IDs
        """
        return iter(self.posting_list)
        
    def _build_skip_pointers(self) -> None:
        """Build skip pointers for the posting list."""
        n = len(self.posting_list)
        
        # If skip size not specified, use sqrt(n)
        if self.skip_size is None:
            self.skip_size = max(1, int(math.sqrt(n)))
            
        # Create skip pointers
        self.skip_pointers = []
        for i in range(0, n, self.skip_size):
            # Skip pointer points to the next skip position or the end
            next_skip = min(i + self.skip_size, n - 1)
            if i != next_skip:
                self.skip_pointers.append((i, next_skip))
                
    def intersection(self, other: Union[Set[str], List[str], 'PostingList']) -> Set[str]:
        """Compute intersection with another posting list or set.
        
        Args:
            other: Another posting list or set of document IDs
            
        Returns:
            Set of document IDs in the intersection
        """
        # Convert other to a PostingList if it's not already
        if not isinstance(other, PostingList):
            other_list = PostingList(other if isinstance(other, list) else list(other))
        else:
            other_list = other
            
        # If either list is empty, return empty set
        if not self.posting_list or not other_list.posting_list:
            return set()
            
        # Intersect the lists using skip pointers
        result = []
        i = j = 0
        
        while i < len(self.posting_list) and j < len(other_list.posting_list):
            if self.posting_list[i] == other_list.posting_list[j]:
                result.append(self.posting_list[i])
                i += 1
                j += 1
            elif self.posting_list[i] < other_list.posting_list[j]:
                # Try to use skip pointers to advance faster
                skipped = False
                for start, end in self.skip_pointers:
                    if i == start and self.posting_list[end] <= other_list.posting_list[j]:
                        i = end
                        skipped = True
                        break
                        
                if not skipped:
                    i += 1
            else:
                # Try to use skip pointers to advance faster
                skipped = False
                for start, end in other_list.skip_pointers:
                    if j == start and other_list.posting_list[end] <= self.posting_list[i]:
                        j = end
                        skipped = True
                        break
                        
                if not skipped:
                    j += 1
                    
        return set(result)
        
    def union(self, other: Union[Set[str], List[str], 'PostingList']) -> Set[str]:
        """Compute union with another posting list or set.
        
        Args:
            other: Another posting list or set of document IDs
            
        Returns:
            Set of document IDs in the union
        """
        # Convert PostingList to set for efficient union
        if isinstance(other, PostingList):
            other_set = set(other.posting_list)
        else:
            other_set = set(other)
            
        return set(self.posting_list).union(other_set)
        
    def difference(self, other: Union[Set[str], List[str], 'PostingList']) -> Set[str]:
        """Compute difference with another posting list or set.
        
        Args:
            other: Another posting list or set of document IDs
            
        Returns:
            Set of document IDs in the difference (self - other)
        """
        # Convert PostingList to set for efficient difference
        if isinstance(other, PostingList):
            other_set = set(other.posting_list)
        else:
            other_set = set(other)
            
        return set(self.posting_list).difference(other_set) 