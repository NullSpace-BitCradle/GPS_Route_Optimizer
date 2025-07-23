# GPS Route Optimizer

A Python script that solves the Traveling Salesman Problem (TSP) for GPS coordinates to find the shortest route through all points in a repeatable loop.

## Features

- **Multiple optimization algorithms** for different dataset sizes
- **Flexible input formats** (comma or space-separated coordinates)
- **Command-line interface** with comprehensive options
- **Input validation** and error handling
- **Output file generation** for processed routes
- **Circular route calculation** (returns to starting point)
- **Real-world GPS distance calculation** using Haversine formula

## Installation

### Requirements

- Python 3.6 or higher
- No external dependencies (uses only standard library)

### Setup

1. Download the `gps_route_optimizer.py` script
2. Make it executable (optional):

   ```bash
   chmod +x gps_route_optimizer.py
   ```

## Usage

### Basic Syntax

```bash
python gps_route_optimizer.py -i <input_file> [options]
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-i, --input` | Input file containing GPS coordinates | **Required** |
| `-o, --output` | Output file for optimized route | None |
| `-m, --method` | Optimization method (see below) | `auto` |
| `-q, --quiet` | Suppress detailed output | False |
| `-h, --help` | Show help message | - |

### Optimization Methods

| Method | Best For | Performance | Accuracy |
|--------|----------|-------------|----------|
| `auto` | Any dataset | Adaptive | High |
| `brute_force` | ≤8 coordinates | Slow but thorough | Optimal |
| `nearest_neighbor` | Quick approximation | Fast | Good |
| `2opt` | Dozens of coordinates | Moderate | Very good |

## Input File Format

### Supported Formats

The script accepts GPS coordinates in two formats:

#### 1. Comma-Separated Values

```text
40.7128,-74.0060
34.0522,-118.2437
41.8781,-87.6298
```

#### 2. Space-Separated Values

```text
40.7128 -74.0060
34.0522 -118.2437
41.8781 -87.6298
```

### File Format Rules

- **One coordinate pair per line**
- **Latitude first, then longitude**
- **Comments**: Lines starting with `#` are ignored
- **Empty lines**: Automatically skipped
- **Coordinate ranges**: Latitude (-90 to 90), Longitude (-180 to 180)

### Example Input File

```text
# GPS Route Optimization Input
# Format: latitude,longitude
# Major US Cities

40.7128,-74.0060    # New York City
34.0522,-118.2437   # Los Angeles
41.8781,-87.6298    # Chicago
29.7604,-95.3698    # Houston
33.4484,-112.0740   # Phoenix
39.9526,-75.1652    # Philadelphia
32.7767,-96.7970    # Dallas
37.7749,-122.4194   # San Francisco
```

## Usage Examples

### Basic Usage

```bash
# Optimize route with automatic method selection
python gps_route_optimizer.py -i coordinates.txt
```

### Save Results to File

```bash
# Save optimized route to output file
python gps_route_optimizer.py -i coordinates.txt -o optimized_route.txt
```

### Specify Optimization Method

```bash
# Use 2-opt algorithm for larger datasets
python gps_route_optimizer.py -i coordinates.txt -m 2opt

# Use brute force for small, critical routes
python gps_route_optimizer.py -i coordinates.txt -m brute_force
```

### Quiet Mode

```bash
# Minimal output (just total distance)
python gps_route_optimizer.py -i coordinates.txt -q
```

### Complete Example

```bash
# Full optimization with all options
python gps_route_optimizer.py -i my_coordinates.txt -o optimized_route.txt -m 2opt
```

## Output

### Console Output

```text
Reading coordinates from 'coordinates.txt'...
Found 8 valid coordinates
Optimizing route using 'auto' method...

Optimized route using brute_force method:
Number of points: 8
Total distance: 9234.56 km

Route order:
   1. ( 40.7128,  -74.0060)
   2. ( 39.9526,  -75.1652)
   3. ( 29.7604,  -95.3698)
   4. ( 32.7767,  -96.7970)
   5. ( 33.4484, -112.0740)
   6. ( 34.0522, -118.2437)
   7. ( 37.7749, -122.4194)
   8. ( 41.8781,  -87.6298)
  Return to start: ( 40.7128,  -74.0060)
```

### Output File Format

When using `-o` option, the script creates a file with:

```text
# Optimized GPS Route
# Total distance: 9234.56 km
# Number of points: 8
# Format: latitude,longitude

40.712800,-74.006000
39.952600,-75.165200
29.760400,-95.369800
32.776700,-96.797000
33.448400,-112.074000
34.052200,-118.243700
37.774900,-122.419400
41.878100,-87.629800
```

## Algorithm Details

### Haversine Distance Calculation

The script uses the Haversine formula to calculate great-circle distances between GPS coordinates, accounting for Earth's curvature:

```text
d = 2r × arcsin(√(sin²(Δφ/2) + cos φ₁ × cos φ₂ × sin²(Δλ/2)))
```

Where:

- `r` = Earth's radius (6,371 km)
- `φ` = latitude in radians
- `λ` = longitude in radians

### Optimization Algorithms

#### 1. Brute Force

- **Method**: Tests all possible route permutations
- **Complexity**: O(n!)
- **Best for**: Small datasets (≤8 points)
- **Guarantees**: Optimal solution

#### 2. Nearest Neighbor

- **Method**: Always move to the closest unvisited point
- **Complexity**: O(n²)
- **Best for**: Quick approximations
- **Typical accuracy**: Within 25% of optimal

#### 3. 2-Opt Improvement

- **Method**: Nearest neighbor + local optimization
- **Complexity**: O(n²)
- **Best for**: Dozens of coordinates
- **Typical accuracy**: Within 5-10% of optimal

## Performance Guidelines

| Dataset Size | Recommended Method | Expected Runtime |
|--------------|-------------------|------------------|
| 2-8 points | `brute_force` | < 1 second |
| 9-20 points | `2opt` | < 5 seconds |
| 21-50 points | `2opt` | < 30 seconds |
| 50+ points | `nearest_neighbor` | < 1 second |

## Error Handling

The script handles various error conditions gracefully:

### File Errors

- **File not found**: Clear error message with exit
- **Permission denied**: IO error with explanation
- **Invalid format**: Line-by-line warnings, continues processing

### Data Validation

- **Invalid coordinates**: Skips invalid lines with warnings
- **Out-of-range values**: Validates latitude/longitude ranges
- **Malformed numbers**: Handles parsing errors per line

### Example Error Output

```text
Warning: Line 3 has invalid latitude 95.0, skipping
Warning: Line 5 has invalid number format, skipping: invalid,coordinate
Found 8 valid coordinates out of 10 total lines
```

## Tips and Best Practices

### Input File Preparation

1. **Use consistent formatting** throughout your file
2. **Include comments** to document coordinate sources
3. **Validate coordinates** before processing large datasets
4. **Remove duplicates** to avoid unnecessary computation

### Method Selection

- **Small datasets (≤8)**: Use `brute_force` for optimal results
- **Medium datasets (9-50)**: Use `2opt` for good balance
- **Large datasets (50+)**: Use `nearest_neighbor` for speed
- **Unknown size**: Use `auto` (default) for adaptive selection

### Performance Optimization

- **Clean your data**: Remove invalid coordinates beforehand
- **Use appropriate methods**: Don't use brute force on large datasets
- **Consider multiple runs**: For critical routes, try different methods

## Troubleshooting

### Common Issues

#### "No valid coordinates found"

- Check file format (comma or space-separated)
- Verify coordinate ranges (lat: -90 to 90, lon: -180 to 180)
- Ensure file is not empty or all comments

#### "Permission denied"

- Check file permissions for input file
- Ensure write permissions for output directory
- Verify file paths are correct

#### Poor route quality

- Try different optimization methods
- Check for data entry errors in coordinates
- Consider if coordinates represent realistic travel routes

### Getting Help

Run the script with `-h` for built-in help:

```bash
python gps_route_optimizer.py -h
```

## License

This script is provided as-is for educational and practical use. Feel free to modify and distribute according to your needs.

## Version History

- **v1.0**: Initial release with basic TSP solving
- **v2.0**: Added command-line interface and file I/O
- **v2.1**: Added 2-opt algorithm for better large dataset handling
