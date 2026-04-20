import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

def check_drift(reference_path="data/alerts.csv", current_alerts=None):
    reference = pd.read_csv(reference_path)

    if current_alerts is None:
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
    check_drift()
