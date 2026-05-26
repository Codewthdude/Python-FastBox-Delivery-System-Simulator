import json
import os
import random
from utils import (
    assign_packages_to_agents,
    calculate_distance,
    export_best_agent_csv,
    load_json_file,
    print_ascii_route,
    round_value,
)


def build_report(assignments):
    """Build the final report dictionary from delivery assignments."""
    report = {}
    for agent_id, data in assignments.items():
        packages_delivered = data["packages_delivered"]
        total_distance = round_value(data["total_distance"])
        efficiency = round_value(total_distance / packages_delivered) if packages_delivered else 0.0

        report[agent_id] = {
            "packages_delivered": packages_delivered,
            "total_distance": total_distance,
            "efficiency": efficiency,
        }

    best_agent = None
    best_efficiency = None
    for agent_id, stats in report.items():
        if stats["packages_delivered"] == 0:
            continue
        if best_efficiency is None or stats["efficiency"] < best_efficiency:
            best_efficiency = stats["efficiency"]
            best_agent = agent_id

    report["best_agent"] = best_agent if best_agent else "None"
    return report


def save_report(report, filename="report.json"):
    """Save the final report to a JSON file."""
    with open(filename, "w", encoding="utf-8") as json_file:
        json.dump(report, json_file, indent=4)
    print(f"Report saved to {filename}")


def list_test_files(folder_path="test_cases"):
    """Return a sorted list of JSON files inside the test_cases folder."""
    if not os.path.isdir(folder_path):
        return []
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(".json")]
    return sorted(files)


def main():
    print("FastBox Delivery System")
    print("=========================")

    available_files = list_test_files()
    if not available_files:
        print("No test case files found in the test_cases folder.")
        return

    print("Available JSON files:")
    for file_name in available_files:
        print(f" - {file_name}")

    selected_file = input("Enter JSON filename: ").strip()
    if not selected_file:
        print("No filename entered. Exiting.")
        return

    file_path = os.path.join("test_cases", selected_file)
    try:
        data = load_json_file(file_path)
    except FileNotFoundError:
        print(f"File not found: {selected_file}")
        return
    except json.JSONDecodeError as error:
        print(f"Invalid JSON format in file: {selected_file}")
        print(f"Error message: {error}")
        return

    assignments, route_data = assign_packages_to_agents(data)

    if not route_data:
        print("No package deliveries were simulated. Check your input data.")
        return

    print("\nDelivery summary by agent:")
    for agent_id, details in assignments.items():
        print(
            f" - {agent_id}: {details['packages_delivered']} packages, "
            f"{round_value(details['total_distance'])} units traveled"
        )

    print("\nSimulated route details:")
    for item in route_data:
        print_ascii_route(item)

    report = build_report(assignments)
    save_report(report)

    if report.get("best_agent") and report[report["best_agent"]]["packages_delivered"] > 0:
        export_best_agent_csv(report["best_agent"], assignments[report["best_agent"]])

    print("\nFinal report: ")
    print(json.dumps(report, indent=4))


if __name__ == "__main__":
    main()
