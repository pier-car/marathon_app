"""
Parser per i dati esportati da Samsung Health / Galaxy Watch.
Supporta i formati CSV esportati dall'app Samsung Health.
"""
import csv
import io
from datetime import datetime


def parse_samsung_health_exercise(file_content):
    """
    Analizza i file CSV di esercizio esportati da Samsung Health.
    Restituisce una lista di dizionari con i dati degli allenamenti.
    """
    workouts = []
    reader = csv.DictReader(io.StringIO(file_content))

    for row in reader:
        workout = {}
        # Samsung Health usa vari formati di header
        # Mappiamo i campi più comuni
        workout['data'] = _parse_date(
            row.get('com.samsung.health.exercise.start_time')
            or row.get('Start time')
            or row.get('start_time', '')
        )
        duration_ms = (
            row.get('com.samsung.health.exercise.duration')
            or row.get('Duration')
            or row.get('duration', '0')
        )
        try:
            workout['durata_minuti'] = round(float(duration_ms) / 60000, 1)
        except (ValueError, TypeError):
            workout['durata_minuti'] = None

        distance = (
            row.get('com.samsung.health.exercise.distance')
            or row.get('Distance')
            or row.get('distance', '0')
        )
        try:
            km = float(distance) / 1000  # Samsung exports in meters
            workout['km'] = round(km, 2)
        except (ValueError, TypeError):
            workout['km'] = None

        if workout['km'] and workout['durata_minuti'] and workout['km'] > 0:
            workout['passo_min_km'] = round(
                workout['durata_minuti'] / workout['km'], 2
            )
        else:
            workout['passo_min_km'] = None

        hr_avg = (
            row.get('com.samsung.health.exercise.mean_heart_rate')
            or row.get('Mean heart rate')
            or row.get('mean_heart_rate', '')
        )
        try:
            workout['fc_media'] = int(float(hr_avg))
        except (ValueError, TypeError):
            workout['fc_media'] = None

        hr_max = (
            row.get('com.samsung.health.exercise.max_heart_rate')
            or row.get('Max heart rate')
            or row.get('max_heart_rate', '')
        )
        try:
            workout['fc_max'] = int(float(hr_max))
        except (ValueError, TypeError):
            workout['fc_max'] = None

        cadence = (
            row.get('com.samsung.health.exercise.mean_cadence')
            or row.get('Mean cadence')
            or row.get('mean_cadence', '')
        )
        try:
            workout['cadenza'] = int(float(cadence))
        except (ValueError, TypeError):
            workout['cadenza'] = None

        calories = (
            row.get('com.samsung.health.exercise.calorie')
            or row.get('Calorie')
            or row.get('calorie', '0')
        )
        try:
            workout['calorie'] = int(float(calories))
        except (ValueError, TypeError):
            workout['calorie'] = None

        exercise_type = (
            row.get('com.samsung.health.exercise.exercise_type')
            or row.get('Exercise type')
            or row.get('exercise_type', '')
        )
        workout['tipo'] = _map_exercise_type(exercise_type)
        workout['sorgente'] = 'galaxy_watch'

        if workout['data'] and workout['km']:
            workouts.append(workout)

    return workouts


def parse_samsung_health_heart_rate(file_content):
    """Analizza i dati di frequenza cardiaca esportati da Samsung Health."""
    records = []
    reader = csv.DictReader(io.StringIO(file_content))

    for row in reader:
        record = {}
        timestamp = (
            row.get('com.samsung.health.heart_rate.start_time')
            or row.get('Start time')
            or row.get('start_time', '')
        )
        record['data'] = _parse_date(timestamp)
        record['ora'] = _parse_time(timestamp)

        hr = (
            row.get('com.samsung.health.heart_rate.heart_rate')
            or row.get('Heart rate')
            or row.get('heart_rate', '')
        )
        try:
            record['fc_riposo'] = int(float(hr))
        except (ValueError, TypeError):
            record['fc_riposo'] = None

        record['sorgente'] = 'galaxy_watch'

        if record['data'] and record['fc_riposo']:
            records.append(record)

    return records


def parse_samsung_health_sleep(file_content):
    """Analizza i dati del sonno esportati da Samsung Health."""
    records = []
    reader = csv.DictReader(io.StringIO(file_content))

    for row in reader:
        record = {}
        record['data'] = _parse_date(
            row.get('com.samsung.health.sleep.start_time')
            or row.get('Start time')
            or row.get('start_time', '')
        )

        duration = (
            row.get('com.samsung.health.sleep.duration')
            or row.get('Duration')
            or row.get('duration', '0')
        )
        try:
            record['ore_sonno'] = round(float(duration) / 3600000, 1)
        except (ValueError, TypeError):
            record['ore_sonno'] = None

        quality = (
            row.get('com.samsung.health.sleep.quality')
            or row.get('Quality')
            or row.get('quality', '')
        )
        try:
            record['qualita_sonno'] = int(float(quality))
        except (ValueError, TypeError):
            record['qualita_sonno'] = None

        record['sorgente'] = 'galaxy_watch'

        if record['data']:
            records.append(record)

    return records


def parse_samsung_health_oxygen(file_content):
    """Analizza i dati SpO2 esportati da Samsung Health."""
    records = []
    reader = csv.DictReader(io.StringIO(file_content))

    for row in reader:
        record = {}
        timestamp = (
            row.get('com.samsung.health.oxygen_saturation.start_time')
            or row.get('Start time')
            or row.get('start_time', '')
        )
        record['data'] = _parse_date(timestamp)
        record['ora'] = _parse_time(timestamp)

        spo2 = (
            row.get('com.samsung.health.oxygen_saturation.spo2')
            or row.get('SpO2')
            or row.get('spo2', '')
        )
        try:
            record['spo2'] = float(spo2)
        except (ValueError, TypeError):
            record['spo2'] = None

        record['sorgente'] = 'galaxy_watch'

        if record['data'] and record['spo2']:
            records.append(record)

    return records


def parse_samsung_health_body_composition(file_content):
    """Analizza i dati di composizione corporea da Samsung Health."""
    records = []
    reader = csv.DictReader(io.StringIO(file_content))

    for row in reader:
        record = {}
        record['data'] = _parse_date(
            row.get('com.samsung.health.body_composition.start_time')
            or row.get('Start time')
            or row.get('start_time', '')
        )

        weight = (
            row.get('com.samsung.health.body_composition.weight')
            or row.get('Weight')
            or row.get('weight', '')
        )
        try:
            record['peso'] = round(float(weight), 1)
        except (ValueError, TypeError):
            record['peso'] = None

        body_fat = (
            row.get('com.samsung.health.body_composition.body_fat')
            or row.get('Body fat')
            or row.get('body_fat', '')
        )
        try:
            record['grasso_corporeo'] = round(float(body_fat), 1)
        except (ValueError, TypeError):
            record['grasso_corporeo'] = None

        muscle = (
            row.get('com.samsung.health.body_composition.skeletal_muscle')
            or row.get('Skeletal muscle')
            or row.get('skeletal_muscle', '')
        )
        try:
            record['massa_muscolare'] = round(float(muscle), 1)
        except (ValueError, TypeError):
            record['massa_muscolare'] = None

        bmi = (
            row.get('com.samsung.health.body_composition.bmi')
            or row.get('BMI')
            or row.get('bmi', '')
        )
        try:
            record['bmi'] = round(float(bmi), 1)
        except (ValueError, TypeError):
            record['bmi'] = None

        water = (
            row.get('com.samsung.health.body_composition.body_water')
            or row.get('Body water')
            or row.get('body_water', '')
        )
        try:
            record['acqua_corporea'] = round(float(water), 1)
        except (ValueError, TypeError):
            record['acqua_corporea'] = None

        if record['data']:
            records.append(record)

    return records


def parse_samsung_health_steps(file_content):
    """Analizza i dati dei passi esportati da Samsung Health."""
    records = []
    reader = csv.DictReader(io.StringIO(file_content))

    for row in reader:
        record = {}
        record['data'] = _parse_date(
            row.get('com.samsung.health.step_count.start_time')
            or row.get('Start time')
            or row.get('start_time', '')
        )

        steps = (
            row.get('com.samsung.health.step_count.count')
            or row.get('Count')
            or row.get('count', '0')
        )
        try:
            record['passi'] = int(float(steps))
        except (ValueError, TypeError):
            record['passi'] = None

        calories = (
            row.get('com.samsung.health.step_count.calorie')
            or row.get('Calorie')
            or row.get('calorie', '0')
        )
        try:
            record['calorie_giornaliere'] = int(float(calories))
        except (ValueError, TypeError):
            record['calorie_giornaliere'] = None

        record['sorgente'] = 'galaxy_watch'

        if record['data'] and record['passi']:
            records.append(record)

    return records


def _parse_date(date_str):
    """Converte vari formati di data in YYYY-MM-DD."""
    if not date_str:
        return None
    formats = [
        '%Y-%m-%d %H:%M:%S.%f',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d',
        '%d/%m/%Y %H:%M:%S',
        '%d/%m/%Y',
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).strftime('%Y-%m-%d')
        except (ValueError, AttributeError):
            continue
    return None


def _parse_time(time_str):
    """Estrae l'ora da un timestamp."""
    if not time_str:
        return None
    formats = [
        '%Y-%m-%d %H:%M:%S.%f',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%S',
    ]
    for fmt in formats:
        try:
            return datetime.strptime(time_str.strip(), fmt).strftime('%H:%M')
        except (ValueError, AttributeError):
            continue
    return None


def _map_exercise_type(type_code):
    """Mappa i codici tipo esercizio Samsung Health ai nomi italiani."""
    type_map = {
        '1001': 'Corsa',
        '1002': 'Camminata',
        '1003': 'Bici',
        '1004': 'Nuoto',
        '14001': 'Corsa',
        'Running': 'Corsa',
        'Walking': 'Camminata',
        'Cycling': 'Bici',
        'Swimming': 'Nuoto',
        'Hiking': 'Escursione',
    }
    return type_map.get(str(type_code).strip(), 'Corsa')
