"""
File Change Analyzer Package
A tool for analyzing and comparing functions between two versions of source code files.
"""

import re
import os
import difflib
from typing import Dict, List, Tuple, Optional, Set
from pathlib import Path


class FileChangeAnalyzer:
    """
    Analyzes and compares functions across before/after versions of source files.
    Detects changes both inside and outside of functions.
    """
    
    EXTENSIONS = ['.c', '.h', '.S', '.py', '.sh', '.cpp', '.hpp', '.cc', '.cxx']
    
    def __init__(self, output_dir: str = "analysis_output"):
        """
        Initialize the analyzer.
        
        Args:
            output_dir (str): Directory where analysis results will be saved
        """
        self.output_dir = Path(output_dir)
        self.hunk_counter = 1
        self._setup_directories()
        
    def _setup_directories(self):
        """Create necessary output directories."""
        (self.output_dir / "patch").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "before_function").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "after_function").mkdir(parents=True, exist_ok=True)
    
    def analyze_files(self, before_file: str, after_file: str) -> Dict:
        """
        Main method to analyze differences between two file versions.
        
        Args:
            before_file (str): Path to the file before changes (accepts raw strings)
            after_file (str): Path to the file after changes (accepts raw strings)
            
        Returns:
            Dict: Analysis results containing statistics and findings
        """
        # Convert to Path object - handles raw strings, forward/backward slashes, etc.
        before_path = Path(before_file).resolve()
        after_path = Path(after_file).resolve()
        
        if not before_path.exists():
            raise FileNotFoundError(f"Previous file not found: {before_path}")
        if not after_path.exists():
            raise FileNotFoundError(f"New file not found: {after_path}")

        print(f"\nAnalyzing: {before_path.name}")
        
        # Extract functions from both files
        before_functions = self._extract_all_functions(str(before_path))
        after_functions = self._extract_all_functions(str(after_path))
        
        print(f"  Found {len(before_functions)} functions in previous file")
        print(f"  Found {len(after_functions)} functions in new file")

        results = {
            'file_before': str(before_path),
            'file_after': str(after_path),
            'identical_functions': 0,
            'modified_functions': 0,
            'unique_functions': 0,
            'non_function_changes': False,
            'hunks_created': []
        }
        
        # Compare common functions
        processed = set()
        for func_name in before_functions:
            if func_name in after_functions:
                func1_code, line1 = before_functions[func_name]
                func2_code, line2 = after_functions[func_name]
                
                is_identical, removed, added, first_del, first_add, diff_output = \
                    self._compare_functions(func1_code, func2_code)
                
                if is_identical:
                    results['identical_functions'] += 1
                    print(f"  ✓ Function '{func_name}' is identical")
                else:
                    results['modified_functions'] += 1
                    print(f"  ✗ Function '{func_name}' has differences")
                    hunk_id = self._save_function_differences(
                        func_name, func1_code, func2_code, line1, line2,
                        removed, added, first_del, first_add,
                        str(before_path), str(after_path), diff_output
                    )
                    results['hunks_created'].append(hunk_id)
                
                processed.add(func_name)
        
        # Handle unique functions
        for func_name in before_functions:
            if func_name not in processed:
                results['unique_functions'] += 1
                func_code, line_num = before_functions[func_name]
                print(f"  + Function '{func_name}' only in before file")
                hunk_id = self._save_unique_function(
                    func_name, func_code, line_num, str(before_path), True
                )
                results['hunks_created'].append(hunk_id)
        
        for func_name in after_functions:
            if func_name not in processed:
                results['unique_functions'] += 1
                func_code, line_num = after_functions[func_name]
                print(f"  + Function '{func_name}' only in after file")
                hunk_id = self._save_unique_function(
                    func_name, func_code, line_num, str(after_path), False
                )
                results['hunks_created'].append(hunk_id)
        
        # Analyze non-function changes
        print(f"  Analyzing non-function changes...")
        has_non_func_changes = self._analyze_non_function_changes(
            str(before_path), str(after_path)
        )
        if has_non_func_changes:
            results['non_function_changes'] = True
            results['hunks_created'].append(f"hunk{self.hunk_counter - 1}")
        
        return results
    
    def analyze_directories(self, before_dir: str, after_dir: str) -> Dict:
        """
        Analyze all matching files between two directories.
        
        Args:
            before_dir (str): Directory with files before changes (accepts raw strings)
            after_dir (str): Directory with files after changes (accepts raw strings)
            
        Returns:
            Dict: Overall analysis results
        """
        # Convert to Path and resolve to absolute path
        before_path = Path(before_dir).resolve()
        after_path = Path(after_dir).resolve()
        
        if not before_path.exists():
            raise FileNotFoundError(f"Previous File directory not found: {before_path}")
        if not after_path.exists():
            raise FileNotFoundError(f"New File directory not found: {after_path}")
        
        if not before_path.is_dir():
            raise NotADirectoryError(f"Previous File path is not a directory: {before_path}")
        if not after_path.is_dir():
            raise NotADirectoryError(f"New File path is not a directory: {after_path}")
        
        # Find matching files
        before_files = self._get_supported_files(before_path)
        after_files = self._get_supported_files(after_path)
        
        # Match by relative paths
        before_rel = {f.relative_to(before_path): f for f in before_files}
        after_rel = {f.relative_to(after_path): f for f in after_files}
        
        common_files = set(before_rel.keys()) & set(after_rel.keys())
        
        print(f"\nFound {len(common_files)} matching files to analyze")
        
        overall_results = {
            'total_files': len(common_files),
            'files_analyzed': [],
            'total_hunks': 0
        }
        
        for rel_path in sorted(common_files):
            try:
                result = self.analyze_files(
                    str(before_rel[rel_path]),
                    str(after_rel[rel_path])
                )
                overall_results['files_analyzed'].append(result)
                overall_results['total_hunks'] += len(result['hunks_created'])
            except Exception as e:
                print(f"Error analyzing {rel_path}: {e}")
        
        return overall_results
    
    def _get_supported_files(self, directory: Path) -> List[Path]:
        """Get all supported files from a directory recursively."""
        files = []
        for ext in self.EXTENSIONS:
            files.extend(directory.rglob(f"*{ext}"))
        return files
    
    def _extract_all_functions(self, filename: str) -> Dict[str, Tuple[str, int]]:
        """Extract all functions from a file with their line numbers."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            ext = Path(filename).suffix.lower()
            
            if ext in ['.py']:
                return self._extract_python_functions(lines)
            elif ext in ['.c', '.h', '.S', '.cpp', '.hpp', '.cc', '.cxx']:
                return self._extract_c_functions(content, lines)
            elif ext in ['.sh']:
                return self._extract_shell_functions(lines)
            else:
                return self._extract_generic_functions(lines)
        except Exception as e:
            print(f"    Error reading file {filename}: {e}")
            return {}
    
    def _extract_python_functions(self, lines: List[str]) -> Dict[str, Tuple[str, int]]:
        """Extract Python functions."""
        functions = {}
        pattern = r'^(\s*)(def\s+(\w+)\s*\([^)]*\):)'
        
        for i, line in enumerate(lines):
            match = re.match(pattern, line)
            if match:
                indent_level = len(match.group(1))
                func_name = match.group(3)
                func_start = i
                func_end = self._find_python_function_end(lines, i, indent_level)
                
                if func_end > func_start:
                    function_code = '\n'.join(lines[func_start:func_end + 1])
                    functions[func_name] = (function_code, func_start + 1)
        
        return functions
    
    def _find_python_function_end(self, lines: List[str], start: int, base_indent: int) -> int:
        """Find end of Python function by indentation."""
        for i in range(start + 1, len(lines)):
            line = lines[i]
            if line.strip() == '':
                continue
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= base_indent and line.strip():
                return i - 1
        return len(lines) - 1
    
    def _extract_c_functions(self, content: str, lines: List[str]) -> Dict[str, Tuple[str, int]]:
        """Extract C/C++ functions."""
        functions = {}
        pattern = r'(?:(?:static|inline|extern|const|unsigned|signed|struct|enum|union|void|int|char|float|double|short|long|size_t|bool)\s+)*(?:\w+\s+)*\b(\w+)\s*\([^)]*\)\s*(?:(?:const|override|final|noexcept)\s*)*(?:(?:->|:)[^{]*?)?\s*{'
        
        for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
            func_name = match.group(1)
            if func_name.lower() in ['if', 'for', 'while', 'switch', 'catch', 'sizeof']:
                continue
            
            start_pos = match.start()
            line_num = content[:start_pos].count('\n')
            line_start = content.rfind('\n', 0, start_pos) + 1
            if line_start == 0:
                line_start = 0
            
            opening_brace = match.end() - 1
            func_code = self._extract_c_function_body(content, line_start, opening_brace)
            
            if func_code and func_code.strip():
                functions[func_name] = (func_code, line_num + 1)
        
        return functions
    
    def _extract_c_function_body(self, content: str, line_start: int, brace_pos: int) -> Optional[str]:
        """Extract complete C function body."""
        bracket_level = 1
        pos = brace_pos + 1
        
        while bracket_level > 0 and pos < len(content):
            if content[pos] == '{':
                bracket_level += 1
            elif content[pos] == '}':
                bracket_level -= 1
            pos += 1
        
        if bracket_level == 0:
            return content[line_start:pos].strip()
        return None
    
    def _extract_shell_functions(self, lines: List[str]) -> Dict[str, Tuple[str, int]]:
        """Extract shell functions."""
        functions = {}
        pattern = r'^(\s*)(\w+)\s*\(\)\s*{'
        
        for i, line in enumerate(lines):
            match = re.match(pattern, line)
            if match:
                func_name = match.group(2)
                func_end = self._find_shell_function_end(lines, i)
                if func_end > i:
                    function_code = '\n'.join(lines[i:func_end + 1])
                    functions[func_name] = (function_code, i + 1)
        
        return functions
    
    def _find_shell_function_end(self, lines: List[str], start: int) -> int:
        """Find end of shell function by brace matching."""
        brace_count = 0
        started = False
        
        for i in range(start, len(lines)):
            for char in lines[i]:
                if char == '{':
                    brace_count += 1
                    started = True
                elif char == '}':
                    brace_count -= 1
                    if started and brace_count == 0:
                        return i
        return len(lines) - 1
    
    def _extract_generic_functions(self, lines: List[str]) -> Dict[str, Tuple[str, int]]:
        """Generic function extraction."""
        functions = {}
        pattern = r'^(\s*)(\w+)\s*\([^)]*\)\s*{'
        
        for i, line in enumerate(lines):
            match = re.match(pattern, line)
            if match:
                func_name = match.group(2)
                func_end = self._find_shell_function_end(lines, i)
                if func_end > i:
                    function_code = '\n'.join(lines[i:func_end + 1])
                    functions[func_name] = (function_code, i + 1)
        
        return functions
    
    def _get_function_line_ranges(self, filename: str) -> List[Tuple[int, int]]:
        """Get line ranges for all functions in a file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            functions = self._extract_all_functions(filename)
            ranges = []
            
            for func_name, (func_code, start_line) in functions.items():
                line_count = func_code.count('\n') + 1
                ranges.append((start_line, start_line + line_count - 1))
            
            return ranges
        except Exception as e:
            print(f"    Error getting function ranges: {e}")
            return []
    
    def _get_non_function_lines(self, filename: str) -> Set[int]:
        """Get line numbers outside functions."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            total_lines = len(lines)
            all_lines = set(range(1, total_lines + 1))
            
            function_ranges = self._get_function_line_ranges(filename)
            function_lines = set()
            
            for start, end in function_ranges:
                function_lines.update(range(start, end + 1))
            
            return all_lines - function_lines
        except Exception as e:
            print(f"    Error analyzing non-function lines: {e}")
            return set()
    
    def _compare_functions(self, func1: str, func2: str) -> Tuple[bool, List, List, int, int, List[str]]:
        """Compare two functions and return detailed differences."""
        lines1 = func1.splitlines(keepends=False)
        lines2 = func2.splitlines(keepends=False)
        
        if func1.strip() == func2.strip():
            return True, [], [], -1, -1, []
        
        diff_lines = list(difflib.unified_diff(
            lines1, lines2,
            fromfile='before_function',
            tofile='after_function',
            lineterm='',
            n=3
        ))
        
        removed, added = [], []
        first_del, first_add = -1, -1
        current_line1, current_line2 = 0, 0
        
        for line in diff_lines:
            if line.startswith('@@'):
                match = re.match(r'@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@', line)
                if match:
                    current_line1 = int(match.group(1))
                    current_line2 = int(match.group(3))
            elif line.startswith('-') and not line.startswith('---'):
                removed.append((current_line1, line[1:]))
                if first_del == -1:
                    first_del = current_line1
                current_line1 += 1
            elif line.startswith('+') and not line.startswith('+++'):
                added.append((current_line2, line[1:]))
                if first_add == -1:
                    first_add = current_line2
                current_line2 += 1
            elif line.startswith(' '):
                current_line1 += 1
                current_line2 += 1
        
        return False, removed, added, first_del, first_add, diff_lines
    
    def _save_function_differences(self, func_name: str, func1: str, func2: str,
                                  line1: int, line2: int, removed: List, added: List,
                                  first_del: int, first_add: int, file1: str, file2: str,
                                  diff_output: List[str]) -> str:
        """Save function differences to files."""
        hunk_id = f"patch{self.hunk_counter}"
        basename = Path(file1).stem
        
        # Save before function
        (self.output_dir / "before_function" / f"{hunk_id}_{Path(file1).name}").write_text(str(func1), encoding="utf-8")
        
        # Save after function
        (self.output_dir / "after_function" / f"{hunk_id}_{Path(file2).name}").write_text(str(func2), encoding="utf-8")

        # Save patch file
        patch_path = self.output_dir / "patch" / f"{hunk_id}_{basename}_patch.txt"
        with open(patch_path, 'w', encoding='utf-8') as f:
            f.write(f"Function Name: {func_name}\n")
            f.write(f"Previous File: {file1}\n")
            f.write(f"New File: {file2}\n")
            f.write(f"Previous File Line: {line1}\n")
            f.write(f"New File Line: {line2}\n")
            f.write(f"First Deletion Line: {first_del if first_del != -1 else 'N/A'}\n")
            f.write(f"First Addition Line: {first_add if first_add != -1 else 'N/A'}\n")
            f.write(f"Removed Lines: {len(removed)}\n")
            f.write(f"Added Lines: {len(added)}\n\n")
            
            f.write("="*70 + "\n")
            f.write("UNIFIED DIFF\n")
            f.write("="*70 + "\n")
            for line in diff_output:
                f.write(f"{line}\n")
            
            f.write("\n" + "="*70 + "\n")
            f.write("REMOVED LINES\n")
            f.write("="*70 + "\n")
            if removed:
                for line_num, content in removed:
                    f.write(f"{line_num:<8} | {content}\n")
            else:
                f.write("No lines removed.\n")
            
            f.write("\n" + "="*70 + "\n")
            f.write("ADDED LINES\n")
            f.write("="*70 + "\n")
            if added:
                for line_num, content in added:
                    f.write(f"{line_num:<8} | {content}\n")
            else:
                f.write("No lines added.\n")
        
        self.hunk_counter += 1
        return hunk_id
    
    def _save_unique_function(self, func_name: str, func_code: str, line_num: int,
                            filename: str, is_before: bool) -> str:
        """Save functions unique to one version."""
        hunk_id = f"patch{self.hunk_counter}"
        basename = Path(filename).stem
        folder = "before_function" if is_before else "after_function"

        (self.output_dir / folder / f"{hunk_id}_{Path(filename).name}").write_text(str(func_code), encoding="utf-8")

        patch_path = self.output_dir / "patch" / f"{hunk_id}_{basename}_unique.txt"
        with open(patch_path, 'w', encoding='utf-8') as f:
            f.write(f"Function Name: {func_name}\n")
            f.write(f"Line Number: {line_num}\n")
            f.write(f"File: {filename}\n")
            f.write(f"Status: Present only in {'before' if is_before else 'after'} file\n\n")
            f.write("="*50 + "\n")
            f.write("FUNCTION CONTENT:\n")
            f.write("="*50 + "\n")
            f.write(func_code)
        
        self.hunk_counter += 1
        return hunk_id
    
    def _analyze_non_function_changes(self, before_file: str, after_file: str) -> bool:
        """Analyze changes outside functions."""
        try:
            with open(before_file, 'r', encoding='utf-8') as f:
                before_lines = f.read().splitlines(keepends=False)
            with open(after_file, 'r', encoding='utf-8') as f:
                after_lines = f.read().splitlines(keepends=False)
            
            before_non_func = self._get_non_function_lines(before_file)
            after_non_func = self._get_non_function_lines(after_file)
            
            diff_lines = list(difflib.unified_diff(
                before_lines, after_lines,
                fromfile=f'before_{Path(before_file).name}',
                tofile=f'after_{Path(after_file).name}',
                lineterm='',
                n=3
            ))
            
            if not diff_lines:
                return False
            
            non_func_removed, non_func_added = [], []
            current_line1, current_line2 = 0, 0
            
            for line in diff_lines:
                if line.startswith('@@'):
                    match = re.match(r'@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@', line)
                    if match:
                        current_line1 = int(match.group(1))
                        current_line2 = int(match.group(3))
                elif line.startswith('-') and not line.startswith('---'):
                    if current_line1 in before_non_func:
                        non_func_removed.append((current_line1, line[1:]))
                    current_line1 += 1
                elif line.startswith('+') and not line.startswith('+++'):
                    if current_line2 in after_non_func:
                        non_func_added.append((current_line2, line[1:]))
                    current_line2 += 1
                elif line.startswith(' '):
                    current_line1 += 1
                    current_line2 += 1
            
            if non_func_removed or non_func_added:
                print(f"      ✗ Non-function changes detected")
                self._save_non_function_changes(
                    before_file, after_file, non_func_removed, non_func_added, diff_lines
                )
                return True
            else:
                print(f"      ✓ No non-function changes")
                return False
        except Exception as e:
            print(f"    Error analyzing non-function changes: {e}")
            return False
    
    def _save_non_function_changes(self, before_file: str, after_file: str,
                                  removed: List, added: List, diff_output: List[str]):
        """Save non-function changes."""
        hunk_id = f"hunk{self.hunk_counter}"
        basename = Path(before_file).stem
        
        patch_path = self.output_dir / "patch" / f"{hunk_id}_{basename}_nonfunction.txt"
        with open(patch_path, 'w', encoding='utf-8') as f:
            f.write(f"Analysis Type: NON-FUNCTION CHANGES\n")
            f.write(f"Previous File: {before_file}\n")
            f.write(f"New File: {after_file}\n")
            f.write(f"Non-Function Lines Removed: {len(removed)}\n")
            f.write(f"Non-Function Lines Added: {len(added)}\n\n")
            
            f.write("="*70 + "\n")
            f.write("COMPLETE FILE DIFF (FOR CONTEXT)\n")
            f.write("="*70 + "\n")
            for line in diff_output:
                f.write(f"{line}\n")
            
            f.write("\n" + "="*70 + "\n")
            f.write("NON-FUNCTION LINES REMOVED\n")
            f.write("="*70 + "\n")
            if removed:
                for line_num, content in removed:
                    safe_content = content if content.strip() else "[EMPTY LINE]"
                    f.write(f"{line_num:<8} | {safe_content}\n")
            else:
                f.write("No non-function lines removed.\n")
            
            f.write("\n" + "="*70 + "\n")
            f.write("NON-FUNCTION LINES ADDED\n")
            f.write("="*70 + "\n")
            if added:
                for line_num, content in added:
                    safe_content = content if content.strip() else "[EMPTY LINE]"
                    f.write(f"{line_num:<8} | {safe_content}\n")
            else:
                f.write("No non-function lines added.\n")
        
        self.hunk_counter += 1


# Example usage
def main():
    """Example usage of FileChangeAnalyzer with various path formats."""
    analyzer = FileChangeAnalyzer("analysis_output")
    
    # All these path formats work correctly:
    
    # Raw string with Windows path
    # results = analyzer.analyze_files(
    #     r"C:\Users\Name\Documents\before.c",
    #     r"C:\Users\Name\Documents\after.c"
    # )
    
    # Forward slashes (cross-platform)
    # results = analyzer.analyze_files(
    #     "C:/Users/Name/Documents/before.c",
    #     "C:/Users/Name/Documents/after.c"
    # )
    
    # Relative paths
    # results = analyzer.analyze_files("./before.c", "./after.c")
    
    # Unix-style absolute paths
    # results = analyzer.analyze_files("/home/user/before.c", "/home/user/after.c")
    
    # Or analyze entire directories with raw strings
    # results = analyzer.analyze_directories(
    #     r"C:\Projects\version1",
    #     r"C:\Projects\version2"
    # )
    
    print("\nAnalysis complete!")
    print(f"Results saved in: {analyzer.output_dir}")


if __name__ == "__main__":
    main()