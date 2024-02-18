import time
import subprocess
import os
import SimpleITK as sitk
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QFileDialog, QCheckBox, QGridLayout

class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.nifti_dir = Path("")

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Deface NIfTI Images")

        layout = QGridLayout()
        self.setLayout(layout)

        btn1 = QPushButton("Select Directory", self)
        btn1.setMaximumWidth(200)
        btn1.clicked.connect(self.select_directory)
        layout.addWidget(btn1, 0, 0, 1, 2)

        btn2 = QPushButton("Run", self)
        btn2.setMaximumWidth(200)
        btn2.clicked.connect(self.run_script)
        layout.addWidget(btn2, 0, 2, 1, 2)

        layout.addWidget(QLabel("Options:"), 1, 0)  # add a label for the checkboxes

        self.checkbox_pydeface = QCheckBox("Deface NIfTI", self)
        self.checkbox_pydeface.setChecked(True)
        layout.addWidget(self.checkbox_pydeface, 2, 0) 

        self.checkbox_dicom = QCheckBox("Convert back to DICOM", self)
        self.checkbox_dicom.setChecked(True)
        layout.addWidget(self.checkbox_dicom, 2, 1)
        
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

    def select_directory(self):
        selected_dir = QFileDialog.getExistingDirectory(self, "Select Directory")
        if selected_dir:
            print(f"Selected directory: {selected_dir}")
            self.nifti_dir = Path(selected_dir)
    
    def get_option(self):
        if self.checkbox_pydeface.isChecked() and self.checkbox_dicom.isChecked():
            return 0
        elif self.checkbox_pydeface.isChecked():
            return 1
        elif self.checkbox_dicom.isChecked():
            return 2
        else:
            print("No option selected.")
            print("Both options will be run.")
    
    def run_script(self):
        if self.nifti_dir:
            main(self.nifti_dir, self.get_option())
            
    def closeApp(self):
        self.close()

def run_pydeface(nifti_dir: Path) -> None:
    """
    Run pydeface on the directory with the NIfTI images for defacing.
    """
    images = list(nifti_dir.rglob("*.nii.gz"))

    for image in images:
        if image.name.endswith("_defaced.nii.gz"):
            continue
        image_stem = Path(image.stem).stem
        defaced_image = image.parent / (image_stem + "_defaced.nii.gz")
        if defaced_image.exists():
            continue
        os.chdir(image.parent)
        command = ["pydeface", image.name]
        subprocess.run(command)

def write_slices(series_tag_values: list, new_img: sitk.SimpleITK.Image, i: int, out_dir: Path) -> None:
    """
    Write the slices to the output directory.
    """
    # Create a new series from a 3D image.
    image_slice = new_img[:,:,i]
    image_slice = sitk.Cast(image_slice, sitk.sitkInt16)
    writer = sitk.ImageFileWriter()
    writer.KeepOriginalImageUIDOn()

    # Tags shared by the series.
    for tag_value in series_tag_values:
        image_slice.SetMetaData(tag_value[0], tag_value[1])

    # Slice specific tags.
    image_slice.SetMetaData("0008|0012", time.strftime("%Y%m%d")) # Instance Creation Date
    image_slice.SetMetaData("0008|0013", time.strftime("%H%M%S")) # Instance Creation Time

    # Setting the type to CT preserves the slice location.
    image_slice.SetMetaData("0008|0060", "CT")  # set the type to CT so the thickness is carried over

    # (0020, 0032) image position patient determines the 3D spacing between slices.
    image_slice.SetMetaData("0020|0032", "\\".join(map(str,new_img.TransformIndexToPhysicalPoint((0,0,i))))) # Image Position (Patient)
    image_slice.SetMetaData("0020,0013", str(i)) # Instance Number

    # Write to the output directory and add the extension dcm, to force writing in DICOM format.
    writer.SetFileName(str(out_dir / f"slice{i:04d}.dcm"))
    writer.Execute(image_slice)

def nifti_to_dicom(in_dir: Path, out_dir: Path) -> None:
    """
    Convert a NIfTI file into a DICOM series.

    in_dir: the path to the NIfTI file
    out_dir: the path to the output
    """

    Path(out_dir).mkdir(parents=True, exist_ok=True)

    new_img = sitk.ReadImage(str(in_dir)) 
    modification_time = time.strftime("%H%M%S")
    modification_date = time.strftime("%Y%m%d")

    direction = new_img.GetDirection()
    series_tag_values = [("0008|0031", modification_time), # Series Time
                    ("0008|0021", modification_date), # Series Date
                    ("0008|0008","DERIVED\\SECONDARY"), # Image Type
                    ("0020|000e", "1.2.826.0.1.3680043.2.1125." + modification_date + ".1" + modification_time), # Series Instance UID
                    ("0020|0037", '\\'.join(map(str, (direction[0], direction[3], direction[6], direction[1], direction[4], direction[7])))), # Image Orientation (Patient)
                    ("0008|103e", "Anonymised")] # Series Description

    # Write slices to output directory
    list(map(lambda i: write_slices(series_tag_values, new_img, i, out_dir), range(new_img.GetDepth())))

    print(f"Conversion of {in_dir} to DICOM completed successfully.")

def run_nifti_to_dicom(nifti_dir: Path) -> None:
    """
    Convert multiple NIfTI files into DICOM files.

    nifti_dir: The global directory path to all of the folders with NIfTI files.
    """
    images = list(nifti_dir.rglob("*_defaced.nii.gz"))
    
    for image in images:
        image_stem = Path(image.stem).stem
        out_dir = image.parent / image_stem
        if out_dir.exists():
            continue
        in_dir = nifti_dir / image
        nifti_to_dicom(in_dir, out_dir)


def main(directory: Path, option: int = 0):
    """
    Main function to run the pipeline.

    directory: The path to the directory containing the NIfTI images.
    """
    gui.closeApp()
    if option == 0:
        run_pydeface(directory)
        run_nifti_to_dicom(directory)
    elif option == 1:
        run_pydeface(directory)
    elif option == 2:
        run_nifti_to_dicom(directory)
    

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    gui = MyApp()
    gui.show()

    sys.exit(app.exec())
