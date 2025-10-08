#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Code duplication checker"""

import hashlib
import re
import typing as t
from collections import defaultdict

from cqas.constructs.duplication import DuplicationResult

__all__: t.Tuple[str, ...] = ("DuplicationDetector",)


class DuplicationDetector:
    """Smarter code duplication detector"""

    BOILERPLATE_PATTERNS: t.Final[t.FrozenSet[re.Pattern[str]]] = frozenset(
        {
            re.compile(r"^\s*#.*$"),  # Entirely comment lines
            re.compile(r"^\s*import\s+"),  # import statements
            re.compile(r"^\s*from\s+.*\s+import\s+"),  # from ... import ...
            re.compile(r"^\s*$"),  # empty lines
        }
    )

    def __init__(
        self,
        min_block_lines: int = 5,
        max_block_lines: int = 10,
        similarity_threshold: float = 0.9,
    ):
        self.min_block_lines: int = min_block_lines
        self.max_block_lines: int = max_block_lines
        self.similarity_threshold: float = similarity_threshold

    def _is_boilerplate_line(self, line: str) -> bool:
        """Detect boilerplate lines to ignore in duplication detection."""
        for pattern in self.BOILERPLATE_PATTERNS:
            if pattern.match(line):
                return True
        return False

    def _normalise_block(self, block: t.List[str]) -> str:
        """Normalise a code block"""
        block_text: str = "\n".join(block)
        block_text = block_text.strip().lower()
        # Replace identifier-like tokens (simple heuristic)
        block_text = re.sub(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", "var", block_text)
        # Collapse multiple spaces
        block_text = re.sub(r"\s+", " ", block_text)
        return block_text

    def _generate_blocks(self, lines: t.List[str]) -> t.Dict[str, t.List[int]]:
        """Generate normalised code blocks with variable sliding window sizes"""

        filtered_lines = [line for line in lines if not self._is_boilerplate_line(line)]
        blocks: t.DefaultDict[str, t.List[int]] = defaultdict(list)

        # To avoid counting overlapping blocks multiple times in the same file,
        # keep track of indices already accounted for in detected duplicates
        accounted_indices: t.Set[int] = set()

        line_count: int = len(filtered_lines)

        for size in range(self.min_block_lines, self.max_block_lines + 1):
            # Sliding window over lines of given size
            for start in range(line_count - size + 1):
                # Skip if any index in this block was already accounted to avoid overlaps
                if any((start + offset) in accounted_indices for offset in range(size)):
                    continue

                block: t.List[str] = filtered_lines[start : start + size]
                if not block or len(block) < self.min_block_lines:
                    continue

                normalised: str = self._normalise_block(block)
                block_hash: str = hashlib.blake2b(
                    normalised.encode("utf-8")
                ).hexdigest()

                blocks[block_hash].append(start)

                # Mark these indices to avoid overlapping duplicates counted again
                for idx in range(start, start + size):
                    accounted_indices.add(idx)

        return blocks

    def check(self, content: str) -> float:
        """Analyse duplication percentage inside a single file"""

        lines: t.List[str] = content.splitlines()
        blocks: t.Dict[str, t.List[int]] = self._generate_blocks(lines)

        duplicated_lines: int = 0

        for _, occurrences in blocks.items():
            if len(occurrences) > 1:
                block_size: int = self.min_block_lines
                duplicated_lines += block_size * (len(occurrences) - 1)

        total_code_lines: int = len(
            [line for line in lines if not self._is_boilerplate_line(line)]
        )

        if total_code_lines == 0:
            return 0.0

        duplication_ratio: float = duplicated_lines / total_code_lines
        return min(duplication_ratio * 100, 100.0)

    def analyse_project(
        self, file_contents: t.List[t.Tuple[str, str]]
    ) -> DuplicationResult:
        """Analyse duplication across multiple files considering intra-file deduplication"""

        project_blocks: t.DefaultDict[str, t.List[t.Tuple[str, int]]] = defaultdict(
            list
        )

        for file_path, content in file_contents:
            lines: t.List[str] = content.splitlines()
            blocks: t.Dict[str, t.List[int]] = self._generate_blocks(lines)
            for block_hash, starts in blocks.items():
                for start in starts:
                    project_blocks[block_hash].append((file_path, start))

        duplicates: t.Dict[str, t.List[t.Tuple[str, int]]] = {
            h: lst for h, lst in project_blocks.items() if len(lst) > 1
        }
        duplicated_lines: int = 0

        for block_hash, occurrences in duplicates.items():
            files_in_occurrences: t.Set[str] = set(f for f, _ in occurrences)
            repeat_files: int = len(files_in_occurrences) - 1
            if repeat_files > 0:
                duplicated_lines += self.min_block_lines * repeat_files

        total_code_lines: int = 0
        for _, content in file_contents:
            total_code_lines += len(
                [
                    line
                    for line in content.splitlines()
                    if not self._is_boilerplate_line(line)
                ]
            )

        if total_code_lines == 0:
            duplication_percentage: float = 0.0
        else:
            duplication_percentage = (duplicated_lines / total_code_lines) * 100

        return DuplicationResult(
            duplicate_blocks_count=len(duplicates),
            duplicated_lines_estimate=duplicated_lines,
            total_code_lines=total_code_lines,
            duplication_percentage=min(duplication_percentage, 100.0),
            duplicates=duplicates,
        )
