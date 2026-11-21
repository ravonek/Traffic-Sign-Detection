# Как воспроизвести проект

Репозиторий уже содержит завершённый запуск: executed notebook, метрики,
визуальные evidence-файлы и выбранный `weights/final_best.pt`. Повторное обучение
для просмотра результатов не требуется.

## Быстро посмотреть результаты

1. Откройте [`CSCI1409_Bonus_Traffic_Signs_Colab.ipynb`](CSCI1409_Bonus_Traffic_Signs_Colab.ipynb).
2. В ноутбуке сохранены outputs всех 10 code cells, включая training logs,
   validation comparison и locked-test metrics.
3. Итоговые источники данных находятся в:
   - `evidence/validation_table.csv`;
   - `evidence/model_selection.json`;
   - `evidence/test_metrics.json`;
   - `evidence/results_summary.json`.
4. Качественные примеры находятся в `evidence/test_predictions_8.png`,
   `evidence/failure_01.png`–`failure_03.png` и `demo/`.

## Запустить inference с готовым checkpoint

```bash
git clone https://github.com/ravonek/Traffic-Sign-Detection.git
cd Traffic-Sign-Detection
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Пример Python:

```python
from ultralytics import YOLO

model = YOLO("weights/final_best.pt")
model.predict(
    source="path/to/image_or_video.mp4",
    imgsz=512,
    conf=0.25,
    iou=0.70,
    save=True,
)
```

SHA-256 checkpoint:

```text
7d3a5c1bec29855be12fd5c065e26ae983fb44af5dd2bc1063e8887146381d1d
```

## Полностью повторить эксперимент в Google Colab

1. Откройте [ноутбук в Colab](https://colab.research.google.com/github/ravonek/Traffic-Sign-Detection/blob/main/CSCI1409_Bonus_Traffic_Signs_Colab.ipynb).
2. Чтобы не смешивать новый запуск с сохранёнными outputs, выберите
   **Runtime → Restart session**.
3. При наличии выберите **Runtime → Change runtime type → T4 GPU**. Зафиксированный
   в репозитории запуск был выполнен на Apple M3 CPU, поэтому численные результаты
   и время нового запуска могут немного отличаться.
4. Выполните **Runtime → Run all**.

Ноутбук автоматически:

- устанавливает зафиксированные основные зависимости;
- скачивает PASCAL VOC archive без Kaggle API key;
- проверяет XML-разметку и bounding boxes;
- создаёт seeded grouped split;
- обучает baseline и brightness run из одного `yolo11n.pt`;
- выбирает модель только по validation;
- один раз оценивает locked test;
- экспортирует `TRAFFIC_SIGN_SUBMISSION_ARTIFACTS.zip`.

Полный запуск считается завершённым только после последней ячейки и появления
ZIP. Установка зависимостей или один каталог `runs/` не являются завершённым
экспериментом.

## Пересобрать презентацию

Из ZIP:

```bash
python scripts/build_defense.py \
  --artifacts TRAFFIC_SIGN_SUBMISSION_ARTIFACTS.zip
```

Или из распакованного каталога, содержащего `evidence/`:

```bash
python scripts/build_defense.py --artifacts path/to/artifacts
```

Генератор берёт только реальные CSV/JSON и изображения. Если метрики отсутствуют,
он создаёт явно помеченную pre-run версию и не подставляет вымышленные числа.

## Важные различия порогов

- validation/test evaluation confidence: `0.001`;
- NMS IoU: `0.70`;
- AP matching IoU: `0.50`;
- prediction visualization confidence: `0.25`.

Порог визуализации выше, чтобы изображения оставались читаемыми; он не заменяет
порог, используемый при расчёте AP.

## Если полный повторный запуск прервался

- Проверьте первую ячейку с ошибкой.
- Не объединяйте checkpoints от разных незавершённых запусков.
- Не редактируйте метрики вручную: берите их из экспортированных JSON/CSV.
- Изменение batch size или других параметров означает новую конфигурацию и должно
  быть отдельно задокументировано.
