# Script para autofirmar el ejecutivo y reducir alertas de antivirus
# Creado por: Dev White (Hector Zambrano)
# Requiere Windows SDK para 'signtool.exe'

# Forzar el directorio de trabajo al de la ubicación del script
Set-Location $PSScriptRoot

$exePath = "dist\WebtoonDownloaderGUI.exe"
$certName = "WebtoonDownloaderCert"

# 0. Verificar y auto-lanzar como Administrador si es necesario
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Lanzando script como administrador..." -ForegroundColor Yellow
    Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

if (-not (Test-Path $exePath)) {
    Write-Host "No se encontró el archivo EXE en 'dist\'." -ForegroundColor Yellow
    $choice = Read-Host "¿Deseas ejecutar la compilación ahora? (S/N)"
    if ($choice -eq "S" -or $choice -eq "s") {
        Write-Host "Iniciando compilación..." -ForegroundColor Cyan
        if (Test-Path ".\.venv\Scripts\python.exe") {
            & ".\.venv\Scripts\python.exe" build.py
        } else {
            python build.py
        }
        
        if (-not (Test-Path $exePath)) {
            Write-Host "ERROR: La compilación falló o no generó el archivo esperado." -ForegroundColor Red
            Read-Host "Presiona Enter para salir"
            exit
        }
    } else {
        Write-Host "Por favor, ejecuta la compilación primero (python build.py)." -ForegroundColor White
        Read-Host "Presiona Enter para salir"
        exit
    }
}

# 1. Limpiar y buscar Certificado Autofirmado
$oldCerts = Get-ChildItem Cert:\CurrentUser\My, Cert:\LocalMachine\My | Where-Object { $_.Subject -like "*CN=$certName*" }

# Si el certificado vence en menos de 4 años, asumimos que es el viejo de 1 año y lo renovamos
if ($oldCerts.Count -eq 1 -and $oldCerts[0].NotAfter -lt (Get-Date).AddYears(4)) {
    Write-Host "Certificado de corta duración detectado. Renovando a 5 años..." -ForegroundColor Gray
    Remove-Item $oldCerts[0].PSPath -ErrorAction SilentlyContinue
    $cert = $null
} elseif ($oldCerts.Count -gt 1) {
    Write-Host "Limpiando certificados duplicados antiguos..." -ForegroundColor Gray
    $oldCerts | ForEach-Object { Remove-Item $_.PSPath -ErrorAction SilentlyContinue }
    $cert = $null
} else {
    $cert = $oldCerts | Select-Object -First 1
}

if (-not $cert) {
    Write-Host "Creando nuevo certificado autofirmado en el almacén de la máquina..." -ForegroundColor Cyan
    try {
        $expiration = (Get-Date).AddYears(5)
        $cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject "CN=$certName" -CertStoreLocation "Cert:\LocalMachine\My" -NotAfter $expiration
    } catch {
        Write-Host "Error al crear el certificado: $($_.Exception.Message)" -ForegroundColor Red
        Read-Host "Presiona Enter para salir"
        exit
    }
} else {
    Write-Host "Cargando certificado existente ($($cert.Thumbprint))..." -ForegroundColor Cyan
}

# Determinar si necesitamos el flag /sm (System Store)
$useLocalMachine = $cert.PSParentPath -like "*LocalMachine*"

# 2. Intentar buscar signtool.exe
$signtool = Get-Command signtool.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source

if (-not $signtool) {
    $sdkPaths = @(
        "C:\Program Files (x86)\Windows Kits\10\bin\*\x64\signtool.exe",
        "C:\Program Files (x86)\Windows Kits\8.1\bin\x64\signtool.exe"
    )
    foreach ($path in $sdkPaths) {
        $found = Get-Command $path -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) { $signtool = $found.Source; break }
    }
}

if ($signtool) {
    Write-Host "Firmando ejecutable con $signtool..." -ForegroundColor Green
    $smFlag = if ($useLocalMachine) { "/sm" } else { "" }
    & $signtool sign /fd SHA256 /sha1 $cert.Thumbprint /tr http://timestamp.digicert.com /td sha256 $smFlag /s My /v /debug $exePath
} else {
    Write-Host "ADVERTENCIA: No se encontró 'signtool.exe'. El ejecutable no estará firmado." -ForegroundColor Yellow
    Write-Host "Esta herramienta es parte del Windows SDK." -ForegroundColor Gray
    Write-Host "Link de descarga: https://developer.microsoft.com/es-es/windows/downloads/windows-sdk/" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Proceso terminado." -ForegroundColor White
Read-Host "Presiona Enter para cerrar esta ventana"
