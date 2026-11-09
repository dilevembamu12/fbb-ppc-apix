# ---------------------------------------------------------------------------
# Construit l'archive de livraison envoyee aux dirigeants de PPC.
#
#   powershell -ExecutionPolicy Bypass -File outils\build_livraison.ps1
#
# Trois pieces, renommees pour etre lues dans l'ordre :
#   1 le document des interfaces (dist\docs)
#   2 la presentation de reunion   (dist\pptx)
#   3 le film de cadrage           (dist\video)
#
# La note de lecture LISEZ-MOI.txt est versionnee ; elle est copiee telle
# quelle dans l'archive.
#
# Ce fichier est volontairement en ASCII : PowerShell 5.1 lit les .ps1 sans BOM
# en ANSI et abimerait les accents. Les accents sont dans LISEZ-MOI.txt, qui est
# en UTF-8 avec BOM et s'ouvre correctement dans le Bloc-notes.
# ---------------------------------------------------------------------------

$ErrorActionPreference = 'Stop'

$racine  = Split-Path $PSScriptRoot -Parent
$sortie  = Join-Path $racine 'dist\livraison'
$zip     = Join-Path $sortie 'APIX-dossier-PPC.zip'
$note    = Join-Path $sortie 'LISEZ-MOI.txt'

if (-not (Test-Path $note)) {
    throw "Note de lecture introuvable : $note"
}

# --- le film : la version retravaillee a la main ---------------------------
# C'est le montage final, pas le rendu brut d'HyperFrames. Il vit dans
# dist\video et il est volontairement hors versionnement (47 Mo).
$film = Join-Path $racine 'dist\video\APIX-Cinq-canaux.mp4'
if (-not (Test-Path $film)) {
    throw "Film introuvable : $film"
}

$pieces = @(
    @{ Source = (Join-Path $racine 'dist\docs\05-Presentation-MVP-interfaces.docx'); Nom = '1-APIX-Presentation-MVP-et-interfaces.docx' }
    @{ Source = (Join-Path $racine 'dist\pptx\APIX-All-In-One-12-slides-PPC.pptx');   Nom = '2-APIX-All-In-One-Presentation-PPC.pptx' }
    @{ Source = $film;                                                               Nom = '3-APIX-Cinq-canaux.mp4' }
)

foreach ($piece in $pieces) {
    if (-not (Test-Path $piece.Source)) { throw "Piece manquante : $($piece.Source)" }
}

# --- atelier temporaire ------------------------------------------------------
$atelier = Join-Path $env:TEMP ('livraison-apix-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
New-Item -ItemType Directory -Path $atelier -Force | Out-Null

try {
    foreach ($piece in $pieces) {
        Copy-Item $piece.Source (Join-Path $atelier $piece.Nom) -Force
    }
    Copy-Item $note (Join-Path $atelier 'LISEZ-MOI.txt') -Force

    $temporaire = Join-Path $env:TEMP ('apix-' + [guid]::NewGuid().ToString('N').Substring(0, 8) + '.zip')
    Compress-Archive -Path (Join-Path $atelier '*') -DestinationPath $temporaire -CompressionLevel Optimal

    if (-not (Test-Path $sortie)) { New-Item -ItemType Directory -Path $sortie -Force | Out-Null }
    if (Test-Path $zip) { Remove-Item $zip -Force }
    Move-Item $temporaire $zip -Force

    $poids = [math]::Round((Get-Item $zip).Length / 1MB, 2)
    Write-Host "Archive : $zip"
    Write-Host "Poids   : $poids Mo"
    foreach ($piece in $pieces) {
        $taille = [math]::Round((Get-Item (Join-Path $atelier $piece.Nom)).Length / 1MB, 2)
        Write-Host ("  {0,-46} {1,6} Mo" -f $piece.Nom, $taille)
    }
    Write-Host '  LISEZ-MOI.txt                                  note de lecture'
}
finally {
    Remove-Item $atelier -Recurse -Force -ErrorAction SilentlyContinue
}
