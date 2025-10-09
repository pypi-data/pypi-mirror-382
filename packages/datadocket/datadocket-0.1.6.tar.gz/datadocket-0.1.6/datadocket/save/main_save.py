import json
import csv
import os


def Txt(
    filepath: str, 
    data: str, 
    mode: str = "w", 
    encoding: str = "utf-8"):
    """
    Saves data to a text file.

    Args:
        filepath (str): Path to the text file.
        data (str): Data to write to the file.
        encoding (str, optional): Encoding to use. Defaults to "utf-8".

    Raises:
        IOError: If there is an error writing the file.
    """
    with open(filepath, mode, encoding=encoding) as f:
        f.write(data)


def Json(
    filepath: str, 
    data: object, 
    mode: str = "w", 
    encoding: str = "utf-8", 
    indent: int = 2, 
    **json_kwargs):
    """
    Saves data to a JSON array file, properly handling append mode.
    
    Args:
        filepath (str): Path to the JSON file.
        data (object): Data to write to the file (must be JSON serializable).
        mode (str): File mode - "w" for write, "a" for append to array.
        encoding (str, optional): Encoding to use. Defaults to "utf-8".
        **json_kwargs: Additional keyword arguments for json.dump().
    """
    if mode == "a":
        # Append mode: load existing array, append new data, save back
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding=encoding) as f:
                existing_data = json.load(f)
            # Ensure it's a list
            if not isinstance(existing_data, list):
                existing_data = [existing_data]
            # Append new data
            if isinstance(data, list):
                existing_data.extend(data)
            else:
                existing_data.append(data)
            # Save back
            with open(filepath, 'w', encoding=encoding) as f:
                json.dump(existing_data, f, indent=indent, **json_kwargs)
        else:
            # Create new file with array containing the data
            with open(filepath, 'w', encoding=encoding) as f:
                if isinstance(data, list):
                    json.dump(data, f, indent=indent, **json_kwargs)
                else:
                    json.dump([data], f, indent=indent, **json_kwargs)
    else:
        # Write mode: standard behavior
        with open(filepath, mode, encoding=encoding) as f:
            json.dump(data, f, indent=indent, **json_kwargs)



def Csv(
    filepath: str, 
    data: list, 
    mode: str = "w", 
    encoding: str = "utf-8", 
    delimiter: str = ",", 
    newline: str = ""):
    """
    Saves data to a CSV file.

    Args:
        filepath (str): Path to the CSV file.
        data (list): List of rows, where each row is a list of values.
        encoding (str, optional): Encoding to use. Defaults to "utf-8".
        delimiter (str, optional): Delimiter to use. Defaults to ",".
        newline (str, optional): Newline parameter for open(). Defaults to "".

    Raises:
        IOError: If there is an error writing the file.
        csv.Error: If there is an error writing the CSV.
    """
    with open(filepath, mode, encoding=encoding, newline=newline) as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerows(data)
