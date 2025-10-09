# Coin Counter Application

A computer vision-based coin detection and counting system with both CLI and GUI interfaces. The application uses ORB (Oriented FAST and Rotated BRIEF) feature matching to identify coins and calculate their total value.

## Features

- **Dual Interface**: Command-line and graphical user interface
- **Multiple Detection Methods**: 
  - Hough Circle Transform
  - Contour-based detection with multiple thresholding techniques
- **Coin Registration**: Register reference coins with front and back images
- **Automatic Identification**: Match detected circles to registered coin types
- **Value Calculation**: Automatically sum the total value of detected coins
- **Visual Output**: 
  - Annotated images with detected coins
  - Pie chart showing coin distribution
- **Adjustable Parameters**: Fine-tune detection for different lighting and backgrounds

## Requirements

```bash
pip install opencv-python numpy matplotlib pillow
```

### Dependencies

- Python 3.7+
- OpenCV (cv2)
- NumPy
- Matplotlib
- Pillow (PIL) - GUI only
- tkinter - GUI only (usually comes with Python)

## Installation

1. Clone or download the repository
2. Install required packages:
```bash
pip install opencv-python numpy matplotlib pillow
```

## Usage

### GUI Version

Run the graphical interface:

```bash
python coin_counter_gui.py
```

#### GUI Workflow:

1. **Register Coins** (Register Coin tab):
   - Enter coin label (e.g., "Quarter", "Dime")
   - Enter coin value in dollars (e.g., 0.25)
   - Browse and select front image
   - Browse and select back image
   - Click "Register Coin"

2. **Detect Coins** (Detect Coins tab):
   - Click "Load Scene Image" to load an image with multiple coins
   - Choose detection method (Hough or Contour)
   - Adjust parameters as needed
   - Click "Detect Coins"
   - View results and pie chart
   - Save annotated image or pie chart

### CLI Version

#### Register a Reference Coin

```bash
python coin_counter_cli.py register --label Quarter --value 0.25 \
  --front quarter_front.jpg --back quarter_back.jpg
```

#### Detect Coins Using Hough Method

```bash
python coin_counter_cli.py detect --scene coins.jpg --method hough \
  --min_radius 10 --max_radius 150 --param2 30
```

#### Detect Coins Using Contour Method

```bash
python coin_counter.py detect --scene coins.jpg --method contour \
  --min_area 1000 --max_area 30000 --circularity 0.6
```

## Detection Methods

### Hough Circle Transform

Best for: Clean backgrounds, well-separated coins, consistent lighting

**Parameters:**
- `--dp`: Inverse ratio of accumulator resolution (default: 1.2)
- `--min_dist`: Minimum distance between circle centers (default: 30)
- `--param1`: Higher threshold for Canny edge detector (default: 100)
- `--param2`: Accumulator threshold for circle detection (default: 30)
- `--min_radius`: Minimum circle radius in pixels (default: 8)
- `--max_radius`: Maximum circle radius in pixels (default: 200)

### Contour Detection

Best for: Challenging backgrounds, overlapping coins, varied lighting

**Parameters:**
- `--min_area`: Minimum contour area in pixels² (default: 500)
- `--max_area`: Maximum contour area in pixels² (default: 50000)
- `--circularity`: Circularity threshold 0-1 (default: 0.7)

Uses multiple thresholding methods:
- Otsu's method
- Inverted Otsu (for dark coins on light background)
- Adaptive thresholding
- Canny edge detection

## Common Parameters

- `--match_threshold`: Minimum ORB feature matches required for identification (default: 8)
  - Increase for stricter matching (fewer false positives)
  - Decrease for more lenient matching (better for poor quality images)

## File Structure

```
coin_counter/
├── coin_counter.py          # CLI version
├── coin_counter_gui.py      # GUI version
├── README.md                # This file
└── refs/                    # Reference coin images (auto-created)
    ├── metadata.json        # Coin information database
    ├── Quarter_front.jpg
    ├── Quarter_back.jpg
    └── ...
```

## Tips for Best Results

### Taking Reference Images

1. Use good lighting (natural daylight works best)
2. Plain, contrasting background
3. Coin should fill most of the frame
4. Image should be in focus
5. Take separate images of front and back

### Scene Images
1. Place coins on a contrasting background
2. Avoid overlapping coins when possible
3. Ensure consistent lighting
4. Keep camera parallel to the surface
5. Use adequate resolution (coins should be at least 50-100 pixels in diameter)

### Parameter Tuning

**If coins are not detected:**
- Hough: Lower `param2`, increase `max_radius`
- Contour: Lower `circularity`, increase `max_area`

**If too many false detections:**
- Hough: Increase `param2`, decrease `max_radius`
- Contour: Increase `circularity`, decrease `max_area`
- Increase `match_threshold` for stricter identification

**If coins are identified incorrectly:**
- Lower `match_threshold` (may cause more "Unknown" results)
- Retake reference images with better quality
- Ensure scene image quality is good

## Output Files

- **Annotated Image**: Shows detected coins with labels and values
- **Pie Chart**: Visual distribution of coin types and total value
- **Console Output**: Detailed detection results and summary

## Limitations

- Works best with circular coins
- Requires good image quality
- May struggle with:
  - Heavily worn or dirty coins
  - Extreme lighting conditions
  - Very small coins in large images
  - Overlapping coins
  - Non-uniform backgrounds

## Troubleshooting

**Problem**: No coins detected
- Try both detection methods
- Adjust radius/area parameters to match actual coin sizes
- Check image quality and lighting

**Problem**: Many false detections
- Increase `param2` (Hough) or `circularity` (Contour)
- Restrict size parameters more narrowly
- Use a cleaner background

**Problem**: Coins detected but labeled "Unknown"
- Lower `match_threshold`
- Improve reference image quality
- Ensure scene image is clear and well-lit
- Register more reference coins if needed

**Problem**: Wrong coin identification
- Increase `match_threshold` for stricter matching
- Retake reference images
- Ensure coins in scene are similar to reference images

## How It Works

1. **Circle Detection**: Finds circular shapes using Hough or Contour methods
2. **Feature Extraction**: Computes ORB features for each detected circle
3. **Feature Matching**: Compares features against registered reference coins
4. **Identification**: Matches detected coins to registered types based on feature similarity
5. **Aggregation**: Counts coins and calculates total value

## Contributing

Feel free to submit issues or pull requests to improve the application.

## Acknowledgments

Built using OpenCV's computer vision algorithms and ORB feature detection.