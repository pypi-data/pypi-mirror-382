import os
import cv2
import json
import argparse
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict


REF_DIR = 'refs'
META_FILE = os.path.join(REF_DIR, "metadata.json")
os.makedirs(REF_DIR, exist_ok=True)


def load_metadata():
    if not os.path.exists(META_FILE):
        return {}
    with open(META_FILE, 'r') as f:
        return json.load(f)


def save_metadata(meta):
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)


def save_reference(label, value, front_path, back_path):
    meta = load_metadata()
    if label in meta:
        print(f"Reference for {label} already exists. — overwriting metadata")
    
    front_dst = os.path.join(REF_DIR, f"{label}_front.jpg")
    back_dst = os.path.join(REF_DIR, f"{label}_back.jpg")
    front_img = cv2.imread(front_path)
    back_img = cv2.imread(back_path)
    if front_img is None or back_img is None:
        raise FileNotFoundError("Could not read front/back image. Check paths.")

    cv2.imwrite(front_dst, front_img)
    cv2.imwrite(back_dst, back_img)

    meta[label] = { "value": float(value), "front": os.path.basename(front_dst), "back": os.path.basename(back_dst) }
    save_metadata(meta)
    print(f"Registered {label} -> {value}. Saved to {front_dst}, {back_dst}")


def make_orb(nfeatures=1000):
    return cv2.ORB_create(nfeatures)


def compute_orb_features(image, orb=None):
    if orb is None:
        orb = make_orb()
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    keypoints, descriptors = orb.detectAndCompute(gray, None)
    return keypoints, descriptors


def match_features(desc1, desc2, ratio=0.75):
    if desc1 is None or desc2 is None:
        return []
    
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    matches = bf.knnMatch(desc1, desc2, k=2)

    good_matches = []
    for m_n in matches:
        if len(m_n) != 2:
            continue
        m, n = m_n
        if m.distance < ratio * n.distance:
            good_matches.append(m)

    return good_matches


def detect_circles_hough(image, dp=1.1, min_dist=30, param1=100, param2=30, min_radius=8, max_radius=200):
    """Detect circles using Hough Circle Transform"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    gray = cv2.medianBlur(gray, 5)

    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp, min_dist,
                               param1=param1, param2=param2,
                               minRadius=min_radius, maxRadius=max_radius)
    
    if circles is None:
        return []
    circles = np.uint16(np.around(circles[0, :]))
    return circles.tolist()


def detect_circles_contour(image, min_area=500, max_area=50000, circularity_thresh=0.7):
    """Detect circles using contour detection with multiple thresholding methods"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Try multiple thresholding methods to find coins
    circles = []
    
    # Method 1: Otsu thresholding
    _, thresh1 = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours1, _ = cv2.findContours(thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Method 2: Inverted Otsu (for coins darker than background)
    _, thresh2 = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours2, _ = cv2.findContours(thresh2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Method 3: Adaptive thresholding
    thresh3 = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY_INV, 11, 2)
    contours3, _ = cv2.findContours(thresh3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Method 4: Canny edge detection
    edges = cv2.Canny(blurred, 50, 150)
    kernel = np.ones((3,3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    contours4, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Combine all contours
    all_contours = contours1 + contours2 + contours3 + contours4
    
    # Process contours to find circles
    found_circles = []
    for contour in all_contours:
        area = cv2.contourArea(contour)
        if area < min_area or area > max_area:
            continue
        
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue
        
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        
        if circularity >= circularity_thresh:
            (cx, cy), radius = cv2.minEnclosingCircle(contour)
            circle_info = [int(cx), int(cy), int(radius)]
            
            # Avoid duplicates (circles very close to each other)
            is_duplicate = False
            for existing in found_circles:
                dist = np.sqrt((existing[0] - circle_info[0])**2 + (existing[1] - circle_info[1])**2)
                if dist < radius * 0.5:  # If centers are very close
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                found_circles.append(circle_info)
    
    return found_circles


def extract_circle(image, cx, cy, r, pad=0.45):
    h, w = image.shape[:2]
    r_pad = int(r * (1 + pad))
    x1 = max(0, cx - r_pad)
    y1 = max(0, cy - r_pad)
    x2 = min(w, cx + r_pad)
    y2 = min(h, cy + r_pad)
    crop = image[y1:y2, x1:x2]
    return crop, (x1, y1, x2, y2)


def load_references(orb=None):
    meta = load_metadata()
    if not meta:
        return {}
    if orb is None:
        orb = make_orb()
    references = {}

    for label, info in meta.items():
        front_path = os.path.join(REF_DIR, info['front'])
        back_path = os.path.join(REF_DIR, info['back'])
        front_img = cv2.imread(front_path)
        back_img = cv2.imread(back_path)
        if front_img is None or back_img is None:
            print(f"Warning: Could not read reference images for {label}. Skipping.")
            continue

        front_kp, front_desc = compute_orb_features(front_img, orb)
        back_kp, back_desc = compute_orb_features(back_img, orb)

        references[label] = {
            "value": float(info['value']),
            "front_img": front_img,
            "back_img": back_img,
            "front_kp": front_kp,
            "front_desc": front_desc,
            "back_kp": back_kp,
            "back_desc": back_desc
        }
    return references


def identify_coin(crop_img, references, orb=None, match_ratio=0.75, match_threshold=8):
    if orb is None:
        orb = make_orb()
    
    kp, desc = compute_orb_features(crop_img, orb)
    best_label = None
    best_matches = 0
    details = {}

    for label, info in references.items():
        front_desc = info.get('front_desc')
        back_desc = info.get('back_desc')
        good_front_matches = match_features(desc, front_desc, ratio=match_ratio)
        good_back_matches = match_features(desc, back_desc, ratio=match_ratio)
        score_front = len(good_front_matches) if good_front_matches is not None else 0
        score_back = len(good_back_matches) if good_back_matches is not None else 0
        score = max(score_front, score_back)

        if score > best_matches:
            best_matches = score
            best_label = label
            which = 'front' if score_front >= score_back else 'back'
            details = {
                "score": score,
                "front_matches": score_front,
                "back_matches": score_back,
                "which": which
            }

    if best_matches >= match_threshold:
        return best_label, best_matches, details
    return best_label, best_matches, details


def annotate_and_report(scene_img, detections, results, out_path=None):
    out = scene_img.copy()
    counts = defaultdict(int)
    total_value = 0.0
    for det, res in zip(detections, results):
        cx, cy, r = det
        label = res.get('label', 'Unknown')
        value = res.get('value', 0.0)
        score = res.get('score')
        cv2.circle(out, (cx, cy), r, (0, 255, 0), 2)
        text = f"{label} (${value:.2f})" if label != 'Unknown' else "Unknown"

        cv2.putText(out, text, (cx - r, cy + r + 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        if label:
            counts[label] += 1
            total_value += value
        
    if out_path:
        cv2.imwrite(out_path, out)
        print(f"Annotated image saved to {out_path}")

    print("\nDetected coins:")
    for label, count in counts.items():
        print(f"  {count} x {label} (value each: ${load_metadata()[label]['value']:.2f})")
    print(f"Total value: ${total_value:.2f}")

    if counts:
        labels = []
        sizes = []
        for label, count in counts.items():
            labels.append(f"{label}\n(${load_metadata()[label]['value']:.2f} each)")
            sizes.append(count)
        plt.figure(figsize=(6,6))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title(f"Coin Distribution (Total Value: ${total_value:.2f})")
        plt.tight_layout()
        chart_path = os.path.splitext(out_path)[0] + "_pie.png" if out_path else "coin_distribution.png"
        plt.savefig(chart_path)
        print(f"Pie chart saved to {chart_path}")

    return out, counts, total_value


def detect_and_identify(scene_path, out_path=None, method='hough', hough_params=None, 
                       contour_params=None, match_threshold=8):
    """
    Detect and identify coins in a scene image
    
    Args:
        scene_path: Path to scene image
        out_path: Output path for annotated image
        method: Detection method ('hough' or 'contour')
        hough_params: Dict of Hough parameters (dp, min_dist, param1, param2, min_radius, max_radius)
        contour_params: Dict of Contour parameters (min_area, max_area, circularity_thresh)
        match_threshold: Minimum ORB feature matches needed
    """
    scene = cv2.imread(scene_path)
    if scene is None:
        raise FileNotFoundError("Could not read scene image")
    
    print(f"\n{'='*60}")
    print(f"Detection Method: {method.upper()}")
    print(f"{'='*60}")
    
    # Detect circles based on selected method
    if method == 'hough':
        hp = hough_params or {}
        dp = hp.get('dp', 1.2)
        min_dist = hp.get('min_dist', 30)
        param1 = hp.get('param1', 100)
        param2 = hp.get('param2', 30)
        min_radius = hp.get('min_radius', 8)
        max_radius = hp.get('max_radius', 200)
        
        print(f"Hough Parameters:")
        print(f"  dp={dp}, min_dist={min_dist}, param1={param1}, param2={param2}")
        print(f"  min_radius={min_radius}, max_radius={max_radius}")
        
        circles = detect_circles_hough(scene, dp=dp, min_dist=min_dist, 
                                      param1=param1, param2=param2,
                                      min_radius=min_radius, max_radius=max_radius)
    
    elif method == 'contour':
        cp = contour_params or {}
        min_area = cp.get('min_area', 500)
        max_area = cp.get('max_area', 50000)
        circularity_thresh = cp.get('circularity_thresh', 0.7)
        
        print(f"Contour Parameters:")
        print(f"  min_area={min_area}, max_area={max_area}, circularity_thresh={circularity_thresh}")
        
        circles = detect_circles_contour(scene, min_area=min_area, 
                                        max_area=max_area,
                                        circularity_thresh=circularity_thresh)
    else:
        raise ValueError(f"Unknown detection method: {method}. Use 'hough' or 'contour'")
    
    print(f"\nFound {len(circles)} circular candidates")
    print(f"Match Threshold: {match_threshold}")
    print(f"{'='*60}\n")

    references = load_references()
    if not references:
        print("Warning: No reference coins found!")
        return None, {}, 0.0
    
    orb = make_orb()

    detections = []
    results = []
    for c in circles:
        cx, cy, r = int(c[0]), int(c[1]), int(c[2])

        crop, bbox = extract_circle(scene, cx, cy, r)
        if crop.size == 0:
            continue

        crop_small = cv2.resize(crop, (200,200), interpolation=cv2.INTER_AREA)
        label, score, details = identify_coin(crop_small, references, orb=orb, 
                                             match_threshold=match_threshold)

        value = references[label]['value'] if label else 0
        detections.append((cx, cy, r))
        results.append({"label": label, "score": score, "details": details, "value": value})
        print(f"Circle at ({cx}, {cy}) r={r} -> {label if label else 'Unknown'} (score={score})")

    annotated, counts, total = annotate_and_report(scene, detections, results, out_path=out_path)
    return annotated, counts, total


def main():
    parser = argparse.ArgumentParser(
        description='Coin Counter - Detect and identify coins using Hough or Contour methods',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Register a coin
  python coin_counter.py register --label Quarter --value 0.25 --front quarter_front.jpg --back quarter_back.jpg
  
  # Detect using Hough method
  python coin_counter.py detect --scene coins.jpg --method hough --min_radius 10 --max_radius 150
  
  # Detect using Contour method
  python coin_counter.py detect --scene coins.jpg --method contour --min_area 1000 --max_area 30000 --circularity 0.6
        """
    )
    
    sub = parser.add_subparsers(dest='cmd')

    # Register command
    p_reg = sub.add_parser('register', help='Register a reference coin')
    p_reg.add_argument('--label', required=True, help='Coin label (e.g., Quarter, Dime)')
    p_reg.add_argument('--value', required=True, type=float, help='Coin value in dollars')
    p_reg.add_argument('--front', required=True, help='Path to front image')
    p_reg.add_argument('--back', required=True, help='Path to back image')

    # Detect command
    p_det = sub.add_parser('detect', help='Detect coins in a scene image')
    p_det.add_argument('--scene', required=True, help='Path to scene image')
    p_det.add_argument('--out', default='annotated.jpg', help='Output path for annotated image')
    p_det.add_argument('--method', choices=['hough', 'contour'], default='hough',
                      help='Detection method: hough or contour (default: hough)')
    p_det.add_argument('--match_threshold', type=int, default=8,
                      help='Minimum ORB feature matches needed (default: 8)')
    
    # Hough-specific parameters
    hough_group = p_det.add_argument_group('Hough Circle Detection Parameters')
    hough_group.add_argument('--dp', type=float, default=1.2,
                            help='Inverse ratio of accumulator resolution (default: 1.2)')
    hough_group.add_argument('--min_dist', type=int, default=30,
                            help='Minimum distance between circle centers (default: 30)')
    hough_group.add_argument('--param1', type=int, default=100,
                            help='Higher threshold for Canny edge detector (default: 100)')
    hough_group.add_argument('--param2', type=int, default=30,
                            help='Accumulator threshold for circle detection (default: 30)')
    hough_group.add_argument('--min_radius', type=int, default=8,
                            help='Minimum circle radius (default: 8)')
    hough_group.add_argument('--max_radius', type=int, default=200,
                            help='Maximum circle radius (default: 200)')
    
    # Contour-specific parameters
    contour_group = p_det.add_argument_group('Contour Detection Parameters')
    contour_group.add_argument('--min_area', type=int, default=500,
                              help='Minimum contour area (default: 500)')
    contour_group.add_argument('--max_area', type=int, default=50000,
                              help='Maximum contour area (default: 50000)')
    contour_group.add_argument('--circularity', type=float, default=0.7,
                              help='Minimum circularity threshold 0-1 (default: 0.7)')

    args = parser.parse_args()
    
    if args.cmd == 'register':
        save_reference(args.label, args.value, args.front, args.back)
        
    elif args.cmd == 'detect':
        hough_params = {
            'dp': args.dp,
            'min_dist': args.min_dist,
            'param1': args.param1,
            'param2': args.param2,
            'min_radius': args.min_radius,
            'max_radius': args.max_radius
        }
        
        contour_params = {
            'min_area': args.min_area,
            'max_area': args.max_area,
            'circularity_thresh': args.circularity
        }
        
        detect_and_identify(args.scene, out_path=args.out, method=args.method,
                          hough_params=hough_params, contour_params=contour_params,
                          match_threshold=args.match_threshold)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()