import re
from typing import Dict, List, Set


class PayeeResolver:

    def __init__(self):
        self.mappings = []
        self._unresolved = set()

    def load_mappings(self, mappings: List[Dict[str, List[str]]]):
        self.mappings = [
            dict(
                name=payee["name"],
                patterns=[re.compile(pattern, re.IGNORECASE) for pattern in payee["patterns"]]
            )
            for payee in mappings
        ]

    def __call__(self, memo: str) -> str:
        """Resolve a memo to a payee name"""
        for payee in self.mappings:
            if any(pattern.search(memo) for pattern in payee["patterns"]):
                return payee["name"]
        
        # Keep track of unresolved memos
        self._unresolved.add(memo)
        
        return ""

    @property
    def unresolved(self) -> Set[str]:
        """Get a list of unresolved memos"""
        return self._unresolved.copy()
