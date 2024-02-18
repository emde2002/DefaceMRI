## Installation Guide

This code has only been tested on Linux distribution Ubuntu 23.10 and 22.04.3.

### Step 1: Install FSL Library

#### Linux and macOS:
1. Download the FSL library from [FSL Downloads](https://fsl.fmrib.ox.ac.uk/fsldownloads_registration).
2. Follow the instructions in the [FSL Installation Guide](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation):
   - Click on the blue box labeled "FSL software license".
   - Scroll down and click "Agree" to accept the license agreement.
   - Fill in your information and select your operating system to register.
3. Download the `fslinstaller.py` script.
4. Run the script to complete the installation.

#### Windows:
1. Install Windows Subsystem for Linux (WSL).
2. Follow the steps for Linux installation.

### Step 2: Install Pydeface

1. Open a terminal and execute:
    ```
    pip install pydeface
    ```
2. Log off or restart your computer.
3. If you want to run deface you can just execute the following command to use Pydeface on a compressed NIfTI file:
    ```
    pydeface /path/to/your/file.nii.gz
    ```

### Step 3: Download MRIcroGL

1. Download MRIcroGL from [here](https://www.nitrc.org/plugins/mwiki/index.php/mricrogl:MainPage).
   
### Step 4: Install Prerequisites

1. Open a terminal and execute the following commands:
    ```
    pip install time
    pip install subprocess
    pip install pathlib
    pip install SimpleITK
    ```

### Step 5: Import and Convert DICOM to NIfTI

1. Open MRIcroGL.
2. Go to `Import > Import DICOM to NIfTI`.
3. Resize the window to make sure you can see the "Files to Convert" section.
4. Convert the files as needed.
5. (Optional) For batch conversion of DICOM to NIfTI you can use MRIcroGL DICOM to NIfTI.py
6. (Optional) You need to manually change the path variable in the Python file and then execute it.

### Step 6: Run Deface.py

1. Locate the `Deface.py` script.
2. Right-click on the folder containing `Deface.py` and select "Open in Terminal".
3. Execute the following command:
    ```
    python3 Deface.py
    ```

