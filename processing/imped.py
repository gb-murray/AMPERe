import argparse
import cv2 as cv
import json
import numpy as np
import os

def main(img_path):

    """Creates an interactive window to determine algorithm parameters for processing melt pool x-ray images."""

    # Check for exceptions and read image
    if not os.path.exists(img_path):
        raise Exception("Image does not exist. Please check the image path.")
    elif img_path is None:
        raise Exception("Please specify an image path.")
    else:
        img = cv.imread(img_path, cv.IMREAD_GRAYSCALE)
    if img is None:
        raise Exception("Failed to load image. Please check the image path and file format.")

    cv.namedWindow('IMPED')

    # Initialize parameters
    global gaussian_val, thresh_val, open_val, close_val, processed_img
    gaussian_val = 0
    thresh_val = 0
    open_val = 0
    close_val = 0

    processed_img = img.copy()  # Global variable to store the processed image

    def find_and_draw_contours():
        global processed_img
        # Check the image is binary
        _, binary_img = cv.threshold(processed_img, 127, 255, cv.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv.findContours(binary_img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Find the upper and lower bounds
            all_points = np.concatenate(contours)
            upper_bound = cv.convexHull(all_points)
            lower_bound = cv.approxPolyDP(upper_bound, 0.01*cv.arcLength(upper_bound, True), True)
            
            # Draw the contours on the original image
            display_img = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
            cv.drawContours(display_img, [upper_bound], -1, (0, 255, 0), 2)
            cv.drawContours(display_img, [lower_bound], -1, (0, 0, 255), 2)
            
            # Draw bounding rectangle
            x, y, w, h = cv.boundingRect(all_points)
            cv.rectangle(display_img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            
            # Calculate and display the area
            convex_area = cv.contourArea(upper_bound) * 2 # Double check x-ray resolution
            approx_area = cv.contourArea(lower_bound) * 2
            melt_pool_area = convex_area - approx_area
            cv.putText(display_img, f'Area: {melt_pool_area:.2f}', (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            cv.imshow('IMPED', display_img)

    # Function to update the image based on current slider values
    def update_image():
        global gaussian_val, thresh_val, open_val, close_val, processed_img
        # Apply Gaussian blur
        if gaussian_val > 0:
            kernelSize = 2 * gaussian_val + 1
            processed_img = cv.GaussianBlur(img, (kernelSize, kernelSize), 0)
        else:
            processed_img = img.copy()
        
        # Apply threshold
        if thresh_val > 0:
            _, processed_img = cv.threshold(processed_img, thresh_val, 255, cv.THRESH_BINARY_INV)
        
        # Apply opening
        if open_val > 0:
            kernelSize = 2 * open_val + 1
            kernel = np.ones((kernelSize, kernelSize), np.uint8)
            processed_img = cv.morphologyEx(processed_img, cv.MORPH_OPEN, kernel)
        
        # Apply closing
        if close_val > 0:
            kernelSize = 2 * close_val + 1
            kernel = np.ones((kernelSize, kernelSize), np.uint8)
            processed_img = cv.morphologyEx(processed_img, cv.MORPH_CLOSE, kernel)
        
        # Show the updated image
        cv.imshow('IMPED', processed_img)

    # Callback functions for trackbars
    def gaussian(val):
        global gaussian_val
        gaussian_val = val
        update_image()

    def thresh(val):
        global thresh_val
        thresh_val = val
        update_image()

    def openimg(val):
        global open_val
        open_val = val
        update_image()

    def close(val):
        global close_val
        close_val = val
        update_image()

    # Function to save the trackbar positions to a JSON file
    def save_config():
        config = {
            "gaussian": gaussian_val,
            "threshold": thresh_val,
            "open": open_val,
            "close": close_val
        }
        with open('config.json', 'w') as file:
            json.dump(config, file, indent=4)
        print("Configuration saved to config.json")

    # Make all the trackbars
    cv.createTrackbar('Gaussian', 'IMPED', 0, 5, gaussian)
    cv.createTrackbar('Threshold', 'IMPED', 0, 255, thresh)
    cv.createTrackbar('Open', 'IMPED', 0, 5, openimg)
    cv.createTrackbar('Close', 'IMPED', 0, 5, close)

    # Initialize the display
    update_image()

    while True:
        key = cv.waitKey(1) & 0xFF
        if key == 27:  # Esc key to exit
            break
        elif key == ord('c'):  # 'c' key to find and draw contours
            find_and_draw_contours()
        elif key == ord('s'):  # 's' key to save configuration
            save_config()

    cv.destroyAllWindows()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process an image and plot histograms.")
    parser.add_argument('img_path', type=str, help="Path to target image file.")
    args = parser.parse_args()
    main(args.img_path)