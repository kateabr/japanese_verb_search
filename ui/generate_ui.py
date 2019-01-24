import os
from pathlib import Path
from shutil import which
from subprocess import check_call, CalledProcessError

if __name__ == "__main__":
    pyuic = "pyuic5"
    pyuicPath = which(pyuic)
    if pyuicPath is None:
        print(f"{pyuic} command not found, cannot compile .ui files!")
    else:
        for ui in Path("").iterdir():
            if ui.suffix != ".ui":
                continue

            base, _ = os.path.splitext(ui.name)

            output = Path("../jvs/uic").joinpath(base + ".py").absolute()
            output.parent.mkdir(parents=True, exist_ok=True)

            cmd = [pyuicPath, str(ui), "-o", str(output)]
            try:
                check_call(cmd)
                print(f"{ui.name} successefully compiled!")
            except CalledProcessError as e:
                print(f"{ui.name} compilation finished with {e.returncode}")
