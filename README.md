## Installation Guide
Download DefaceMRI from [GitHub](https://github.com/emde2002/DefaceMRI).

### Step 1: Install FSL Library

#### Linux and MacOS:
1. Follow the instructions in the [FSL Installation Guide](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation).
2. Download the FSL library from [FSL Downloads](https://fsl.fmrib.ox.ac.uk/fsldownloads_registration):
    - Click "FSL software license" and then "Agree" to accept the license agreement.
    - Fill in the personal information and select the operating system.
    - Click "Register" and then "Download FSL" to obtain the `fslinstaller.py` script.
    - Run the script to complete the installation.

#### Windows:
1. Install Windows Subsystem for Linux (WSL).
2. Follow the steps for Linux installation.

### Step 2: Install Dependencies

1. Open a terminal and execute the following command:
```
pip install pydeface pathlib SimpleITK PyQt6
```

### Step 3: Download MRIcroGL and dcm2niix

1. Download MRIcroGL from [NITRC](https://www.nitrc.org/projects/mricrogl).
    - Select the appropriate operating system version and agree to the License Agreement.
2. Transfer dcm2niix from MRIcroGL's "Resources" folder to the DefaceMRI's "Resources" folder.

### Step 4: Build code

1. In a terminal inside DefaceMRI's "Resources" folder, run:
    - Replace the path to dcm2niix, e.g. replace "User" with the appropriate username.
```
pyinstaller --noconsole --add-data '/home/User/Desktop/DefaceMRI/Resources/dcm2niix:.' DefaceMRI.py
```
2. The software can be found at "dist/DefaceMRI/DefaceMRI".

## DefaceMRI

### Step 1: Anonymise Metadata

1. Run DefaceMRI.
2. Click "Select Directory" to choose the directory containing the MRI scans.
3. Click "Convert DICOM to NIfTI (Review NIfTI files before proceeding)":
    - Review all files and delete any not to be defaced to save time and ensure only scans are anonymised.

### Step 2: Image Defacing

1. Click "Run".
    - Uncheck any unnecessary options.

## Cite
Emmanouil Demosthenous. (2024) DefaceMRI. GitHub. https://github.com/emde2002/DefaceMRI