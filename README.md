# FastBox Delivery System

A simple Python logistics delivery simulator that reads package delivery data from JSON test files, assigns packages to agents, simulates deliveries, and generates a final `report.json` output.

## Project Structure

```
FastBox_Delivery_System/
│
├── main.py
├── utils.py
├── report.json
├── README.md
│
├── test_cases/
│   ├── base_case.json
│   ├── test_case_1.json
│   ├── test_case_2.json
│   └── etc...
```

## Requirements

- Python 3.7 or newer
- No external dependencies required

## How it works

1. `main.py` asks the user to enter a JSON filename from the `test_cases` folder.
2. The program loads and validates the JSON input.
3. Each package is assigned to the nearest agent based on the agent-to-warehouse distance.
4. The package delivery route is simulated: agent travels from their location to the warehouse, then from the warehouse to the package destination.
5. The simulator tracks packages delivered, total distance traveled, and delivery efficiency.
6. The final summary is stored in `report.json`.

## Running the project

1. Open a terminal in the `FastBox_Delivery_System` folder.
2. Run:

```bash
python main.py
```

3. Enter one of the available JSON file names when prompted, for example:

```text
Enter JSON filename: test_case_1.json
```

4. The program will print delivery summaries and save `report.json`.

## Sample output

The final `report.json` contains statistics like:

```json
{
    "A1": {
        "packages_delivered": 2,
        "total_distance": 85.32,
        "efficiency": 42.66
    },
    "best_agent": "A1"
}
```

## Bonus features included

- random delivery delays
- CSV export for the best agent (`best_agent.csv`)
- ASCII-style route visualization in the console
- error handling for invalid JSON and missing data
- support for empty packages or missing warehouses

## Notes

- The application uses `round(value, 2)` for distance calculations and efficiency.
- If the selected JSON file is invalid, the program prints a helpful error message and exits cleanly.
