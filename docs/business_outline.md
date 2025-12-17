# Business Presentation Outline

## Introduction
- Challenge: prevent stockouts across branches while optimizing inventory.
- Goal: automated pipeline predicting 7-day safety-stock breaches using existing CSV data.

## Development
- Data ingestion + validation (schema, missing values) from stock, sales, movements.
- Feature engineering: hashed identifiers, cross-features (`Item×Branch`, `Item×Month`), temporal stats, movement trends.
- Modeling: LightGBM ensemble with class imbalance handling, checkpoints for resumability.
- MLflow governance: experiment tracking, registry promotions, staged releases.
- Orchestration & CI/CD: Prefect DAG, GitLab CI (lint/tests/build/acceptance), Dockerized FastAPI service.
- Monitoring: CME + drift (PSI/KS), alerts triggering fallback/rollback to prior model or rule-based heuristic.

## Conclusion
- Operational efficiency: automated retraining/deployment reduces manual effort.
- Risk mitigation: drift/performance monitoring with fallbacks prevents degraded predictions in production.
- Next steps: extend to batch scoring and integrate with live inventory systems.
