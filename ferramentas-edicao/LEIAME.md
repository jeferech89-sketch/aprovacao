# Ferramentas de IA para edição de vídeo

Instala de uma vez as 7 ferramentas + 4 bônus:

| # | Ferramenta | Para que serve |
|---|---|---|
| 01 | WhisperX | Transcrição com tempo de cada palavra (legendas) |
| 02 | FFmpeg | Converter, cortar, juntar vídeo e áudio |
| 03 | YuNet | Detecta rostos (reenquadrar para vertical) |
| 04 | MediaPipe | Rosto, mãos e corpo |
| 05 | BEN2 | Separa a pessoa do fundo |
| 06 | HyperFrames | Animações feitas em HTML → MP4 |
| 07 | Depth Anything V2 | Mapa de profundidade (efeito 3D/parallax) |
| ★ | CLAP | Categoriza áudio (achar SFX/músicas por descrição) |
| ★ | SAM 2 | Recorta qualquer objeto e segue no vídeo |
| ★ | Demucs | Separa voz, música e ruído |
| ★ | PySceneDetect | Detecta os cortes de cena |

## Como instalar

**Windows** (PowerShell, dentro desta pasta):
```powershell
Set-ExecutionPolicy -Scope Process Bypass; .\instalar-windows.ps1
```

**Mac / Linux:**
```bash
bash instalar-mac-linux.sh
```

O script instala Python 3.11, FFmpeg, Node.js e Git, cria um ambiente isolado (`.venv`),
instala o PyTorch (com GPU NVIDIA se tiver), as ferramentas, baixa os modelos e roda `testar.py`.
Precisa de ~10 GB livres. Com placa NVIDIA tudo fica muito mais rápido.

## Exemplos rápidos

```bash
# ativar o ambiente antes (Windows: .\.venv\Scripts\Activate.ps1)
source .venv/bin/activate

whisperx video.mp4 --language pt --output_format srt              # legenda .srt
demucs --two-stems=vocals video.mp4                                # voz isolada
scenedetect -i video.mp4 detect-adaptive list-scenes split-video   # corta por cena
ffmpeg -i entrada.mov -c:v libx264 -crf 18 saida.mp4               # converter
npx hyperframes init minha-animacao                                # projeto de animação
```
