# Defense Q&A / Вопросы к защите

## 1. What is the task? / Какая задача решается?

**EN:** Four-class object detection. The model predicts a bounding box, class
and confidence for every detected road sign or signal.

**RU:** Детекция четырёх классов. Модель предсказывает bounding box, класс и
уверенность для каждого найденного знака или сигнала.

## 2. Why is this not classification? / Почему это не классификация?

**EN:** One street image may contain several objects. Classification assigns a
label to the whole image; detection localizes each object separately.

**RU:** В одном кадре может быть несколько объектов. Классификация даёт метку
всему изображению, а детекция отдельно локализует каждый объект.

## 3. What data did you use? / Какие данные использовались?

**EN:** The Road Sign Detection dataset distributed as a prepared PASCAL VOC
archive: 877 images and 1,244 annotated objects. The final split is 559 train,
140 validation and 178 locked test images.

**RU:** Road Sign Detection в подготовленном формате PASCAL VOC: 877 изображений
и 1 244 объекта. Итоговый split: 559 train, 140 validation и 178 locked test.

## 4. Why YOLO11n? / Почему YOLO11n?

**EN:** It is a compact pretrained detector suitable for a modest dataset and
limited compute. The project fine-tunes it and does not claim a new architecture.

**RU:** Это компактный предобученный детектор, подходящий для небольшого
датасета и ограниченных вычислений. Новая архитектура не заявляется.

## 5. What changed between runs? / Что изменялось между запусками?

**EN:** Only HSV value augmentation: `hsv_v=0.00` versus `hsv_v=0.35`. Split,
weights, image size, epochs, batch, optimizer, learning rate, seed and other
augmentations were fixed.

**RU:** Только яркость HSV: `hsv_v=0.00` против `hsv_v=0.35`. Split, веса,
размер изображения, epochs, batch, optimizer, learning rate, seed и остальные
аугментации одинаковы.

## 6. How did you reduce leakage? / Как уменьшался data leakage?

**EN:** The provider hold-out was locked for testing. The remaining images were
grouped by SHA-256 and perceptual hash before the seeded split, so a detected
duplicate group stays in one split.

**RU:** Исходный hold-out зафиксирован для теста. Остальные изображения
группировались по SHA-256 и perceptual hash до seeded split, поэтому обнаруженная
группа дубликатов остаётся в одной части.

## 7. How was the model selected? / Как выбиралась модель?

**EN:** By the highest validation mAP@0.50, using validation Precision only as a
tie-breaker. Test metrics were calculated after selection and were not used for
tuning.

**RU:** По максимальному validation mAP@0.50; validation Precision использовался
только при равенстве. Test-метрики считались после выбора.

## 8. Did brightness augmentation help? / Помогла ли яркость?

**EN:** On this split, yes for Recall and mAP. Recall increased from 0.8548 to
0.8915 and mAP@0.50 from 0.9098 to 0.9184, while Precision decreased from
0.9404 to 0.9198.

**RU:** На этом split — да для Recall и mAP. Recall вырос с 0.8548 до 0.8915,
mAP@0.50 — с 0.9098 до 0.9184, но Precision снизился с 0.9404 до 0.9198.

## 9. What are the final test results? / Какие итоговые результаты?

**EN:** Precision 0.9315, Recall 0.8717, mAP@0.50 0.9183 and
mAP@0.50:0.95 0.7403 on the locked test split.

**RU:** Precision 0.9315, Recall 0.8717, mAP@0.50 0.9183 и
mAP@0.50:0.95 0.7403 на locked test split.

## 10. Why are confidence thresholds different?

**EN:** Evaluation uses `conf=0.001` to collect low-score detections for PR/AP
calculation. Visual examples use `conf=0.25` to remain readable. NMS IoU is 0.70
and AP matching IoU is 0.50.

**RU:** Для оценки используется `conf=0.001`, чтобы собрать предсказания для
PR/AP. Визуализация использует `conf=0.25`. NMS IoU равен 0.70, AP matching IoU
равен 0.50.

## 11. What failures did you observe? / Какие ошибки обнаружены?

**EN:** A speed-limit 50 sign was classified as stop; three annotated traffic
lights were missed in another image; and a very small crosswalk sign was missed
and overlapped by a low-confidence speed-limit prediction.

**RU:** Знак ограничения 50 был классифицирован как stop; в другом кадре
пропущены три traffic light; маленький дальний crosswalk был пропущен и перекрыт
низкоуверенным предсказанием speedlimit.

## 12. What are the limitations? / Какие ограничения?

**EN:** One run per condition, a small imbalanced dataset, unavailable source-video
IDs, possible domain shift and difficulty with small or unusual objects. The
model is not validated for safety-critical use.

**RU:** Один запуск на условие, небольшой несбалансированный датасет, отсутствие
ID исходных видео, domain shift и сложность маленьких или необычных объектов.
Модель не валидирована для safety-critical применения.

## 13. How do you prove the checkpoint is the selected model?

**EN:** `final_best.pt` is byte-for-byte equal to the brightness run's `best.pt`.
Its SHA-256 is
`7d3a5c1bec29855be12fd5c065e26ae983fb44af5dd2bc1063e8887146381d1d`,
which matches `model_selection.json`.

**RU:** `final_best.pt` побайтово совпадает с `best.pt` brightness run. SHA-256
совпадает со значением в `model_selection.json`.

## 14. How was AI assistance used? / Как использовался AI?

**EN:** AI helped structure code, documentation and presentation drafts. I ran
the experiments, preserved the outputs, reviewed the failures and am responsible
for explaining and verifying the project.

**RU:** AI помог со структурой кода, документацией и презентацией. Я выполнил
эксперименты, сохранил outputs, проверил ошибки и отвечаю за объяснение проекта.

