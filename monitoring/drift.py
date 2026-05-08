import pandas as pd
import sys
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

def check_drift(reference_path="data/alerts.csv", current_alerts=None):
    reference = pd.read_csv(reference_path, on_bad_lines="skip")

    if current_alerts is None:
        # simulate current data as recent slice for testing
        current = reference.tail(50).copy()
    else:
        current = pd.DataFrame({
            "alert_text": current_alerts,
            "severity": ["unknown"] * len(current_alerts)
        })

    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=reference, current_data=current)
    report.save_html("monitoring/drift_report.html")

    result = report.as_dict()
    drift_detected = result["metrics"][0]["result"]["dataset_drift"]

    if drift_detected:
        print("DRIFT DETECTED — model may need retraining")
    else:
        print("No drift detected — model is healthy")

    return drift_detected

if __name__ == "__main__":
    drift = check_drift()
    # exit code 1 signals drift to CI — triggers retraining workflow
    sys.exit(1 if drift else 0)
