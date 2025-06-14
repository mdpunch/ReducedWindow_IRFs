# %% [markdown]
# # Read Prod6 simtel file and test reduced readout window effect
#
# Use env variables for PROD_DIR and OUT_DIR, if they exist.
#
# If not interactive, use command line arguments, with defaults.

# %%
from ctapipe.io import EventSource,DataWriter
from ctapipe import utils
from matplotlib import pyplot as plt
import numpy as np
# %matplotlib inline

# %%
from ctapipe.visualization import CameraDisplay
from ctapipe.coordinates import EngineeringCameraFrame
from ctapipe.calib import CameraCalibrator
from ctapipe.instrument import SoftwareTrigger
from ctapipe.image import tailcuts_clean

# %%
from ctapipe.image import (
     ImageProcessor,
     camera_to_shower_coordinates,
     concentration_parameters,
     hillas_parameters,
     leakage_parameters,
     number_of_islands,
     timing_parameters,
     toymodel,
 )
from traitlets.config import Config
from ctapipe.reco import ShowerProcessor

# %%
from astropy import units as u

# %%
from astropy.coordinates import AltAz, angular_separation

# %%
import os
import sys

# %%
from glob import glob,iglob

# %%
import argparse

# %%
from ctapipe.version import version

# %%
version

# %% [markdown]
# ## Get Env variables

# %%
if hasattr(sys,'ps1'):
    site = "LaPalma"
    particle = "gamma-diffuse"
    ReduceWindow = True
else:
    parser = argparse.ArgumentParser(
                    prog='Make_reduced_Readout_window',
                    description='Makes DL2(?) files with a reduced readout window (or not)',
                    #epilog='',
                    )
    parser.add_argument("--site","-s",help="Choose site: LaPalma or Paranal (default LaPalma)",
                       nargs='?', default='LaPalma')
    parser.add_argument("--particle","-p",help="Choose particle: gamma, gamma-diffuse, proton, electron",
                       nargs='?', default='gamma')
    parser.add_argument("--reduced-window","-r",action=argparse.BooleanOptionalAction,
                        default=True,help="Hardwired reduced window, or standard as simulated")
    args = parser.parse_args()
    #print("args:",args)
    
    site = args.site
    particle = args.particle
    ReduceWindow = True if args.reduced_window else False
    if particle not in ["gamma", "gamma-diffuse", "proton", "electron"]:
        print(f"Error:\n" 
              f"  Particle type \"{particle}\" unknown. \n"
               "  Must choose particle type in : gamma, gamma-diffuse, proton, electron")
        sys.exit()

# %%
# If environment variable exists, use it
try:
    PROD_DIR = '{PROD_DIR}'.format(**os.environ)
except KeyError:
    PROD_DIR = f"/media/punch/CTA_Data/Prod6/LaPalma/2025/{particle}"

try:
    OUT_DIR = '{OUT_DIR}'.format(**os.environ)
except KeyError:
    OUT_DIR = "/scr/punch/CTA/Prod6/LaPalma/2025/"+f"{particle}/"

# %%
print("Running with:\n",
      site,particle,"ReducedWindow" if ReduceWindow else "StandardWindow","\n",
      PROD_DIR,"\n",OUT_DIR)

# %% [markdown]
# ## Forget about CTAO-S

# %%
#gamma_file = "/scr/punch/CTA/Prod6/Paranal/gamma_20deg_0deg_run000001___cta-prod6-2147m-Paranal-dark.simtel.zst"
#proton_file = "/scr/punch/CTA/Prod6/Paranal/proton_20deg_0deg_run000001___cta-prod6-2147m-Paranal-dark.simtel.zst"

# %% [markdown]
# ## CTAO-N files

# %%
if particle != "gamma-diffuse":
    simtel_files = glob(PROD_DIR+f"/{particle}*.simtel.zst")
    if particle == "gamma": # Sift out any diffuse files there might be in there
        simtel_files = [sf for sf in simtel_files if not "cone" in sf]
else:
    simtel_files = glob(PROD_DIR+f"/gamma*cone*.simtel.zst")

# %%
if len(simtel_files):
    print(f"{len(simtel_files)} files found.")
else:
    if os.path.isdir(PROD_DIR):
        print(f"Error: No {particle} files found in {PROD_DIR}.")
    else:
        print(f"Error: Prod directory {PROD_DIR} does not exist.")
    sys.exit()

# %%
if not os.path.isdir(OUT_DIR):
    print(f"Error: Output directory {OUT_DIR} does not exist.")
else:
    print(f"Writing outputs in {OUT_DIR}.")

# %%
first_file = simtel_files[0]

# %%
#simtel_files = simtel_files[17:]

# %%
if "palma" in site.lower():
    # This looks something like the layout in 
    # https://indico.cta-observatory.org/event/3962/contributions/32718/attachments/21055/29677/20220310_NorthernArray.pdf
    tels_alpha = [1,2,3,4,5,6,7,8,9,10,11,14,19]
else:
    # 
    # https://indico.cta-observatory.org/event/4368/contributions/36020/attachments/22589/32376/AD-6%20INFRA%20DES%20100-058-S.pdf
    tels_alpha = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,
                  38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,
                  58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77]  # Maybe should stop at (including) 74?? https://github.com/Eventdisplay/Eventdisplay_AnalysisFiles_CTA/blob/a534e533199b0305b86d4006956f032388636b56/DetectorGeometry/CTA.prod6S.Am-0LSTs14MSTs37SSTs.lis#L4


# %%
source = EventSource(first_file,allowed_tels=tels_alpha)
#source = EventSource(proton_file)


# %%
source.allowed_tels

# %%
#sub_alpha = source.subarray.select_subarray(tel_ids=tels_alpha)
#sub_alpha = source.subarray.select_subarray(tel_ids=[2,3,4])
#ArrayDisplay(sub_alpha)
#sub_alpha.peek()
source.subarray.peek()
plt.xlim([-300,400])
plt.ylim([-350,350])
#
plt.show(block=False)
from time import sleep
sleep(10)

# %% [markdown]
# ## From https://ctapipe.readthedocs.io/en/v0.20.0/auto_examples/tutorials/ctapipe_overview.html
#
# But, thresholds taken from ctapipe-process base_config.yaml
#
# And subarray as sub_alpha

# %%
source = EventSource(first_file,allowed_tels=tels_alpha)
#source = EventSource(proton_file)

# %%
source = EventSource(first_file,allowed_tels=tels_alpha)
event_iter = iter(source)

# %%
source.subarray

# %%
tels_alpha

# %%
#sub_alpha = source.subarray.select_subarray(tels_alpha)

# %%
#sub_alpha

# %%
event = next(event_iter)

# %%
event.trigger.tels_with_trigger

# %%
calibrator = CameraCalibrator(subarray=source.subarray)

# %%

# %%
calibrator(event)

# %%
source.close()

# %% [markdown]
# ## Main Loop
# ### Adapting from https://ctapipe.readthedocs.io/en/latest/auto_examples/tutorials/ctapipe_overview.html
#
# But then using the configs for running on the grid: https://gitlab.cta-observatory.org/cta-computing/dpps/datapipe/pipeline-configurations
# ... which I've saved here, so can read in.


# %%
import yaml

# %%
from pprint import pprint

# %%
with open("dl0_to_dl1.yml") as stream:
    try:
        dl0_to_dl1 = yaml.safe_load(stream)
        if hasattr(sys,'ps1'):
            pprint(dl0_to_dl1)
    except yaml.YAMLError as exc:
        print(exc)

# %%
with open("dl1_to_dl2.yml") as stream:
    try:
        dl1_to_dl2 = yaml.safe_load(stream)
        if hasattr(sys,'ps1'):
            pprint(dl1_to_dl2)
    except yaml.YAMLError as exc:
        print(exc)

# %%
from copy import deepcopy


# %%
def ReadoutWindowReducer(event,subarray):
    """
    Fixed Readout Window Reducer
    (Fixed over all camera)
    Reduce the readout window for MSTs and LSTs.
    Hardcoded for now, with for MSTs [12:27] and LSTs [10:30],
    so a reduction of a factor of 4 for MST-NectarCAM, and factor 2 for LST
    """

    for tel_id in event.trigger.tels_with_trigger:
        # Maybe this would be faster? tel in subarray.get_tel_ids_for_type("MST_MST_NectarCam"):
        cam_name_lower = source.subarray.tel[tel_id].camera_name.lower()
        if "nectarcam" == cam_name_lower:
            event.r0.tel[tel_id].waveform = event.r0.tel[tel_id].waveform[:, :, 12:27]
            event.r1.tel[tel_id].waveform = event.r1.tel[tel_id].waveform[:, :, 12:27]
        elif "lstcam" == cam_name_lower: 
            event.r0.tel[tel_id].waveform = event.r0.tel[tel_id].waveform[:, :, 10:30]
            event.r1.tel[tel_id].waveform = event.r1.tel[tel_id].waveform[:, :, 10:30]
        else:
            print(f"For {tel_id}, unknown camera type {source.subarray.tel[tel_id].camera_name}!!!")


# %%
from pathlib import Path

# %%
for num_file,in_file in enumerate(simtel_files):
    
    #for ReduceWindow in [False,True]:

        in_path = Path(in_file)
        print(f"File {num_file+1} of {len(simtel_files)}:",
              in_path.stem,"ReducedWindow" if ReduceWindow else "StandardWindow")

        out_file = in_path.stem[:-7]
        
        #ReduceWindow = True # False # 
        
        out_file = OUT_DIR+out_file
        if ReduceWindow:
           out_file += ".redwindow.h5"
        else:
           out_file += ".stdwindow.h5"
        
        source = EventSource(in_file,allowed_tels=tels_alpha)
        
        image_processor_config = Config(dl1_to_dl2["ImageProcessor"])
        shower_processor_config = Config(dl1_to_dl2["ShowerProcessor"])
        software_trigger_config = Config(dl1_to_dl2["SoftwareTrigger"])
                                     
        software_trigger = SoftwareTrigger(subarray=source.subarray, config=software_trigger_config)
        
        calibrator = CameraCalibrator(subarray=source.subarray)
        
        image_processor = ImageProcessor(
             subarray=source.subarray, config=image_processor_config
        )
        
        shower_processor = ShowerProcessor(subarray=source.subarray)
        horizon_frame = AltAz()
        
        with DataWriter(source, output_path=out_file, overwrite=True, write_dl1_parameters=True, write_dl2=True) as writer:
        
             for event in source:
                 event_count = event.count
                 if not event_count%1000:
                     print(event_count, end=" ")
                 if software_trigger(event):
                     if ReduceWindow:
                         ReadoutWindowReducer(event,subarray=source.subarray)
                     calibrator(event)
                     image_processor(event)
                     shower_processor(event)
        
                     writer(event)
        
                     if len(event.trigger.tels_with_trigger) > 9:
                         plotting_event = deepcopy(event)

             # Added to get the shower distribution histograms in the file
             writer.write_simulated_shower_distributions(source.simulated_shower_distributions)
             print()

# %% [markdown]
# ## Show some results on the last file

# %%
from ctapipe.io import DataWriter, EventSource, TableLoader

# %%
loader = TableLoader(out_file)
events = loader.read_subarray_events()

# %%
events.colnames

# %%
theta = angular_separation(
     events["HillasReconstructor_az"].quantity,
     events["HillasReconstructor_alt"].quantity,
     events["true_az"].quantity,
     events["true_alt"].quantity,
)

plt.hist(theta.to_value(u.deg) ** 2, bins=500, range=[0, 0.1])
plt.xlabel(r"$\theta² / deg²$")
None

# %%
from ctapipe.visualization import ArrayDisplay, CameraDisplay

angle_offset = plotting_event.pointing.array_azimuth

plotting_hillas = {
    tel_id: dl1.parameters.hillas for tel_id, dl1 in plotting_event.dl1.tel.items()
}

plotting_core = {
    tel_id: dl1.parameters.core.psi for tel_id, dl1 in plotting_event.dl1.tel.items()
}


disp = ArrayDisplay(source.subarray)

disp.set_line_hillas(plotting_hillas, plotting_core, 500)

plt.scatter(
     plotting_event.simulation.shower.core_x,
     plotting_event.simulation.shower.core_y,
     s=200,
     c="k",
     marker="x",
     label="True Impact",
)
plt.scatter(
     plotting_event.dl2.stereo.geometry["HillasReconstructor"].core_x,
     plotting_event.dl2.stereo.geometry["HillasReconstructor"].core_y,
     s=200,
     c="r",
     marker="x",
     label="Estimated Impact",
)

plt.legend(loc="lower right")
plt.xlim(-350, 350)
plt.ylim(-375, 225)
None

# %%

# %%
