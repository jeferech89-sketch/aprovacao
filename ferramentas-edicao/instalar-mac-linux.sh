#!/usr/bin/env bash
# Instala as ferramentas de IA para edição de vídeo no macOS ou Linux.
# Uso:  bash instalar-mac-linux.sh
set -euo pipefail
cd "$(dirname "$0")"

echo "== 1/5 Programas base (Python, FFmpeg, Node.js, Git) =="
if [[ "$(uname)" == "Darwin" ]]; then
  for b in /opt/homebrew/bin/brew /usr/local/bin/brew; do [[ -x $b ]] && eval "$($b shellenv)"; done
  if ! command -v brew >/dev/null; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    for b in /opt/homebrew/bin/brew /usr/local/bin/brew; do [[ -x $b ]] && eval "$($b shellenv)"; done
  fi
  brew install python@3.11 ffmpeg node git
  PY=python3.11
else
  sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip ffmpeg git nodejs npm
  PY=python3
fi

echo "== 2/5 Ambiente Python isolado (.venv) =="
$PY -m venv .venv
. .venv/bin/activate
pip install --upgrade pip wheel

echo "== 3/5 PyTorch =="
if command -v nvidia-smi >/dev/null; then
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
elif [[ "$(uname)" == "Darwin" ]]; then
  pip install torch torchvision torchaudio            # usa a GPU do Mac (MPS) automaticamente
else
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
fi

echo "== 4/5 Ferramentas de IA =="
pip install -r requirements.txt
npm install -g hyperframes 2>/dev/null || sudo npm install -g hyperframes

echo "== 5/5 Modelos + teste =="
python baixar_modelos.py
python testar.py
echo; echo "Para usar depois:  source $(pwd)/.venv/bin/activate"
