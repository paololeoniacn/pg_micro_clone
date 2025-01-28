# Imposta il percorso del virtual environment
$envPath = ".\venv"

try {
    # Controlla se il virtual environment esiste
    if (!(Test-Path $envPath)) {
        Write-Host "Creazione del virtual environment..."
        python -m venv $envPath
        if ($LASTEXITCODE -ne 0) {
            throw "Errore durante la creazione del virtual environment."
        }
    }

    # Attiva il virtual environment
    Write-Host "Attivazione del virtual environment..."
    & "$envPath\Scripts\Activate.ps1"
    if ($LASTEXITCODE -ne 0) {
        throw "Errore durante l'attivazione del virtual environment."
    }

    # Installa i requisiti
    Write-Host "Installazione delle dipendenze..."
    pip install -r .\app\requirements.txt
    if ($LASTEXITCODE -ne 0) {
        throw "Errore durante l'installazione delle dipendenze."
    }

    # Esegui lo script Python
    Write-Host "Esecuzione dello script..."
    python .\app\app.py
    if ($LASTEXITCODE -ne 0) {
        throw "Errore durante l'esecuzione dello script Python."
    }

} catch {
    # Gestione degli errori
    Write-Error "Si è verificato un errore: $_"
    exit 1
} finally {
    # Disattiva il virtual environment
    Write-Host "Disattivazione del virtual environment..."
    try {
        deactivate
    } catch {
        Write-Error "Errore durante la disattivazione del virtual environment: $_"
    }
}
