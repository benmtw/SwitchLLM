$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$EnvChangesFile = Join-Path $ScriptDir "env_changes.tmp"

# 1. Run the Python GUI
# Check for local venv and use that java python if available to ensure dependencies are found
$VenvPython = Join-Path $ScriptDir ".venv\Scripts\python.exe"
if (Test-Path $VenvPython) {
    Write-Host "Using venv python: $VenvPython" -ForegroundColor Gray
    & $VenvPython "$ScriptDir\switch_claude_llm_provider.py"
}
else {
    Write-Host "Venv not found, using system python..." -ForegroundColor Yellow
    python "$ScriptDir\switch_claude_llm_provider.py"
}

# 2. Check if the temp file exists
if (Test-Path $EnvChangesFile) {
    try {
        $JsonContent = Get-Content $EnvChangesFile -Raw
        $EnvVars = $JsonContent | ConvertFrom-Json
        
        Write-Host "Updating Environment Variables..." -ForegroundColor Green
        
        # 3. Apply variables to current session
        # $EnvVars is a PSCustomObject, we can iterate its properties
        foreach ($Prop in $EnvVars.PSObject.Properties) {
            $Key = $Prop.Name
            $Value = $Prop.Value
            
            # Set the env var in the current session scope
            [Environment]::SetEnvironmentVariable($Key, $Value, "Process")
            
            # Also update the $env: drive for immediate visibility in this script scope if needed
            Set-Item -Path "env:$Key" -Value $Value

            $DisplayValue = $Value
            if ($DisplayValue.Length -gt 50) {
                # Truncate long keys for clean display, or keep full if preferred. 
                # User asked to see values, but full keys can be spammy. Let's show full for non-keys, masked for keys?
                # User said "tell you what it set these values to". I'll show full value for now as requested.
            }
            Write-Host "  Set $Key = $DisplayValue" -ForegroundColor Gray
        }

        Write-Host "Successfully switched profile." -ForegroundColor Green
        Write-Host ""
        Write-Host "To verify variables are set correctly, you can run:" -ForegroundColor Yellow
        Write-Host "    Get-ChildItem Env:ANTHROPIC*" -ForegroundColor Cyan
    }
    catch {
        Write-Host "Error reading environment changes: $_" -ForegroundColor Red
    }
    finally {
        # 4. Clean up
        Remove-Item $EnvChangesFile -Force
    }
}
else {
    Write-Host "No changes applied (cancelled or no selection made)." -ForegroundColor Yellow
}
