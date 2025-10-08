# readgrid

**readgrid** is a Python package for **document layout analysis and content extraction**.  
It lets you upload scanned documents, automatically detect tables and images, manually adjust bounding boxes for all document elements, and extract clean structured output using LLMs.

---

## ✨ Features
- **Stage 1 – Upload & Detect**
  - Upload document images in batch mode.
  - Automatically detect **tables** (red boxes) and **images** (green boxes).
  - Manually draw bounding boxes for **columns** (blue boxes), **headers** (orange boxes), and **footers** (magenta boxes).
  - Interactive editor supports multiple boxes per type with add/edit/delete functionality.

- **Stage 2 – Coordinate Testing**
  - Verify detected regions with side-by-side previews.
  - Test either existing detections or custom coordinates.
  - Works with all box types (tables, images, columns, headers, footers).

- **Stage 3 – Content Extraction**
  - Extract structured JSON output with layout-aware reading order.
  - Supports multi-column layouts (single, two, three, four columns).
  - Replace detected tables with clean HTML `<table>` tags.
  - Insert `[image]` placeholders with captions in correct reading order.
  - Proper header/footer separation from main content.
  - Supports LaTeX formatting for mathematical equations.
  - Customizable output fields with inclusion/exclusion options.

- **Utility Functions**
  - `pretty_print_page_with_image()` – inspect extracted results with annotated images.
  - `show_comparison_view()` – compare annotated vs. reconstructed content with multiple view modes.
  - `cleanup_pipeline()` – reset all artifacts.
  - `editor()` – interactive JSON correction with LLM assistance and diff visualization.

---

## 🚀 Installation
```bash
pip install readgrid
```

---

## 🛠️ Usage

### Stage 1: Upload, Detect, and Edit

```python
from readgrid import stage_1

stage_1()
```

### Stage 2: Test Coordinates

```python
from readgrid import stage_2

stage_2(
    row_id="ID_1",
    box_type="tables",
    box_index=0
)
```

### Stage 3: Extract with Gemini

```python
from readgrid import stage_3

stage_3(api_key="YOUR_API_KEY")
```

---
## ✏️ Editor

```python
from readgrid import editor

# Basic usage - will prompt for API key
editor(row_id="ID_1")

# With all options
editor(
    row_id="ID_1",
    api_key="YOUR_API_KEY",
    model="gemini-2.0-flash",
    clean=True,        # Auto-clean tables, LaTeX, newlines
    font_size=12       # Adjust display size
)
```

### Features:

* Currently supports just JSON file types.
* Automatic cleaning of tables, LaTeX formatting, and broken words
* Side-by-side view: original image vs. current JSON
* Conversational interface: "Add newline after Table 1" or "Fix the header"
* Real-time diff view (unified or side-by-side with color coding)
* Undo/reset functionality
* Saves corrections back to `final_outputs/`

---

## 📦 Requirements

* Python 3.8+
* [OpenCV](https://pypi.org/project/opencv-python/)
* [NumPy](https://pypi.org/project/numpy/)
* [Pillow](https://pypi.org/project/Pillow/)
* google-generativeai

---

## 📄 License

MIT License.
See LICENSE for details.