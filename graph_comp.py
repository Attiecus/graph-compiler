"""
Image Panel Combiner - Streamlit App
=====================================
pip install streamlit Pillow
streamlit run combine_images_app.py
"""

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import math
import io

st.set_page_config(page_title="Image Panel Combiner", layout="wide")
st.title("🖼️ Image Panel Combiner")
st.caption("Upload images and combine them into a single figure panel for your thesis.")

uploaded = st.file_uploader("Upload images", type=["png", "jpg", "jpeg", "tiff", "bmp", "webp"],
                            accept_multiple_files=True)

if uploaded:
    images = [Image.open(f).convert("RGBA") for f in uploaded]
    n = len(images)

    st.subheader("Preview uploads")
    preview_cols = st.columns(min(n, 6))
    for i, img in enumerate(images):
        preview_cols[i % len(preview_cols)].image(img, caption=uploaded[i].name, use_container_width=True)

    st.divider()
    st.subheader("Settings")

    c1, c2, c3 = st.columns(3)
    cols = c1.number_input("Columns", 1, n, min(n, math.ceil(math.sqrt(n))))
    padding = c2.number_input("Padding (px)", 0, 100, 10)
    label_size = c3.number_input("Label font size", 10, 72, 28)

    c4, c5, c6 = st.columns(3)
    bg = c4.color_picker("Background colour", "#ffffff")
    add_labels = c5.checkbox("Add labels (A, B, C…)", value=True)
    stretch = c6.checkbox("Stretch to fill (instead of fit)")

    if st.button("🔨 Combine", type="primary"):
        rows = math.ceil(n / cols)

        widths = sorted(img.width for img in images)
        heights = sorted(img.height for img in images)
        tw = widths[len(widths) // 2]
        th = heights[len(heights) // 2]

        resized = []
        for img in images:
            if stretch:
                resized.append(img.resize((tw, th), Image.LANCZOS))
            else:
                copy = img.copy()
                copy.thumbnail((tw, th), Image.LANCZOS)
                canvas = Image.new("RGBA", (tw, th), bg)
                x = (tw - copy.width) // 2
                y = (th - copy.height) // 2
                canvas.paste(copy, (x, y), copy)
                resized.append(canvas)

        labels = [chr(65 + i) for i in range(n)] if add_labels else []
        label_space = (label_size + 8) if labels else 0
        cell_w = tw + padding
        cell_h = th + padding + label_space
        total_w = cols * cell_w + padding
        total_h = rows * cell_h + padding

        panel = Image.new("RGBA", (total_w, total_h), bg)
        draw = ImageDraw.Draw(panel)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", label_size)
        except OSError:
            font = ImageFont.load_default()

        for i, img in enumerate(resized):
            row, col = divmod(i, cols)
            x = padding + col * cell_w
            y = padding + row * cell_h
            if labels and i < len(labels):
                draw.text((x, y), labels[i], fill="black", font=font)
            panel.paste(img, (x, y + label_space), img)

        panel = panel.convert("RGB")

        st.subheader("Result")
        st.image(panel, use_container_width=True)

        buf = io.BytesIO()
        panel.save(buf, format="PNG", dpi=(300, 300))
        st.download_button("⬇️ Download Panel (300 DPI)", buf.getvalue(),
                           file_name="panel.png", mime="image/png")
else:
    st.info("Upload two or more images to get started.")