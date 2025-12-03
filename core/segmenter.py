import nibabel as nib
import numpy as np
from core.mask_image import MaskImage
import shutil
from scipy import ndimage
from skimage import morphology, measure, filters
import os

# Todo: Comments

IMAGES_DIR = 'images/'
ORIGINAL_IMAGES_DIR = 'original/'
MASKED_IMAGES_DIR = 'masked/'
FINAL_IMAGES_DIR = 'final/'
MASK_I_MAX = 1300
MASK_START_INTERVAL = 150
MASK_END_INTERVAL = 500
MASK_INTERVAL = 14


class Segmenter:

    def __init__(self, nifti_file):
        original_file_path = os.path.join(IMAGES_DIR, ORIGINAL_IMAGES_DIR, nifti_file.filename)
        self._file_name = nifti_file.filename
        with open(original_file_path, "wb") as buffer:
            shutil.copyfileobj(nifti_file.file, buffer)
        self._nifti_img = nib.load(original_file_path)

    def run_segmentation(self):
        img, final_filename, minima = self._skeleton_th_finder()
        print(f'file: {final_filename}, minima: {minima}')
        print('_________________')
        return img, final_filename, minima

    def _skeleton_th_finder(self):
        i_max = MASK_I_MAX
        interval = MASK_INTERVAL
        start_interval = MASK_START_INTERVAL
        end_interval = MASK_END_INTERVAL
        i_min = start_interval
        minimas = []
        masks = []  # We only need an array of size ((end_interval - start_interval) // interval)

        while i_min <= end_interval:
            components_count, success = self._segmentation_by_th(i_min, i_max)
            masks.append(MaskImage(i_min, components_count))
            print(f'i_min: {i_min}')
            print(f'components_count: {components_count}')
            print(f'---------')
            i_min += interval

        for i in range(1, len(masks) - 1):
            if (masks[i].components_count < masks[i - 1].components_count and
                    masks[i].components_count < masks[i + 1].components_count):
                print(f'Vally: {masks[i].i_min}')
                minimas.append(masks[i].i_min)
        if len(minimas) == 0:  # No vally
            if masks[0].components_count < masks[len(masks) - 1].components_count:
                minimas.append(masks[0].i_min)
            else:
                minimas.append(masks[len(masks) - 1].i_min)
        minima = min(minimas)

        print(f'Final minima: {minima}')
        print(f'---------')

        img = nib.load(f'{IMAGES_DIR}{MASKED_IMAGES_DIR}{self.get_filename(True)}_seg_{minima}_{i_max}.nii.gz')
        img_data = img.get_fdata()

        masked = img_data.astype(bool)

        processed = morphology.binary_closing(masked, morphology.ball(2))
        processed = morphology.binary_dilation(processed, morphology.ball(1))
        processed = morphology.binary_closing(processed, morphology.ball(3))

        print(f'components_count after Post Processing: {self.count_components(processed)[0]}')

        components_count, labels = self.count_components(processed)
        # Retrieving the largest component and removing everything else:
        props = measure.regionprops(labels)
        largest = max(props, key=lambda p: p.area)
        processed = (labels == largest.label)

        print(f'components_count after staying only with the largest: {components_count}')

        final_img = nib.Nifti1Image(processed.astype(np.uint8), affine=img.affine)
        final_filename = f'{IMAGES_DIR}{FINAL_IMAGES_DIR}{self.get_filename(True)}_SkeletonSegmentation.nii.gz'
        nib.save(final_img, final_filename)
        return final_img, final_filename, minima

    def _segmentation_by_th(self, i_min, i_max):
        success = 1
        img_data = self._nifti_img.get_fdata()
        shape = self._nifti_img.shape
        masked = np.zeros(shape, dtype=np.bool)
        np.greater_equal(img_data, i_min, out=masked)
        np.less_equal(img_data, i_max, out=masked, where=masked)
        masked = masked.astype(np.uint8)

        masked_img = nib.Nifti1Image(masked, affine=self._nifti_img.affine)
        nib.save(masked_img, f'{IMAGES_DIR}{MASKED_IMAGES_DIR}{self.get_filename(True)}_seg_{i_min}_{i_max}.nii.gz')
        return self.count_components(masked)[0], success

    def get_filename(self, base=False):
        if base:
            return self._file_name.split('.')[0]
        return self._file_name

    @staticmethod
    def count_components(img_data):
        labels, components_count = measure.label(img_data, return_num=True, connectivity=3)
        return components_count, labels
