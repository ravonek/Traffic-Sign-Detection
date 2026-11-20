# Traffic Sign Detection with YOLO11n

**CSCI1409 Deep Learning · KBTU · Fall 2026 · Individual Bonus Project**

> **Project status:** The complete training and evaluation pipeline is implemented, but the provided source package does **not** contain trained checkpoints or measured results yet. Run the Colab notebook, export the evidence, and replace the result placeholders below **before submission**. Do not report fabricated metrics.

## 1. Project overview

This project fine-tunes a pretrained **YOLO11n object detector** to recognize four types of road signs and signals in real street photographs. Unlike image classification, object detection predicts **where an object is** (a bounding box), **what it is** (class), and **how confident the model is** (confidence score).

**Classes (class IDs used by the notebook):**

| ID | Class | Meaning |
| ---: | --- | --- |
| 0 | `crosswalk` | Pedestrian crossing sign |
| 1 | `speedlimit` | Speed limit sign |
| 2 | `stop` | Stop sign |
| 3 | `trafficlight` | Traffic light |

**Research question:** Does adding brightness augmentation during fine-tuning improve road-sign detection under different lighting conditions?

**Deliverables:** a reproducible Google Colab notebook, two controlled training runs, validation comparison, an independently evaluated final checkpoint, visual predictions, failure analysis, and a 3-minute defense presentation.

## 2. Dataset and annotations

- **Dataset:** [Road Sign Detection — andrewmvd (Kaggle)](https://www.kaggle.com/datasets/andrewmvd/road-sign-detection).
- **Download used by the notebook:** the [PaddleDetection prepared PASCAL VOC archive](https://paddlemodels.bj.bcebos.com/object_detection/roadsign_voc.tar), described in the [PaddleDetection dataset instructions](https://github.com/PaddlePaddle/PaddleDetection/blob/release/2.9/docs/tutorials/data/PrepareDetDataSet_en.md).
- **Documented source size:** 877 images, four classes. The actual split sizes are computed from the downloaded data; the code does **not** assume that the final group-aware split has fixed numbers.
- **Original annotations:** PASCAL VOC `.xml` files with labels and pixel-coordinate bounding boxes (`xmin`, `ymin`, `xmax`, `ymax`).
- **Training annotations:** converted to YOLO `.txt` format: `class_id x_center y_center width height`, where the four coordinates are normalized to `[0, 1]`.

The notebook checks for missing XML annotations, unknown classes, invalid bounding boxes, image sizes, and exact/perceptual near-duplicates. It displays at least **five real images with ground-truth boxes** prior to training.

### Data split and leakage prevention

The source archive's provided held-out list, when available (`test.txt`, `valid.txt`, or `val.txt`), is reserved for the **locked final test set**. Remaining images are assigned to train/validation by a deterministic seeded grouped split. The notebook groups identical images (SHA-256) and visually similar images (perceptual hash, Hamming distance ≤ 4), keeping each group in **one split only**.

- **Split random seed:** `42`
- **Training set:** used to fine-tune the detector.
- **Validation set:** used to compare the two runs and select the winning checkpoint.
- **Test set:** used **once, after model selection**, for final metrics and predictions.

**Important limitation:** Source-video IDs are not provided. Perceptual-hash grouping reduces near-duplicate leakage but cannot guarantee that different frames from the same original video stay in one split.

The following files are generated on execution:

- `evidence/dataset_counts.csv` — image **and object** counts for train/val/test, broken down by class.
- `evidence/split_manifest.csv` — split membership, checksums, perceptual hashes, group IDs.
- `evidence/dataset_audit.json` — validation checks and the split method.
- `evidence/ground_truth_examples.png` — labeled example images.

**Fill in the observed counts after running Colab:**

| Split | Images | Total annotated objects | Crosswalk | Speedlimit | Stop | Trafficlight |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Train | _From `dataset_counts.csv`_ | — | — | — | — | — |
| Validation | _From `dataset_counts.csv`_ | — | — | — | — | — |
| Test | _From `dataset_counts.csv`_ | — | — | — | — | — |

**Usage rights:** The dataset is publicly accessible, but its **original license and redistribution permissions must be verified** at the Kaggle source. This repository does not redistribute the source photographs. Credit the original dataset publisher and PaddleDetection. Ultralytics software is subject to its own licensing terms (including AGPL-3.0 in its open-source distribution).

## 3. Model and implementation

- **Framework:** [Ultralytics](https://docs.ultralytics.com/) `8.3.220`, based on PyTorch.
- **Detector:** `YOLO11n` (nano), initialized from `yolo11n.pt` pretrained detection weights for **both** experiments.
- **Why YOLO11n:** a relatively lightweight detector that is practical for a modest dataset and limited Colab GPU time. No architecture is built from scratch.
- **Input image size:** `512 × 512`.
- **Batch size:** `16`.
- **Epochs:** `14`.
- **Optimizer:** SGD.
- **Initial learning rate:** `0.01` (`lr0`).
- **Weight decay:** `0.0005`.
- **Random seed:** `42`; deterministic mode enabled.
- **Additional augmentation settings:** fixed to the values recorded in the notebook and `controlled_experiment_config.json`; e.g., mosaic, horizontal/vertical flips, hue/saturation jitter, rotation and translation are disabled in both runs.
- **Compute environment and total training time:** automatically recorded during actual execution; GPU/torch versions depend on the Colab runtime.

The notebook pins its main Python dependencies. See [`requirements.txt`](requirements.txt) for the standalone list. CUDA-enabled PyTorch is provided by the selected Colab runtime.

## 4. Controlled experiment

**Hypothesis written before training:** moderate HSV brightness augmentation (`hsv_v=0.35`) may improve generalization across darker and brighter road scenes and increase **validation mAP@0.50**.

Both runs share the **same dataset split, initial pretrained weights, image size, optimizer, training duration, seed, learning rate, and other augmentation settings**. Exactly one deliberate hyperparameter changes:

| Setting | Run A — Baseline | Run B — Experiment |
| --- | --- | --- |
| Run directory | `baseline_no_brightness` | `experiment_brightness_035` |
| Initial checkpoint | `yolo11n.pt` | `yolo11n.pt` |
| `hsv_v` brightness jitter | **0.00** | **0.35** |
| Image size | 512 | 512 |
| Batch size | 16 | 16 |
| Epochs | 14 | 14 |
| Optimizer / LR | SGD / 0.01 | SGD / 0.01 |
| Seed | 42 | 42 |

Each run writes training logs, a learning-curve plot, configuration arguments, and its best checkpoint selected by validation results. Timing is measured separately for each run. The search is **controlled**; an improvement is not required to complete the experiment.

### Validation comparison (fill from the real run)

| Run | Precision | Recall | mAP@0.50 | Training time (minutes) |
| --- | ---: | ---: | ---: | ---: |
| A — `hsv_v=0.00` | _Pending_ | _Pending_ | _Pending_ | _Pending_ |
| B — `hsv_v=0.35` | _Pending_ | _Pending_ | _Pending_ | _Pending_ |

Generated source of truth: `evidence/validation_table.csv`, `evidence/validation_comparison.json`, and `evidence/training_times.json`.

### How the final model is selected

Select the run with the **highest validation mAP@0.50**, breaking ties by validation Precision (then a deterministic baseline preference). Copy its validated `best.pt` to `weights/final_best.pt`. Do **not** use the final test results to select a model or to revise settings.

## 5. Metrics and evaluation

- **Precision:** proportion of predicted detections that are correct, given the detection matching criteria.
- **Recall:** proportion of ground-truth objects successfully detected.
- **IoU (Intersection over Union):** overlap area divided by union area for two bounding boxes.
- **mAP@0.50:** mean Average Precision across the four classes, using IoU ≥ 0.50 to match predicted and ground-truth boxes.
- **Training time:** wall-clock time, recorded separately for each complete training run.

**Evaluation settings in the notebook:**

| Setting | Value | Purpose |
| --- | ---: | --- |
| Validation/test evaluation confidence cutoff | `0.001` | Collect low-score detections for PR/AP computation |
| NMS IoU threshold | `0.70` | Suppress overlapping duplicate predictions |
| AP matching IoU | `0.50` | Define a correct match for mAP@0.50 |
| Prediction-visualization confidence cutoff | `0.25` | Display readable predictions |
| Prediction-visualization NMS IoU | `0.70` | Filter duplicate displayed boxes |

The selected checkpoint is evaluated on the **locked test set once**. **These numbers must be copied from the executed notebook, not estimated:**

| Final test metric | Result |
| --- | --- |
| Selected run | _From `evidence/model_selection.json`_ |
| Precision | _From `evidence/test_metrics.json`_ |
| Recall | _From `evidence/test_metrics.json`_ |
| mAP@0.50 | _From `evidence/test_metrics.json`_ |
| Final checkpoint | [**ADD PUBLIC DOWNLOAD URL** after training and upload](#7-evidence-and-checkpoints) |

## 6. Prediction examples and failure analysis

The notebook saves **eight test prediction examples**, each displaying bounding boxes, predicted labels, and confidence scores. A separate diagnostic analyzes ground-truth/prediction overlap and produces up to **three** representative failure cases (or challenging cases if fewer failures are found):

1. **Missed sign / false negative:** a real annotated object is not successfully matched to any prediction.
2. **False detection / false positive:** an extra predicted box is not matched to a ground-truth object.
3. **Wrong class or inaccurate box:** the predicted class is wrong or its location does not sufficiently overlap the ground truth.

Potential causes include small distant signs, low contrast, occlusion, or difficult lighting. **These are possible causes, not confirmed findings.** Review the actual saved test examples and update the explanations based on what is visible.

Generated files include `evidence/test_predictions_8.png`, `evidence/prediction_*.png`, `evidence/failure_01.png`–`failure_03.png` when applicable, and `evidence/failure_analysis_candidates.json`. In failure images, **green boxes are ground truth** and **orange boxes are predictions**.

**Failure-review notes (complete after examining real images):**

| Case | Image | Actual failure or challenge | Likely cause | Suggested improvement |
| --- | --- | --- | --- | --- |
| 1 | _Pending_ | _Pending_ | _Pending_ | _Pending_ |
| 2 | _Pending_ | _Pending_ | _Pending_ | _Pending_ |
| 3 | _Pending_ | _Pending_ | _Pending_ | _Pending_ |

## 7. Reproduce in Google Colab

### Open the notebook

**Notebook:** [`CSCI1409_Bonus_Traffic_Signs_Colab.ipynb`](CSCI1409_Bonus_Traffic_Signs_Colab.ipynb)

**Colab link:**

<https://colab.research.google.com/github/ravonek/Traffic-Sign-Detection/blob/main/CSCI1409_Bonus_Traffic_Signs_Colab.ipynb>

1. Upload the notebook to [Google Colab](https://colab.research.google.com/) or open it from GitHub.
2. Select **Runtime → Change runtime type → T4 GPU** if available.
3. Choose **Runtime → Run all**. The notebook downloads the dataset and pretrained weights, audits and converts annotations, creates the split, trains both runs, evaluates and exports evidence.
4. Save the executed notebook **with cell outputs**.
5. Download the generated `TRAFFIC_SIGN_SUBMISSION_ARTIFACTS.zip` (the notebook offers the download in Colab).
6. Extract the ZIP and add **selected evidence files** to this repository. Upload the final checkpoint to accessible external storage if it exceeds GitHub's limits. Add its verified download link below.
7. Regenerate your 5-slide defense presentation using the saved evidence:

```bash
python -m pip install -r requirements.txt
python scripts/build_defense.py --artifacts TRAFFIC_SIGN_SUBMISSION_ARTIFACTS.zip
```

A Russian-language walk-through is in [`HOW_TO_RUN_RU.md`](HOW_TO_RUN_RU.md).

### Final checkpoint download

**Trained checkpoint (`final_best.pt`):** **[INSERT WORKING PUBLIC LINK AFTER TRAINING]**

To run inference after downloading `final_best.pt`:

```python
from ultralytics import YOLO

model = YOLO("final_best.pt")
results = model.predict(
    source="path/to/test_image.jpg",
    imgsz=512,
    conf=0.25,
    iou=0.70,
    save=True,
)
```

Upload only checkpoints actually produced by the completed run, and confirm that the instructor can open the link without signing into your account.

## 8. Evidence and checkpoints

After successful execution, the evidence bundle is expected to contain:

| Artifact | Purpose |
| --- | --- |
| `evidence/dataset_counts.csv` | Class and object counts per split |
| `evidence/dataset_audit.json` and `split_manifest.csv` | Annotation checks and split reproducibility |
| `evidence/ground_truth_examples.png` | At least five real images with correct boxes |
| `evidence/controlled_experiment_config.json` | Fixed settings and the single changed parameter |
| `evidence/baseline_no_brightness_results.csv/png` | Baseline learning curves and history |
| `evidence/experiment_brightness_035_results.csv/png` | Experiment learning curves and history |
| `evidence/validation_table.csv` | Both-run validation metrics and times |
| `evidence/model_selection.json` | Final-run selection from validation |
| `evidence/test_metrics.json` | Independent final test evaluation |
| `evidence/test_predictions_8.png` | Test images with predictions and confidences |
| `evidence/failure_analysis_candidates.json` and `failure_*.png` | Three error/challenging examples for manual review |
| `evidence/results_summary.json` | Consolidated experiment settings and results |
| `weights/final_best.pt` | Selected final detector checkpoint |

The generated ZIP also includes run-specific training data in `runs/`, and best checkpoints for both runs in `weights/`. Large binaries need not be committed into Git; share a direct, accessible weight-download link instead.

## 9. Repository structure

```text
Traffic-Sign-Detection/
├── README.md
├── requirements.txt
├── .gitignore
├── CSCI1409_Bonus_Traffic_Signs_Colab.ipynb
├── CSCI1409_Bonus_Traffic_Signs_Defense_3min.pptx
├── CSCI1409_Bonus_Traffic_Signs_Speech_EN.md
├── HOW_TO_RUN_RU.md
├── DEFENSE_QA_RU_EN.md
├── PROJECT_STATUS.txt
├── scripts/
│   └── build_defense.py
├── evidence/
│   ├── README.txt                 # replace with real evidence after training
│   └── ...                        # generated files described above
└── weights/                       # generated after training; link externally
    └── final_best.pt
```

### Final GitHub submission checklist

1. Keep `README.md` and the notebook at the root of this repository.
2. Run the full notebook, save output evidence, add your real values to the tables, and upload the selected checkpoint to accessible storage.
3. Regenerate the presentation from the completed artifact ZIP.
4. Check the notebook and checkpoint links from a logged-out browser session.
5. Send the repository URL to the instructor through Teams with **your full name and student ID**, and defend the work on **November 21, 2026**.

## 10. Presentation and academic integrity

A **three-minute, five-slide presentation** is included. It covers the dataset and preparation, solution, model, controlled experiment, and evaluation/results. Final slides should present **actual measured results**, not placeholders.

**Limitations:** small dataset; possible distribution differences from real road environments; small/distant objects; lighting and occlusion; absence of source-video IDs; no claims of safety-critical deployment suitability. A single controlled run per condition gives limited evidence for a general conclusion.

**Credits and assistance disclosure:** The detector uses Ultralytics' pretrained YOLO11n implementation rather than a novel architecture. Data and annotations come from the sources credited above. AI assistance was used to structure and draft the implementation, documentation, and presentation; the student is responsible for verifying code, executing experiments, inspecting errors, and explaining results during the individual defense.

---

**Course:** CSCI1409 Deep Learning — Bonus Project · **Deadline/defense:** Saturday, **November 21, 2026** · **Maximum:** 3 bonus points.
