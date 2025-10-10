import argparse
from atlas.core import run_analysis, export_results

def main():
    parser = argparse.ArgumentParser(description="Atlas Research Network Software CLI")
    parser.add_argument("command", choices=["run", "export"], help="Command to execute")
    parser.add_argument("--query", "-q", help="Research topic or keyword")
    args = parser.parse_args()

    if args.command == "run":
        run_analysis(args.query)
    elif args.command == "export":
        export_results()
    else:
        print("Unknown command")

if __name__ == "__main__":
    main()
