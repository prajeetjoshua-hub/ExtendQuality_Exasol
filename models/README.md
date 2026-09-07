# Optional historical bearing model

The public analytics demonstration does not require model weights. Without compatible weights, the visual application reports an OpenCV fallback and routes unverified evidence for review.

## Checkpoint exercised locally

| Field | Value |
|---|---|
| Filename | `bearing_real_3class.pt` |
| Expected path | `models/weights/bearing_real_3class.pt` |
| SHA-256 | `48a3f19f4dd1261737f32e58540eee954eede37989b95672b3286a6bc4767003` |
| Runtime | Ultralytics whole-image classifier |
| Labels | Normal, displaced ball arrangement, surface condition (rust/grease) |
| Distribution | Not bundled; local research asset |

Install optional vision dependencies with `pip install -r backend/requirements-vision.txt -c backend/constraints-validated.txt` inside the environment. Only load trusted PyTorch checkpoints. Set `EXTENDQUALITY_YOLO_WEIGHTS` to the permitted local file.

## Limitations

Training photographs are not independent physical bearings; folds based on image index do not establish cross-bearing generalization. Surface-condition data include grease/rust ambiguity. This model does not detect missing balls reliably, localize individual balls, measure dimensions, establish rotational function or classify another product family.

Prepared demonstrations do not establish production accuracy. No public download is invented: model redistribution and dataset rights must be settled before adding a checkpoint or photographs. Ultralytics and its model licensing terms must be checked for the intended distribution/use.
