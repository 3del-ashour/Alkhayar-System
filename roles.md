# Roles and Responsibilities

- **Data Engineer:** Owns data ingestion, schema validation, and pipeline reliability for CSV sources and feature tables.
- **ML Engineer:** Designs features (hashing + crosses), trains LightGBM ensemble, tunes metrics/thresholds, and manages MLflow experiments/registry.
- **DevOps Engineer:** Maintains CI/CD (GitLab CI), Docker images, infrastructure-as-code for MLflow/Prefect, and deployment automation.
- **Monitoring/Observability:** Tracks drift & performance (CME), maintains dashboards/reports in `reports/`, and triggers fallback/rollback playbooks.
