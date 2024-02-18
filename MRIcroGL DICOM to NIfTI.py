import subprocess
from pathlib import Path

nifti_dir = Path("/home/user/Desktop/Projects")

directories = [x for x in nifti_dir.glob("*/") if x.is_dir()]


for directory in directories:
    command = ['/home/user/Desktop/MRIcroGL/Resources/dcm2niix', '-f', '"%f_%p_%s"', '-b', 'n', '-z', 'y', str(directory)]
    subprocess.run(command)
