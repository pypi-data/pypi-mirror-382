@echo off
echo Installing Agentic AI Device Analysis Package locally...
echo.

echo Uninstalling previous version (if exists)...
pip uninstall -y agentic-ai-device-analysis

echo Installing from local build...
if exist dist\*.whl (
    for %%f in (dist\*.whl) do (
        echo Installing %%f
        pip install "%%f"
    )
) else (
    echo No wheel file found. Building first...
    call build_package.bat
    for %%f in (dist\*.whl) do (
        echo Installing %%f
        pip install "%%f"
    )
)

echo.
echo Installation complete!
echo You can now run: agentic-demo
echo Or: device-analysis-demo
echo.
pause