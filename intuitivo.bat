```bat
@echo off
setlocal EnableDelayedExpansion

title Instalador e Executor - Projeto Darwin

echo ==========================================
echo       DARWIN - INSTALADOR AUTOMATICO
echo ==========================================
echo.

REM ============================================================
REM 1. VERIFICAR PYTHON
REM ============================================================

echo [1/6] Verificando Python...

where py >nul 2>&1

if %errorlevel%==0 (
    set "PY=py"
    goto PYTHON_OK
)

where python >nul 2>&1

if %errorlevel%==0 (
    set "PY=python"
    goto PYTHON_OK
)

echo.
echo [AVISO] Python nao encontrado.
echo.
echo Tentando instalar automaticamente...
echo.

REM ============================================================
REM 2. VERIFICAR WINGET
REM ============================================================

where winget >nul 2>&1

if %errorlevel% neq 0 (
    echo [ERRO] O winget nao foi encontrado.
    echo.
    echo Este Windows nao possui o gerenciador de pacotes winget.
    echo.
    echo Instale o Python manualmente:
    echo https://www.python.org/downloads/windows/
    echo.
    pause
    exit /b 1
)

echo [OK] winget encontrado.
echo.
echo Instalando Python...
echo.

REM ============================================================
REM 3. INSTALAR PYTHON
REM ============================================================

winget install --id Python.Python.3.12 -e --scope user --accept-source-agreements --accept-package-agreements

if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao instalar Python.
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Python instalado.
echo.

REM ============================================================
REM ATUALIZAR PATH DA SESSAO
REM ============================================================

echo Atualizando PATH...

set "PATH=%PATH%;%LocalAppData%\Programs\Python\Python312;%LocalAppData%\Programs\Python\Python312\Scripts"

REM ============================================================
REM VERIFICAR NOVAMENTE
REM ============================================================

where py >nul 2>&1

if %errorlevel%==0 (
    set "PY=py"
    goto PYTHON_OK
)

where python >nul 2>&1

if %errorlevel%==0 (
    set "PY=python"
    goto PYTHON_OK
)

echo.
echo [ERRO] Python foi instalado, mas nao foi encontrado.
echo.
echo Feche este terminal e execute o .bat novamente.
echo.
pause
exit /b 1


:PYTHON_OK

echo.
echo [OK] Python encontrado:
%PY% --version
echo.


REM ============================================================
REM 4. CRIAR AMBIENTE VIRTUAL
REM ============================================================

echo [2/6] Verificando ambiente virtual...

if not exist ".venv" (

    echo Criando ambiente virtual...

    %PY% -m venv .venv

    if errorlevel 1 (
        echo.
        echo [ERRO] Falha ao criar ambiente virtual.
        echo.
        pause
        exit /b 1
    )

    echo [OK] Ambiente virtual criado.

) else (

    echo [OK] Ambiente virtual ja existe.

)

echo.


REM ============================================================
REM 5. ATUALIZAR PIP
REM ============================================================

echo [3/6] Atualizando pip...

echo [OK] pip atualizado.
echo.


REM ============================================================
REM 6. INSTALAR DEPENDENCIAS
REM ============================================================

echo [4/6] Instalando dependencias...

if not exist "requirements.txt" (
    echo.
    echo [ERRO] requirements.txt nao encontrado!
    echo.
    pause
    exit /b 1
)

call ".venv\Scripts\python.exe" -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao instalar dependencias.
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Dependencias instaladas.
echo.


REM ============================================================
REM 7. EXECUTAR DARWIN
REM ============================================================

echo [5/6] Iniciando Darwin...
echo.
echo ==========================================
echo              DARWIN INICIADO
echo ==========================================
echo.

if not exist "main.py" (
    echo [ERRO] main.py nao encontrado!
    echo.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" main.py

echo.
echo ==========================================
echo           DARWIN FINALIZADO
echo ==========================================
echo.


REM ============================================================
REM 8. ABRIR RELATORIO.PDF
REM ============================================================

echo [6/6] Abrindo relatorio_darwin_population.pdf...

if exist "relatorio_darwin_population.pdf" (

    echo [OK] Abrindo relatorio_darwin_population.pdf...
    start "" "relatorio_darwin_population.pdf"

) else (

    echo [AVISO] relatorio_darwin_population.pdf nao encontrado!

)

echo.
echo ==========================================
echo          DARWIN - FINALIZADO
echo ==========================================
echo.

pause
```
