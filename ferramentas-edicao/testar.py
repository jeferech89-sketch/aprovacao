"""Confere se todas as ferramentas foram instaladas."""
import importlib, shutil, subprocess

ok = True
def checar(nome, fn):
    global ok
    try:
        info = fn()
        print(f"[OK]    {nome} {info or ''}")
    except Exception as e:
        ok = False
        print(f"[FALHA] {nome}: {e}")

def mod(m, attr="__version__"):
    return lambda: getattr(importlib.import_module(m), attr, "")

def ffmpeg():
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg não está no PATH")
    return subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True).stdout.split("\n")[0]

def yunet():
    import cv2
    assert hasattr(cv2, "FaceDetectorYN"), "OpenCV sem FaceDetectorYN"
    return cv2.__version__

def hyperframes():
    exe = shutil.which("hyperframes") or shutil.which("npx")
    if not exe:
        raise RuntimeError("Node/npm não encontrado")
    return "(via npx hyperframes)" if exe.endswith(("npx", "npx.cmd")) else exe

def torch_info():
    import torch
    return f"{torch.__version__} | GPU: {'sim - ' + torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'não (CPU)'}"

checar("PyTorch", torch_info)
checar("01 WhisperX", mod("whisperx", "__name__"))
checar("02 FFmpeg", ffmpeg)
checar("03 YuNet (OpenCV)", yunet)
checar("04 MediaPipe", mod("mediapipe"))
checar("05 BEN2", mod("ben2", "__name__"))
checar("06 HyperFrames", hyperframes)
checar("07 Depth Anything (transformers)", lambda: __import__("transformers").DepthAnythingForDepthEstimation and "ok")
checar("Bônus CLAP (transformers)", lambda: __import__("transformers").ClapModel and "ok")
checar("Bônus SAM 2", mod("sam2", "__name__"))
checar("Bônus Demucs", mod("demucs"))
checar("Bônus PySceneDetect", mod("scenedetect"))
print("\nTudo certo!" if ok else "\nAlgo falhou — veja as linhas [FALHA] acima.")
