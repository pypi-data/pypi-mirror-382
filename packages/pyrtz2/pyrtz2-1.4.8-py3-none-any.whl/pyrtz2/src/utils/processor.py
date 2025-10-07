import ast

import json
import io

import pandas as pd
import PyPDF2 as pdf

from tqdm import tqdm
from io import BytesIO
from PyPDF2 import PdfMerger

from ..components.image import read, get_cell_info, process_image, handle_image
from ...afm import AFM


def process_experiment(experiment: AFM, cp_data: str, vd_data: str, indentation: float | list[float]) -> tuple[AFM, pd.DataFrame]:
    cp_annotations = json.loads(cp_data)
    cp_annotations = {ast.literal_eval(
        key): value for key, value in cp_annotations.items()}

    vd_annotations = json.loads(vd_data)
    vd_annotations = {ast.literal_eval(
        key): value for key, value in vd_annotations.items()}

    experiment.experiment.update_annotations(cp_annotations)
    experiment.experiment.update_annotations(vd_annotations)

    df = experiment.experiment.get_fit_all(
        experiment.probe_diameter, ind=indentation)
    return experiment, df


def process_indentation(indentation: str) -> float | list[float]:
    try:
        indentation_list = indentation.split(';')
        ind = [float(i) for i in indentation_list]
    except (ValueError, AttributeError):
        return 0.0

    if len(ind) == 1:
        ind = ind[0]
    return ind


def process_pixel(pixel: str) -> float:
    try:
        pixel_size = float(pixel)
    except (ValueError, TypeError):
        return 1.0

    return pixel_size


def get_pdf(pdf_merger: PdfMerger) -> BytesIO:
    pdf_bytes = BytesIO()
    pdf_merger.write(pdf_bytes)
    pdf_bytes.seek(0)

    return pdf_bytes


def process_images(images: dict, keys: list[tuple[str, ...]], im_data: str, pixel: float = 1.0) -> pd.DataFrame:
    cell_info_list = []

    for key in keys:
        cell_info = get_cell_info([])
        new_key = key[:-1] if len(key) > 1 else key

        if new_key in images:
            annotations = json.loads(im_data)
            im = annotations[repr(key)]

            image_path = images[new_key][0]
            image_array = read(image_path)
            cell_contours = process_image(image_array, im)

            if len(cell_contours) == 1:
                cell_info = get_cell_info(cell_contours[0], pixel)

        cell_info_list.append(cell_info)

    return pd.DataFrame(cell_info_list)


def merge_images(images: dict, im_data: str):
    merger = pdf.PdfMerger()
    annotations = json.loads(im_data)

    for key, im in tqdm(annotations.items()):
        key = eval(key)
        new_key = key[:-1] if len(key) > 1 else key
        for image_key, image_paths in images.items():
            if image_key != new_key:
                continue

            # THIS ONLY SHOWS THE FIRST IMAGE IF THERE IS ONE
            image_path = image_paths[0]
            img = handle_image(image_path, im)

            title = ("").join(image_path.split('\\')[-1].split('.')[:-1])
            title = fr"$\text{{{title}}}$"
            img.update_layout(
                title={
                    'text': title,
                    'x': 0.5,
                    'y': 0.95,
                    'xanchor': 'center'
                }
            )
            img_pdf = io.BytesIO(img.to_image(format='pdf'))
            merger.append(img_pdf)

    return merger
