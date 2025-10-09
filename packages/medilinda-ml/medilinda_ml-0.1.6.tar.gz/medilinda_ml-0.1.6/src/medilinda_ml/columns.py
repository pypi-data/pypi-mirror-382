TARGET_COLUMN = "causality_assessment_level"

INITIAL_CATEGORICAL_COLUMNS = [
    "known_allergy",
    "dechallenge",
    "rechallenge",
    "severity",
    "is_serious",
    "criteria_for_seriousness",
    "action_taken",
    "outcome",
]

# This list includes the original categoricals AND the new one you create
COLUMNS_FOR_ONE_HOT = INITIAL_CATEGORICAL_COLUMNS + ["num_suspected_drugs"]

DATE_COLUMNS = [
    "patient_date_of_birth",
    "date_of_onset_of_reaction",
    "rifampicin_start_date",
    "rifampicin_stop_date",
    "isoniazid_start_date",
    "isoniazid_stop_date",
    "pyrazinamide_start_date",
    "pyrazinamide_stop_date",
    "ethambutol_start_date",
    "ethambutol_stop_date",
    "created_at",
]

DRUG_NAMES = [
    "rifampicin",
    "isoniazid",
    "pyrazinamide",
    "ethambutol",
]


COLUMNS_TO_DROP = [
    # Patient Info
    "patient_name",
    "inpatient_or_outpatient_number",
    "patient_address",
    "ward_or_clinic",
    "patient_gender",
    "pregnancy_status",
    # Rifampicin
    "rifampicin_frequency_number",
    "rifampicin_route",
    "rifampicin_batch_no",
    "rifampicin_manufacturer",
    "rifampicin_dose_amount",
    # Isoniazid
    "isoniazid_frequency_number",
    "isoniazid_route",
    "isoniazid_batch_no",
    "isoniazid_manufacturer",
    "isoniazid_dose_amount",
    # Pyrazinamide
    "pyrazinamide_frequency_number",
    "pyrazinamide_route",
    "pyrazinamide_batch_no",
    "pyrazinamide_manufacturer",
    "pyrazinamide_dose_amount",
    # Ethambutol
    "ethambutol_frequency_number",
    "ethambutol_route",
    "ethambutol_batch_no",
    "ethambutol_manufacturer",
    "ethambutol_dose_amount",
]


FINAL_COLUMNS = [
    "dechallenge_yes",
    "rechallenge_yes",
    "severity_fatal",
    "num_suspected_drugs_1",
    "patient_bmi",
    "rifampicin_start_stop_difference",
    "isoniazid_start_stop_difference",
    "pyrazinamide_start_stop_difference",
    "ethambutol_start_stop_difference",
]


NUMERICAL_COLUMNS = [
    "patient_age",
    "patient_weight_kg",
    "patient_height_cm",
    "patient_bmi",
    "rifampicin_start_to_onset_days",
    "rifampicin_stop_to_onset_days",
    "rifampicin_start_stop_difference",
    "isoniazid_start_to_onset_days",
    "isoniazid_stop_to_onset_days",
    "isoniazid_start_stop_difference",
    "pyrazinamide_start_to_onset_days",
    "pyrazinamide_stop_to_onset_days",
    "pyrazinamide_start_stop_difference",
    "ethambutol_start_to_onset_days",
    "ethambutol_stop_to_onset_days",
    "ethambutol_start_stop_difference",
    "num_suspected_drugs",
]
