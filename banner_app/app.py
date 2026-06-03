#!/usr/bin/env python3
import io
import sys
import base64
from flask import Flask, render_template, request, send_file, jsonify

sys.path.insert(0, "..")
from banner_generator import generate_banner, SPEED_PRESETS

app = Flask(__name__)


def hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()

    text       = data.get("text", "SALES").strip() or "SALES"
    speed_raw  = data.get("speed", "normal").strip()
    width      = int(data.get("width", 600))
    height     = int(data.get("height", 40))
    font_size  = int(data.get("font_size", 28))
    frames     = int(data.get("frames", 60))
    text_color = hex_to_rgb(data.get("text_color", "#ffffff"))
    bg_color   = hex_to_rgb(data.get("bg_color", "#000000"))

    if speed_raw in SPEED_PRESETS:
        speed_ms = SPEED_PRESETS[speed_raw]
    else:
        try:
            speed_ms = max(1, int(speed_raw))
        except ValueError:
            speed_ms = 40

    font_name  = data.get("font", "arial").strip().lower()

    buf = io.BytesIO()

    from PIL import Image, ImageDraw, ImageFont
    import os

    _BASE = os.path.dirname(__file__)

    FONT_MAP = {
        "arial":      ["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                       "/System/Library/Fonts/Supplemental/Arial.ttf"],
        "montserrat": [os.path.join(_BASE, "fonts", "Montserrat-Bold.ttf")],
        "roboto":     [os.path.join(_BASE, "fonts", "Roboto-Bold.ttf")],
        "comic_sans": ["/System/Library/Fonts/Supplemental/Comic Sans MS Bold.ttf",
                       "/System/Library/Fonts/Supplemental/Comic Sans MS.ttf"],
        "impact":     ["/System/Library/Fonts/Supplemental/Impact.ttf"],
        "georgia":    ["/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
                       "/System/Library/Fonts/Supplemental/Georgia.ttf"],
    }

    font = None
    for path in FONT_MAP.get(font_name, FONT_MAP["arial"]):
        try:
            font = ImageFont.truetype(path, font_size)
            break
        except (IOError, OSError):
            continue
    if font is None:
        font = ImageFont.load_default()

    gap        = int(data.get("gap", 60))

    dummy = Image.new("RGB", (1, 1))
    draw  = ImageDraw.Draw(dummy)
    bbox  = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_y = (height - text_h) // 2 - bbox[1]

    # step = largura de uma repetição (texto + espaço)
    step = text_w + gap
    gif_frames = []

    for i in range(frames):
        # offset avança 1 step completo ao longo dos frames (loop perfeito)
        offset = int(i / frames * step)
        img = Image.new("RGB", (width, height), bg_color)
        d   = ImageDraw.Draw(img)
        # desenha cópias suficientes para cobrir toda a largura
        x = -offset
        while x < width:
            d.text((x, text_y), text, font=font, fill=text_color)
            x += step
        gif_frames.append(img.convert("P", palette=Image.ADAPTIVE))

    gif_frames[0].save(
        buf,
        format="GIF",
        save_all=True,
        append_images=gif_frames[1:],
        loop=0,
        duration=speed_ms,
        optimize=False,
    )
    buf.seek(0)
    gif_b64 = base64.b64encode(buf.getvalue()).decode()

    filename = text.lower().replace(" ", "_") + "_banner.gif"
    return jsonify({"gif": gif_b64, "filename": filename})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
