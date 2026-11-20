# Как запустить проект в Google Colab

## Быстрый запуск

1. Откройте [ноутбук в Google Colab](https://colab.research.google.com/github/ravonek/Traffic-Sign-Detection/blob/main/CSCI1409_Bonus_Traffic_Signs_Colab.ipynb).
2. В Colab выберите **Runtime → Change runtime type → T4 GPU**.
3. Проверьте, что в правом верхнем углу указан GPU, затем выберите **Runtime → Run all**.
4. Не закрывайте вкладку до завершения обеих тренировок и финального экспорта.
5. Скачайте предложенный файл `TRAFFIC_SIGN_SUBMISSION_ARTIFACTS.zip`.

Ноутбук сам скачивает датасет, проверяет VOC-разметку, строит train/validation/test split, обучает два YOLO11n и оценивает выбранную модель. Kaggle API-ключ не требуется.

## Что должно завершиться

Успешный полный запуск заканчивается строками с путём к ZIP, выбранным run и реальными test Precision/Recall/mAP50. Установка зависимостей или появление папки `runs/` ещё не означает, что эксперимент завершён.

В ZIP должны быть как минимум:

- `evidence/dataset_counts.csv`;
- `evidence/validation_table.csv`;
- `evidence/model_selection.json`;
- `evidence/test_metrics.json`;
- `evidence/test_predictions_8.png`;
- `evidence/failure_analysis_candidates.json`;
- `weights/final_best.pt`.

Если одного из этих файлов нет, найдите первую ячейку с ошибкой и запустите её повторно после исправления. Не заполняйте метрики вручную по памяти.

## После обучения

1. Сохраните копию ноутбука **с outputs** через **File → Save a copy in GitHub** или скачайте `.ipynb` и замените файл в репозитории.
2. Распакуйте ZIP локально.
3. Скопируйте небольшие файлы из `evidence/` в одноимённую папку репозитория.
4. Сгенерируйте обновлённую презентацию:

   ```bash
   python -m pip install -r requirements.txt
   python scripts/build_defense.py --artifacts TRAFFIC_SIGN_SUBMISSION_ARTIFACTS.zip
   ```

5. Загрузите `weights/final_best.pt` в Google Drive или другое хранилище с публичным доступом по ссылке. Не добавляйте большой checkpoint в обычный Git-коммит.
6. Вставьте фактические числа и публичную ссылку на checkpoint в `README.md`.
7. Откройте ссылки на ноутбук и checkpoint в приватном окне браузера.

## Типичные проблемы

### Colab показывает CPU

Смените тип среды выполнения на T4 GPU и перезапустите среду. На CPU две тренировки займут существенно больше времени.

### Закончилась память GPU

Перезапустите runtime и повторите полный запуск. Если проблема повторяется, уменьшение `batch` меняет конфигурацию эксперимента — отразите это честно в README и в защите.

### Сессия Colab отключилась

Стандартная среда Colab временная. Если training run не закончен и его `best.pt` не попал в скачанный ZIP, этот run считается незавершённым и должен быть выполнен снова.

### Результаты двух запусков уже существуют

Ноутбук настроен на воспроизводимый запуск, но перед финальной сдачей лучше начать с новой среды Colab. Так оба run гарантированно стартуют из одного `yolo11n.pt` и не смешиваются со старыми файлами.

