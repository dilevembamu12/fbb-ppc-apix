# ---------------------------------------------------------------------------
# Lance le MVP APIX en local, base remise a zero.
#
#   powershell -ExecutionPolicy Bypass -File mvp\lancer.ps1
#   powershell -ExecutionPolicy Bypass -File mvp\lancer.ps1 -Port 9000 -ConserverBase
#
# Sans -ConserverBase, la base de demonstration est effacee a chaque demarrage :
# c'est ce qu'on veut avant une repetition, pour repartir d'un etat propre.
#
# Ce fichier est en ASCII volontairement (PowerShell 5.1 lit les .ps1 sans BOM
# en ANSI et abimerait les accents).
# ---------------------------------------------------------------------------

param(
    [int]$Port = 8765,
    [switch]$ConserverBase
)

$ErrorActionPreference = 'Stop'
$racine = Split-Path $PSScriptRoot -Parent
$serveur = Join-Path $racine 'mvp\serveur.py'

if (-not (Test-Path $serveur)) {
    throw "Serveur introuvable : $serveur"
}

$arguments = @($serveur, '--port', $Port)
if (-not $ConserverBase) { $arguments += '--reinitialiser' }

$etatBase = 'remise a zero'
if ($ConserverBase) { $etatBase = 'conservee' }

Write-Host "MVP APIX" -ForegroundColor Cyan
Write-Host "  adresse : http://127.0.0.1:$Port"
Write-Host "  base    : $etatBase"
Write-Host "  arret   : Ctrl+C"
Write-Host ""

$env:PYTHONIOENCODING = 'utf-8'
& python @arguments
