#!/usr/bin/env python3
"""
Banner GIF Generator
Gera um banner animado com texto scrollando da esquerda para a direita.
"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Erro: Pillow não instalado. Execute: pip install Pillow")
    sys.exit(1)

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "C:/Windows/Fonts/arialbd.ttf",
]

SPEED_PRESETS = {
    "lento": 80,
    "normal": 40,
    "rapido": 20,
    "muito_rapido": 10,
}


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()


def generate_banner(
    text: str,
    output: str,
    width: int = 600,
    height: int = 40,
    font_size: int = 28,
    speed: int = 40,
    text_color: tuple = (255, 255, 255),
    bg_color: tuple = (0, 0, 0),
    num_frames: int = 60,
) -> None:
    font = load_font(font_size)

    dummy = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_y = (height - text_h) // 2 - bbox[1]

    total_travel = width + text_w
    frames = []

    for i in range(num_frames):
        x = width - int(i / (num_frames - 1) * total_travel)
        img = Image.new("RGB", (width, height), bg_color)
        d = ImageDraw.Draw(img)
        d.text((x, text_y), text, font=font, fill=text_color)
        frames.append(img.convert("P", palette=Image.ADAPTIVE))

    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=speed,
        optimize=False,
    )
    print(f"✓ Banner gerado: {output}")
    print(f"  Texto     : {text}")
    print(f"  Tamanho   : {width}x{height}px")
    print(f"  Velocidade: {speed}ms por frame")
    print(f"  Frames    : {num_frames}")


def parse_color(value: str) -> tuple:
    """Aceita 'R,G,B' ou nome simples como 'white', 'red', 'yellow'."""
    named = {
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "yellow": (255, 255, 0),
        "cyan": (0, 255, 255),
        "magenta": (255, 0, 255),
        "orange": (255, 165, 0),
    }
    v = value.lower().strip()
    if v in named:
        return named[v]
    try:
        parts = [int(x) for x in v.split(",")]
        if len(parts) == 3:
            return tuple(parts)
    except ValueError:
        pass
    raise argparse.ArgumentTypeError(
        f"Cor inválida '{value}'. Use nome (white, red...) ou R,G,B (ex: 255,0,0)"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Gera um banner GIF animado com texto scrollando.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "-t", "--texto",
        default="SALES",
        help="Texto a exibir no banner (padrão: SALES)",
    )
    parser.add_argument(
        "-v", "--velocidade",
        default="normal",
        help=(
            "Velocidade do scroll. Pode ser:\n"
            "  lento, normal, rapido, muito_rapido\n"
            "  ou um número em ms por frame (ex: 30)\n"
            "(padrão: normal = 40ms)"
        ),
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Nome do arquivo de saída (padrão: <texto>_banner.gif)",
    )
    parser.add_argument(
        "--largura", type=int, default=600,
        help="Largura do banner em pixels (padrão: 600)",
    )
    parser.add_argument(
        "--altura", type=int, default=40,
        help="Altura do banner em pixels (padrão: 40)",
    )
    parser.add_argument(
        "--fonte", type=int, default=28,
        help="Tamanho da fonte em pixels (padrão: 28)",
    )
    parser.add_argument(
        "--frames", type=int, default=60,
        help="Número de frames da animação (padrão: 60)",
    )
    parser.add_argument(
        "--cor-texto", type=parse_color, default="white",
        dest="cor_texto",
        help="Cor do texto: nome ou R,G,B (padrão: white)",
    )
    parser.add_argument(
        "--cor-fundo", type=parse_color, default="black",
        dest="cor_fundo",
        help="Cor de fundo: nome ou R,G,B (padrão: black)",
    )

    args = parser.parse_args()

    # Resolve velocidade
    v = args.velocidade.lower().strip()
    if v in SPEED_PRESETS:
        speed_ms = SPEED_PRESETS[v]
    else:
        try:
            speed_ms = int(v)
            if speed_ms < 1:
                raise ValueError
        except ValueError:
            parser.error(
                f"Velocidade inválida '{args.velocidade}'. "
                "Use: lento, normal, rapido, muito_rapido ou um número em ms."
            )

    # Nome do output
    output = args.output or f"{args.texto.lower().replace(' ', '_')}_banner.gif"

    generate_banner(
        text=args.texto,
        output=output,
        width=args.largura,
        height=args.altura,
        font_size=args.fonte,
        speed=speed_ms,
        text_color=args.cor_texto,
        bg_color=args.cor_fundo,
        num_frames=args.frames,
    )


if __name__ == "__main__":
    main()
