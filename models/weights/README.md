# Model weights

The backend loads `best.pt` from this directory at startup. Replace it with trusted, Ultralytics-compatible detection weights and restart the backend to change models. Class names come from the checkpoint and are visible at `/health`.

The supplied `exp.pt` has the same SHA-256 hash as `best.pt`; it is not a different model. A failed model load is reported as an error and does not enable simulated detections.
