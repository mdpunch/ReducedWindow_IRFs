# ReducedWindow_IRFs

Testing the effect of reducing readout windows on the IRFs.

For now, the readout windows reduction is hardwired (based on what is seen in simulations), with for MSTs [12:27] and LSTs [10:30] (so, MST-NectarCAM window divided by a factor 4, and the LSTs by a factor 2).

Using LaPalma alpha configuration.

Process simtel files with `dl0_to_dl1.yml`, then `dl1_to_dl2.yml`

