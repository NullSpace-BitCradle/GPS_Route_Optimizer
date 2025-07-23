#!/usr/bin/env python3

import math
import itertools
import argparse
import sys
from typing import List, Tuple

def haversine_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calculate the great circle distance between two GPS coordinates using the Haversine formula.
    
    Args:
        coord1: Tuple of (latitude, longitude) for first point
        coord2: Tuple of (latitude, longitude) for second point
    
    Returns:
        Distance in kilometers
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r

def calculate_total_distance(route: List[Tuple[float, float]]) -> float:
    """
    Calculate the total distance for a complete route (including return to start).
    
    Args:
        route: List of GPS coordinates in order
    
    Returns:
        Total distance in kilometers
    """
    total_distance = 0.0
    
    # Calculate distance between consecutive points
    for i in range(len(route)):
        current_point = route[i]
        next_point = route[(i + 1) % len(route)]  # Use modulo for circular route
        total_distance += haversine_distance(current_point, next_point)
    
    return total_distance

def find_shortest_route_brute_force(coordinates: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Find the shortest route using brute force (suitable for small number of points).
    
    Args:
        coordinates: List of GPS coordinates as (latitude, longitude) tuples
    
    Returns:
        List of coordinates in optimal order
    """
    if len(coordinates) <= 1:
        return coordinates
    
    # Fix the first point to avoid duplicate rotations
    first_point = coordinates[0]
    remaining_points = coordinates[1:]
    
    shortest_distance = float('inf')
    best_route = coordinates  # Initialize with original coordinates
    
    # Try all possible permutations of remaining points
    for perm in itertools.permutations(remaining_points):
        route = [first_point] + list(perm)
        distance = calculate_total_distance(route)
        
        if distance < shortest_distance:
            shortest_distance = distance
            best_route = route

    return best_route

def find_shortest_route_nearest_neighbor(coordinates: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Find a good route using nearest neighbor heuristic (suitable for larger number of points).
    This is much faster but may not find the optimal solution.
    
    Args:
        coordinates: List of GPS coordinates as (latitude, longitude) tuples
    
    Returns:
        List of coordinates in a good order
    """
    if len(coordinates) <= 1:
        return coordinates
    
    unvisited = coordinates.copy()
    route = [unvisited.pop(0)]  # Start with first coordinate
    
    while unvisited:
        current_point = route[-1]
        nearest_point = min(unvisited, key=lambda p: haversine_distance(current_point, p))
        route.append(nearest_point)
        unvisited.remove(nearest_point)
    
    return route

def two_opt_improvement(route: List[Tuple[float, float]], max_iterations: int = 1000) -> List[Tuple[float, float]]:
    """
    Improve a route using the 2-opt algorithm.
    
    Args:
        route: Initial route
        max_iterations: Maximum number of iterations
    
    Returns:
        Improved route
    """
    best_route = route.copy()
    best_distance = calculate_total_distance(best_route)
    
    for iteration in range(max_iterations):
        improved = False
        
        for i in range(len(route)):
            for j in range(i + 2, len(route)):
                if j == len(route) - 1 and i == 0:
                    continue  # Skip if it would just reverse the entire route
                
                # Create new route by reversing the segment between i and j
                new_route = route.copy()
                new_route[i:j+1] = reversed(new_route[i:j+1])
                
                new_distance = calculate_total_distance(new_route)
                
                if new_distance < best_distance:
                    best_route = new_route
                    best_distance = new_distance
                    route = new_route
                    improved = True
                    break
            
            if improved:
                break
        
        if not improved:
            break
    
    return best_route

def find_shortest_route_2opt(coordinates: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Find a good route using nearest neighbor + 2-opt improvement.
    
    Args:
        coordinates: List of GPS coordinates as (latitude, longitude) tuples
    
    Returns:
        List of coordinates in optimized order
    """
    # Start with nearest neighbor solution
    initial_route = find_shortest_route_nearest_neighbor(coordinates)
    
    # Improve with 2-opt
    optimized_route = two_opt_improvement(initial_route)
    
    return optimized_route

def optimize_route(coordinates: List[Tuple[float, float]], method: str = "auto") -> Tuple[List[Tuple[float, float]], float]:
    """
    Find the shortest route through all GPS coordinates.
    
    Args:
        coordinates: List of GPS coordinates as (latitude, longitude) tuples
        method: "brute_force", "nearest_neighbor", "2opt", or "auto"
    
    Returns:
        Tuple of (optimized_route, total_distance)
    """
    if not coordinates:
        return [], 0
    
    if len(coordinates) == 1:
        return coordinates, 0
    
    if method == "auto":
        # Use brute force for very small problems, 2-opt for larger ones
        if len(coordinates) <= 8:
            method = "brute_force"
        else:
            method = "2opt"
    
    if method == "brute_force":
        route = find_shortest_route_brute_force(coordinates)
    elif method == "nearest_neighbor":
        route = find_shortest_route_nearest_neighbor(coordinates)
    elif method == "2opt":
        route = find_shortest_route_2opt(coordinates)
    else:
        raise ValueError("Method must be 'brute_force', 'nearest_neighbor', '2opt', or 'auto'")
    
    total_distance = calculate_total_distance(route)
    
    return route, total_distance

def read_coordinates_from_file(filename: str) -> List[Tuple[float, float]]:
    """
    Read GPS coordinates from a text file.
    
    Expected formats:
    - lat,lon (one pair per line)
    - lat lon (space separated)
    - Lines starting with # are treated as comments
    
    Args:
        filename: Path to the input file
    
    Returns:
        List of GPS coordinate tuples
    """
    coordinates = []
    
    try:
        with open(filename, 'r') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                try:
                    # Try comma-separated first
                    if ',' in line:
                        parts = line.split(',')
                    else:
                        # Try space-separated
                        parts = line.split()
                    
                    if len(parts) != 2:
                        print(f"Warning: Line {line_num} has invalid format, skipping: {line}")
                        continue
                    
                    lat = float(parts[0].strip())
                    lon = float(parts[1].strip())
                    
                    # Basic validation
                    if not (-90 <= lat <= 90):
                        print(f"Warning: Line {line_num} has invalid latitude {lat}, skipping")
                        continue
                    if not (-180 <= lon <= 180):
                        print(f"Warning: Line {line_num} has invalid longitude {lon}, skipping")
                        continue
                    
                    coordinates.append((lat, lon))
                    
                except ValueError:
                    print(f"Warning: Line {line_num} has invalid number format, skipping: {line}")
                    continue
                    
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except IOError as e:
        print(f"Error reading file '{filename}': {e}")
        sys.exit(1)
    
    return coordinates

def write_route_to_file(route: List[Tuple[float, float]], filename: str, total_distance: float):
    """
    Write the optimized route to a file.
    
    Args:
        route: Optimized route
        filename: Output filename
        total_distance: Total distance of the route
    """
    try:
        with open(filename, 'w') as file:
            file.write("# Optimized GPS Route\n")
            file.write(f"# Total distance: {total_distance:.2f} km\n")
            file.write(f"# Number of points: {len(route)}\n")
            file.write("# Format: latitude,longitude\n\n")
            
            for i, coord in enumerate(route):
                file.write(f"{coord[0]:.6f},{coord[1]:.6f}\n")
        
        print(f"Route saved to '{filename}'")
        
    except IOError as e:
        print(f"Error writing to file '{filename}': {e}")

def print_route_info(route: List[Tuple[float, float]], total_distance: float, method: str):
    """
    Print formatted information about the route.
    """
    print(f"\nOptimized route using {method} method:")
    print(f"Number of points: {len(route)}")
    print(f"Total distance: {total_distance:.2f} km")
    print("\nRoute order:")
    for i, coord in enumerate(route):
        print(f"  {i+1:2d}. ({coord[0]:8.4f}, {coord[1]:9.4f})")
    print(f"  Return to start: ({route[0][0]:8.4f}, {route[0][1]:9.4f})")

def main():
    parser = argparse.ArgumentParser(
        description="Optimize GPS route to find shortest path through all coordinates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i coordinates.txt
  %(prog)s -i coords.txt -o optimized_route.txt
  %(prog)s -i coords.txt -m 2opt
  %(prog)s -i coords.txt -m brute_force -o result.txt

Input file format:
  latitude,longitude (one pair per line)
  OR
  latitude longitude (space separated)
  
  Lines starting with # are treated as comments.
  
Methods:
  auto         - Automatically choose best method (default)
  brute_force  - Find optimal solution (slow, use for ≤8 points)
  nearest_neighbor - Fast heuristic
  2opt         - Nearest neighbor + 2-opt improvement (good for larger datasets)
        """
    )
    
    parser.add_argument('-i', '--input', required=True, 
                       help='Input file containing GPS coordinates')
    parser.add_argument('-o', '--output', 
                       help='Output file for optimized route')
    parser.add_argument('-m', '--method', 
                       choices=['auto', 'brute_force', 'nearest_neighbor', '2opt'],
                       default='auto',
                       help='Optimization method (default: auto)')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Suppress detailed output')
    
    args = parser.parse_args()
    
    # Read coordinates from file
    if not args.quiet:
        print(f"Reading coordinates from '{args.input}'...")
    
    coordinates = read_coordinates_from_file(args.input)
    
    if not coordinates:
        print("Error: No valid coordinates found in input file")
        sys.exit(1)
    
    if not args.quiet:
        print(f"Found {len(coordinates)} valid coordinates")
    
    # Optimize route
    if not args.quiet:
        print(f"Optimizing route using '{args.method}' method...")
    
    optimal_route, distance = optimize_route(coordinates, args.method)
    
    # Print results
    if not args.quiet:
        print_route_info(optimal_route, distance, args.method)
    else:
        print(f"Total distance: {distance:.2f} km")
    
    # Write output file if specified
    if args.output:
        write_route_to_file(optimal_route, args.output, distance)

if __name__ == "__main__":
    main()