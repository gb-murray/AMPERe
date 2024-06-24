import argparse
import cv2 as cv
import json
import os
import numpy as np

def apply_processing(img_path, config, save_dir=None):
    """Apply image processing with given configuration."""
    img = cv.imread(img_path, cv.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Failed to read image: {img_path}")
        return

    # Apply Gaussian blur
    gaussian_val = config.get('gaussian', 0)
    if gaussian_val > 0:
        kernelSize = 2 * gaussian_val + 1
        img = cv.GaussianBlur(img, (kernelSize, kernelSize), 0)

    # Apply threshold
    thresh_val = config.get('threshold', 0)
    if thresh_val > 0:
        _, img = cv.threshold(img, thresh_val, 255, cv.THRESH_BINARY_INV)

    # Apply opening
    open_val = config.get('open', 0)
    if open_val > 0:
        kernelSize = 2 * open_val + 1
        kernel = np.ones((kernelSize, kernelSize), np.uint8)
        img = cv.morphologyEx(img, cv.MORPH_OPEN, kernel)

    # Apply closing
    close_val = config.get('close', 0)
    if close_val > 0:
        kernelSize = 2 * close_val + 1
        kernel = np.ones((kernelSize, kernelSize), np.uint8)
        img = cv.morphologyEx(img, cv.MORPH_CLOSE, kernel)

    # Find contours
    _, binary_img = cv.threshold(img, 127, 255, cv.THRESH_BINARY)
    contours, _ = cv.findContours(binary_img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    # Calculate upper bound (convex hull)
    all_points = np.concatenate(contours)
    upper_bound = cv.convexHull(all_points)

    # Calculate lower bound (approximation of convex hull)
    epsilon = 0.01 * cv.arcLength(upper_bound, True)
    lower_bound = cv.approxPolyDP(upper_bound, epsilon, True)

    # Draw contours and bounding rectangle on the image
    display_img = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    cv.drawContours(display_img, [upper_bound], -1, (0, 255, 0), 2)
    cv.drawContours(display_img, [lower_bound], -1, (0, 0, 255), 2)
    x, y, w, h = cv.boundingRect(all_points)
    cv.rectangle(display_img, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # Calculate and display the area between upper and lower bounds
    convex_area = cv.contourArea(upper_bound) * 2  # Double check x-ray resolution
    approx_area = cv.contourArea(lower_bound) * 2
    melt_pool_area = convex_area - approx_area
    cv.putText(display_img, f'Area: {melt_pool_area:.2f}', (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Save processed image with contours applied
    if save_dir:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        filename = os.path.basename(img_path)
        save_path = os.path.join(save_dir, filename)
        cv.imwrite(save_path, display_img)
        print(f"Processed image saved: {save_path}")
    else:
        cv.imshow('Processed Image', display_img)
        cv.waitKey(0)
        cv.destroyAllWindows()

def main(input_dir, output_dir=None, config_file='config.json'):
    # Load configuration file
    with open(config_file, 'r') as f:
        config = json.load(f)

    # Create output directory if specified and doesn't exist
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Process each image in the input directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            img_path = os.path.join(input_dir, filename)
            apply_processing(img_path, config, output_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Apply image processing to a directory of images using a configuration file.")
    parser.add_argument('input_dir', type=str, help="Path to directory containing images.")
    parser.add_argument('-o', '--output_dir', type=str, help="Path to directory for saving processed images with contours.")
    parser.add_argument('-c', '--config_file', type=str, default='config.json', help="Path to configuration file.")
    args = parser.parse_args()

    main(args.input_dir, args.output_dir, args.config_file)