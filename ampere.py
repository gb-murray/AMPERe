import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io
from skimage import filters, measure, restoration, io

image_pattern = "C:/Users/dev/Documents/IMQCAM/Data/sample_batch/*.tif"
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

# Compute image deltas
smoothed = filters.gaussian(image_sequence)
image_deltas = smoothed[1:, :, :] - smoothed[:-1, :, :]

# Clip lowest and highest intensities
p_low, p_high = np.percentile(image_deltas, [5, 90])
clipped = image_deltas - p_low
clipped[clipped < 0.0] = 0.0
clipped = clipped / p_high
clipped[clipped > 1.0] = 1.0

# Invert and denoise
inverted = 1 - clipped
denoised = restoration.denoise_tv_chambolle(inverted, weight=0.30)

# Binarize
thresh_val = filters.threshold_li(denoised)
binarized = denoised > thresh_val

# Function to draw bounding box and print dimensions
def draw_bounding_box_and_dimensions(image, region_props):
    minr, minc, maxr, maxc = (region_props[f'bbox-{i}'] for i in range(4))
    height = maxr - minr
    width = maxc - minc

    fig = px.imshow(image, binary_string=True)
    fig.add_shape(
        type='rect', x0=minc, y0=minr, x1=maxc, y1=maxr, line=dict(color='Red')
    )
    fig.add_annotation(
        text=f'Height: {height}px, Width: {width}px',
        x=minc - 10, y=minr - 10, showarrow=False,
        font=dict(color="Red", size=12),
        align="left"
    )
    plotly.io.show(fig)

# Process each image delta
for i in range(len(binarized)):
    labeled = measure.label(binarized[i, :, :])
    props = measure.regionprops_table(labeled, properties=('label', 'area', 'bbox'))
    props_df = pd.DataFrame(props)
    props_df = props_df.sort_values('area', ascending=False)

    if not props_df.empty:
        largest_region = labeled == props_df.iloc[0]['label']
        draw_bounding_box_and_dimensions(largest_region, props_df.iloc[0])