# 3-minute defense speech

## Slide 1 — Task and question

Hello. My bonus project is traffic-sign detection with YOLO11n. The detector recognizes four classes: crosswalk, speed limit, stop sign and traffic light. Unlike classification, this task predicts both the class and the bounding-box location. My research question is whether brightness augmentation improves detection under varied lighting.

## Slide 2 — Dataset and preparation

The public source contains 877 annotated road images in PASCAL VOC format. The notebook checks XML files and bounding boxes, converts them to normalized YOLO labels and displays real ground-truth examples. I reserve the provider hold-out for final testing. The remaining images are grouped using exact checksums and perceptual hashes before the seeded train-validation split, which reduces duplicate leakage. A limitation is that original video IDs are unavailable.

## Slide 3 — Model and experiment

Both experiments fine-tune the same pretrained YOLO11n with 512-pixel images for 14 epochs using SGD. I keep the split, initialization, optimizer, seed and all other augmentation settings fixed. The baseline uses no brightness jitter, while the experimental run changes only HSV value augmentation from zero to 0.35. My pre-training hypothesis is that this may improve validation mAP at IoU 0.50.

## Slide 4 — Validation and selection

Replace this paragraph after the actual run: report the baseline and experimental Precision, Recall, mAP@0.50 and training time from `validation_table.csv`. State which run won on validation mAP@0.50. Do not use test results to justify the choice, because the test set stays locked until after model selection.

## Slide 5 — Test result, failures and conclusion

Replace this paragraph after the actual run: report final held-out test Precision, Recall and mAP@0.50 from `test_metrics.json`. Show real prediction and failure images, then describe what is actually visible. Possible issues include small distant signs, low contrast, occlusion or inaccurate boxes, but they must be confirmed by inspection. The main limitations are the small dataset, one run per condition and missing source-video IDs. This experiment is educational and is not validated for safety-critical deployment.

