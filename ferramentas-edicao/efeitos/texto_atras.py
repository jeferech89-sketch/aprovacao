"""
EFEITO: TEXTO ATRÁS DA PESSOA
Recorta a pessoa com o BEN2 e coloca um título grande entre o fundo e ela.

Uso básico:
    python efeitos/texto_atras.py video.mp4 --texto "ZUMBIDO"

Opções úteis:
    --cor "#00FF88"        cor do texto (padrão branco)
    --fonte caminho.ttf    fonte do cliente (.ttf ou .otf)
    --altura 0.30          posição vertical do centro do texto (0 = topo, 1 = base)
    --largura 0.92         largura máxima do texto em relação ao vídeo
    --inicio 0.5 --fim 4   quando o texto aparece/some (segundos)
    --animacao zoom        zoom | subir | nenhuma
    --saida final.mp4      nome do arquivo final

O recorte da pessoa fica salvo numa pasta "<video>_mascaras". Rodar de novo com
outro texto, cor ou posição reaproveita o recorte e fica bem mais rápido.
"""
import argparse, os, pathlib, shutil, subprocess, sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONTES_PADRAO = [
    "/System/Library/Fonts/Supplemental/Arial Black.ttf",
    "/System/Library/Fonts/Supplemental/Impact.ttf",
    "/Library/Fonts/Arial Black.ttf",
    "C:/Windows/Fonts/ariblk.ttf",
    "C:/Windows/Fonts/impact.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


# ---------------------------------------------------------------- recorte (BEN2)
def carregar_ben2():
    import torch
    from ben2 import BEN_Base

    if torch.backends.mps.is_available():
        disp = "mps"          # chip Apple
    elif torch.cuda.is_available():
        disp = "cuda"         # placa NVIDIA
    else:
        disp = "cpu"
    print(f"Carregando BEN2 ({disp})...")
    modelo = BEN_Base.from_pretrained("PramaLLC/BEN2").to(disp).eval()
    return modelo


def mascara_ben2(modelo, frame_bgr):
    rgb = Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
    recorte = modelo.inference(rgb)              # RGBA, alfa = pessoa
    return np.array(recorte.getchannel("A"))


def gerar_mascaras(video, pasta, total, funcao_mascara=None):
    """Salva uma máscara PNG por quadro. Pula as que já existem."""
    pasta.mkdir(exist_ok=True)
    faltando = [i for i in range(total) if not (pasta / f"{i:06d}.png").exists()]
    if not faltando:
        print("Recorte da pessoa já existe, reaproveitando.")
        return
    if funcao_mascara is None:
        modelo = carregar_ben2()
        funcao_mascara = lambda f: mascara_ben2(modelo, f)
    cap = cv2.VideoCapture(str(video))
    faltando = set(faltando)
    i = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if i in faltando:
            cv2.imwrite(str(pasta / f"{i:06d}.png"), funcao_mascara(frame))
            print(f"\rRecortando pessoa: {i + 1}/{total}", end="", flush=True)
        i += 1
    cap.release()
    print()


# ---------------------------------------------------------------- texto
def achar_fonte(caminho):
    if caminho:
        if not os.path.exists(caminho):
            sys.exit(f"Fonte não encontrada: {caminho}")
        return caminho
    for f in FONTES_PADRAO:
        if os.path.exists(f):
            return f
    return None


def cor_rgba(hexa):
    hexa = hexa.lstrip("#")
    r, g, b = (int(hexa[i:i + 2], 16) for i in (0, 2, 4))
    return (r, g, b, 255)


def desenhar_texto(texto, fonte_path, largura_max, cor):
    """Gera o texto em RGBA, no maior tamanho que cabe em largura_max."""
    linhas = texto.split("\\n") if "\\n" in texto else texto.split("\n")
    tam = 400
    while True:
        fonte = (ImageFont.truetype(fonte_path, tam) if fonte_path
                 else ImageFont.load_default(tam))
        caixas = [fonte.getbbox(l) for l in linhas]
        larg = max(b[2] - b[0] for b in caixas)
        if larg <= largura_max or tam <= 20:
            break
        tam = int(tam * 0.95)
    alt_linha = int(tam * 1.0)
    img = Image.new("RGBA", (larg + 40, alt_linha * len(linhas) + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for n, (l, b) in enumerate(zip(linhas, caixas)):
        x = (img.width - (b[2] - b[0])) // 2 - b[0]
        d.text((x, 20 + n * alt_linha - b[1] + (alt_linha - (b[3] - b[1])) // 2),
               l, font=fonte, fill=cor)
    return img


def suavizar(t):
    return 1 - (1 - t) ** 3


def camada_texto(base, w, h, t, args):
    """Texto posicionado e animado no tempo t (segundos), em RGBA do tamanho do vídeo."""
    camada = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if t < args.inicio or (args.fim is not None and t > args.fim):
        return camada
    dur = 0.6
    p = suavizar(min(1.0, (t - args.inicio) / dur))
    saida = 1.0
    if args.fim is not None and t > args.fim - 0.3:
        saida = max(0.0, (args.fim - t) / 0.3)

    img, dy = base, 0
    if args.animacao == "zoom":
        esc = 1.25 - 0.25 * p
        img = base.resize((max(1, int(base.width * esc)), max(1, int(base.height * esc))),
                          Image.LANCZOS)
    elif args.animacao == "subir":
        dy = int((1 - p) * h * 0.08)
    opac = (p if args.animacao != "nenhuma" else 1.0) * saida
    if opac < 1:
        a = img.getchannel("A").point(lambda v: int(v * opac))
        img = img.copy()
        img.putalpha(a)
    x = (w - img.width) // 2
    y = int(h * args.altura - img.height / 2) + dy
    camada.paste(img, (x, y), img)
    return camada


# ---------------------------------------------------------------- montagem
def montar(args, funcao_mascara=None):
    video = pathlib.Path(args.video).expanduser().resolve()
    if not video.exists():
        sys.exit(f"Vídeo não encontrado: {video}")
    saida = pathlib.Path(args.saida).expanduser() if args.saida else \
        video.with_name(video.stem + "_texto_atras.mp4")
    pasta_masc = video.with_name(video.stem + "_mascaras")

    cap = cv2.VideoCapture(str(video))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    ok, primeiro = cap.read()
    cap.release()
    if not ok:
        sys.exit("Não consegui ler o vídeo.")
    h, w = primeiro.shape[:2]
    print(f"Vídeo {w}x{h}, {fps:.2f} fps, {total} quadros")

    gerar_mascaras(video, pasta_masc, total, funcao_mascara)

    base = desenhar_texto(args.texto, achar_fonte(args.fonte), int(w * args.largura),
                          cor_rgba(args.cor))

    ffmpeg = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}", "-r", f"{fps}", "-i", "-",
         "-i", str(video), "-map", "0:v", "-map", "1:a?",
         "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(saida)],
        stdin=subprocess.PIPE)

    cap = cv2.VideoCapture(str(video))
    i = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        t = i / fps
        texto = np.array(camada_texto(base, w, h, t, args)).astype(np.float32) / 255
        mpath = pasta_masc / f"{i:06d}.png"
        masc = cv2.imread(str(mpath), cv2.IMREAD_GRAYSCALE) if mpath.exists() else None
        if masc is None:
            masc = np.zeros((h, w), np.uint8)
        if masc.shape != (h, w):
            masc = cv2.resize(masc, (w, h))
        pessoa = (masc.astype(np.float32) / 255)[..., None]

        f = frame.astype(np.float32)
        a_txt = texto[..., 3:4]
        txt_bgr = texto[..., 2::-1] * 255
        fundo_com_texto = f * (1 - a_txt) + txt_bgr * a_txt     # texto por cima do fundo
        final = fundo_com_texto * (1 - pessoa) + f * pessoa     # pessoa por cima do texto
        ffmpeg.stdin.write(final.clip(0, 255).astype(np.uint8).tobytes())
        i += 1
        if i % 30 == 0 or i == total:
            print(f"\rMontando vídeo: {i}/{total}", end="", flush=True)
    cap.release()
    ffmpeg.stdin.close()
    ffmpeg.wait()
    print(f"\nPronto: {saida}")
    return saida


def argumentos(lista=None):
    p = argparse.ArgumentParser(description="Texto atrás da pessoa (BEN2)")
    p.add_argument("video")
    p.add_argument("--texto", required=True, help='use \\n para quebrar linha')
    p.add_argument("--cor", default="#FFFFFF")
    p.add_argument("--fonte")
    p.add_argument("--altura", type=float, default=0.30)
    p.add_argument("--largura", type=float, default=0.92)
    p.add_argument("--inicio", type=float, default=0.0)
    p.add_argument("--fim", type=float)
    p.add_argument("--animacao", choices=["zoom", "subir", "nenhuma"], default="zoom")
    p.add_argument("--saida")
    return p.parse_args(lista)


if __name__ == "__main__":
    if not shutil.which("ffmpeg"):
        sys.exit("FFmpeg não encontrado.")
    montar(argumentos())
