import docker
import subprocess
import shutil
import os
import sys
import pymzml
import numpy as np
import pyimzml.ImzMLWriter as imzmlw
from bs4 import BeautifulSoup, Tag
import string
import re
import tkinter as tk
from tkinter import filedialog,messagebox
import time
import json
import logging
import warnings
import pyimzml.ImzMLParser as imzmlp
from pathlib import Path

from imzml_writer.recalibrate_mz import recalibrate
from imzml_writer import __version__

logger = logging.getLogger(__name__)
logging.basicConfig(filename = "LOGFILE_imzML_Writer.log",level = logging.INFO)
logger.info("NEW INSTANCE STARTING...")


##Colors and FONTS
TEAL = "#2da7ad"
BEIGE = "#dbc076"
GREEN = "#22d10f"
FONT = ("HELVETICA", 18, 'bold')

def get_drives():
    """On windows machines, retrieves the accessible drives (e.g C:\\, D:\\, etc.) in to for automated seeking
    of msconvert.

    :return: Available drives, as a list of strings."""
    from ctypes import windll
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(letter)
        
        bitmask >>= 1
    
    return drives


def find_file(target:str, folder:str):
    """Recursely searches the folder for the target file - helps find msconvert in cases
    where it isn't specified in the path.
    
    :param target: Target file as a string
    :param folder: Top-level folder to search through
    :return: full path to file if found, [ ] if not present"""
    try:
        for f in os.listdir(folder):
            path = os.path.join(folder,f)
            if os.path.isdir(path):
                result = find_file(target, path)
                if result is not None:
                    return result
                continue
            if f == target:
                return path
    except Exception as e:
        pass

def msconvert_searchUI() -> str:
    """Launches a dialog window to ask the user whether to search manually or automatically for msconvert install path
    
    :return: Specified mode to search for msconvert ("auto" or "manual")"""
    search_mode = ""
    def set_auto():
        nonlocal search_mode
        search_mode = "auto"
        msconv_finder.destroy()
    def set_manual():
        nonlocal search_mode
        search_mode = "manual"
        msconv_finder.destroy()

    msconv_finder = tk.Tk()
    msconv_finder.title("Find msconvert...")
    msconv_finder.config(padx=5,pady=5,bg=TEAL)

    autofind = tk.Button(msconv_finder,text="Auto Search...(Warning : Slow for large drives)",bg=TEAL,highlightbackground=TEAL,command=set_auto)
    autofind.grid(row=1,column=1,padx=15,pady=15)

    man_find = tk.Button(msconv_finder,text="Manual Search",bg=TEAL,highlightbackground=TEAL,command=set_manual)
    man_find.grid(row=1,column=2,padx=15,pady=15)

    while search_mode == "":
        msconv_finder.update()
        time.sleep(0.5)

    return search_mode

def autofind_msconvert():
    """Finds msconvert by searching all available drives, verifies success by calling
    info of msconvert
    
    :return: Full path to msconvert.exe"""
    drives = get_drives()

    candidates = []
    for drive in drives:
        drive_str = (f"{drive}:\\".__repr__()).replace("'","")
        candidates.append(find_file("msconvert.exe",drive_str))
    

    for candidate in candidates:
        if candidate is not None:
            if "msconvert.exe" in candidate:
                res = subprocess.run(candidate, shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            stdin=subprocess.PIPE,
                            cwd=os.getcwd(),
                            env=os.environ)
                if res.returncode == 0:
                    #msconvert successfully found and called
                    return candidate


def check_msconvert():
    """Checks that msconvert is available for the current python environment - returns msconvert path/callable"""
    msconvert = "msconvert"
    try:
        res = subprocess.run(msconvert, shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            stdin=subprocess.PIPE,
                            cwd=os.getcwd(),
                            env=os.environ) 
        if res.returncode == 0:
            # Found as default
            return msconvert
            
        elif res.returncode != 0:
            try:
                mod_path = os.path.dirname(os.path.abspath(__file__))
                settings_path = os.path.join(mod_path,"msconvert_path.json")
                with open(settings_path,'r') as file:
                    path_data = json.load(file)
                msconvert = path_data["msconvert_path"]
                res = subprocess.run(msconvert, shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            stdin=subprocess.PIPE,
                            cwd=os.getcwd(),
                            env=os.environ)
                
                if res.returncode != 0:
                    raise
                # Found in saved config
                return msconvert
            except:
                    search_method = msconvert_searchUI()
                    if search_method == "manual":
                        msconvert = filedialog.askopenfilename(initialdir=os.getcwd(),title="Please select msconvert.exe",filetypes=[("msconvert.exe","msconvert.exe")])
                        msconvert = os.path.abspath(msconvert)
                    elif search_method == "auto":
                        msconvert = autofind_msconvert()
                        msconvert = os.path.abspath(msconvert)
                    res = subprocess.run(msconvert, shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        stdin=subprocess.PIPE,
                        cwd=os.getcwd(),
                        env=os.environ)
                    if res.returncode == 0:
                        # Found by manual/autosearch, saving to config
                        mod_path = os.path.dirname(os.path.abspath(__file__))
                        settings_path = os.path.join(mod_path,"msconvert_path.json")
                        set_path = {"msconvert_path": msconvert}
                        with open(settings_path,'w') as file:
                            json.dump(set_path,file)
                        
                        return msconvert
                    else:
                        raise
    except:
        raise Exception("msConvert not available, check installation and verify msConvert path is specified correctly")


def viaPWIZ(path:str,write_mode:str,combine_ion_mobility:bool):
    """Method to call msconvert directly if the detected platform is on windows. Converts all target files in the path to mzML in the specified mode.

    :param path: path to the target files
    :param write_mode: "Centroid" or "Profile" modes
    :param combine_ion_mobility: Whether or not --combineIonMobility flag is passed to msconvert
    :return: None"""
    ##check pwiz availability:
    file_type = get_file_type(path)
    current_dir = os.getcwd()
    os.chdir(path)

    
    msconvert = check_msconvert()

    ms_convert_args = [msconvert,fr"{path}\*.{file_type}", "--mzML", "--64"]
    if write_mode=="Centroid":
        ms_convert_args.append("--filter")
        ms_convert_args.append("peakPicking true 1-")
    
    ms_convert_args.append("--simAsSpectra")
    ms_convert_args.append("--srmAsSpectra")
    if combine_ion_mobility:
        ms_convert_args.append("--combineIonMobility")
    


    convert_process = subprocess.run(ms_convert_args,
                                       stdout=subprocess.DEVNULL,
                                       shell=True,
                                       stderr=subprocess.STDOUT,
                                       stdin=subprocess.PIPE,
                                       cwd=os.getcwd(),
                                       env=os.environ)


    os.chdir(current_dir)

##The below three functions (tryint, alphanum_keys, human_sort) are borrowed from an excellent post by Ned Batchelder for 'natural sorting' in Python
##http://nedbatchelder.com/blog/200712/human_sorting.html
def tryint(s):
    """
    Part of the human sorting collection of functions borrowed from http://nedbatchelder.com/blog/200712/human_sorting.html. Returns an int if possible, or `s` unchanged.

    :param s: Trial variable to test if it can be converted to an integer
    :return: integer if convertible, s if not.
    """
    try:
        return int(s)
    except ValueError:
        return s

def alphanum_key(s:str) -> list:
    """
    Part of the human sortable collection of functions borrowed from http://nedbatchelder.com/blog/200712/human_sorting.html. Turn a string into a list of string and number chunks.

    :param s: String to be chunked out
    :return: List of string/number chunks
    """
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]

def human_sort(l:list) -> list:
    """
    Part of the human sortable collection of functions borrowed from http://nedbatchelder.com/blog/200712/human_sorting.html. Sorts a list in the way that humans expect.

    :param l: List to be sorted in a human-intuitive wave.
    :return: Sorted list.
    """
    return l.sort(key=alphanum_key)


def get_file_type(path:str):
    """Identifies the most abundant file type in the specified path, ignoring hidden files.

    :param path: path to files specified as a string.
    :return: Most abundant file extension in path"""
    files = os.listdir(path)
    file_poss = {}
    for file in files:
        if not file.startswith("."):
            ext = file.split(".")[-1]
            if ext not in file_poss.keys():
                file_poss[ext] = 1
            else:
                file_poss[ext]+= 1
    
    num_biggest = 0
    for ext in file_poss.keys():
        if file_poss[ext] > num_biggest:
            extension = ext
            num_biggest = file_poss[ext]
    
    return extension

def Check_Docker_Image():
    """Tests that docker is available, prompts the user to update/install if available"""
    DOCKER_IMAGE = "chambm/pwiz-skyline-i-agree-to-the-vendor-licenses"
    try:
        client = docker.from_env()
    except:
        res = subprocess.run(["open", "--background", "-a", "Docker"])
        if res.returncode == 0:
            time.sleep(2.5)
            client = docker.from_env()
        else:
            messagebox.showwarning(title="No Docker",message="Docker unavailable - please launch/install Docker desktop before proceeding...")
            client = docker.from_env()

    try:
        data = client.images.get(DOCKER_IMAGE)
        if "latest" not in str(data):
            resp = messagebox.askquestion("Newer docker image available", "A newer version of the msconvert docker image is available, would you like to update?")
            if resp == "yes":
                client.images.pull(DOCKER_IMAGE)
    except:
        resp = messagebox.askquestion("Docker image unavailable", "No docker image for msconvert is available, would you like to download it now? (WARNING: May take several minutes)")
        if resp == "yes":
            client.images.pull(DOCKER_IMAGE)
        else:
            raise
    
    return client



def RAW_to_mzML(path:str,write_mode:str="Centroid", combine_ion_mobility:bool=False):
    """Calls msConvert via docker on linux and Mac, or calls viaPwiz method on PC to manage conversion of raw vendor files to mzML format within the specified path

    :param path: path to files containing raw instrument data.
    :param write_mode: Write mode for msconvert - 'Profile' or 'Centroid'.
    :param combine_ion_mobility: Whether or not to hand --combineIonMobilitySpectra flag to msconvert (default false)"""
    if "win" in sys.platform and sys.platform != "darwin":
        viaPWIZ(path,write_mode, combine_ion_mobility)
    else:
        DOCKER_IMAGE = "chambm/pwiz-skyline-i-agree-to-the-vendor-licenses"
        client = Check_Docker_Image()
        file_type = get_file_type(path)

        vol = {path: {'bind': fr"/{DOCKER_IMAGE}/data", 'mode': 'rw'}}


        comm = fr"wine msconvert /{DOCKER_IMAGE}/data/*.{file_type} --zlib=off --mzML --64 --outdir /{DOCKER_IMAGE}/data"

        if write_mode=="Centroid":
            comm += fr" --filter '"'peakPicking true 1-'"'"

        comm+= " --simAsSpectra --srmAsSpectra"
        if combine_ion_mobility:
            comm += " --combineIonMobilitySpectra"

        env_vars = {"WINEDEBUG": "-all"}
        
        ##Call/run the docker container
        client.containers.run(
            image=DOCKER_IMAGE,
            environment=env_vars,
            volumes = vol,
            command=comm,
            working_dir=path,
            auto_remove= True,
            detach=False
            )
        
        

def clean_raw_files(path:str,file_type:str):
    """Cleans up file system after RAW_to_mzML has completed, creating two folders within the specified path:

    **Initial RAW files** - raw vendor files

    **Output mzML Files** - processed mzML files output by msConvert

    :param path: path to directory to clean up
    :param file_type: extension for raw vendor data to place into raw file directory"""
    mzML_folder = os.path.join(path,"Output mzML Files")
    RAW_folder = os.path.join(path,"Initial RAW files")
    if not os.path.isdir(mzML_folder):
        os.mkdir(mzML_folder)
    if not os.path.isdir(RAW_folder):
        os.mkdir(RAW_folder)

    for file in os.listdir(path):
        if not file.startswith("."):
            logger.info(f"Starting file transfer: {file}")
            if ".mzML".lower() in file.lower():
                shutil.move(os.path.join(path,file),os.path.join(mzML_folder,file))
            elif file_type in file and file != "Initial RAW files":
                shutil.move(os.path.join(path,file),os.path.join(RAW_folder,file))

def get_final_scan_time(run:pymzml.run.Reader):
    """Returns the final scan time from the specified mzML

    :param run: pymzml reader object
    :return scan_time: Scan time in minutes (float)"""
    for spec in run:
        scan_time = spec.scan_time_in_minutes()
    
    return scan_time

def mzML_to_imzML_convert(progress_target=None,PATH:str=os.getcwd(),LOCK_MASS:float=0,TOLERANCE:float=20,zero_indexed:bool=False,no_duplicating:bool=False,scan_mode:str = "x-scan"):
    """Handles conversion of mzML files to the imzML format using the pyimzml library. Converts data line-by-line (one mzML at a time),
    aligning data based on scan time and splitting into separate imzML files for each scan in the source mzML.
    
    :param progress_target: tkinter progress bar object from the GUI to update as conversion progresses
    :param PATH: - Working path for source mzML files
    :param LOCK_MASS: - m/z to use for coarse m/z recalibration if desired. 0 = No recalibration
    :param TOLERANCE: Search tolerance (in ppm) with which to correct m/z based on the specified lock mass. Default 20 ppm
    :param zero_indexed: Specifies whether pixel dimensions should start from 1 (default - False) or 0 (True)
    :param no_duplicating: Specifies whether spectra can be duplicated into adjacent pixels for sparsely sampled lines. Default True
    :param scan_mode: Whether the data was acquired in 'x-scan' or 'y-scan' mode."""

    ##Ensure lock mass and tolerance are formatted as float
    LOCK_MASS = float(LOCK_MASS)
    TOLERANCE = float(TOLERANCE)
    files = os.listdir(PATH)
    human_sort(files)

    ##Extracts filter strings, num pixels for each scan, etc
    scan_filts=[]
    polarities = []
    ms_levels = []
    file_iter=-1
    spectrum_counts=[]
    mzml_files=[]
    spec_counts=[]
    list_type = False
    for file in files:
        if ".mzML".lower() in file.lower():
            file_iter+=1
            tmp = pymzml.run.Reader(os.path.join(PATH,file))
            spec_counts.append(tmp.get_spectrum_count())
            ##Ignore partially collected datafiles that were cut-short (threshold of <50% the scans of the mean datafile)
            if np.mean(spec_counts)*0.5 > tmp.get_spectrum_count():
                break
            
            
            mzml_files.append(file)
            

            ##Retrieve list of filter strings from first file
            if file_iter==0:
                for spectrum in tmp:
                    if isinstance(spectrum["filter string"],list):
                            list_type = True
                    if list_type:
                        logger.warning(f"LIST TYPE filter strings detected")
                        scan_filts = spectrum["filter string"][0]
                        ms_levels = int(spectrum['MS:1000511'])
                        if spectrum["MS:1000129"]:
                            polarities = "negative"
                        elif spectrum["MS:1000130"]:
                            polarities = "positive"
                    else: 
                        if spectrum["filter string"] not in scan_filts:
                            scan_filts.append(spectrum["filter string"])
                            ms_levels.append(int(spectrum['MS:1000511']))
                            if spectrum["MS:1000129"]:
                                polarities.append("negative")
                            elif spectrum["MS:1000130"]:
                                polarities.append("positive")

            if not list_type:
                tmp_spectrum_counts = {filt_name:0 for filt_name in scan_filts}
            else:
                str_list = set(spectrum["filter string"])
                str_list = list(str_list)
                tmp_spectrum_counts={}
                for entry in str_list:
                    tmp_spectrum_counts[entry]=0

            for spectrum in tmp:
                if not list_type:
                    tmp_spectrum_counts[spectrum["filter string"]] += 1
                elif list_type:
                    tmp_spectrum_counts[spectrum["filter string"][0]]+= 1
            
            spectrum_counts.append(tmp_spectrum_counts)

    tmp.close()
    del spectrum

    #Find conserved portion of name for output filename
    str_array = [letter for letter in mzml_files[0]]
    OUTPUT_NAME = "".join(str_array)
    while OUTPUT_NAME not in mzml_files[-1]:
        str_array.pop(-1)
        OUTPUT_NAME = "".join(str_array)

    #Compute max number of pixels in each scan filter to construct pixel grids
    max_x_pixels = {}
    y_pixels = len(spectrum_counts)
    contender_idx=[]
    if isinstance(scan_filts,str):
        scan_filts = [scan_filts]

    for filt in scan_filts:
        max_x = 0
        idx =-1
        for spec_file in spectrum_counts:
            idx += 1
            if spec_file[filt] > max_x:
                max_x = spec_file[filt]
                contender_idx.append(idx)
        max_x_pixels[filt] = max_x

    #Retrieve max times for time-alignment on longest spectra, build ideal time array
    max_times = []
    for idx in contender_idx:
        tmp = pymzml.run.Reader(os.path.join(PATH,mzml_files[idx]))
        scan_time = get_final_scan_time(tmp)
        max_times.append(scan_time)

    time_targets={}
    iter = -1
    for key in max_x_pixels:
        iter += 1
        time_array = np.linspace(0,max_times[iter],max_x_pixels[key])
        time_targets[key] = time_array

    #Initiate imzmL objects
    image_files = {}
    output_files ={}
    for filt_idx, filt in enumerate(scan_filts):
        if filt == None:
            image_files[filt]=imzmlw.ImzMLWriter(output_filename=fr"{OUTPUT_NAME}_None",mode="processed",polarity=polarities[filt_idx])
        else:
            image_files[filt] = imzmlw.ImzMLWriter(output_filename=fr"{OUTPUT_NAME}_{filt.split(".")[0]}",mode="processed",polarity=polarities[filt_idx])
        output_files[filt]=(fr"{OUTPUT_NAME}_{filt}")

    num_duplicates = 0
    num_total = 0
    #Build image grid, write directly to an imzML
    for y_row in range(y_pixels):
        active_file = pymzml.run.Reader(os.path.join(PATH,mzml_files[y_row]))
        for filt in scan_filts:
            tmp_times = []
            spec_list = []
            for spectrum in active_file:
                if spectrum["filter string"] == filt:
                    tmp_times.append(spectrum.scan_time_in_minutes())
                    spec_list.append(spectrum)
                elif list_type:
                    tmp_times.append(spectrum.scan_time_in_minutes())
                    spec_list.append(spectrum)

            pvs_ppm_off = 0
            used_idx = []
            
            for x_row in range(max_x_pixels[filt]):
                align_time = time_targets[filt][x_row]
                time_diffs = abs(tmp_times - align_time)
                match_idx = np.where(time_diffs == min(time_diffs))[0][0]
                num_total += 1
                if zero_indexed:
                    x_coord = x_row
                    y_coord = y_row
                else:
                    x_coord = x_row + 1
                    y_coord = y_row + 1
                
                if scan_mode == "x-scan":
                    coords = (x_coord, y_coord, 1)
                elif scan_mode == 'y-scan':
                    coords = (y_coord, x_coord, 1)
                
                if not match_idx in used_idx:
                    used_idx.append(match_idx)
                    if len(used_idx) > 15:
                        used_idx.pop(0)

                    match_spectra = spec_list[match_idx]
                    [recalibrated_mz, pvs_ppm_off] = recalibrate(mz=match_spectra.mz, int=match_spectra.i,lock_mz=LOCK_MASS,search_tol=TOLERANCE,ppm_off=pvs_ppm_off)
                    if len(recalibrated_mz) != 0:
                        image_files[filt].addSpectrum(recalibrated_mz,match_spectra.i,coords)
                else:
                    num_duplicates += 1
                    if not no_duplicating:
                        match_spectra = spec_list[match_idx]
                        [recalibrated_mz, pvs_ppm_off] = recalibrate(mz=match_spectra.mz, int=match_spectra.i,lock_mz=LOCK_MASS,search_tol=TOLERANCE,ppm_off=pvs_ppm_off)
                        if len(recalibrated_mz) != 0:
                            image_files[filt].addSpectrum(recalibrated_mz,match_spectra.i,coords,userParams=[{"name":"DuplicatedSpectrum","value":"True"}])

                    # print(f"Duplicated pixel detected - {num_duplicates} / {num_total} ({num_duplicates * 100 / num_total:.2f}%)")


        ##Update progress bar in the GUI as each mzML finishes
        progress = int(y_row*100/(y_pixels-1)) 

        if progress > 0 and progress_target != None:   
            progress_target.stop() 
            progress_target.config(mode="determinate",value=int(y_row*100/(y_pixels-1)))

    ##Close imzML objects for downstream annotation
    update_files = os.listdir()
    update_files.sort()

    for filt in scan_filts:
        image_files[filt].close()

def imzML_metadata_process(model_files:str,x_speed:float,y_step:float,path:str,tgt_progress=None, scan_mode:str = "x-scan"):
    """Manages annotation of imzML files with metadata from source mzML files and user-specified fields (GUI). 
    
    :param model_files: Directory to the folder containing mzML files
    :param x_speed: scan speed in the x-direction, µm/sec
    :param y_step: step between strip lines, µm
    :param path: path to the directory where imzML files should be stored after annotation
    :param tgt_progress: Tkinter progress bar object to update as the process continues
    :param scan_mode: Whether the data was acquired in 'x-scan' or 'y-scan' mode."""
    
    global OUTPUT_NAME, time_targets

    ##Retrieve and sort files from the working directory (imzML) and model file directory (mzML)
    update_files = os.listdir()
    update_files.sort()

    scan_filts=[]
    polarities = []
    ms_levels = []
    model_file_list = os.listdir(model_files)
    model_file_list.sort()

    ##Ignore hidden files
    while model_file_list[0].startswith("."):
        model_file_list.pop(0)

    ##Extract filter strings from the first mzML source file
    tmp = pymzml.run.Reader(os.path.join(model_files,model_file_list[0]))
    for spectrum in tmp:
        if spectrum["filter string"] not in scan_filts:
            scan_filts.append(spectrum["filter string"])
            ms_levels.append(int(spectrum['MS:1000511'])) #record ms_level
            if spectrum["MS:1000129"]: #record polarities
                polarities.append("negative") 
            elif spectrum["MS:1000130"]:
                polarities.append("positive")
    
        # final_time_point = spectrum["scan time"]
        final_time_point = spectrum.scan_time_in_minutes()

    ##Extract common output name based on common characters in first and last mzML file
    str_array = [letter for letter in model_file_list[0]]
    OUTPUT_NAME = "".join(str_array)
    while OUTPUT_NAME not in model_file_list[-1]:
        str_array.pop(-1)
        OUTPUT_NAME = "".join(str_array)


    ##Loop to annotate each imzML file
    iter = 0
    for filt_idx, filt in enumerate(scan_filts):
        #Find the target file based on a filter string match
        iter+=1
        for file in update_files:
            if ".imzML" in file:
                partial_filter_string = file.split(OUTPUT_NAME+"_")[-1].split(".imzML")[0]
                if partial_filter_string == "None":
                    target_file = file
                elif partial_filter_string in filt:
                    target_file = file

        ##Calls the actual annotation function
        annotate_imzML(
                    annotate_file=target_file,
                    SRC_mzML=os.path.join(model_files,model_file_list[0]),
                    scan_time=final_time_point,
                    filter_string=filt,
                    x_speed=x_speed,
                    y_step=y_step,
                    ms_level = ms_levels[filt_idx],
                    polarity = polarities[filt_idx],
                    scan_mode = scan_mode)

        ##Update progress bar in the GUI
        progress = int(iter*100/len(scan_filts))
        if progress > 0 and tgt_progress != None:
            tgt_progress.stop()
            tgt_progress.config(mode="determinate",value=progress)

    ##After conversion is complete, clean up files by putting the annotated imzML files in a new directory within the datafile folder           
    move_files(OUTPUT_NAME,path)

def move_files(probe_txt:str,path:str):
    """Moves files matching a search string (probe_txt) in the current working directory into the specified directory in a new folder called 'probe_txt'
    
    :param probe_txt: The search string to find in the current directory.
    :param path: The target directory to move files to"""
    files = os.listdir()
    new_directory = os.path.join(path, probe_txt)
    try:
        print(new_directory)
        os.makedirs(new_directory, exist_ok=True)
    except:
        pass
    
    for file in files:
        if probe_txt in file:
                try:
                    shutil.copy2(file, os.path.join(new_directory,file))
                except Exception as e:
                    logger.info("Copy object claimed failure")
                finally:
                    os.remove(file)


def annotate_imzML(annotate_file:str,SRC_mzML:str,scan_time:float=0.001,filter_string:str="none given",x_speed:float=1,y_step:float=1,polarity:str="positive",ms_level:int=1, scan_mode:str = 'x-scan'):
    """Takes pyimzml output imzML files and annotates them using GUI inputs and the corresponding mzML source file, then cleans up errors in the imzML structure
    for compatibility with imzML viewers/processors.

    :param annotate_file: the imzML file to be annotated
    :param SRC_mzML: the source file to pull metadata from
    :param scan_time: The total time required to scan across the imaging area at speed x_speed (mins)
    :param filter_string: what scan filter is actually captured  (default = "none given")
    :param x_speed: The scan speed across the imaging area during linescans (µm/s)
    :param y_step: The distance between adjacent strip lines across the imaging area (µm/s)
    :param scan_mode: Whether the data was acquired in 'x-scan' or 'y-scan' mode.
    """

    #Error handling for when scan filter extraction fails
    result_file = annotate_file
    if filter_string == None:
        filter_string = "None"

    #Retrieve data from source mzml
    with open(SRC_mzML) as file:
        data = file.read()
    data = BeautifulSoup(data,'xml')

    #Grab instrument model from the source mzML
    try:
        instrument_model = data.referenceableParamGroup.cvParam.get("name")
    except:
        instrument_model = "Could not find"

    #Open un-annotated imzML
    with open(annotate_file) as file:
        data_need_annotation = file.read()
    data_need_annotation = BeautifulSoup(data_need_annotation,'xml')

    #Replace template data with key metadata from mzML
    replace_list = ['instrumentConfigurationList']
    for replace_item in replace_list:
        data_need_annotation.find(replace_item).replace_with(data.find(replace_item))

    #Write instrument model to imzML, filter string
    data_need_annotation.instrumentConfigurationList.instrumentConfiguration.attrs['id']=instrument_model
    new_tag = Tag(builder=data_need_annotation.builder,
                  name="cvParam",
                  attrs={'accession':'MS:1000031',"cvRef":"MS","name":instrument_model})
    # new_tag = data_need_annotation.new_tag("cvParam", accession="MS:1000031", cvRef="MS")
    data_need_annotation.instrumentConfigurationList.instrumentConfiguration.append(new_tag)

    #Remove empty instrument ref from imzML template
    for paramgroup in data_need_annotation.select("referenceableParamGroupRef"):
        if paramgroup['ref']=="CommonInstrumentParams":
            paramgroup.extract()
    
    for cvParam in data_need_annotation.select("cvParam"):
        if cvParam["accession"]=="MS:1000530":
            del cvParam["value"]
        if cvParam["accession"]=="IMS:1000411":
            cvParam["accession"]="IMS:1000413"
            cvParam["name"]="flyback"
        ##Future y-scan mode - accession:
#         [Term]
# id: IMS:1000481
# name: vertical line scan
# def: "The scanning line is a vertical one." [COMPUTIS:IMS]
# is_a: IMS:1000048 ! Scan Type



    for tag in data_need_annotation.referenceableParamGroupList:
        if "scan1" in str(tag):
            for tag2 in tag:
                if "MS:1000512" in str(tag2):
                    tag2["value"] = filter_string
                    

        
    #Read pixel grid information from imzML
    for tag in data_need_annotation.scanSettingsList.scanSettings:
        if 'cvParam' in str(tag):
            if tag.get("accession") == "IMS:1000042": #num pixels x
                x_pixels = tag.get("value")
            elif tag.get("accession") == "IMS:1000043": #num pixels y
                y_pixels = tag.get("value")

    #Calculate pixel sizes and overall dimensions from size of pixel grid, scan speed, step sizes
    if scan_mode == "x-scan":
        x_pix_size = float(x_speed * scan_time * 60 / float(x_pixels))
        y_pix_size = y_step
    elif scan_mode == "y-scan":
        y_pix_size = float(x_speed * scan_time * 60 / float(y_pixels))
        x_pix_size = y_step
    
    max_x = int(x_pix_size * float(x_pixels))
    max_y = int(y_pix_size * float(y_pixels))



    ##TODO - Test changing this into 'pixel size x' instead for compatibility with all, if everyone still works will leave as default. Otherwise another advanced tab for mutually exclusive compatibility?
    accessions = ["IMS:1000046", "IMS:1000047", "IMS:1000044", "IMS:1000045"]
    names = ["pixel size x", "pixel size y", "max dimension x", "max dimension y"]
    values = [x_pix_size, y_pix_size, max_x, max_y]

    #Actual insertion of data - need to write string into a beautiful soup object with NO FORMATTING to append it
    for i in range(4):
        append_item = f'<cvParam cvRef="IMS" accession="{accessions[i]}" name="{names[i]}" value="{values[i]}"/>\n'
        append_item = BeautifulSoup(append_item,'xml')
        data_need_annotation.scanSettingsList.scanSettings.append(append_item)


    for cvParam in data_need_annotation.select("cvParam"):
        if cvParam["accession"] in accessions:
            cvParam["unitCvRef"]="UO"
            cvParam["unitAccession"]="UO:0000017"
            cvParam["unitName"]="micrometer"

                    
    ##Specify imzML writer involvement and version in the resulting imzML
    for soft_list in data_need_annotation.select("softwareList"):
        count = int(soft_list.attrs['count']) + 1
        new_tag = Tag(builder=data_need_annotation.builder,
                    name = "software",
                    attrs = {'id':'imzML_Writer',"version":__version__})
        descr_tag = Tag(builder=data_need_annotation.builder,
                    name = "cvParam",
                    attrs = {'accession':'MS:1000799',"cvRef":"MS","name":"Custom unreleased software tool","value":f"imzML Writer v{__version__}"})
        

        soft_list.append(new_tag)
        for software in soft_list.select("software"):
            if software.attrs["id"] == "imzML_Writer":
                software.append(descr_tag)

        soft_list.attrs['count'] = count        

    #Write the new file
    with open(result_file,'w') as file:
        file.write(str(data_need_annotation.prettify()))


def annotate_from_model_imzML(model:str, to_annotate:str):
    """Annotates an imzML file based on an example file - intended for conjunction with write_masked_imzML to preserve metadata"""

    with open(model) as file:
        data = file.read()
    source_imzML = BeautifulSoup(data,'xml')

    with open(to_annotate) as file:
        data = file.read()
    needs_annotation_imzML = BeautifulSoup(data,'xml')

    try:
        instrument_model = source_imzML.instrumentConfigurationList.instrumentConfiguration.attrs['id']
    except:
        instrument_model = "Not found"
    finally:
        needs_annotation_imzML.instrumentConfigurationList.instrumentConfiguration.attrs['id'] = instrument_model

    replace = 'instrumentConfigurationList'
    needs_annotation_imzML.find(replace).replace_with(source_imzML.find(replace))


    new_tag = Tag(builder=needs_annotation_imzML.builder,
                  name="cvParam",
                  attrs={'accession':'MS:1000031',"cvRef":"MS","name":instrument_model})
    needs_annotation_imzML.instrumentConfigurationList.instrumentConfiguration.append(new_tag)

    #Remove empty instrument ref from imzML template
    for paramgroup in needs_annotation_imzML.select("referenceableParamGroupRef"):
        if paramgroup['ref']=="CommonInstrumentParams":
            paramgroup.extract()
    
    for cvParam in needs_annotation_imzML.select("cvParam"):
        if cvParam["accession"]=="MS:1000530":
            del cvParam["value"]
        if cvParam["accession"]=="IMS:1000411":
            cvParam["accession"]="IMS:1000413"
            cvParam["name"]="flyback"
    
    filter_string = source_imzML.find("cvParam", accession="MS:1000512")['value']
    for tag in needs_annotation_imzML.referenceableParamGroupList:
        if "scan1" in str(tag):
            for tag2 in tag:
                if "MS:1000512" in str(tag2):
                    tag2["value"] = filter_string
    
    x_pix_size = source_imzML.find("cvParam", accession="IMS:1000046")['value']
    y_pix_size = source_imzML.find("cvParam", accession="IMS:1000047")['value']
    max_x = source_imzML.find("cvParam", accession="IMS:1000044")['value']
    max_y = source_imzML.find("cvParam", accession="IMS:1000045")['value']

    accessions = ["IMS:1000046", "IMS:1000047", "IMS:1000044", "IMS:1000045"]
    names = ["pixel size x", "pixel size y", "max dimension x", "max dimension y"]
    values = [x_pix_size, y_pix_size, max_x, max_y]

    for i in range(4):
        append_item = f'<cvParam cvRef="IMS" accession="{accessions[i]}" name="{names[i]}" value="{values[i]}"/>\n'
        append_item = BeautifulSoup(append_item,'xml')
        needs_annotation_imzML.scanSettingsList.scanSettings.append(append_item)


    for cvParam in needs_annotation_imzML.select("cvParam"):
        if cvParam["accession"] in accessions:
            cvParam["unitCvRef"]="UO"
            cvParam["unitAccession"]="UO:0000017"
            cvParam["unitName"]="micrometer"

    for soft_list in needs_annotation_imzML.select("softwareList"):
        count = int(soft_list.attrs['count']) + 1
        new_tag = Tag(builder=needs_annotation_imzML.builder,
                    name = "software",
                    attrs = {'id':'imzML_Writer',"version":__version__})
        descr_tag = Tag(builder=needs_annotation_imzML.builder,
                    name = "cvParam",
                    attrs = {'accession':'MS:1000799',"cvRef":"MS","name":"Custom unreleased software tool","value":f"imzML Writer v{__version__}"})

        soft_list.append(new_tag)
        for software in soft_list.select("software"):
            if software.attrs["id"] == "imzML_Writer":
                software.append(descr_tag)

        soft_list.attrs['count'] = count

    #Write the new file
    with open(to_annotate,'w') as file:
        file.write(str(needs_annotation_imzML.prettify())) 
    
    



def write_masked_imzML(source_file:str,roi_mask:np.array,save_dir:str=None) -> str:
    """Rewrites the specified imzML file as masked by the ROI, useful to truncate out only the tissue for reduced file sizes
    
    :param source_file: path to the source imzML
    :param roi_mask: numpy array matching dimensions of source file, where 0 indicates an excluded pixel and 1 is an included pixel
    :param save_dir: Where to save the resulting imzML, defaults to the same directory as the source file
    
    :return: Full file path to the resulting imzML"""

    if not save_dir:
        save_dir = os.path.dirname(source_file)

    filename = Path(source_file).stem
    new_filename = f"{filename}-masked.imzML"
    new_filepath = os.path.join(save_dir,new_filename)

    with warnings.catch_warnings(action='ignore'):
        with imzmlp.ImzMLParser(filename=source_file,parse_lib='lxml') as img:
            with imzmlw.ImzMLWriter(new_filepath, mode='processed') as new_imzml:
                zero_offset = 1
                for idx, (x,y,z) in enumerate(img.coordinates):
                    if x == 0 or y == 0:
                        zero_offset = 0

                    if roi_mask[y-zero_offset,x-zero_offset] == 1:
                        mzs, ints = img.getspectrum(idx)
                        new_imzml.addSpectrum(mzs,ints,(x,y,z))
    
    annotate_from_model_imzML(source_file, new_filepath)

    
    

    





    