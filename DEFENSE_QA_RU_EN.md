# Defense Q&A / Вопросы к защите

## 1. What is the task? / Какая задача решается?

**EN:** Object detection of four road-sign classes. The model must predict a class, confidence and bounding box for every detected object.

**RU:** Детекция четырёх классов дорожных знаков. Модель предсказывает класс, уверенность и bounding box для каждого найденного объекта.

## 2. Why is this not image classification? / Почему это не классификация?

**EN:** A street image may contain several objects. Classification gives one label for the whole image, while detection localizes every object separately.

**RU:** На одном кадре может быть несколько объектов. Классификация даёт одну метку всему изображению, а детекция отдельно локализует каждый объект.

## 3. Why YOLO11n? / Почему YOLO11n?

**EN:** It is a small pretrained detector that is practical for a modest dataset and limited Colab GPU time. The project fine-tunes it; it does not claim a new architecture.

**RU:** Это компактный предобученный детектор, подходящий для небольшого датасета и ограниченного времени Colab GPU. В проекте выполняется fine-tuning, новая архитектура не заявляется.

## 4. What is the controlled variable? / Какая переменная изменялась?

**EN:** Only HSV value augmentation: `hsv_v=0.00` in the baseline and `hsv_v=0.35` in the experiment. Data split, initialization, optimizer, epochs, image size and the other augmentations are fixed.

**RU:** Только яркость HSV: `hsv_v=0.00` в baseline и `hsv_v=0.35` в experiment. Split, инициализация, optimizer, epochs, размер изображения и остальные аугментации одинаковы.

## 5. What was the hypothesis? / Какая гипотеза?

**EN:** Moderate brightness variation may improve validation mAP@0.50 by exposing the model to lighter and darker versions of training scenes. An improvement is not assumed in advance.

**RU:** Умеренная вариация яркости может повысить validation mAP@0.50, показывая модели более светлые и тёмные варианты сцен. Улучшение заранее не считается гарантированным.

## 6. How was leakage reduced? / Как уменьшили data leakage?

**EN:** The provider hold-out is locked for final testing. Remaining images are grouped by SHA-256 and perceptual hash before a seeded split, so exact or near duplicates do not cross splits. Source-video IDs were unavailable, so video-level leakage cannot be ruled out completely.

**RU:** Исходный hold-out оставлен для финального теста. Остальные изображения группируются по SHA-256 и perceptual hash до seeded split, поэтому точные и близкие дубликаты не попадают в разные части. ID исходных видео отсутствуют, поэтому полностью исключить video-level leakage нельзя.

## 7. How was the final model selected? / Как выбиралась финальная модель?

**EN:** By the highest validation mAP@0.50, with validation precision as the tie-breaker. Test metrics are computed only after selection and are not used for tuning.

**RU:** По максимальному validation mAP@0.50, затем по validation precision при равенстве. Test-метрики считаются только после выбора и не используются для настройки.

## 8. What do Precision, Recall and mAP@0.50 mean?

**EN:** Precision measures how many predicted detections are correct; Recall measures how many ground-truth objects were found. mAP@0.50 averages class AP using IoU 0.50 as the matching threshold.

**RU:** Precision показывает долю правильных предсказаний; Recall — долю найденных реальных объектов. mAP@0.50 усредняет AP по классам при пороге сопоставления IoU 0.50.

## 9. Why are evaluation and display confidence thresholds different?

**EN:** Evaluation uses `conf=0.001` to collect low-score detections for PR/AP calculation. Visual examples use `conf=0.25` so the figures remain readable. These settings serve different purposes.

**RU:** Оценка использует `conf=0.001`, чтобы собрать низкооценённые предсказания для PR/AP. Визуализация использует `conf=0.25`, чтобы изображения оставались читаемыми. Это разные задачи.

## 10. What are the main limitations? / Основные ограничения?

**EN:** Small data, one controlled run per condition, unknown source-video groups, possible domain shift, small distant signs, occlusion and lighting. This is not validated for safety-critical deployment.

**RU:** Малый датасет, один run на условие, неизвестные группы исходных видео, domain shift, маленькие дальние знаки, окклюзия и освещение. Проект не валидирован для safety-critical применения.

## 11. Did brightness augmentation help? / Помогла ли аугментация яркости?

Use only the executed notebook's `evidence/validation_table.csv`. State the observed difference and avoid a broad general claim from one run per condition.

Используйте только реальный `evidence/validation_table.csv`. Назовите наблюдаемую разницу и не делайте общий вывод по одному запуску на условие.

## 12. How was AI assistance used? / Как использовался AI?

**EN:** AI assisted with implementation structure, documentation and presentation drafting. I am responsible for running the experiment, validating outputs, reviewing errors and explaining the choices.

**RU:** AI помог со структурой реализации, документацией и черновиком презентации. Я отвечаю за запуск эксперимента, проверку outputs, анализ ошибок и объяснение решений.

