import argparse
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio
from skimage import filters, measure, restoration, io, morphology, exposure

def apply_processing(img_path):
    image_pattern = f"{img_path}/*tif"
    images = io.ImageCollection(image_pattern)

    image_sequence = np.stack(images, axis=0)

    y0, y1, x0, x1 = 0, 400, 0, 1024

    image_sequence = image_sequence[:, y0:y1, x0:x1]

    # Average and remove background
    def remove_background(image):
        avg = np.mean(image, axis=0)
        return image - avg

    image_sequence = remove_background(image_sequence)

    # Compute image deltas
    smoothed = filters.gaussian(image_sequence, sigma=1.0)
    image_deltas = smoothed[1:, :, :] - smoothed[:-1, :, :]

    # Clip lowest and highest intensities
    p_low, p_high = np.percentile(image_deltas, [5, 80])
    clipped = image_deltas - p_low
    clipped[clipped < 0.0] = 0.0
    clipped = clipped / p_high
    clipped[clipped > 1.0] = 1.0

    # Invert, equalize, and denoise
    inverted = 1 - clipped
    denoised = restoration.denoise_tv_chambolle(inverted, weight=0.25)
    eqed = exposure.equalize_hist(denoised)

    vis_sequence = inverted.copy() # Copy for later visualization

    # Binarize
    thresh_val = filters.threshold_li(eqed)
    binarized = denoised > thresh_val  

    def draw_bounding_box_and_dimensions(image, region_props, i):
        minr, minc, maxr, maxc = (region_props[f'bbox-{j}'] for j in range(4))
        height = maxr - minr
        width = maxc - minc

        fig = px.imshow(vis_sequence[i], binary_string=True)
        fig.add_shape(
            type='rect', 
            x0=minc, y0=minr, x1=maxc, y1=maxr, 
            line=dict(color='Red')
        )
        fig.add_annotation(
            text=f'Height: {height}px, Width: {width}px',
            x=minc - 10, y=minr - 10, showarrow=False,
            font=dict(color="Red", size=12),
            align="left"
        )
        fig.show()

    # Process each image delta
    for i in range(len(binarized)):
        labeled = measure.label(binarized[i, :, :])
        props = measure.regionprops_table(labeled, properties=('label', 'area', 'bbox'))
        props_df = pd.DataFrame(props)
        props_df = props_df.sort_values('area', ascending=False)

        if not props_df.empty:
            largest_region = labeled == props_df.iloc[0]['label']
            chull = morphology.convex_hull_image(largest_region)
            draw_bounding_box_and_dimensions(chull, props_df.iloc[0], i)       

def main(input_dir):
    apply_processing(input_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Apply image processing to a directory of .tif images.")
    parser.add_argument('input_dir', type=str, help="Path to directory containing .tif images.")
    args = parser.parse_args()

    main(args.input_dir)