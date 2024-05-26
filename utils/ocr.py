import numpy as np
from tqdm.auto import tqdm
import csv
from PIL import Image
import pytesseract

# Set tesseract_cmd to the path of the Tesseract executable if it's not in your PATH
# pytesseract.pytesseract.tesseract_cmd = r'<full_path_to_your_tesseract_executable>'

# Set the languages you want to use for OCR
custom_config = r'-l eng+spa --psm 6'


def apply_ocr(cell_coordinates, cropped_table):
    data = dict()
    max_num_columns = 0
    for idx, row in enumerate(cell_coordinates):  # Removed tqdm here
        row_text = []
        for cell in row["cells"]:
            cell_image = np.array(cropped_table.crop(cell["cell"]))
            cell_image_pil = Image.fromarray(cell_image)
            result = pytesseract.image_to_string(cell_image_pil, config=custom_config)
            row_text.append(result.strip())
        if len(row_text) > max_num_columns:
            max_num_columns = len(row_text)
        data[idx] = row_text

    print("Max number of columns:", max_num_columns)
    for row, row_data in data.copy().items():
        if len(row_data) != max_num_columns:
            row_data = row_data + ["" for _ in range(max_num_columns - len(row_data))]
        data[row] = row_data
    return data

def save_csv(data):
    with open('output.csv', 'w') as result_file:
        wr = csv.writer(result_file, dialect='excel')
        for row, row_text in data.items():
            wr.writerow(row_text)

def get_cell_coordinates_by_row(table_data):
    # Extract rows and columns
    rows = [entry for entry in table_data if entry['label'] == 'table row']
    columns = [entry for entry in table_data if entry['label'] == 'table column']

    # Sort rows and columns by their Y and X coordinates, respectively
    rows.sort(key=lambda x: x['bbox'][1])
    columns.sort(key=lambda x: x['bbox'][0])

    # Function to find cell coordinates
    def find_cell_coordinates(row, column):
        cell_bbox = [column['bbox'][0], row['bbox'][1], column['bbox'][2], row['bbox'][3]]
        return cell_bbox

    # Generate cell coordinates and count cells in each row
    cell_coordinates = []

    for row in rows:
        row_cells = []
        for column in columns:
            cell_bbox = find_cell_coordinates(row, column)
            row_cells.append({'column': column['bbox'], 'cell': cell_bbox})

        # Sort cells in the row by X coordinate
        row_cells.sort(key=lambda x: x['column'][0])

        # Append row information to cell_coordinates
        cell_coordinates.append({'row': row['bbox'], 'cells': row_cells, 'cell_count': len(row_cells)})

    # Sort rows from top to bottom
    cell_coordinates.sort(key=lambda x: x['row'][1])

    return cell_coordinates
