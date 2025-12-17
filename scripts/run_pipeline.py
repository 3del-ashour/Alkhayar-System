"""CLI to run Prefect flow end-to-end."""
from orchestration.prefect_flow import stockout_flow


if __name__ == "__main__":
    stockout_flow()
