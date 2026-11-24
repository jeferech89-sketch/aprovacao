# Instala as ferramentas de IA para edição de vídeo no Windows.
# Rode no PowerShell, dentro desta pasta:
#   Set-ExecutionPolicy -Scope Process Bypass; .\instalar-windows.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "== 1/5 Programas base (Python 3.11, FFmpeg, Node.js, Git) ==" -ForegroundColor Green
winget install -e --id Python.Python.3.11 --accept-source-agreements --accept-package-agreements
winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
winget install -e --id OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements
winget install -e --id Git.Git --accept-source-agreements --accept-package-agreements
# Atualiza o PATH nesta janela para enxergar o que acabou de ser instalado
$env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")

Write-Host "== 2/5 Ambiente Python isolado (.venv) ==" -ForegroundColor Green
py -3.11 -m venv .venv
$py = ".\.venv\Scripts\python.exe"
& $py -m pip install --upgrade pip wheel

Write-Host "== 3/5 PyTorch (GPU NVIDIA se houver, senão CPU) ==" -ForegroundColor Green
if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    & $py -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
} else {
    & $py -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
}

Write-Host "== 4/5 Ferramentas de IA ==" -ForegroundColor Green
& $py -m pip install -r requirements.txt
npm install -g hyperframes

Write-Host "== 5/5 Modelos + teste ==" -ForegroundColor Green
& $py baixar_modelos.py
& $py testar.py
Write-Host "`nPara usar depois: .\.venv\Scripts\Activate.ps1" -ForegroundColor Cyan
