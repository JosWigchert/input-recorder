from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but they might need fine-tuning.
build_exe_options = {"includes": ["pynput.keyboard._win32", "pynput.mouse._win32"]}

setup(
    name="input-recorder",
    version="0.1",
    description="InputRecorder",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base="gui")],
)
