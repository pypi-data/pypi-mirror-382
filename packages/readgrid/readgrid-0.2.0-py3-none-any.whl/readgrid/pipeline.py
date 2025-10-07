# ==================== IMPORTS ====================
import cv2
import numpy as np
import json
import os
import re
import base64
import time
import shutil
import textwrap
from io import BytesIO
from PIL import Image
from getpass import getpass
from typing import List, Tuple, Dict, Any, Optional

# Imports for Google Colab
from google.colab import files
from google.colab.patches import cv2_imshow
from google.colab import output
from IPython.display import display, Image as IPImage, clear_output, HTML
import ipywidgets as widgets

# Imports for Stage 3 (LLM)
try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Warning: 'google-genai' not found. Stage 3 will not be available.")
    print("Please run: !pip install -q google-genai")

# ==================== UTILITY FUNCTIONS ====================
def cleanup_pipeline():
    """Removes all generated files and folders from the pipeline."""
    print("🧹 Cleaning up pipeline artifacts...")
    items_to_remove = [
        'uploads',
        'bounded_images',
        'final_outputs',
        'coords.json'
    ]
    for item in items_to_remove:
        try:
            if os.path.exists(item):
                if os.path.isdir(item):
                    shutil.rmtree(item)
                    print(f"  - Removed directory: {item}/")
                else:
                    os.remove(item)
                    print(f"  - Removed file: {item}")
        except Exception as e:
            print(f"  - Error removing {item}: {e}")
    print("✅ Cleanup complete.")

def pretty_print_page_with_image(json_path: str):
    """
    Pretty prints the content of a final JSON file and displays its
    corresponding annotated image.
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File '{json_path}' not found.")
        return

    row_id = os.path.splitext(os.path.basename(json_path))[0]
    print("=" * 100)
    print(f"📄 DOCUMENT PREVIEW: {row_id}")
    print("=" * 100)

    header = data.get("Page header", "") or "(none)"
    page_text = data.get("Page text", "") or "(none)"
    footer = data.get("Page footer", "") or "(none)"

    print(f"📋 HEADER:\n---\n{textwrap.fill(header, 100)}\n")
    print(f"📖 PAGE TEXT:\n---\n{textwrap.fill(page_text, 100)}")
    print(f"\n📝 FOOTER:\n---\n{textwrap.fill(footer, 100)}\n")

    table_bbox = data.get("table_bbox", [])
    image_bbox = data.get("image_bbox", [])

    print("🟥 TABLE BBOX ([ymin, xmin, ymax, xmax]):")
    print("---" if table_bbox else "(none)")
    if table_bbox:
        for i, bbox in enumerate(table_bbox, 1): print(f"  Table {i}: {bbox}")

    print("\n🟩 IMAGE BBOX ([ymin, xmin, ymax, xmax]):")
    print("---" if image_bbox else "(none)")
    if image_bbox:
        for i, bbox in enumerate(image_bbox, 1): print(f"  Image {i}: {bbox}")

    img_path = os.path.join('bounded_images', f"{row_id}.jpg")
    if os.path.exists(img_path):
        print(f"\n📸 CORRESPONDING ANNOTATED IMAGE:")
        cv2_imshow(cv2.imread(img_path))
    else:
        print(f"\n⚠️ Annotated image not found at: {img_path}")
    print("=" * 100)

def show_comparison_view(json_path: str, mode: str = "ir", uploads_dir: str = 'uploads', coords_file: str = 'coords.json'):
    """
    Renders a flexible, side-by-side HTML view of document annotations.

    Args:
        json_path (str): Path to the JSON annotation file (e.g., 'final_outputs/1.json').
        mode (str): View mode. 
                    "ir" = image vs rendered text
                    "ij" = image vs raw JSON
                    "jr" = raw JSON vs rendered text
        uploads_dir (str): Directory containing original images (default: 'uploads').
        coords_file (str): File containing coordinate mappings (default: 'coords.json').
    """
    # Map short mode codes to panels
    mode_map = {
        "ir": ("image", "rendered_text"),
        "ij": ("image", "raw_json"),
        "jr": ("raw_json", "rendered_text")
    }
    left_panel, right_panel = mode_map.get(mode, ("image", "rendered_text"))

    print(f"--- 🖼️  Generating comparison: [{left_panel.upper()}] vs [{right_panel.upper()}] for {os.path.basename(json_path)} ---")

    # --- 1. Load JSON Data ---
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: JSON file not found at '{json_path}'")
        return
    except json.JSONDecodeError:
        print(f"❌ Error: Could not parse the JSON file. It might be malformed: '{json_path}'")
        return

    # --- 2. Prepare All Possible Content Blocks ---
    image_html, raw_json_html, rendered_text_html = "", "", ""

    # A. Prepare Image HTML
    if 'image' in [left_panel, right_panel]:
        row_id = os.path.splitext(os.path.basename(json_path))[0]
        img_path = os.path.join('bounded_images', f"{row_id}.jpg")

        if os.path.exists(img_path):
            try:
                image = cv2.imread(img_path)
                image_rgb = image
                _, buffer = cv2.imencode('.jpg', image_rgb)
                base64_image = base64.b64encode(buffer).decode('utf-8')
                image_html = f'''
                    <h3 class="panel-title">Annotated Page Image</h3>
                    <div class="inner-card">
                        <img src="data:image/jpeg;base64,{base64_image}" style="width: 100%; border: 1px solid #ccc;">
                    </div>
                '''
            except Exception as e:
                image_html = f"<p style='color:red;'>⚠️ Could not load image: {e}</p>"
        else:
            image_html = f"<p style='color:red;'>❌ Image not found at {img_path}</p>"

    # B. Prepare Raw JSON HTML
    if 'raw_json' in [left_panel, right_panel]:
        pretty_json = json.dumps(data, indent=2, ensure_ascii=False)
        escaped_json = pretty_json.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        raw_json_html = f'''
            <h3 class="panel-title">Raw JSON Content</h3>
            <div class="inner-card">
                <pre style="white-space: pre-wrap; word-wrap: break-word;"><code>{escaped_json}</code></pre>
            </div>
        '''

    # C. Prepare Rendered Text HTML
    if 'rendered_text' in [left_panel, right_panel]:
        header = (data.get("Page header") or "").strip()
        page_text = (data.get("Page text") or "No 'Page text' found in JSON.").strip()
        footer = (data.get("Page footer") or "").strip()

        processed_text = page_text.replace('\\(', '$').replace('\\)', '$')
        processed_text = processed_text.replace('\\[', '$$').replace('\\]', '$$')

        pattern = re.compile(r"\$\$(.*?)\$\$\s*?\n\s*?\((\d+)\)", re.DOTALL)
        final_text = pattern.sub(r"$$\1 \\tag{\2}$$", processed_text)
        final_text = final_text.replace('\n', '<br>')
        
        rendered_parts = []
        if header:
            rendered_parts.append(f'<div class="header-section">{header}</div>')
        rendered_parts.append(f'<div class="rendered-body">{final_text}</div>')
        if footer:
            rendered_parts.append(f'<div class="footer-section">{footer}</div>')
        
        rendered_content = ''.join(rendered_parts)

        rendered_text_html = f'''
            <h3 class="panel-title">Rendered Document Preview</h3>
            <div class="inner-card">{rendered_content}</div>
        '''

    # --- 3. Assemble the Final HTML View ---
    content_map = {
        'image': image_html,
        'raw_json': raw_json_html,
        'rendered_text': rendered_text_html
    }
    left_html = content_map.get(left_panel, "Invalid left_panel choice")
    right_html = content_map.get(right_panel, "Invalid right_panel choice")

    mathjax_scripts = ""
    if 'rendered_text' in [left_panel, right_panel]:
        mathjax_scripts = """
        <script>
          window.MathJax = {
            tex: { inlineMath: [['$', '$'], ['\\(', '\\)']], tags: 'ams', tagSide: 'right', tagIndent: '0.8em' },
            chtml: { scale: 1.05 }
          };
        </script>
        <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        """

    full_html = f"""
    <html><head>{mathjax_scripts}<style>
        .container {{ display: flex; gap: 20px; font-family: 'Times New Roman', 'Times', serif; }}
        
        .panel {{ 
            flex: 1; 
            border: 1px solid #ddd; 
            padding: 15px; 
            border-radius: 8px; 
            overflow-x: auto; 
            background-color: #fdfdfd; 
        }}
        
        .panel-title {{
            text-align: center;
            font-family: sans-serif;
            margin: 0 0 15px 0;
            font-weight: 600;
        }}

        .inner-card {{
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            background: #fff;
        }}
        
        .document-container {{ margin: 0; padding: 0; }}
        
        .rendered-body {{ 
            text-align: justify; 
            line-height: 1.8; 
            font-size: 18px; 
            color: #000;
        }}
        
        .header-section {{
            margin-bottom: 15px;
            font-size: 18px;
            color: #000;
            text-align: left;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            background: #fafafa;
        }}
        
        .footer-section {{
            margin-top: 20px;
            font-size: 18px;
            color: #000;
            text-align: center;
            line-height: 1.2;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            background: #fafafa;
        }}
        
        .document-container > *:last-child {{
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }}
        
        mjx-container[jax="CHTML"][display="true"] {{ margin: 1.5em 0; }}
    </style></head><body><div class="container">
        <div class="panel">{left_html}</div>
        <div class="panel">{right_html}</div>
    </div></body></html>
    """
    display(HTML(full_html))

# ==================== HELPER & EDITOR FUNCTIONS ====================

def xywh_to_yminmax(box: tuple) -> List[int]:
    """Converts (x, y, w, h) to [ymin, xmin, ymax, xmax]."""
    x, y, w, h = box
    return [y, x, y + h, x + w]

def yminmax_to_xywh(box: list) -> List[int]:
    """Converts [ymin, xmin, ymax, xmax] to [x, y, w, h]."""
    ymin, xmin, ymax, xmax = box
    return [xmin, ymin, xmax - xmin, ymax - ymin]

def detect_tables(image: np.ndarray) -> List[List[int]]:
    """Detects tables in an image. Returns xywh format."""
    boxes = []
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    binary = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, -2)
    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    h_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, h_kernel, iterations=2)
    v_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, v_kernel, iterations=2)
    mask = cv2.add(h_lines, v_lines)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        if cv2.contourArea(c) > 2000:
            x, y, w, h = cv2.boundingRect(c)
            if w > 50 and h > 50:
                boxes.append([x, y, w, h])
    return boxes

def detect_image_regions(image: np.ndarray, min_area_percentage=1.5) -> List[List[int]]:
    """Detects image regions. Returns xywh format."""
    h, w, _ = image.shape
    min_area = (min_area_percentage / 100) * (h * w)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edged = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 100, 200)
    contours, _ = cv2.findContours(cv2.dilate(edged, None, iterations=2), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for c in contours:
        if cv2.contourArea(c) > min_area:
            x, y, w_box, h_box = cv2.boundingRect(c)
            if 0.2 < (w_box / float(h_box) if h_box > 0 else 0) < 5.0 and w_box > 80 and h_box > 80:
                boxes.append([x, y, w_box, h_box])
    return boxes

def create_annotated_image(
    image: np.ndarray,
    table_boxes: List[List[int]],
    image_boxes: List[List[int]],
    column_boxes: List[List[int]] = None,
    header_boxes: List[List[int]] = None,
    footer_boxes: List[List[int]] = None
) -> np.ndarray:
    """Creates annotated image with all bounding box types with proper sequential labeling."""
    annotated_img = image.copy()

    # Set defaults
    column_boxes = column_boxes or []
    header_boxes = header_boxes or []
    footer_boxes = footer_boxes or []

    # Filter out empty/invalid boxes before drawing and use sequential numbering
    
    # Draw table boxes (red) - only valid boxes, numbered sequentially
    valid_table_boxes = [box for box in table_boxes if box and len(box) == 4 and any(box) and box != [0,0,0,0]]
    for i, box in enumerate(valid_table_boxes):
        x, y, w, h = box
        cv2.rectangle(annotated_img, (x, y), (x + w, y + h), (0, 0, 255), 3)
        cv2.putText(annotated_img, f"T{i+1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    # Draw image boxes (green) - only valid boxes, numbered sequentially
    valid_image_boxes = [box for box in image_boxes if box and len(box) == 4 and any(box) and box != [0,0,0,0]]
    for i, box in enumerate(valid_image_boxes):
        x, y, w, h = box
        cv2.rectangle(annotated_img, (x, y), (x + w, y + h), (0, 255, 0), 3)
        cv2.putText(annotated_img, f"I{i+1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Draw column boxes (blue) - only valid boxes, numbered sequentially
    valid_column_boxes = [box for box in column_boxes if box and len(box) == 4 and any(box) and box != [0,0,0,0]]
    for i, box in enumerate(valid_column_boxes):
        x, y, w, h = box
        cv2.rectangle(annotated_img, (x, y), (x + w, y + h), (255, 0, 0), 3)
        cv2.putText(annotated_img, f"C{i+1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    # Draw header boxes (cyan) - only valid boxes, numbered sequentially
    valid_header_boxes = [box for box in header_boxes if box and len(box) == 4 and any(box) and box != [0,0,0,0]]
    for i, box in enumerate(valid_header_boxes):
        x, y, w, h = box
        cv2.rectangle(annotated_img, (x, y), (x + w, y + h), (255, 255, 0), 3)
        cv2.putText(annotated_img, f"H{i+1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)

    # Draw footer boxes (magenta) - only valid boxes, numbered sequentially
    valid_footer_boxes = [box for box in footer_boxes if box and len(box) == 4 and any(box) and box != [0,0,0,0]]
    for i, box in enumerate(valid_footer_boxes):
        x, y, w, h = box
        cv2.rectangle(annotated_img, (x, y), (x + w, y + h), (255, 0, 255), 3)
        cv2.putText(annotated_img, f"F{i+1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 255), 2)

    return annotated_img

def create_context_image(
    image: np.ndarray,
    context_table_boxes: List[Tuple[List[int], int]],  # (box, original_index)
    context_image_boxes: List[Tuple[List[int], int]],   # (box, original_index)
    context_column_boxes: List[Tuple[List[int], int]] = None,
    context_header_boxes: List[Tuple[List[int], int]] = None,
    context_footer_boxes: List[Tuple[List[int], int]] = None
) -> np.ndarray:
    """Creates image with context boxes (all boxes except the one being edited) with proper sequential labeling."""
    context_img = image.copy()

    # Set defaults
    context_column_boxes = context_column_boxes or []
    context_header_boxes = context_header_boxes or []
    context_footer_boxes = context_footer_boxes or []

    # Filter out empty/invalid boxes and use sequential numbering for each type
    
    # Draw context table boxes (red) - filter and renumber sequentially
    valid_context_tables = [(box, original_idx) for box, original_idx in context_table_boxes 
                           if box and len(box) == 4 and any(box) and box != [0,0,0,0]]
    for i, (box, original_idx) in enumerate(valid_context_tables):
        x, y, w, h = box
        cv2.rectangle(context_img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(context_img, f"T{i + 1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # Draw context image boxes (green) - filter and renumber sequentially
    valid_context_images = [(box, original_idx) for box, original_idx in context_image_boxes 
                           if box and len(box) == 4 and any(box) and box != [0,0,0,0]]
    for i, (box, original_idx) in enumerate(valid_context_images):
        x, y, w, h = box
        cv2.rectangle(context_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(context_img, f"I{i + 1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Draw context column boxes (blue) - filter and renumber sequentially
    valid_context_columns = [(box, original_idx) for box, original_idx in context_column_boxes 
                            if box and len(box) == 4 and any(box) and box != [0,0,0,0]]
    for i, (box, original_idx) in enumerate(valid_context_columns):
        x, y, w, h = box
        cv2.rectangle(context_img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.putText(context_img, f"C{i + 1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    # Draw context header boxes (cyan) - filter and renumber sequentially
    valid_context_headers = [(box, original_idx) for box, original_idx in context_header_boxes 
                            if box and len(box) == 4 and any(box) and box != [0,0,0,0]]
    for i, (box, original_idx) in enumerate(valid_context_headers):
        x, y, w, h = box
        cv2.rectangle(context_img, (x, y), (x + w, y + h), (255, 255, 0), 2)
        cv2.putText(context_img, f"H{i + 1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    # Draw context footer boxes (magenta) - filter and renumber sequentially
    valid_context_footers = [(box, original_idx) for box, original_idx in context_footer_boxes 
                            if box and len(box) == 4 and any(box) and box != [0,0,0,0]]
    for i, (box, original_idx) in enumerate(valid_context_footers):
        x, y, w, h = box
        cv2.rectangle(context_img, (x, y), (x + w, y + h), (255, 0, 255), 2)
        cv2.putText(context_img, f"F{i + 1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)

    return context_img

def interactive_editor(img: np.ndarray, initial_boxes: List[List[int]], editor_title: str) -> List[List[int]]:
    """Launches the HTML/JS editor for editing multiple bounding boxes with drag-to-resize functionality."""

    _, buffer = cv2.imencode('.png', img)
    img_str = base64.b64encode(buffer).decode('utf-8')
    img_data_url = f'data:image/png;base64,{img_str}'

    # Accept multiple initial boxes (or empty list)
    initial_boxes = initial_boxes if initial_boxes else []
    boxes_json = json.dumps(initial_boxes)

    html_template = f"""
    <div style="border: 2px solid #ccc; padding: 10px; display: inline-block;">
        <h3 style="font-family: sans-serif;">{editor_title}</h3>
        <p style="font-family: sans-serif; margin-top: 0; line-height: 1.4;">
            <b>Click and drag</b> to draw a new box.<br>
            <b>Click inside a box</b> to delete it.<br>
            <b>Drag box edges/corners</b> to resize existing boxes.<br>
            <b>Use ↩️ Undo Last</b> to remove the most recent box.<br>
            You can draw multiple boxes before submitting.
        </p>
        <canvas id="editor-canvas" style="cursor: crosshair; border: 1px solid black;"></canvas>
        <br>
        <button id="undo-button" style="margin-top: 10px; font-size: 14px; padding: 6px 12px;">↩️ Undo Last</button>
        <button id="done-button" style="margin-top: 10px; font-size: 16px; padding: 8px 16px;">✅ Submit</button>
        <div id="status" style="margin-top: 10px; font-family: sans-serif; font-size: 14px;"></div>
    </div>
    <script>
    const canvas = document.getElementById('editor-canvas');
    const ctx = canvas.getContext('2d');
    const doneButton = document.getElementById('done-button');
    const undoButton = document.getElementById('undo-button');
    const status = document.getElementById('status');
    const img = new Image();

    window.finished = false;
    window.finalBoxes = [];
    let boxes = JSON.parse('{boxes_json}');
    let isDrawing = false;
    let isResizing = false;
    let resizeHandle = null;
    let resizeBoxIndex = -1;
    let startX, startY;
    let currentCursor = 'crosshair';

    function updateStatus(message) {{ status.textContent = message; }}

    img.onload = function() {{
        canvas.width = img.width;
        canvas.height = img.height;
        redraw();
        updateStatus('Image loaded. Ready for editing.');
    }};
    img.src = '{img_data_url}';

    function redraw() {{
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);
        
        // Draw all boxes
        boxes.forEach(([x, y, w, h], idx) => {{
            // Draw the main box
            ctx.strokeStyle = 'blue';
            ctx.lineWidth = 2;
            ctx.strokeRect(x, y, w, h);
            
            // Draw resize handles (small squares at corners and edges)
            ctx.fillStyle = 'blue';
            const handleSize = 6;
            const handles = [
                [x - handleSize/2, y - handleSize/2], // top-left
                [x + w/2 - handleSize/2, y - handleSize/2], // top-center
                [x + w - handleSize/2, y - handleSize/2], // top-right
                [x + w - handleSize/2, y + h/2 - handleSize/2], // right-center
                [x + w - handleSize/2, y + h - handleSize/2], // bottom-right
                [x + w/2 - handleSize/2, y + h - handleSize/2], // bottom-center
                [x - handleSize/2, y + h - handleSize/2], // bottom-left
                [x - handleSize/2, y + h/2 - handleSize/2], // left-center
            ];
            
            handles.forEach(([hx, hy]) => {{
                ctx.fillRect(hx, hy, handleSize, handleSize);
            }});
            
            // Label each box
            ctx.fillStyle = "blue";
            ctx.font = "14px sans-serif";
            ctx.fillText(idx+1, x+5, y+20);
        }});
        
        updateStatus(`Current boxes: ${{boxes.length}}`);
    }}

    function getResizeHandle(mouseX, mouseY, boxIndex) {{
        if (boxIndex === -1) return null;
        
        const [x, y, w, h] = boxes[boxIndex];
        const handleSize = 6;
        const tolerance = 3;
        
        const handles = [
            {{name: 'nw', x: x, y: y, cursor: 'nw-resize'}},
            {{name: 'n', x: x + w/2, y: y, cursor: 'n-resize'}},
            {{name: 'ne', x: x + w, y: y, cursor: 'ne-resize'}},
            {{name: 'e', x: x + w, y: y + h/2, cursor: 'e-resize'}},
            {{name: 'se', x: x + w, y: y + h, cursor: 'se-resize'}},
            {{name: 's', x: x + w/2, y: y + h, cursor: 's-resize'}},
            {{name: 'sw', x: x, y: y + h, cursor: 'sw-resize'}},
            {{name: 'w', x: x, y: y + h/2, cursor: 'w-resize'}}
        ];
        
        for (let handle of handles) {{
            if (Math.abs(mouseX - handle.x) <= handleSize/2 + tolerance && 
                Math.abs(mouseY - handle.y) <= handleSize/2 + tolerance) {{
                return handle;
            }}
        }}
        
        return null;
    }}

    function getBoxAtPosition(mouseX, mouseY) {{
        for (let i = boxes.length - 1; i >= 0; i--) {{
            const [x, y, w, h] = boxes[i];
            if (mouseX >= x && mouseX <= x + w && mouseY >= y && mouseY <= y + h) {{
                return i;
            }}
        }}
        return -1;
    }}

    function updateCursor(mouseX, mouseY) {{
        const boxIndex = getBoxAtPosition(mouseX, mouseY);
        const handle = getResizeHandle(mouseX, mouseY, boxIndex);
        
        if (handle) {{
            canvas.style.cursor = handle.cursor;
            currentCursor = handle.cursor;
        }} else if (boxIndex !== -1) {{
            canvas.style.cursor = 'pointer';
            currentCursor = 'pointer';
        }} else {{
            canvas.style.cursor = 'crosshair';
            currentCursor = 'crosshair';
        }}
    }}

    canvas.addEventListener('mousemove', (e) => {{
        const rect = canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        if (isDrawing) {{
            // Drawing new box
            redraw();
            ctx.strokeStyle = 'red';
            ctx.lineWidth = 2;
            ctx.strokeRect(startX, startY, mouseX - startX, mouseY - startY);
        }} else if (isResizing && resizeBoxIndex !== -1) {{
            // Resizing existing box
            const [origX, origY, origW, origH] = boxes[resizeBoxIndex];
            let newX = origX, newY = origY, newW = origW, newH = origH;
            
            switch (resizeHandle.name) {{
                case 'nw':
                    newX = mouseX;
                    newY = mouseY;
                    newW = origX + origW - mouseX;
                    newH = origY + origH - mouseY;
                    break;
                case 'n':
                    newY = mouseY;
                    newH = origY + origH - mouseY;
                    break;
                case 'ne':
                    newY = mouseY;
                    newW = mouseX - origX;
                    newH = origY + origH - mouseY;
                    break;
                case 'e':
                    newW = mouseX - origX;
                    break;
                case 'se':
                    newW = mouseX - origX;
                    newH = mouseY - origY;
                    break;
                case 's':
                    newH = mouseY - origY;
                    break;
                case 'sw':
                    newX = mouseX;
                    newW = origX + origW - mouseX;
                    newH = mouseY - origY;
                    break;
                case 'w':
                    newX = mouseX;
                    newW = origX + origW - mouseX;
                    break;
            }}
            
            // Ensure minimum size
            if (newW < 10) {{
                newW = 10;
                if (resizeHandle.name.includes('w')) {{
                    newX = origX + origW - 10;
                }}
            }}
            if (newH < 10) {{
                newH = 10;
                if (resizeHandle.name.includes('n')) {{
                    newY = origY + origH - 10;
                }}
            }}
            
            boxes[resizeBoxIndex] = [Math.round(newX), Math.round(newY), Math.round(newW), Math.round(newH)];
            redraw();
        }} else {{
            // Update cursor based on position
            updateCursor(mouseX, mouseY);
        }}
    }});

    canvas.addEventListener('mousedown', (e) => {{
        const rect = canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        const boxIndex = getBoxAtPosition(mouseX, mouseY);
        const handle = getResizeHandle(mouseX, mouseY, boxIndex);
        
        if (handle) {{
            // Start resizing
            isResizing = true;
            resizeHandle = handle;
            resizeBoxIndex = boxIndex;
            updateStatus('Resizing box...');
        }} else if (boxIndex !== -1) {{
            // Delete box
            boxes.splice(boxIndex, 1);
            redraw();
            updateStatus('Box deleted.');
        }} else {{
            // Start drawing new box
            isDrawing = true;
            startX = mouseX;
            startY = mouseY;
            updateStatus('Drawing new box...');
        }}
    }});

    canvas.addEventListener('mouseup', (e) => {{
        if (isDrawing) {{
            const rect = canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;
            
            const x = Math.min(startX, mouseX);
            const y = Math.min(startY, mouseY);
            const w = Math.abs(mouseX - startX);
            const h = Math.abs(mouseY - startY);
            
            if (w > 5 && h > 5) {{
                boxes.push([Math.round(x), Math.round(y), Math.round(w), Math.round(h)]);
                updateStatus('New box created.');
            }} else {{
                updateStatus('Box too small, not created.');
            }}
            
            isDrawing = false;
            redraw();
        }} else if (isResizing) {{
            isResizing = false;
            resizeHandle = null;
            resizeBoxIndex = -1;
            updateStatus('Box resized.');
        }}
    }});

    undoButton.addEventListener('click', () => {{
        if (boxes.length > 0) {{
            boxes.pop();
            redraw();
            updateStatus('Last box removed (undo).');
        }} else {{
            updateStatus('No boxes to undo.');
        }}
    }});

    doneButton.addEventListener('click', () => {{
        doneButton.textContent = '⏳ Submitting...';
        doneButton.disabled = true;
        canvas.style.cursor = 'default';
        window.finalBoxes = boxes;
        window.finished = true;
        updateStatus('✅ Submitted! Python is now processing...');
    }});
    </script>
    """

    display(HTML(html_template))
    print(f"\n✍️ Edit the {editor_title.lower()} above. Draw multiple boxes if needed, then click 'Submit'.")
    print("Waiting for manual correction... ⏳")

    final_boxes = None
    for _ in range(600):  # Wait for up to 5 minutes
        try:
            is_done = output.eval_js('window.finished')
            if is_done:
                final_boxes = output.eval_js('window.finalBoxes')
                break
        except Exception:
            pass
        time.sleep(0.5)

    clear_output(wait=False)
    if final_boxes is not None:
        if len(final_boxes) > 0:
            print(f"✅ {len(final_boxes)} box(es) received!")
        else:
            print("✅ All boxes removed (empty list submitted).")
        return final_boxes
    else:
        print("⚠️ No response received. Using original box(es)." if initial_boxes else "⚠️ No response received. No boxes will be saved.")
        return initial_boxes if initial_boxes else []

def clean_table_html(html: str) -> str:
    """Remove forbidden attributes/tags and flatten table newlines."""
    if not html:
        return html
    
    # Remove disallowed attributes
    html = re.sub(r'\s(?:class|id|style|border|cellspacing|cellpadding)="[^"]*"', '', html, flags=re.IGNORECASE)
    
    # Remove forbidden tags but keep their inner content
    forbidden_tags = ['caption', 'p', 'em', 'strong', 'span', 'div']
    for tag in forbidden_tags:
        html = re.sub(fr'</?{tag}.*?>', '', html, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove newlines inside <table>…</table>
    def strip_table_newlines(match):
        content = match.group(0)
        return re.sub(r'\s*\n\s*', '', content)
    html = re.sub(r'<table.*?>.*?</table>', strip_table_newlines, html, flags=re.DOTALL | re.IGNORECASE)
    
    return html

def fix_broken_words(text: str) -> str:
    """Fix broken words like 'Ac-\\ncordingly' -> 'Accordingly\\n'."""
    if not text:
        return text
    
    def replacer(match):
        part1, part2 = match.group(1), match.group(2)
        return part1 + part2 + "\n"
    
    return re.sub(r'(\w+)-\n(\w+)', replacer, text)

def clean_latex(text: str) -> str:
    r"""Normalize LaTeX inline/display delimiters and strip \left \right."""
    if not text:
        return text

    # Normalize display math: $$...$$ → \[...\]
    text = re.sub(r'\$\$(.*?)\$\$', r'\\[\1\\]', text, flags=re.DOTALL)

    # Normalize inline math: $...$ → \(...\)
    # BUT: avoid matching currency (dollar signs followed/preceded by digits/commas)
    # This regex requires at least one non-digit, non-comma character inside
    # OR math symbols like =, +, -, *, /, ^, _, \, {, }
    def is_likely_math(content):
        """Check if content between $ signs is likely LaTeX math, not currency."""
        # If it contains LaTeX-specific characters, it's math
        math_indicators = ['\\', '{', '}', '^', '_', '=', r'\frac', r'\sum', r'\int']
        if any(indicator in content for indicator in math_indicators):
            return True
        # If it's only digits, commas, periods, and spaces, it's likely currency
        if re.match(r'^[\d,.\s]+$', content):
            return False
        # If it contains letters (variable names), it's likely math
        if re.search(r'[a-zA-Z]', content):
            return True
        return False
    
    # Find all $...$ patterns and only convert if they're likely math
    def replace_inline_math(match):
        content = match.group(1)
        if is_likely_math(content):
            return f'\\({content}\\)'
        else:
            return match.group(0)  # Keep original $...$
    
    text = re.sub(r'\$(.*?)\$', replace_inline_math, text)

    # Remove \left and \right safely
    text = re.sub(r'\\left', '', text)
    text = re.sub(r'\\right', '', text)

    return text

def clean_json_fields(data: dict) -> dict:
    """Apply all cleaning functions to JSON text fields."""
    cleaned = data.copy()
    for key in ["Page header", "Page text", "Page footer"]:
        if key in cleaned and isinstance(cleaned[key], str):
            cleaned[key] = clean_table_html(cleaned[key])
            cleaned[key] = fix_broken_words(cleaned[key])
            cleaned[key] = clean_latex(cleaned[key])
    return cleaned


def editor(
    row_id: str,
    api_key: Optional[str] = None,
    model: str = "gemini-2.0-flash",
    file_type: str = "json",
    clean: bool = True,
    font_size: int = 12,
    uploads_dir: str = 'uploads',
    coords_file: str = 'coords.json',
    final_outputs_dir: str = 'final_outputs'
):
    """
    Interactive JSON editor with LLM assistance for correcting document extraction errors.
    
    Args:
        row_id: The document ID to edit
        api_key: Gemini API key (will prompt if not provided)
        model: Gemini model name (default: gemini-2.0-flash)
        file_type: Type of file to edit (default: "json")
        clean: Whether to apply automatic cleaning first (default: True)
        font_size: Font size for JSON display (default: 12)
        uploads_dir: Directory containing original images
        coords_file: Path to coords.json file
        final_outputs_dir: Directory containing final JSON outputs
    """
    import ipywidgets as widgets
    import difflib
    
    print("=" * 60)
    print(f"JSON EDITOR: {row_id}")
    print("=" * 60)
    
    # --- 1. Validate inputs ---
    if file_type != "json":
        print(f"Warning: Only 'json' file type is currently supported. Got '{file_type}'.")
        return
    
    json_path = os.path.join(final_outputs_dir, f"{row_id}.json")
    if not os.path.exists(json_path):
        print(f"Error: JSON file not found at '{json_path}'")
        return
    
    if not os.path.exists(coords_file):
        print(f"Error: Coords file not found at '{coords_file}'")
        return
    
    # --- 2. Load JSON and get original image path ---
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    with open(coords_file, 'r') as f:
        all_coords = json.load(f)
    
    if row_id not in all_coords:
        print(f"Error: Row ID '{row_id}' not found in coords.json")
        return
    
    original_filename = all_coords[row_id].get("original_filename")
    if not original_filename:
        print(f"Error: 'original_filename' not found for '{row_id}'")
        return
    
    image_path = os.path.join(uploads_dir, original_filename)
    if not os.path.exists(image_path):
        print(f"Error: Original image not found at '{image_path}'")
        return
    
    # --- 3. Apply cleaning if requested ---
    if clean:
        print("Cleaning JSON...")
        json_data = clean_json_fields(json_data)
        print("Cleaning complete")
    
    # --- 4. Configure API ---
    if not api_key:
        try:
            api_key = getpass("Please enter your Gemini API Key: ")
        except Exception as e:
            print(f"Could not read API key: {e}")
            return
    
    try:
        client = genai.Client(api_key=api_key)
        print("API client configured successfully")
    except Exception as e:
        print(f"Error configuring API: {e}")
        return
    
    # --- 5. Initialize editor state ---
    original_json = json_data.copy()
    current_json = json_data.copy()
    history = [json_data.copy()]
    conversation_history = []
    
    # Load image
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    
    # System prompt
    SYSTEM_PROMPT = """You are a JSON editor that corrects document extraction errors by comparing JSON data with the original document image.

Your task:
1. Analyze the provided document image
2. Compare it with the JSON representation
3. Follow user instructions to make corrections
4. Return ONLY the corrected JSON object with the same structure

Common tasks:
- Add or remove newline characters (\\n)
- Fix text that should be on separate lines
- Correct spacing between words
- Move text to correct fields (header/footer/text)

Return format: Valid JSON object with the same keys, only modified values where corrections are needed."""
    
    # --- 6. Helper functions ---
    def show_initial_view(json_data, image_path):
        """Display initial view with image on left and JSON on right"""
        json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
        
        left_output = widgets.Output(layout=widgets.Layout(width='50%', padding='10px'))
        right_output = widgets.Output(layout=widgets.Layout(width='50%', padding='10px'))
        
        # Left side - Image
        with left_output:
            print("Original Document")
            print("-" * 40)
            if image_path and os.path.exists(image_path):
                display(IPImage(filename=image_path))
            else:
                print("No image available")
        
        # Right side - JSON
        with right_output:
            print("Current JSON")
            print("-" * 40)
            html = [f'<div style="font-family: monospace; font-size: {font_size}px; white-space: pre-wrap; word-wrap: break-word; color: #000; max-height: 600px; overflow-y: auto;">']
            for line in json_str.splitlines():
                html.append(f'<div>{line}</div>')
            html.append('</div>')
            display(HTML(''.join(html)))
        
        display(widgets.HBox([left_output, right_output], layout=widgets.Layout(width='100%')))
    
    def generate_unified_diff(original, corrected):
        """Generate unified diff"""
        original_str = json.dumps(original, indent=2, ensure_ascii=False)
        corrected_str = json.dumps(corrected, indent=2, ensure_ascii=False)
        
        diff = list(difflib.unified_diff(
            original_str.splitlines(keepends=True),
            corrected_str.splitlines(keepends=True),
            fromfile='before',
            tofile='after',
            lineterm=''
        ))
        
        return ''.join(diff)
    
    def show_compact_diff(diff_text):
        """Display unified diff with color coding"""
        html_lines = [f'<div style="font-family: monospace; font-size: {font_size}px; white-space: pre-wrap; word-wrap: break-word; max-width: 100%; overflow-wrap: break-word;">']
        
        for line in diff_text.split('\n'):
            if line.startswith('+++') or line.startswith('---'):
                html_lines.append(f'<span style="color: #666; font-weight: bold;">{line}</span>')
            elif line.startswith('@@'):
                html_lines.append(f'<span style="color: #0969da; font-weight: bold;">{line}</span>')
            elif line.startswith('+'):
                html_lines.append(f'<span style="background-color: #d1f0d1; color: #0a6e0a;">{line}</span>')
            elif line.startswith('-'):
                html_lines.append(f'<span style="background-color: #ffd7d5; color: #d1242f;">{line}</span>')
            else:
                html_lines.append(f'<span style="color: #333;">{line}</span>')
        
        html_lines.append('</div>')
        display(HTML('\n'.join(html_lines)))
    
    def show_side_by_side_diff(original, corrected):
        """Display side-by-side diff with color coding"""
        original_str = json.dumps(original, indent=2, ensure_ascii=False)
        corrected_str = json.dumps(corrected, indent=2, ensure_ascii=False)
        
        original_lines = original_str.splitlines()
        corrected_lines = corrected_str.splitlines()
        
        matcher = difflib.SequenceMatcher(None, original_lines, corrected_lines)
        
        html = [f'<div style="display: flex; gap: 10px; font-family: monospace; font-size: {font_size}px; max-width: 100%;">']
        
        # Left side (Original - Red)
        html.append('<div style="flex: 1; border: 1px solid #ddd; padding: 10px; background-color: #fff; overflow-x: auto;">')
        html.append('<div style="font-weight: bold; margin-bottom: 10px; color: #d1242f;">Original (Before)</div>')
        html.append('<div style="white-space: pre-wrap; word-wrap: break-word;">')
        
        # Right side (Corrected - Green)
        right_html = ['<div style="flex: 1; border: 1px solid #ddd; padding: 10px; background-color: #fff; overflow-x: auto;">']
        right_html.append('<div style="font-weight: bold; margin-bottom: 10px; color: #0a6e0a;">Corrected (After)</div>')
        right_html.append('<div style="white-space: pre-wrap; word-wrap: break-word;">')
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                for line in original_lines[i1:i2]:
                    html.append(f'<div style="color: #333;">{line}</div>')
                for line in corrected_lines[j1:j2]:
                    right_html.append(f'<div style="color: #333;">{line}</div>')
            elif tag == 'delete':
                for line in original_lines[i1:i2]:
                    html.append(f'<div style="background-color: #ffd7d5; color: #d1242f;">- {line}</div>')
            elif tag == 'insert':
                for line in corrected_lines[j1:j2]:
                    right_html.append(f'<div style="background-color: #d1f0d1; color: #0a6e0a;">+ {line}</div>')
            elif tag == 'replace':
                for line in original_lines[i1:i2]:
                    html.append(f'<div style="background-color: #ffd7d5; color: #d1242f;">- {line}</div>')
                for line in corrected_lines[j1:j2]:
                    right_html.append(f'<div style="background-color: #d1f0d1; color: #0a6e0a;">+ {line}</div>')
        
        html.append('</div></div>')
        right_html.append('</div></div>')
        html.append(''.join(right_html))
        html.append('</div>')
        
        display(HTML(''.join(html)))
    
    # --- 7. Create UI widgets ---
    instruction_input = widgets.Textarea(
        value='Compare the JSON with the document image and correct any formatting errors.',
        placeholder='Type your instruction here...',
        description='',
        layout=widgets.Layout(width='100%', height='80px')
    )
    
    send_button = widgets.Button(description="Send", button_style="primary")
    undo_button = widgets.Button(description="Undo", button_style="warning")
    reset_button = widgets.Button(description="Reset", button_style="danger")
    save_button = widgets.Button(description="Save", button_style="success")
    
    include_image_checkbox = widgets.Checkbox(
        value=True,
        description='Include image in request',
        indent=False
    )
    
    diff_style_dropdown = widgets.Dropdown(
        options=[('Unified', 'unified'), ('Side-by-Side', 'side-by-side')],
        value='unified',
        description='Diff view:',
        style={'description_width': 'auto'}
    )
    
    output_area = widgets.Output()
    
    # --- 8. Button handlers ---
    def on_send(b):
        nonlocal current_json, history, conversation_history
        
        with output_area:
            clear_output(wait=True)
            instruction = instruction_input.value.strip()
            
            if not instruction:
                print("Please enter an instruction")
                return
            
            print(f"You: {instruction}")
            print("\nProcessing...\n")
            
            previous_json = current_json.copy()
            
            try:
                prompt = f"""Current JSON:
{json.dumps(current_json, indent=2, ensure_ascii=False)}

User request: {instruction}

Return the corrected JSON object."""
                
                parts = [SYSTEM_PROMPT + "\n\n" + prompt]
                
                if include_image_checkbox.value:
                    parts.append(
                        types.Part.from_bytes(
                            data=image_bytes,
                            mime_type='image/jpeg'
                        )
                    )
                
                response = client.models.generate_content(
                    model=model,
                    contents=parts
                )
                
                response_text = response.text.strip()
                
                # Clean markdown fences
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.startswith("```"):
                    response_text = response_text[3:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                corrected_json = json.loads(response_text)
                
                if previous_json != corrected_json:
                    print("Changes made:\n")
                    
                    if diff_style_dropdown.value == 'side-by-side':
                        show_side_by_side_diff(previous_json, corrected_json)
                    else:
                        diff = generate_unified_diff(previous_json, corrected_json)
                        show_compact_diff(diff)
                    
                    current_json = corrected_json
                    history.append(corrected_json.copy())
                    conversation_history.append({
                        'instruction': instruction,
                        'response': response_text
                    })
                else:
                    print("No changes needed or no changes detected")
                
                print("\n" + "="*60)
                
            except json.JSONDecodeError as e:
                print(f"Could not parse LLM response as JSON: {e}")
            except Exception as e:
                print(f"Error during LLM request: {e}")
    
    def on_undo(b):
        nonlocal current_json, history
        
        with output_area:
            clear_output(wait=True)
            if len(history) > 1:
                history.pop()
                current_json = history[-1].copy()
                print("Undone last change")
                print("\nCurrent state:")
                print(json.dumps(current_json, indent=2, ensure_ascii=False)[:500] + "...")
            else:
                print("Nothing to undo")
    
    def on_reset(b):
        nonlocal current_json, history, conversation_history
        
        with output_area:
            clear_output(wait=True)
            current_json = original_json.copy()
            history = [original_json.copy()]
            conversation_history = []
            print("Reset to original JSON")
    
    def on_save(b):
        with output_area:
            clear_output(wait=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(current_json, f, indent=4, ensure_ascii=False)
            print(f"Saved to '{json_path}'")
    
    send_button.on_click(on_send)
    undo_button.on_click(on_undo)
    reset_button.on_click(on_reset)
    save_button.on_click(on_save)
    
    # --- 9. Display UI ---
    print("\nJSON EDITOR WITH CONVERSATIONAL INTERFACE")
    print("="*60)
    print("\nType instructions naturally, like:")
    print("  - 'Add a newline after the phrase \"See table 13\"'")
    print("  - 'Remove the newline in the header'")
    print("  - 'Fix the Page footer'")
    print("  - 'Compare with image and fix all errors'")
    print("\n" + "="*60 + "\n")
    
    display(widgets.VBox([
        widgets.Label("Your instruction:"),
        instruction_input,
        widgets.HBox([send_button, undo_button, reset_button, save_button]),
        widgets.HBox([include_image_checkbox, diff_style_dropdown]),
        output_area
    ]))
    
    # Show initial view
    with output_area:
        show_initial_view(current_json, image_path)

# ==================== STAGE 1: UPLOAD, DETECT, & EDIT ====================

def save_coords(row_id, filename, table_coords_xywh, image_coords_xywh, column_coords_xywh, header_coords_xywh, footer_coords_xywh):
    """Helper: Save current coords to coords.json after each edit (append mode) with automatic cleanup."""
    
    # Convert to yminmax format and filter out empty/invalid boxes
    def clean_and_convert(coords_xywh):
        """Convert xywh to yminmax and remove empty/invalid boxes"""
        clean_coords = []
        for box in coords_xywh:
            # Skip empty boxes, [0,0,0,0] placeholders, or invalid boxes
            if box and len(box) == 4 and any(box) and box != [0, 0, 0, 0]:
                clean_coords.append(xywh_to_yminmax(box))
        return clean_coords
    
    table_coords_yminmax = clean_and_convert(table_coords_xywh)
    image_coords_yminmax = clean_and_convert(image_coords_xywh)
    column_coords_yminmax = clean_and_convert(column_coords_xywh)
    header_coords_yminmax = clean_and_convert(header_coords_xywh)
    footer_coords_yminmax = clean_and_convert(footer_coords_xywh)

    # Load existing coords if file exists
    if os.path.exists('coords.json'):
        with open('coords.json', 'r') as f:
            try:
                all_coords = json.load(f)
            except json.JSONDecodeError:
                all_coords = {}
    else:
        all_coords = {}

    # Update / overwrite only this row_id
    all_coords[row_id] = {
        "original_filename": filename,
        "tables": table_coords_yminmax,
        "images": image_coords_yminmax,
        "columns": column_coords_yminmax,
        "headers": header_coords_yminmax,
        "footers": footer_coords_yminmax
    }

    # Save back to file
    with open('coords.json', 'w') as f:
        json.dump(all_coords, f, indent=4)

    # Count only non-empty boxes for status message
    n_tables = len(table_coords_yminmax)
    n_images = len(image_coords_yminmax)
    n_columns = len(column_coords_yminmax)
    n_headers = len(header_coords_yminmax)
    n_footers = len(footer_coords_yminmax)

    print(f"💾 Updated coords.json → {row_id} ({n_tables} tables, {n_images} images, {n_columns} columns, {n_headers} headers, {n_footers} footers)")


def stage_1():
    """
    Handles multiple document uploads, detection, and interactive editing (batch mode).
    For each uploaded file:
      - Ask for row ID upfront (for all files at once).
      - Process files one by one with editing loop.
    """
    print("=" * 60 + "\nSTAGE 1: UPLOAD, DETECT, AND EDIT (BATCH)\n" + "=" * 60)

    # Create directories
    for folder in ['uploads', 'bounded_images']:
        os.makedirs(folder, exist_ok=True)

    # Upload files
    print("\n📤 Please upload your document images...")
    uploaded = files.upload()
    if not uploaded:
        print("❌ No files uploaded.")
        return

    # === Step 1: Ask for row IDs for all files ===
    row_ids = {}
    for i, filename in enumerate(uploaded.keys(), start=1):
        row_id = input(f"➡️ Enter a unique Row ID for '{filename}' (default: {os.path.splitext(filename)[0]}): ").strip()
        if not row_id:
            row_id = os.path.splitext(filename)[0]
        row_ids[filename] = row_id

    # === Step 2: Process each file one by one ===
    for filename, filedata in uploaded.items():
        filepath = os.path.join('uploads', filename)
        with open(filepath, 'wb') as f:
            f.write(filedata)

        row_id = row_ids[filename]
        print("\n" + "=" * 50)
        print(f"📄 Now processing file: {filename} (Row ID: {row_id})")
        print("=" * 50)

        # === Run single-file processing ===
        process_single_image(filename, filepath, row_id)


def process_single_image(filename, filepath, row_id):
    """
    Process a single image file with detection + interactive editing.
    Extracted from stage_1 so we can reuse for batch processing.
    """
    original_img = cv2.imread(filepath)

    # Resize for consistent display
    MAX_WIDTH = 1200
    original_h, original_w, _ = original_img.shape
    scale = MAX_WIDTH / original_w if original_w > MAX_WIDTH else 1.0
    display_w = int(original_w * scale)
    display_h = int(original_h * scale)
    display_img = cv2.resize(original_img, (display_w, display_h), interpolation=cv2.INTER_AREA)

    print("\n" + "=" * 50 + f"\nProcessing: {filename} (Row ID: {row_id})\n" + "=" * 50)
    print("Analyzing Document Content...")

    # Detect on original image, then scale for display
    table_coords_xywh = detect_tables(original_img)
    image_coords_xywh = detect_image_regions(original_img)
    column_coords_xywh = []  # Start empty, user will add manually
    header_coords_xywh = []  # Start empty, user will add manually  
    footer_coords_xywh = []  # Start empty, user will add manually

    table_coords_display = [[int(x * scale), int(y * scale), int(w * scale), int(h * scale)]
                            for x, y, w, h in table_coords_xywh]
    image_coords_display = [[int(x * scale), int(y * scale), int(w * scale), int(h * scale)]
                            for x, y, w, h in image_coords_xywh]
    column_coords_display = [[int(x * scale), int(y * scale), int(w * scale), int(h * scale)]
                            for x, y, w, h in column_coords_xywh]
    header_coords_display = [[int(x * scale), int(y * scale), int(w * scale), int(h * scale)]
                            for x, y, w, h in header_coords_xywh]
    footer_coords_display = [[int(x * scale), int(y * scale), int(w * scale), int(h * scale)]
                            for x, y, w, h in footer_coords_xywh]

    print(f"✅ Found {len(table_coords_xywh)} tables and {len(image_coords_xywh)} images.")

    print("\n📋 ANNOTATION KEY:")
    print("   T# = Table    I# = Image    C# = Column    H# = Header    F# = Footer")

    def get_valid_box_mapping(boxes_list):
            """Returns mapping from visual indices (1,2,3...) to actual array indices."""
            mapping = {}
            visual_index = 1
            for array_index, box in enumerate(boxes_list):
                if box and len(box) == 4 and any(box) and box != [0,0,0,0]:
                    mapping[visual_index] = array_index
                    visual_index += 1
            return mapping

    def batch_delete_boxes(box_type, visual_numbers, display_coords, xywh_coords):
        """
        Delete multiple boxes at once by their visual numbers.
        Returns updated display_coords and xywh_coords lists.
        """
        valid_mapping = get_valid_box_mapping(display_coords)
        
        # Validate all visual numbers exist
        invalid_numbers = [num for num in visual_numbers if num not in valid_mapping]
        if invalid_numbers:
            available = list(valid_mapping.keys())
            print(f"❌ {box_type.title()} {invalid_numbers} don't exist. Available: {available}")
            return display_coords, xywh_coords
        
        # Get actual array indices and sort them in descending order
        # (delete from highest index to lowest to avoid index shifting issues)
        array_indices = [valid_mapping[num] for num in visual_numbers]
        array_indices.sort(reverse=True)
        
        print(f"🗑️ Deleting {box_type} boxes: {sorted(visual_numbers)}")
        
        # Delete from both arrays
        for idx in array_indices:
            display_coords.pop(idx)
            xywh_coords.pop(idx)
        
        return display_coords, xywh_coords


    # === LOOP FOR MULTIPLE EDITS ===
    while True:
        final_annotated = create_annotated_image(display_img, table_coords_display, image_coords_display, 
                                                column_coords_display, header_coords_display, footer_coords_display)
        comparison = np.hstack((display_img, final_annotated))
        cv2_imshow(comparison)

        time.sleep(0.5)

        print("\n" + "=" * 50)
        print("ACTION MENU")
        print("=" * 50)
        
        choice = input(
            "❓ What would you like to do?\n"
            f"  - To edit a table, type 'table 1' to 'table {len(table_coords_display)}'\n"
            f"  - To edit an image, type 'image 1' to 'image {len(image_coords_display)}'\n"
            f"  - To edit a column, type 'column 1' to 'column {len(column_coords_display)}'\n"
            f"  - To edit a header, type 'header 1' to 'header {len(header_coords_display)}'\n"
            f"  - To edit a footer, type 'footer 1' to 'footer {len(footer_coords_display)}'\n"
            f"  - To DELETE multiple boxes, type 'delete table 1,2,5' or 'delete image 1,3', etc. \n"
            "  - To ADD a new box, type 'add table', 'add image', 'add column', 'add header', or 'add footer'\n"
            "  - Type 'done' to approve all and finish.\n\n"
            "Your choice: "
        ).strip().lower()
        
        # === 1. Handle DONE ===
        if choice == "done":
            # ✅ Make sure we save results before breaking
            save_coords(row_id, filename, table_coords_xywh, image_coords_xywh, column_coords_xywh, header_coords_xywh, footer_coords_xywh)
            break

        # === 2. Handle ADD ===
        if choice.startswith("add "):
            _, add_type = choice.split()
            if add_type not in ["table", "image", "column", "header", "footer"]:
                print("❌ Invalid add type. Use 'add table', 'add image', 'add column', 'add header', or 'add footer'.")
                continue

            # Build context
            context_table_boxes = [(box, i) for i, box in enumerate(table_coords_display)]
            context_image_boxes = [(box, i) for i, box in enumerate(image_coords_display)]
            context_column_boxes = [(box, i) for i, box in enumerate(column_coords_display)]
            context_header_boxes = [(box, i) for i, box in enumerate(header_coords_display)]
            context_footer_boxes = [(box, i) for i, box in enumerate(footer_coords_display)]

            context_img = create_context_image(display_img, context_table_boxes, context_image_boxes,
                                     context_column_boxes, context_header_boxes, context_footer_boxes)

            print(f"\n➕ Adding a new {add_type}...")
            corrected_boxes = interactive_editor(context_img, [], f"New {add_type.capitalize()} Editor")

            if corrected_boxes and len(corrected_boxes) > 0:
                for cb in corrected_boxes:
                    if add_type == "table":
                        table_coords_display.append(cb)
                        table_coords_xywh.append([int(v / scale) for v in cb])
                    elif add_type == "image":
                        image_coords_display.append(cb)
                        image_coords_xywh.append([int(v / scale) for v in cb])
                    elif add_type == "column":
                        column_coords_display.append(cb)
                        column_coords_xywh.append([int(v / scale) for v in cb])
                    elif add_type == "header":
                        header_coords_display.append(cb)
                        header_coords_xywh.append([int(v / scale) for v in cb])
                    elif add_type == "footer":
                        footer_coords_display.append(cb)
                        footer_coords_xywh.append([int(v / scale) for v in cb])
                save_coords(row_id, filename, table_coords_xywh, image_coords_xywh, column_coords_xywh, header_coords_xywh, footer_coords_xywh)
            else:
                print("⚠️ No box added.")

            continue

        # === 3. Handle BATCH DELETE ===
        if choice.startswith("delete "):
            try:
                # Parse "delete table 1,2,5" or "delete image 1,3"
                delete_part = choice[7:]  # Remove "delete "
                parts = delete_part.split()
                
                if len(parts) != 2:
                    print("❌ Invalid format. Use 'delete table 1,2,5' or 'delete image 1,3'.")
                    continue
                    
                box_type, numbers_str = parts[0], parts[1]
                if box_type not in ["table", "image", "column", "header", "footer"]:
                    print("❌ Invalid type. Use 'table', 'image', 'column', 'header', or 'footer'.")
                    continue
                    
                # Parse the numbers (handle both "1,2,5" and "1 2 5" formats)
                numbers_str = numbers_str.replace(',', ' ')
                visual_numbers = [int(x) for x in numbers_str.split()]
                
                if not visual_numbers:
                    print("❌ No numbers provided.")
                    continue
                    
                # Perform batch delete
                if box_type == "table":
                    table_coords_display, table_coords_xywh = batch_delete_boxes(
                        box_type, visual_numbers, table_coords_display, table_coords_xywh)
                elif box_type == "image":
                    image_coords_display, image_coords_xywh = batch_delete_boxes(
                        box_type, visual_numbers, image_coords_display, image_coords_xywh)
                elif box_type == "column":
                    column_coords_display, column_coords_xywh = batch_delete_boxes(
                        box_type, visual_numbers, column_coords_display, column_coords_xywh)
                elif box_type == "header":
                    header_coords_display, header_coords_xywh = batch_delete_boxes(
                        box_type, visual_numbers, header_coords_display, header_coords_xywh)
                elif box_type == "footer":
                    footer_coords_display, footer_coords_xywh = batch_delete_boxes(
                        box_type, visual_numbers, footer_coords_display, footer_coords_xywh)
                
                # Save the changes
                save_coords(row_id, filename, table_coords_xywh, image_coords_xywh, 
                          column_coords_xywh, header_coords_xywh, footer_coords_xywh)
                
                print(f"✅ Batch deletion complete!")
                continue
                
            except ValueError:
                print("❌ Invalid number format. Use 'delete table 1,2,5'.")
                continue
            except Exception as e:
                print(f"❌ Error during batch delete: {e}")
                continue
        
        # === 4. Handle EDIT ===
        try:
            if choice in ["table", "image", "column", "header", "footer"]:
                box_type = choice
                
                # Get the appropriate boxes list
                if box_type == "table":
                    current_boxes = table_coords_display
                elif box_type == "image":
                    current_boxes = image_coords_display
                elif box_type == "column":
                    current_boxes = column_coords_display
                elif box_type == "header":
                    current_boxes = header_coords_display
                elif box_type == "footer":
                    current_boxes = footer_coords_display
                    
                # Check if there's only one valid box
                valid_mapping = get_valid_box_mapping(current_boxes)
                if len(valid_mapping) == 0:
                    print(f"❌ No {box_type} boxes exist.")
                    continue
                elif len(valid_mapping) == 1:
                    box_index = valid_mapping[1]  # Get the actual array index
                else:
                    print(f"❌ Multiple {box_type} boxes detected. Please specify '{box_type} N'.")
                    continue
            else:
                parts = choice.split()
                if len(parts) != 2:
                    print("❌ Invalid format. Use 'table 1' or 'image 2'.")
                    continue
                    
                box_type, visual_number = parts[0], int(parts[1])
                if box_type not in ["table", "image", "column", "header", "footer"]:
                    print("❌ Invalid type. Use 'table', 'image', 'column', 'header', or 'footer'.")
                    continue
                    
                # Get the appropriate boxes list and mapping
                if box_type == "table":
                    current_boxes = table_coords_display
                elif box_type == "image":
                    current_boxes = image_coords_display
                elif box_type == "column":
                    current_boxes = column_coords_display
                elif box_type == "header":
                    current_boxes = header_coords_display
                elif box_type == "footer":
                    current_boxes = footer_coords_display
                    
                valid_mapping = get_valid_box_mapping(current_boxes)
                
                if visual_number not in valid_mapping:
                    print(f"❌ {box_type.title()} {visual_number} doesn't exist. Available: {list(valid_mapping.keys())}")
                    continue
                    
                box_index = valid_mapping[visual_number]  # Convert visual number to actual array index
                

            # === TABLE EDITING ===
            if box_type == "table":
                if not (0 <= box_index < len(table_coords_display)):
                    print(f"❌ Table {box_index+1} doesn't exist.")
                    continue

                context_table_boxes = [(box, i) for i, box in enumerate(table_coords_display) if i != box_index]
                context_image_boxes = [(box, i) for i, box in enumerate(image_coords_display)]
                context_img = create_context_image(display_img, context_table_boxes, context_image_boxes)

                print(f"\n✏️ Editing Table {box_index+1}...")
                corrected_boxes = interactive_editor(context_img, [], f"Table {box_index+1} Editor")

                if corrected_boxes and len(corrected_boxes) > 0:
                    # Replace this one entry with multiple
                    new_display_boxes = []
                    new_xywh_boxes = []
                    for cb in corrected_boxes:
                        new_display_boxes.append(cb)
                        new_xywh_boxes.append([int(v / scale) for v in cb])

                    # Remove the old one and extend with new
                    table_coords_display.pop(box_index)
                    table_coords_xywh.pop(box_index)
                    table_coords_display.extend(new_display_boxes)
                    table_coords_xywh.extend(new_xywh_boxes)
                else:
                    # User deleted all boxes
                    table_coords_display[box_index] = [0, 0, 0, 0]
                    table_coords_xywh[box_index] = [0, 0, 0, 0]

                save_coords(row_id, filename, table_coords_xywh, image_coords_xywh, column_coords_xywh, header_coords_xywh, footer_coords_xywh)

            # === IMAGE EDITING ===
            elif box_type == "image":
                if not (0 <= box_index < len(image_coords_display)):
                    print(f"❌ Image {box_index+1} doesn't exist.")
                    continue

                context_table_boxes = [(box, i) for i, box in enumerate(table_coords_display)]
                context_image_boxes = [(box, i) for i, box in enumerate(image_coords_display) if i != box_index]
                context_img = create_context_image(display_img, context_table_boxes, context_image_boxes)

                print(f"\n✏️ Editing Image {box_index+1}...")
                # FIXED: Start with empty canvas like tables do, but show existing box as context
                corrected_boxes = interactive_editor(context_img, [], f"Image {box_index+1} Editor")

                if corrected_boxes and len(corrected_boxes) > 0:
                    new_display_boxes = []
                    new_xywh_boxes = []
                    for cb in corrected_boxes:
                        new_display_boxes.append(cb)
                        new_xywh_boxes.append([int(v / scale) for v in cb])

                    image_coords_display.pop(box_index)
                    image_coords_xywh.pop(box_index)
                    image_coords_display.extend(new_display_boxes)
                    image_coords_xywh.extend(new_xywh_boxes)
                else:
                    # FIXED: Remove the box entirely when no boxes are returned
                    print("✅ Image box removed.")
                    image_coords_display.pop(box_index)
                    image_coords_xywh.pop(box_index)

                save_coords(row_id, filename, table_coords_xywh, image_coords_xywh, column_coords_xywh, header_coords_xywh, footer_coords_xywh)

            # === COLUMN EDITING ===
            elif box_type == "column":
                if not (0 <= box_index < len(column_coords_display)):
                    print(f"❌ Column {box_index+1} doesn't exist.")
                    continue

                context_table_boxes = [(box, i) for i, box in enumerate(table_coords_display)]
                context_image_boxes = [(box, i) for i, box in enumerate(image_coords_display)]
                context_column_boxes = [(box, i) for i, box in enumerate(column_coords_display) if i != box_index]
                context_header_boxes = [(box, i) for i, box in enumerate(header_coords_display)]
                context_footer_boxes = [(box, i) for i, box in enumerate(footer_coords_display)]
                context_img = create_context_image(display_img, context_table_boxes, context_image_boxes,
                                                context_column_boxes, context_header_boxes, context_footer_boxes)

                print(f"\n✏️ Editing Column {box_index+1}...")
                # FIXED: Start with empty canvas
                corrected_boxes = interactive_editor(context_img, [], f"Column {box_index+1} Editor")

                if corrected_boxes and len(corrected_boxes) > 0:
                    new_display_boxes = []
                    new_xywh_boxes = []
                    for cb in corrected_boxes:
                        new_display_boxes.append(cb)
                        new_xywh_boxes.append([int(v / scale) for v in cb])

                    column_coords_display.pop(box_index)
                    column_coords_xywh.pop(box_index)
                    column_coords_display.extend(new_display_boxes)
                    column_coords_xywh.extend(new_xywh_boxes)
                else:
                    # FIXED: Remove the box entirely when no boxes are returned
                    print("✅ Column box removed.")
                    column_coords_display.pop(box_index)
                    column_coords_xywh.pop(box_index)

                save_coords(row_id, filename, table_coords_xywh, image_coords_xywh, column_coords_xywh, header_coords_xywh, footer_coords_xywh)
            
            # === HEADER EDITING ===
            elif box_type == "header":
                if not (0 <= box_index < len(header_coords_display)):
                    print(f"❌ Header {box_index+1} doesn't exist.")
                    continue

                context_table_boxes = [(box, i) for i, box in enumerate(table_coords_display)]
                context_image_boxes = [(box, i) for i, box in enumerate(image_coords_display)]
                context_column_boxes = [(box, i) for i, box in enumerate(column_coords_display)]
                context_header_boxes = [(box, i) for i, box in enumerate(header_coords_display) if i != box_index]
                context_footer_boxes = [(box, i) for i, box in enumerate(footer_coords_display)]
                context_img = create_context_image(display_img, context_table_boxes, context_image_boxes,
                                                context_column_boxes, context_header_boxes, context_footer_boxes)

                print(f"\n✏️ Editing Header {box_index+1}...")
                # FIXED: Start with empty canvas
                corrected_boxes = interactive_editor(context_img, [], f"Header {box_index+1} Editor")

                if corrected_boxes and len(corrected_boxes) > 0:
                    new_display_boxes = []
                    new_xywh_boxes = []
                    for cb in corrected_boxes:
                        new_display_boxes.append(cb)
                        new_xywh_boxes.append([int(v / scale) for v in cb])

                    header_coords_display.pop(box_index)
                    header_coords_xywh.pop(box_index)
                    header_coords_display.extend(new_display_boxes)
                    header_coords_xywh.extend(new_xywh_boxes)
                else:
                    # FIXED: Remove the box entirely when no boxes are returned
                    print("✅ Header box removed.")
                    header_coords_display.pop(box_index)
                    header_coords_xywh.pop(box_index)

                save_coords(row_id, filename, table_coords_xywh, image_coords_xywh, column_coords_xywh, header_coords_xywh, footer_coords_xywh)

            # === FOOTER EDITING ===
            elif box_type == "footer":
                if not (0 <= box_index < len(footer_coords_display)):
                    print(f"❌ Footer {box_index+1} doesn't exist.")
                    continue

                context_table_boxes = [(box, i) for i, box in enumerate(table_coords_display)]
                context_image_boxes = [(box, i) for i, box in enumerate(image_coords_display)]
                context_column_boxes = [(box, i) for i, box in enumerate(column_coords_display)]
                context_header_boxes = [(box, i) for i, box in enumerate(header_coords_display)]
                context_footer_boxes = [(box, i) for i, box in enumerate(footer_coords_display) if i != box_index]
                context_img = create_context_image(display_img, context_table_boxes, context_image_boxes,
                                                context_column_boxes, context_header_boxes, context_footer_boxes)

                print(f"\n✏️ Editing Footer {box_index+1}...")
                # FIXED: Start with empty canvas
                corrected_boxes = interactive_editor(context_img, [], f"Footer {box_index+1} Editor")

                if corrected_boxes and len(corrected_boxes) > 0:
                    new_display_boxes = []
                    new_xywh_boxes = []
                    for cb in corrected_boxes:
                        new_display_boxes.append(cb)
                        new_xywh_boxes.append([int(v / scale) for v in cb])

                    footer_coords_display.pop(box_index)
                    footer_coords_xywh.pop(box_index)
                    footer_coords_display.extend(new_display_boxes)
                    footer_coords_xywh.extend(new_xywh_boxes)
                else:
                    # FIXED: Remove the box entirely when no boxes are returned
                    print("✅ Footer box removed.")
                    footer_coords_display.pop(box_index)
                    footer_coords_xywh.pop(box_index)

                save_coords(row_id, filename, table_coords_xywh, image_coords_xywh, column_coords_xywh, header_coords_xywh, footer_coords_xywh)

        except Exception as e:
            print(f"❌ Error: {e}")

    # === FINAL SAVE ===
    final_annotated_img = create_annotated_image(original_img, table_coords_xywh, image_coords_xywh,
                                                 column_coords_xywh, header_coords_xywh, footer_coords_xywh)
    bounded_path = os.path.join('bounded_images', f"{row_id}.jpg")
    cv2.imwrite(bounded_path, final_annotated_img)

    print("\n" + "=" * 60)
    print(f"✅ STAGE COMPLETE for {filename} — Final annotated image saved to {bounded_path}")
    print("=" * 60)

def stage_2(
    row_id: str,
    box_type: Optional[str] = None,
    box_index: Optional[int] = None,
    custom_coords: Optional[List[int]] = None
):
    """
    Tests and visualizes a specific bounding box region from an original image.

    This function can be used in two ways:
    1.  **By Index:** Provide `row_id`, `box_type` ('tables' or 'images'), and `box_index`.
    2.  **By Custom Coordinates:** Provide `row_id` and `custom_coords` as [ymin, xmin, ymax, xmax].
    """
    print("=" * 60)
    print("STAGE 2: COORDINATE TESTING")
    print("=" * 60)

    # --- 1. Input Validation ---
    if custom_coords is None and not (box_type and box_index is not None):
        print("❌ Error: You must provide either `custom_coords` or both `box_type` and `box_index`.")
        return

    if box_type and box_type not in ['tables', 'images']:
        print(f"❌ Error: `box_type` must be either 'tables' or 'images', not '{box_type}'.")
        return

    # --- 2. Load Data and Image ---
    coords_path = 'coords.json'
    uploads_dir = 'uploads'

    if not os.path.exists(coords_path):
        print(f"❌ Error: '{coords_path}' not found. Please run stage_1() first.")
        return

    with open(coords_path, 'r') as f:
        all_coords = json.load(f)

    if row_id not in all_coords:
        print(f"❌ Error: `row_id` '{row_id}' not found in '{coords_path}'.")
        return

    # Look up the original filename using the row_id
    original_filename = all_coords[row_id].get("original_filename")
    if not original_filename:
        print(f"❌ Error: 'original_filename' not found for '{row_id}' in coords.json.")
        return

    original_image_path = os.path.join(uploads_dir, original_filename)
    if not os.path.exists(original_image_path):
        print(f"❌ Error: Could not find original image at '{original_image_path}'.")
        return

    original_image = cv2.imread(original_image_path)
    if original_image is None:
        print(f"❌ Error: Failed to load image from '{original_image_path}'.")
        return

    # --- 3. Get Coordinates to Test ---
    coords_to_test = None
    if custom_coords:
        print(f"🧪 Testing custom coordinates for '{row_id}'...")
        if len(custom_coords) != 4:
            print("❌ Error: `custom_coords` must be a list of 4 integers: [ymin, xmin, ymax, xmax].")
            return
        coords_to_test = custom_coords
    else:
        print(f"🧪 Testing '{box_type}' at index {box_index} for '{row_id}'...")
        try:
            boxes_list = all_coords[row_id][box_type]
            coords_to_test = boxes_list[box_index]
        except IndexError:
            box_count = len(all_coords[row_id].get(box_type, []))
            print(f"❌ Error: `box_index` {box_index} is out of bounds. There are only {box_count} boxes for '{box_type}'.")
            return
        except KeyError:
             print(f"❌ Error: `box_type` '{box_type}' not found for '{row_id}'.")
             return

    # --- 4. Check for empty/removed boxes ---
    if coords_to_test == [0,0,0,0] or not coords_to_test:
        print("⚠️ Skipping empty/removed box.")
        return

    # --- 5. Crop and Display ---
    if coords_to_test:
        ymin, xmin, ymax, xmax = map(int, coords_to_test)

        # Ensure coordinates are within image bounds
        h, w, _ = original_image.shape
        ymin, xmin = max(0, ymin), max(0, xmin)
        ymax, xmax = min(h, ymax), min(w, xmax)

        if ymin >= ymax or xmin >= xmax:
            print(f"❌ Error: The coordinates {coords_to_test} result in an empty image region.")
            return

        # Create the side-by-side view
        image_with_box = original_image.copy()
        cv2.rectangle(image_with_box, (xmin, ymin), (xmax, ymax), (255, 0, 255), 3) # Bright magenta box

        print(f"\n📸 Side-by-Side Preview (Original vs. Tested Coordinate):")
        cv2_imshow(np.hstack((original_image, image_with_box)))

        # Also show the zoomed-in crop for detail
        cropped_region = original_image[ymin:ymax, xmin:xmax]
        print(f"\n🖼️  Zoomed-in View of Cropped Region:")
        cv2_imshow(cropped_region)
        print("\n✅ STAGE 2 COMPLETE")


def stage_3(
    api_key: Optional[str] = None, 
    custom_system_prompt: Optional[str] = None,
    output_fields: Optional[List[str]] = None,
    exclude_fields: Optional[List[str]] = None,
    model_name: Optional[str] = None,
):
    """
    Processes annotated images through LLM with customizable JSON output.
    """
    print("=" * 60)
    print("STAGE 3: LLM CONTENT EXTRACTION")
    print("=" * 60)

    # --- 1. Determine Final Output Fields ---
    ALL_POSSIBLE_FIELDS = ["Page header", "Page text", "Page footer", "table_bbox", "image_bbox"]
    
    if output_fields is not None:
        fields_to_include = [field for field in output_fields if field in ALL_POSSIBLE_FIELDS]
    else:
        fields_to_include = ALL_POSSIBLE_FIELDS.copy()

    if exclude_fields is not None:
        fields_to_include = [field for field in fields_to_include if field not in exclude_fields]
        print(f"Excluding fields: {exclude_fields}")

    print(f"Final JSON will include: {fields_to_include}")

    # Determine model
    chosen_model = model_name or "gemini-2.0-flash"
    print(f"Using model: {chosen_model}")

    # --- 2. Configure Model API ---
    if not api_key:
        try:
            api_key = getpass("Please enter your Model's API Key: ")
        except Exception as e:
            print(f"Could not read API key: {e}")
            return

    # Create client with new SDK
    try:
        client = genai.Client(api_key=api_key)
        print("API client configured successfully")
    except Exception as e:
        print(f"Error configuring API: {e}")
        return

    # --- 3. Define System Prompt ---
    if custom_system_prompt:
        system_prompt = custom_system_prompt
    else:
        system_prompt = r"""
You are a specialist in Spatial Document Intelligence. Your role is to perform **Layout-Aware Content Extraction** with absolute precision.  

For every document page you process, you must:  
1. Accurately analyze its structure.  
2. Extract *all content* in the correct human-readable order.  
3. Output the result as a **single, valid JSON object** in the exact schema provided.  

Every rule below is **mandatory** unless explicitly marked otherwise. Do not skip, merge, or reinterpret them.

---

### 1. Reading Order (Critical Sequence Rule)
* The definitive extraction order is:  
  1. **Headers (H1, H2 if present)**  
  2. **Columns (C1 → C2 → C3 → C4 …)**  
     - Within each column, capture all text, tables, and images in correct top-to-bottom order.  
  3. **Footers (F1, F2 if present)**  
* **Box numbering (H1, C1, C2, T1, I1, F1, etc.) defines reading sequence.**  
  - Always finish C1 completely before moving to C2.  
  - Insert tables (T#) and images (I#) at their correct vertical positions inside the column where they appear.  
  - Continue this process until all numbered boxes are exhausted.  
* **No interleaving between columns** — each column must be read fully, top → bottom.

---

### 2. Layout Detection
* Identify the layout type: `single_column`, `two_column`, `three_column`, or `four_column`.  
* **CRITICAL:** If text is in distinct vertical blocks side-by-side, it is multi-column.  
* **Blue boxes (C#):** Define column boundaries.  
* **If no blue boxes exist:** Detect columns by:  
  - Vertical whitespace between text blocks  
  - Consistent margins  
  - Continuous vertical flow of text in separate bands  

---

### 3. Headers & Footers
* **Cyan boxes (H#):** Headers.  
* **Magenta boxes (F#):** Footers.  
* Rules:  
  - If no cyan box → `"Page header": ""`.  
  - If no magenta box → `"Page footer": ""`.  
* **Header content:** titles, section IDs, page numbers at top.  
* **Footer content:** page numbers at bottom, journal citations, copyright.  
* Do **not** mix section titles, captions, or references into header/footer.  

---

### 4. Source Citations
* Citations tied to **figures, tables, or specific sections** go in `"Page text"`.  
* Only document-level references (e.g., copyright, global citations) go in `"Page footer"`.  
* Place figure/table citations immediately after the related figure/table.

---

### 5. Images
* **Green boxes (I#):** Image regions.  
* Insert `[image]` placeholder in `"Page text"` where the image belongs.  
* If image has caption → place `[image]` immediately **before** its caption.  
* Number of `[image]` placeholders must equal number of green boxes.  

---

### 6. Tables
* **Red boxes (T#):** Table regions.  
* Must be extracted as valid HTML `<table>`.  
* Include table titles (e.g., "Table 1. …") directly above `<table>`.  
* Structure:  
  - `<thead>` for header rows  
  - `<tbody>` for data rows  
  - Preserve merged cells with `rowspan`/`colspan`  
* Number of `<table>` elements must equal red boxes.  
* Even short columnar lists count as tables.

---

### 7. Mathematical Content
* All math must be in **LaTeX format**.  
* Use `\\[ ... \\]` for block equations, `\\( ... \\)` for inline.  
* Escape every backslash (`\` → `\\`) for JSON safety.  
  - Correct: `"\\(x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}\\)"`  

---

### 8. Content Completeness
* Extract **all visible text**, even faint, marginal, or small notes.  
* Check all page edges (top, bottom, left, right).  
* If truncated, extract what is visible.  
* Do not omit references, footnotes, or small annotations.

---

### 9. Edge Content Rules
* Figure/table sources at bottom margins → `"Page text"`.  
* Document-wide metadata → `"Page footer"`.  
* If an image or table appears between two columns, insert it **after the previous text block of the leftmost column** at that vertical level.  

---

### 10. Visual Cues Summary
* **H# (Cyan):** Headers → `"Page header"`.  
* **C# (Blue):** Columns → `"Page text"` in order (C1 → C2 → C3 → …).  
* **T# (Red):** Tables → HTML `<table>`, inserted inline in `"Page text"`.  
* **I# (Green):** Images → `[image]` placeholders, inserted inline in `"Page text"`.  
* **F# (Magenta):** Footers → `"Page footer"`.  

---

### 11. Extraction Priority
1. Headers (H#)  
2. Columns (C1 → Cn, with inline T# and I#)  
3. Footers (F#)  

---

### 12. JSON Output Requirements
* **Return ONLY JSON.** No explanations, no markdown fences.  

```
{
  "layout_type": "single_column | two_column | three_column | four_column",
  "Page header": "Extracted text from H# boxes (or empty string).",
  "Page text": "Extracted body text from C# boxes, including [image] placeholders, LaTeX equations, and HTML tables, in correct reading order.",
  "Page footer": "Extracted text from F# boxes (or empty string)."
}

```
* **Final Rule:** JSON must be valid. Escape every LaTeX backslash.  

"""
    # --- 4. Load Data ---
    coords_path = 'coords.json'
    bounded_images_dir = 'bounded_images'
    final_outputs_dir = 'final_outputs'
    os.makedirs(final_outputs_dir, exist_ok=True)

    try:
        with open(coords_path, 'r') as f:
            all_coords = json.load(f)
    except FileNotFoundError:
        print(f"Error: '{coords_path}' not found. Please run stage_1() first.")
        return

    bounded_images = sorted([f for f in os.listdir(bounded_images_dir) if f.endswith('.jpg')])
    if not bounded_images:
        print(f"Error: No images found in '{bounded_images_dir}/'. Please run stage_1() first.")
        return

    # --- 5. Main Processing Loop ---
    print(f"\nFound {len(bounded_images)} annotated image(s) to process.")
    not_approved_finals = []

    for img_file in bounded_images:
        row_id = os.path.splitext(img_file)[0]
        print("\n" + "=" * 50 + f"\nProcessing: {img_file}\n" + "=" * 50)

        if row_id not in all_coords:
            print(f"Warning: No coordinates found for '{row_id}'. Skipping.")
            continue

        try:
            img_path = os.path.join(bounded_images_dir, img_file)
            
            # Load image and convert to PIL
            bounded_img = Image.open(img_path)
            
            # Convert to bytes
            img_bytes = BytesIO()
            bounded_img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            
            print("✨ Extracting content...")
            response = client.models.generate_content(
                model=chosen_model,
                contents=[
                    system_prompt,
                    types.Part.from_bytes(
                        data=img_bytes.read(),
                        mime_type='image/jpeg'
                    )
                ]
            )
            
            gem_json_str = response.text.strip()
            
            # Clean markdown fences
            if gem_json_str.startswith("```json"):
                gem_json_str = gem_json_str[7:]
            if gem_json_str.endswith("```"):
                gem_json_str = gem_json_str[:-3]
            gem_json_str = gem_json_str.strip()

            # Fix stray backslashes
            safe_json_str = re.sub(
                r'(?<!\\)\\(?![\\/"bfnrtu])',
                r'\\\\',
                gem_json_str
            )
            
            gem_json = json.loads(safe_json_str)

            # try:
            #     gem_json = json.loads(gem_json_str)
            # except json.JSONDecodeError as e:
            #     print("❌ JSON decode failed:", e)
            #     print("---- Offending string around error ----")
            #     err_pos = e.pos
            #     print(gem_json_str[max(0, err_pos-50): err_pos+50])
            #     raise

            print("✅ Extraction results ready.")

            # Build the final JSON dynamically based on the final list of fields
            final_json = {}
            for field in fields_to_include:
                if field == "Page header":
                    final_json["Page header"] = gem_json.get("Page header", "")
                elif field == "Page text":
                    final_json["Page text"] = gem_json.get("Page text", "").replace("[image]", "📷")
                elif field == "Page footer":
                    final_json["Page footer"] = gem_json.get("Page footer", "")
                elif field == "table_bbox":
                    final_json["table_bbox"] = all_coords[row_id].get("tables", [])
                elif field == "image_bbox":
                    final_json["image_bbox"] = all_coords[row_id].get("images", [])
            
            print("\nFinal JSON for Approval:")
            print("-" * 40)
            print(json.dumps(final_json, indent=2))
            print("-" * 40)

            approval = input("Approve this output? (Enter=Yes, n=No): ").strip().lower()
            if approval == 'n':
                not_approved_finals.append(img_file)
                print("Marked as not approved. Continuing...")
            else:
                output_path = os.path.join(final_outputs_dir, f"{row_id}.json")
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(final_json, f, indent=4, ensure_ascii=False)
                print(f"Approved and saved to: {output_path}")

        except Exception as e:
            print(f"An error occurred while processing {img_file}: {e}")
            import traceback
            traceback.print_exc()
            not_approved_finals.append(img_file)
            continue
            
    # --- 6. Final Summary ---
    print("\n" + "=" * 60 + "\nSTAGE 3 COMPLETE")
    print(f"Total images processed: {len(bounded_images)}")
    approved_count = len(bounded_images) - len(not_approved_finals)
    print(f"  - Approved and saved: {approved_count}")
    print(f"  - Not approved/Failed: {len(not_approved_finals)}")