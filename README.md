# CT-Segmentation

A medical image processing application designed to isolate and segment skeletal structures from CT scans (NIFTI format). This project combines a Python-based image processing engine using `scipy.ndimage` and `scikit-image` with a modern React frontend for visualization.

# Overview

This project implements the "Bones Segmentation in Contrast CT" algorithm. The core challenge in medical imaging is often handling observer variability and noise; this solution uses automated threshold detection and morphological operations to achieve a clean segmentation of the skeleton.

# Core Features
* NIFTI Support: Reads and writes `.nii.gz` medical image files using `nibabel`.
* Automated Thresholding: Implements an algorithm to find the optimal Hounsfield Unit (HU) threshold for bone density.
* Connectivity Analysis: Utilizes connected component analysis to determine the best segmentation candidates.
* Morphological Post-Processing: Cleans noise and fills holes using `scipy.ndimage` operations.
* Modern UI: A React + Tailwind CSS client to upload scans and visualize the segmentation results.

# Tech Stack

# Core / Processing (Python)
* Python3
* Nibabel: For loading and saving NIFTI images.
* SciPy ('ndimage'): For morphological operations (dilation, erosion) and connectivity analysis.
* Scikit-Image: For additional image processing utilities.
* NumPy: For high-performance array manipulation.

# Client (Web)
* React: UI library.
* Tailwind CSS: For responsive and modern styling.

# Algorithm Details

The segmentation process follows a specific heuristic to ensure accuracy:

1.  Threshold Search: The system iterates over candidate 'i_min' thresholds in the range of [150, 500] HU.
2.  Connectivity Graph: For each threshold, it calculates the number of connected components in the 3D volume.
3.  Optimal Selection: It plots the results and selects the 'i_min' corresponding to the first or second local minima in the graph, representing the most stable skeletal structure.
4.  Morphological Cleaning: Post-processing is applied to remove isolated pixels and close small holes within the bone structure to ensure a single connectivity component.
