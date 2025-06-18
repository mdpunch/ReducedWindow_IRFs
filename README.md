# ReducedWindow_IRFs

Testing the effect of reducing readout windows on the IRFs.

For now, the readout windows reduction is hardwired (based on what is seen in simulations), with for MSTs [12:27] and LSTs [10:30] (so, MST-NectarCAM window divided by a factor 4, and the LSTs by a factor 2).

Using LaPalma alpha configuration.

## Run Make_reduced_Readout_window

Choose tels_alpha for CTAO-N.

Process simtel files, reducing the window as specified (can also be run without window reduction, as a check).
For each event, run `ReadoutWindowReducer`, `calibrator`, `image_processor`, `shower_processor`, and then write dl1_parameters and dl2.
(see `dl0_to_dl1.yml` and `dl1_to_dl2.yml` for the configs used).

e.g. run:
```bash
python3 Make_reduced_Readout_window_file.py -p gamma -r
python3 Make_reduced_Readout_window_file.py -p gamma --no-r
python3 Make_reduced_Readout_window_file.py -p gamma-diffuse -r
python3 Make_reduced_Readout_window_file.py -p gamma-diffuse --no-r
python3 Make_reduced_Readout_window_file.py -p proton -r
python3 Make_reduced_Readout_window_file.py -p proton --no-r
python3 Make_reduced_Readout_window_file.py -p electron -r
python3 Make_reduced_Readout_window_file.py -p electron --no-r
```
(uses default directories, but otherwise specify $PROD_DIR and $OUT_DIR environmental variables).
Command line arguments for `--site, --particle, --reduced-window`, see command help.

##  Getting the data

> Max says
> 
> * 4 gamma diffuse datasets (train energy regressor, train particle classifier, optimize cuts, sensitivity & IRFs)
> * 3 proton datasets (train particle classifier, optimize cuts, sensitivity & IRFs)
> * 2 electron datasets (optimize cuts, sensitivity & IRFs)
> The separate gamma diffuse dataset for training the energy regressor is only needed if you want to use the energy as feature in the particle classifier, but i'd recommend it.

> You could add
> 
>* 2 gamma point-like datasets (optimize cuts, sensitivity & IRFs)
> if you are interested only in point sources in the center of the field of view, where we have higher statistics thanks to the point like simulations.

## Data used:

*  `gamma`: 50
	* Separate into 2x25
* `gamma-diffuse`: 40
	* Separate into 4x10 files
* `proton`: 60
	* Separate into 3x20
* `electron`: 32
	* Separate into 2x16



## Making File Lists:

```bash
export OUTPUT_DIR=/scr/punch/CTA/Prod6/LaPalma/2025/
ls $OUTPUT_DIR/gamma/ga*std* | split -n 2 -a 1 - gamma_std_
ls $OUTPUT_DIR/gamma/ga*red* | split -n 2 -a 1 - gamma_red_
ls $OUTPUT_DIR/gamma-diffuse/ga*std* | split -n 4 -a 1 - gamma_diffuse_std_
ls $OUTPUT_DIR/gamma-diffuse/ga*red* | split -n 4 -a 1 - gamma_diffuse_red_
ls $OUTPUT_DIR/proton/pr*red* | split -n 3 -a 1 - proton_red_
ls $OUTPUT_DIR/proton/pr*std* | split -n 3 -a 1 - proton_std_
ls $OUTPUT_DIR/electron/el*red* | split -n 2 -a 1 - electron_red_
ls $OUTPUT_DIR/electron/el*std* | split -n 2 -a 1 - electron_std_
```

## Merge the files in the lists

### Merge Files !!! Execute this twice, with either std or red in STD_OR_RED

```bash
export STD_OR_RED=red
# Gamma (diffuse) train energy
ctapipe-merge $(cat gamma_diffuse_${STD_OR_RED}_a) --output $OUTPUT_DIR/gamma_diffuse_merged_train_en.$STD_OR_RED.dl2.h5 --overwrite
# Gamma (diffuse) train classifier
ctapipe-merge $(cat gamma_diffuse_${STD_OR_RED}_b) --output $OUTPUT_DIR/gamma_diffuse_merged_train_cls.$STD_OR_RED.dl2.h5 --overwrite
ctapipe-merge $(cat gamma_diffuse_red_b) --output $OUTPUT_DIR/gamma_diffuse_merged_train_cls.red.dl2.h5 --overwrite
# Gamma (diffuse) optimize cuts
ctapipe-merge $(cat gamma_diffuse_${STD_OR_RED}_c) --output $OUTPUT_DIR/gamma_diffuse_merged_optimize_cuts.$STD_OR_RED.dl2.h5 --overwrite
ctapipe-merge $(cat gamma_diffuse_red_c) --output $OUTPUT_DIR/gamma_diffuse_merged_optimize_cuts.red.dl2.h5 --overwrite
# Gamma (diffuse) IRFs
ctapipe-merge $(cat gamma_diffuse_${STD_OR_RED}_d) --output $OUTPUT_DIR/gamma_diffuse_merged_irfs.$STD_OR_RED.dl2.h5 --overwrite
# Proton train classifier
ctapipe-merge $(cat proton_${STD_OR_RED}_a) --output $OUTPUT_DIR/proton_merged_train_cls.$STD_OR_RED.dl2.h5 --overwrite
# Proton optimize cuts
ctapipe-merge $(cat proton_${STD_OR_RED}_b) --output $OUTPUT_DIR/proton_merged_optimize_cuts.$STD_OR_RED.dl2.h5 --overwrite
# Proton IRFs
ctapipe-merge $(cat proton_${STD_OR_RED}_c) --output $OUTPUT_DIR/proton_merged_irfs.$STD_OR_RED.dl2.h5 --overwrite
# Electron (diffuse) optimize cuts
ctapipe-merge $(cat electron_${STD_OR_RED}_a) --output $OUTPUT_DIR/electron_merged_optimize_cuts.$STD_OR_RED.dl2.h5 --overwrite
# Electron (diffuse) IRFs
ctapipe-merge $(cat electron_${STD_OR_RED}_b) --output $OUTPUT_DIR/electron_merged_irfs.$STD_OR_RED.dl2.h5 --overwrite
# Gamma (point-like) optimize cuts
ctapipe-merge $(cat gamma_${STD_OR_RED}_a) --output $OUTPUT_DIR/gamma_point_merged_optimize_cuts.$STD_OR_RED.dl2.h5 --overwrite
# Gamma (point-like) IRFs
ctapipe-merge $(cat gamma_${STD_OR_RED}_b) --output $OUTPUT_DIR/gamma_point_merged_irfs.$STD_OR_RED.dl2.h5 --overwrite
```

### Configs
```bash
export REG_CONF_FILE=./train_energy_regressor.yml 
export CLF_CONF_FILE=./train_particle_classifier.yml 
export DISP_CONF_FILE=./train_disp_reconstructor.yml
```

```bash
export STD_OR_RED=red
export INPUT_GAMMA_EN_FILE=$OUTPUT_DIR/gamma_diffuse_merged_train_en.$STD_OR_RED.dl2.h5 
export INPUT_GAMMA_CLF_FILE=$OUTPUT_DIR/gamma_diffuse_merged_train_cls.$STD_OR_RED.dl2.h5
export EVAL_GAMMA_FILE=$OUTPUT_DIR/gamma_diffuse_merged_optimize_cuts.$STD_OR_RED.dl2.h5 
export INPUT_PROTON_FILE=$OUTPUT_DIR/proton_merged_train_cls.$STD_OR_RED.dl2.h5
export EVAL_PROTON_FILE=$OUTPUT_DIR/proton_merged_irfs.$STD_OR_RED.dl2.h5 
export EVAL_ELECTRON_FILE=$OUTPUT_DIR/electron_merged_irfs.$STD_OR_RED.dl2.h5 
```

## The following commands directly from https://ctapipe.readthedocs.io/en/latest/user-guide/tools/dl2_guide.html

### Training

```bash
export STD_OR_RED=red
ctapipe-train-energy-regressor --input $INPUT_GAMMA_EN_FILE   --output $OUTPUT_DIR/energy_regressor_${STD_OR_RED}.pkl   --config $REG_CONF_FILE   --cv-output $OUTPUT_DIR/cv_energy_${STD_OR_RED}.h5   --provenance-log $OUTPUT_DIR/train_energy_${STD_OR_RED}.provenance.log   --log-file $OUTPUT_DIR/train_energy_${STD_OR_RED}.log   --log-level INFO --overwrite
ctapipe-apply-models --input $INPUT_GAMMA_CLF_FILE   --output $OUTPUT_DIR/gamma_train_clf_$STD_OR_RED.dl2.h5   --reconstructor $OUTPUT_DIR/energy_regressor_$STD_OR_RED.pkl   --provenance-log $OUTPUT_DIR/apply_gamma_train_clf_$STD_OR_RED.provenance.log   --log-file $OUTPUT_DIR/apply_gamma_train_clf_$STD_OR_RED.log   --log-level INFO --overwrite
ctapipe-apply-models --input $INPUT_PROTON_FILE    --output $OUTPUT_DIR/proton_train_clf_$STD_OR_RED.dl2.h5   --reconstructor $OUTPUT_DIR/energy_regressor_$STD_OR_RED.pkl   --provenance-log $OUTPUT_DIR/apply_proton_train_$STD_OR_RED.provenance.log   --log-file $OUTPUT_DIR/apply_proton_train_$STD_OR_RED.log   --log-level INFO --overwrite
ctapipe-train-particle-classifier --signal $OUTPUT_DIR/gamma_train_clf_$STD_OR_RED.dl2.h5   --background $OUTPUT_DIR/proton_train_clf_$STD_OR_RED.dl2.h5   --output $OUTPUT_DIR/particle_classifier_$STD_OR_RED.pkl   --config $CLF_CONF_FILE   --cv-output $OUTPUT_DIR/cv_particle_$STD_OR_RED.h5   --provenance-log $OUTPUT_DIR/train_particle_$STD_OR_RED.provenance.log   --log-file $OUTPUT_DIR/train_particle_$STD_OR_RED.log   --log-level INFO  --overwrite
ctapipe-train-disp-reconstructor --input $OUTPUT_DIR/gamma_train_clf_$STD_OR_RED.dl2.h5   --output $OUTPUT_DIR/disp_reconstructor_$STD_OR_RED.pkl   --config $DISP_CONF_FILE   --cv-output $OUTPUT_DIR/cv_disp_$STD_OR_RED.h5   --provenance-log $OUTPUT_DIR/train_disp_$STD_OR_RED.provenance.log   --log-file $OUTPUT_DIR/train_disp_$STD_OR_RED.log   --log-level INFO --overwrite
```

### Apply Models

```
export STD_OR_RED=red
ctapipe-apply-models --input $EVAL_GAMMA_FILE \
  --output $OUTPUT_DIR/gamma_final_$STD_OR_RED.dl2.h5 \
  --reconstructor $OUTPUT_DIR/energy_regressor_$STD_OR_RED.pkl \
  --reconstructor $OUTPUT_DIR/particle_classifier_$STD_OR_RED.pkl \
  --reconstructor $OUTPUT_DIR/disp_reconstructor_$STD_OR_RED.pkl \
  --provenance-log $OUTPUT_DIR/apply_gamma_final_$STD_OR_RED.provenance.log \
  --log-file $OUTPUT_DIR/apply_gamma_final_$STD_OR_RED.log \
  --log-level INFO

ctapipe-apply-models --input $EVAL_PROTON_FILE \
  --output $OUTPUT_DIR/proton_final_$STD_OR_RED.dl2.h5 \
  --reconstructor $OUTPUT_DIR/energy_regressor_$STD_OR_RED.pkl \
  --reconstructor $OUTPUT_DIR/particle_classifier_$STD_OR_RED.pkl \
  --reconstructor $OUTPUT_DIR/disp_reconstructor_$STD_OR_RED.pkl \
  --provenance-log $OUTPUT_DIR/apply_proton_final_$STD_OR_RED.provenance.log \
  --log-file $OUTPUT_DIR/apply_proton_final_$STD_OR_RED.log \
  --log-level INFO --overwrite

ctapipe-apply-models --input $EVAL_ELECTRON_FILE \
  --output $OUTPUT_DIR/electron_final_$STD_OR_RED.dl2.h5 \
  --reconstructor $OUTPUT_DIR/energy_regressor_$STD_OR_RED.pkl \
  --reconstructor $OUTPUT_DIR/particle_classifier_$STD_OR_RED.pkl \
  --reconstructor $OUTPUT_DIR/disp_reconstructor_$STD_OR_RED.pkl \
  --provenance-log $OUTPUT_DIR/apply_electron_final_$STD_OR_RED.provenance.log \
  --log-file $OUTPUT_DIR/apply_electron_final_$STD_OR_RED.log \
  --log-level INFO
```

## Then make IRFs, or otherwise evaluate performance

https://ctapipe.readthedocs.io/en/latest/user-guide/tools/irf_guide.html not done yet.

Using `performance` script from Max, updated for `ctapipe_0.24` and for now with lower statistics required per bin (9 instead of 25 for sensitivity, 9 instead of 100 for Theta2 cut).

And Tomas Bylund's benchmark script:

```bash
export STD_OR_RED=red
ctapipe-optimize-event-selection \
		--config optimize_cuts.yaml \
		--gamma-file=$OUTPUT_DIR/gamma_final_$STD_OR_RED.dl2.h5 \
		--electron-file=$OUTPUT_DIR/electron_final_$STD_OR_RED.dl2.h5 \
		--proton-file=$OUTPUT_DIR/proton_final_$STD_OR_RED.dl2.h5 \
		--output $OUTPUT_DIR/cuts.$STD_OR_RED.fits \
		--overwrite

ctapipe-compute-irf \
  --config compute_irf.yaml \
  --cuts $OUTPUT_DIR/cuts.$STD_OR_RED.fits \
  --gamma-file=$OUTPUT_DIR/gamma_final_$STD_OR_RED.dl2.h5 \
  --electron-file=$OUTPUT_DIR/electron_final_$STD_OR_RED.dl2.h5 \
  --proton-file=$OUTPUT_DIR/proton_final_$STD_OR_RED.dl2.h5 \
  --output $OUTPUT_DIR/irf.$STD_OR_RED.fits \
  --benchmark-output $OUTPUT_DIR/benchmark.$STD_OR_RED.fits \
  --overwrite
```

https://gitlab.cta-observatory.org/cta-computing/dpps/datapipe/datapipe-testbench



