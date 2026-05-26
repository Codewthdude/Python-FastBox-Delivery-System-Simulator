import csv
import json
import math
import os
import random


def load_json_file(file_path):
    """Load JSON data from a file and return it as a Python dictionary."""
    with open(file_path, "r", encoding="utf-8") as json_file:
        return json.load(json_file)


def round_value(value, digits=2):
    """Round a number to the specified number of decimal places."""
    return round(value, digits)


def validate_input(data):
    """Validate that the normalized input JSON contains the required fields."""
    if not isinstance(data, dict):
        raise ValueError("Input JSON must be an object.")

    for key in ["warehouses", "agents", "packages"]:
        if key not in data:
            raise ValueError(f"Missing required field: {key}")
        if not isinstance(data[key], list):
            raise ValueError(f"{key} must be a list.")

    if not data["warehouses"]:
        raise ValueError("The warehouses list cannot be empty.")


def normalize_point(point):
    """Convert a point represented as list or dict to a standard x/y dict."""
    if isinstance(point, dict):
        if "x" in point and "y" in point:
            return {"x": point["x"], "y": point["y"]}
        if "location" in point and isinstance(point["location"], list) and len(point["location"]) == 2:
            return {"x": point["location"][0], "y": point["location"][1]}
    elif isinstance(point, list) and len(point) == 2:
        return {"x": point[0], "y": point[1]}
    raise ValueError(f"Invalid point format: {point}")


def normalize_input(data):
    """Normalize multiple accepted JSON input shapes into a standard internal format."""
    if not isinstance(data, dict):
        raise ValueError("Input JSON must be an object.")

    if "warehouses" not in data or "agents" not in data or "packages" not in data:
        raise ValueError("Input JSON must include warehouses, agents, and packages.")

    warehouses = data["warehouses"]
    agents = data["agents"]
    packages = data["packages"]

    if isinstance(warehouses, dict):
        warehouses = [
            {"id": warehouse_id, **normalize_point(location)}
            for warehouse_id, location in warehouses.items()
        ]
    else:
        normalized = []
        for warehouse in warehouses:
            if not isinstance(warehouse, dict):
                raise ValueError(f"Invalid warehouse format: {warehouse}")
            point = normalize_point(warehouse)
            normalized.append({"id": warehouse.get("id"), **point})
        warehouses = normalized

    if isinstance(agents, dict):
        agents = [
            {"id": agent_id, **normalize_point(location)}
            for agent_id, location in agents.items()
        ]
    else:
        normalized = []
        for agent in agents:
            if not isinstance(agent, dict):
                raise ValueError(f"Invalid agent format: {agent}")
            point = normalize_point(agent)
            normalized.append({"id": agent.get("id"), **point})
        agents = normalized

    normalized_packages = []
    for package in packages:
        if not isinstance(package, dict):
            raise ValueError(f"Invalid package format: {package}")

        warehouse_id = package.get("warehouse_id") or package.get("warehouse")
        destination = package.get("destination")
        if destination is None:
            raise ValueError(f"Package missing destination: {package}")

        destination = normalize_point(destination)
        normalized_packages.append(
            {
                "id": package.get("id"),
                "warehouse_id": warehouse_id,
                "destination": destination,
            }
        )

    normalized_data = {
        "warehouses": warehouses,
        "agents": agents,
        "packages": normalized_packages,
    }

    validate_input(normalized_data)
    return normalized_data


def calculate_distance(point1, point2):
    """Calculate Euclidean distance between two points."""
    dx = point2["x"] - point1["x"]
    dy = point2["y"] - point1["y"]
    return math.sqrt(dx * dx + dy * dy)


def find_warehouse_by_id(warehouses, warehouse_id):
    """Return a warehouse object by its ID."""
    for warehouse in warehouses:
        if warehouse.get("id") == warehouse_id:
            return warehouse
    return None


def find_agent_by_id(agents, agent_id):
    """Return an agent object by its ID."""
    for agent in agents:
        if agent.get("id") == agent_id:
            return agent
    return None


def choose_nearest_agent(package, agents, warehouses):
    """Choose the nearest agent for a package based on agent-to-warehouse distance."""
    warehouse = find_warehouse_by_id(warehouses, package.get("warehouse_id"))
    if not warehouse:
        raise ValueError(f"Warehouse not found: {package.get('warehouse_id')}")

    best_agent = None
    best_distance = None
    for agent in agents:
        distance = calculate_distance(agent, warehouse)
        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_agent = agent
    return best_agent, best_distance


def simulate_delivery(package, agent, warehouse):
    """Simulate the delivery route for a single package and return distance details."""
    start_distance = calculate_distance(agent, warehouse)
    delivery_distance = calculate_distance(warehouse, package["destination"])
    total_distance = start_distance + delivery_distance

    delay = random.uniform(0, 3)
    return {
        "package_id": package.get("id"),
        "agent_id": agent.get("id"),
        "warehouse_id": warehouse.get("id"),
        "destination": package.get("destination"),
        "distance_agent_to_warehouse": round_value(start_distance),
        "distance_warehouse_to_destination": round_value(delivery_distance),
        "total_distance": round_value(total_distance),
        "delay_minutes": round_value(delay),
    }


def assign_packages_to_agents(data):
    """Assign packages to agents and return summary assignment statistics."""
    normalized_data = normalize_input(data)

    warehouses = normalized_data["warehouses"]
    agents = normalized_data["agents"]
    packages = normalized_data["packages"]

    if not packages:
        return ({agent.get("id"): {"packages_delivered": 0, "total_distance": 0.0} for agent in agents}, [])

    assignments = {
        agent.get("id"): {"packages_delivered": 0, "total_distance": 0.0} for agent in agents
    }
    route_data = []

    for package in packages:
        if not package.get("destination") or not isinstance(package["destination"], dict):
            print(f"Skipping package with invalid destination: {package}")
            continue

        try:
            agent, _ = choose_nearest_agent(package, agents, warehouses)
        except ValueError as error:
            print(f"Error assigning package {package.get('id')}: {error}")
            continue

        warehouse = find_warehouse_by_id(warehouses, package.get("warehouse_id"))
        if warehouse is None:
            continue

        delivery_details = simulate_delivery(package, agent, warehouse)
        route_data.append(delivery_details)

        agent_stats = assignments[agent.get("id")]
        agent_stats["packages_delivered"] += 1
        agent_stats["total_distance"] += delivery_details["total_distance"]

    return assignments, route_data


def export_best_agent_csv(agent_id, agent_stats, filename="best_agent.csv"):
    """Export the best agent summary to a CSV file."""
    headers = ["agent_id", "packages_delivered", "total_distance", "efficiency"]
    efficiency = round_value(agent_stats["total_distance"] / agent_stats["packages_delivered"]) if agent_stats["packages_delivered"] else 0.0
    values = [agent_id, agent_stats["packages_delivered"], round_value(agent_stats["total_distance"]), efficiency]

    with open(filename, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(headers)
        writer.writerow(values)

    print(f"Best agent CSV saved to {filename}")


def print_ascii_route(route):
    """Print a simple ASCII route summary for a package delivery."""
    print(
        f"Package {route['package_id']} -> Agent {route['agent_id']} -> Warehouse {route['warehouse_id']} "
        f"-> Destination {route['destination']} | Distance: {route['total_distance']} | Delay: {route['delay_minutes']}m"
    )
