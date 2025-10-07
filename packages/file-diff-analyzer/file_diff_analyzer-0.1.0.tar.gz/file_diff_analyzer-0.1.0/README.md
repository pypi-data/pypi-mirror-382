# 🧩 File Diff Analyzer (FDA)

> Analyze function-level and line-level differences between two source code versions — ideal for vulnerability tracking, patch comparison, and static analysis.

---

### 🪶 **Highlights**
- 🧠 Compare two files and extract unified diffs (line-level) using Python file diff analyzer.
- 🧩 Detect added, removed, or modified functions and save them to structured folders.
- 📁 Analyze entire directories recursively to find and compare matching files.
- 🪟 File writing uses **Windows-safe sanitized names** and creates directories automatically.
- 🧰 Zero external dependencies — **Python Standard Library only**.

---

## ⚙️ Requirements
- Python **3.8 or later**
- Works on **Windows**, **macOS**, and **Linux**
- No external dependencies!

---

## 📦 Installation

pip install file_diff_analyzer

from file_diff_analyzer import FileChangeAnalyzer

## Compare two files:

- analyzer = FileChangeAnalyzer(output_dir="my_analysis_output")
- result = analyzer.analyze_files(
-    r"D:\Projects\old_version\main.c",
-    r"D:\Projects\new_version\main.c"
- )
- print("Saved analysis to:", result)


## Compare two directories:

- results = analyzer.analyze_directories(
-    r"C:\Projects\version1",
-    r"C:\Projects\version2"
- )
- print("Directory analysis complete. Output folder:", results)



