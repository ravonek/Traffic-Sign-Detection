# 3-minute defense speech

## Slide 1 — Task and research question

Hello. My project is four-class traffic-sign detection with a pretrained
YOLO11n model. It detects crosswalk signs, speed-limit signs, stop signs and
traffic lights. Unlike image classification, object detection must predict both
the class and the bounding-box location. My research question was whether one
controlled change—brightness augmentation—would improve detection on this
dataset.

## Slide 2 — Dataset and leakage-aware preparation

The public PASCAL VOC source contains 877 images and 1,244 annotated objects. My
final split has 559 training images, 140 validation images and 178 locked test
images. The notebook validates XML labels and bounding boxes, converts them to
normalized YOLO format and displays real ground-truth examples. Before splitting,
it groups exact duplicates by SHA-256 and near duplicates by perceptual hash.
The provider hold-out is reserved for testing. A limitation is that original
video IDs are unavailable, so video-level separation cannot be guaranteed.

## Slide 3 — Controlled experiment

Both runs start from the same `yolo11n.pt` weights and use 512-pixel images, 14
epochs, batch size 16, SGD with learning rate 0.01 and seed 42. Both were run on
an Apple M3 CPU. The baseline uses `hsv_v` zero. The experimental run changes
only `hsv_v` to 0.35. All other listed augmentations and settings remain fixed.
My pre-training hypothesis was that moderate brightness variation could improve
validation mAP at IoU 0.50.

## Slide 4 — Validation results and selection

The baseline reached 0.9404 Precision, 0.8548 Recall and 0.9098 mAP at 0.50 in
51.48 minutes. The brightness run reached 0.9198 Precision, 0.8915 Recall and
0.9184 mAP at 0.50 in 49.35 minutes. Therefore, brightness augmentation improved
Recall by about 0.0367 and mAP by about 0.0085, but reduced Precision by about
0.0206. According to the predefined validation rule, I selected
`experiment_brightness_035`. The test set was not used for selection or tuning.

## Slide 5 — Locked test, failures and conclusion

The selected checkpoint achieved 0.9315 Precision, 0.8717 Recall, 0.9183 mAP at
0.50 and 0.7403 mAP from 0.50 to 0.95 on the locked test set. Manual review shows
three representative errors: a speed-limit 50 sign classified as stop, three
missed traffic-light annotations in one scene, and a very small crosswalk sign
classified as a low-confidence speed-limit sign. Small scale or cropping may
contribute in the latter cases, but these are hypotheses, not proven causes.
Overall, the brightness run performed better on validation Recall and mAP for
this split. With only one run per condition, I do not claim that it will always
generalize better under every lighting condition.

