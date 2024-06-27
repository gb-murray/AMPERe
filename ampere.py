import argparse
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io
from skimage import filters, measure, restoration, io, morphology

def apply_processing(img_path):
    image_pattern = f"{img_path}/*tif"
    images = io.ImageCollection(image_pattern)

    image_sequence = np.stack(images, axis=0)

    y0, y1, x0, x1 = 0, 400, 0, 1024

    image_sequence = image_sequence[:, y0:y1, x0:x1]

    fig = px.imshow(
        image_sequence,
        animation_frame=0,
        binary_string=True,
        labels={'animation_frame': 'time point'},
    )
    plotly.io.show(fig)

    # Average and remove background
    def remove_background(image):
        avg = np.mean(image, axis=0)
        return image - avg

    image_sequence = remove_background(image_sequence)

    # Compute image deltas
    smoothed = filters.gaussian(image_sequence, sigma=1.0)
    image_deltas = smoothed[1:, :, :] - smoothed[:-1, :, :]

    # Clip lowest and highest intensities
    p_low, p_high = np.percentile(image_deltas, [5, 70])
    clipped = image_deltas - p_low
    clipped[clipped < 0.0] = 0.0
    clipped = clipped / p_high
    clipped[clipped > 1.0] = 1.0

    # Invert and denoise
    inverted = 1 - clipped
    denoised = restoration.denoise_tv_chambolle(inverted, weight=0.30)

    vis_sequence = denoised.copy() # Copy for later visualization

    # Binarize
    thresh_val = filters.threshold_li(denoised)
    binarized = denoised > thresh_val

    # Select largest region
    labeled_0 = measure.label(binarized[0, :, :])
    props_0 = measure.regionprops_table(labeled_0, properties=('label', 'area', 'bbox'))
    props_0_df = pd.DataFrame(props_0)
    props_0_df = props_0_df.sort_values('area', ascending=False)

    props_0_df.head()

    largest_region_0 = labeled_0 == props_0_df.iloc[0]['label']
    
    # Find the convex hull and create a mask
    chull = morphology.convex_hull_image(largest_region_0)
    contours = measure.find_contours(chull)

    # Draw a bounding box
    minr, minc, maxr, maxc = (props_0_df.iloc[0][f'bbox-{i}'] for i in range(4))
    height = maxr - minr
    width = maxc - minc

    fig = px.imshow(
        vis_sequence, 
        animation_frame=0, 
        binary_string=True
        )
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
    plotly.io.show(fig)          

def main(input_dir):
    apply_processing(input_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Apply image processing to a directory of images using a configuration file.")
    parser.add_argument('input_dir', type=str, help="Path to directory containing images.")
    args = parser.parse_args()

    main(args.input_dir)