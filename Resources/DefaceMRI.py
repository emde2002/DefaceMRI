import time
import subprocess
import os
import sys
import SimpleITK as sitk
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QFileDialog, QCheckBox, QGridLayout
from PyQt6.QtCore import Qt, QThread


class Worker(QThread):
    def __init__(self, directory: Path, option: int):
        super().__init__()
        self.directory = directory
        self.option = option

    def run(self):
        if stop_thread:
            return           
        if self.option == 0:
            run_dicom_to_nifti(self.directory)
        elif self.option == 1:
            run_pydeface(self.directory)
            if stop_thread:
                return
            run_nifti_to_dicom(self.directory)
        elif self.option == 2:
            run_pydeface(self.directory)
        elif self.option == 3:
            run_nifti_to_dicom(self.directory)

class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.nifti_dir = Path("")
        self.initUI()

    def initUI(self):
        self.setWindowTitle("DefaceMRI")

        layout = QGridLayout()
        self.setLayout(layout)

        self.btn1 = QPushButton("Select Directory", self)
        self.btn1.setMaximumWidth(200)
        self.btn1.clicked.connect(self.select_directory)
        layout.addWidget(self.btn1, 0, 0, 1, 2)

        self.btn2 = QPushButton("Run", self)
        self.btn2.setMaximumWidth(200)
        self.btn2.clicked.connect(self.run_script2)
        layout.addWidget(self.btn2, 0, 2, 1, 2)

        self.btn3 = QPushButton("Convert DICOM to NIfTI (Review NIfTI files before proceeding)", self)
        self.btn3.setMaximumWidth(550)
        self.btn3.clicked.connect(self.run_script1)
        layout.addWidget(self.btn3, 1, 0)   

        layout.addWidget(QLabel("Options:"), 2, 0)     
        
        self.checkbox_pydeface = QCheckBox("Deface NIfTI", self)
        self.checkbox_pydeface.setChecked(True)
        layout.addWidget(self.checkbox_pydeface, 3, 0) 

        self.checkbox_dicom = QCheckBox("Convert back to DICOM", self)
        self.checkbox_dicom.setChecked(True)
        layout.addWidget(self.checkbox_dicom, 3, 1)
        
        self.status_label = QLabel("Code is executing...", self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centre the text.
        self.status_label.setStyleSheet("font-size: 30px;")  # Increase the font size.
        self.status_label.setVisible(False)  # Hide the label initially.

        layout.addWidget(self.status_label, 0, 0, 3, 3)  # Add the label to the layout.

        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

    def select_directory(self):
        selected_dir = QFileDialog.getExistingDirectory(self, "Select Directory")
        if selected_dir:
            print(f"Selected directory: {selected_dir}")
            self.nifti_dir = Path(selected_dir)
    
    def get_option(self):
        if self.checkbox_pydeface.isChecked() and self.checkbox_dicom.isChecked():
            return 1
        elif self.checkbox_pydeface.isChecked():
            return 2
        elif self.checkbox_dicom.isChecked():
            return 3
        else:
            print("No option selected.")

    def start_worker(self, option):
        if self.nifti_dir:
            self.worker = Worker(self.nifti_dir, option)
            self.worker.finished.connect(self.enable_buttons)
            self.worker.start()
            self.update_status()

    def run_script1(self):
        self.start_worker(0)

    def run_script2(self):
        self.start_worker(self.get_option())

    def update_status(self):
        self.status_label.setVisible(True)
        self.btn1.setDisabled(True)
        self.btn2.setDisabled(True)
        self.btn3.setDisabled(True)
                   
    def closeEvent(self, event):
        close_subprocesses()
        # Close the application.
        event.accept()

    def enable_buttons(self):
        # Enable all buttons.
        self.status_label.setVisible(False)
        self.btn1.setDisabled(False)
        self.btn2.setDisabled(False)
        self.btn3.setDisabled(False)

subprocesses = []
stop_thread = False

def close_subprocesses():
    """
    Close the subprocess.
    """
    global stop_thread 
    stop_thread = True
    for process in subprocesses:
        process.terminate()
        process.wait()

def run_dicom_to_nifti(dicom_dir: Path) -> None:
    """
    Convert DICOM files to NIfTI format using dcm2niix.
    """
    directories = [dir_path for dir_path in dicom_dir.glob("*/") if dir_path.is_dir()]
    if getattr(sys, 'frozen', False):
        bundle_dir = Path(sys._MEIPASS)
    else:
        bundle_dir = Path(__file__).parent
    dcm2niix_path = bundle_dir / "dcm2niix"
    for dicom in directories:
        print(f"Converting {dicom} to NIfTI...")
        command = [str(dcm2niix_path), '-f', '"%f_%p_%s"', '-b', 'n', '-z', 'y', str(dicom)]
        process = subprocess.Popen(command)
        subprocesses.append(process)
        process.wait()
        if stop_thread:  # Check if the thread should be stopped.
            break

def run_pydeface(nifti_dir: Path) -> None:
    """
    Run pydeface on the directory with the NIfTI images for defacing.
    """
    images = list(nifti_dir.rglob("*.nii.gz"))
    print("Defacing images...")
    for image in images:
        if image.name.endswith("_defaced.nii.gz"):
            continue
        image_stem = Path(image.stem).stem
        defaced_image = image.parent / (image_stem + "_defaced.nii.gz")
        if defaced_image.exists():
            continue
        os.chdir(image.parent)
        command = ["pydeface", image.name]
        process = subprocess.Popen(command)
        subprocesses.append(process)
        process.wait()
        if stop_thread:  # Check if the thread should be stopped.
            break

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
    image_slice.SetMetaData("0008|0060", "CT")  # set the type to CT so the thickness is carried over.

    # Image position of patient (0020, 0032) determines the 3D spacing between slices.
    image_slice.SetMetaData("0020|0032", "\\".join(map(str,new_img.TransformIndexToPhysicalPoint((0,0,i))))) # Image Position (Patient).
    image_slice.SetMetaData("0020,0013", str(i)) # Instance Number.

    # Write to the output directory and add the extension dcm, to force writing in DICOM format.
    writer.SetFileName(str(out_dir / f"slice{i:04d}.dcm"))
    writer.Execute(image_slice)

def nifti_to_dicom(in_dir: Path, out_dir: Path) -> None:
    """
    Convert a NIfTI file into a DICOM series.

    in_dir: the path to the NIfTI file.
    out_dir: the path to the output.
    """

    Path(out_dir).mkdir(parents=True, exist_ok=True)

    new_img = sitk.ReadImage(str(in_dir)) 
    modification_time = time.strftime("%H%M%S")
    modification_date = time.strftime("%Y%m%d")
    rootUID = "1.2.826.0.1.3680043.2" # Medical Connections root for publicly available OIDs (UIDs)
    direction = new_img.GetDirection()
    
    series_tag_values = [("0008|0031", modification_time), # Series Time.
                    ("0008|0021", modification_date), # Series Date.
                    ("0008|0008","DERIVED\\SECONDARY"), # Image Type.
                    ("0020|000d", rootUID + ".1125." + modification_date + modification_time), # Study Instance UID.
                    ("0020|000e", rootUID + ".1125." + modification_date + ".1" + modification_time), # Series Instance UID.
                    ("0020|0037", '\\'.join(map(str, (direction[0], direction[3], direction[6], direction[1], direction[4], direction[7])))), # Image Orientation (Patient).
                    ("0008|103e", "Anonymised")] # Series Description.

    # Write slices to output directory.
    list(map(lambda i: write_slices(series_tag_values, new_img, i, out_dir), range(new_img.GetDepth())))

    print(f"Conversion of {in_dir} to DICOM completed successfully.")

def run_nifti_to_dicom(deface_dir: Path) -> None:
    """
    Convert multiple NIfTI files into DICOM files.

    deface_dir: The global directory path to all of the folders with NIfTI files.
    """
    images = list(deface_dir.rglob("*_defaced.nii.gz"))
    
    for image in images:
        image_stem = Path(image.stem).stem
        out_dir = image.parent / image_stem
        if out_dir.exists():
            continue
        in_dir = deface_dir / image
        nifti_to_dicom(in_dir, out_dir)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    gui = MyApp()
    gui.show()

    sys.exit(app.exec())
