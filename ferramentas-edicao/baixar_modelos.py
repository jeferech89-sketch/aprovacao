"""Baixa os modelos que não vêm junto com o pip (YuNet) e pré-carrega os do Hugging Face."""
import pathlib, urllib.request

PASTA = pathlib.Path(__file__).parent / "modelos"
PASTA.mkdir(exist_ok=True)

YUNET = PASTA / "face_detection_yunet_2023mar.onnx"
if not YUNET.exists():
    print("Baixando YuNet...")
    try:
        urllib.request.urlretrieve(
            "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
            YUNET,
        )
    except Exception as e:
        print("  Falhou YuNet:", e)

from huggingface_hub import snapshot_download
for repo in [
    "depth-anything/Depth-Anything-V2-Small-hf",  # profundidade
    "laion/clap-htsat-unfused",                   # CLAP
    "PramaLLC/BEN2",                              # remoção de fundo
    "facebook/sam2.1-hiera-small",                # SAM 2
]:
    print("Baixando", repo, "...")
    try:
        snapshot_download(repo)
    except Exception as e:
        print("  Falhou", repo, ":", e)
print("Modelos prontos em", PASTA, "e no cache do Hugging Face.")
