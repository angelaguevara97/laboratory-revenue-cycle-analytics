from generate_data import build_dataset, write_outputs
from analytics_engine import run_analytics


def main() -> None:
    print("Generating 25,000 synthetic laboratory accessions...")
    tables = build_dataset(25_000)
    write_outputs(tables)
    print("Running revenue cycle analytics...")
    results = run_analytics()
    print(f"Accessions: {len(tables['accessions']):,}")
    print(f"Claims: {len(tables['claims']):,}")
    print(f"Billing exceptions: {len(results['queue']):,}")
    print(f"Denial rate: {results['metrics']['denial_rate']:.1%}")
    print(f"Recovery rate: {results['metrics']['recovery_rate']:.1%}")
    print("Project data is ready. Launch the dashboard with: streamlit run dashboard/app.py")


if __name__ == "__main__":
    main()
