from pathlib import Path


def produce_replay_compare_shortcuts(function_saver_root_path: Path):
    compare_shortcut = function_saver_root_path / "compare_replay.bat"
    if compare_shortcut.exists():
        return

    bat = """
@echo off
setlocal

if "%FUNCTION_SAVER_COMPARE_TOOL_PATH%"=="" (
    set Compare_Tool_Path=%ProgramFiles%\Beyond Compare 4\BCompare.exe
) else (
    set Compare_Tool_Path=%FUNCTION_SAVER_COMPARE_TOOL_PATH%
)

if not exist "%Compare_Tool_Path%" (
    echo "Compare tool not found at %Compare_Tool_Path%"
    pause
    exit /b 1
)

start "" "%Compare_Tool_Path%" output output_replay
start "" "%Compare_Tool_Path%" internal internal_replay

endlocal
"""
    compare_shortcut.write_text(bat)
