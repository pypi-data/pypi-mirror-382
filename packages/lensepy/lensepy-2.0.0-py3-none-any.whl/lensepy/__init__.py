__all__ = [
    "images",      # refers to the 'images' dir
    "css",      # refers to the 'css' file
    'load_dictionary', # refers to the load_dictionnary function
    'translate', # refers to the translate function
    'dictionary', # refers to the global variable dictionary
]

version = '2.0.0'
print('SupOptique LEnsE Package (v.'+version+') / lensepy')
import numpy as np
import os


# Translation
# -----------
dictionary = {}

def load_dictionary(language_path: str) -> dict:
    """
    Load a dictionary from a CSV file based on the specified language.

    Parameters
    ----------
    language : str
        The language path to specify which CSV file to load.

    Returns
    -------
    dict containing 'key_1': 'language_word_1'

    Notes
    -----
    This function reads a CSV file that contains key-value pairs separated by semicolons (';')
    and stores them in a global dictionary variable. The CSV file may contain comments
    prefixed by '#', which will be ignored.

    The file should have the following format:
        # comment
        # comment
        key_1 ; language_word_1
        key_2 ; language_word_2

    The function will strip any leading or trailing whitespace from the keys and values.

    See Also
    --------
    numpy.genfromtxt : Load data from a text file, with missing values handled as specified.
    """
    try:
        global dictionary
        if os.path.exists(language_path):
            # Read the CSV file, ignoring lines starting with '//'
            data = np.genfromtxt(language_path, delimiter=';', dtype=str, comments='#', encoding='UTF-8')
            # Populate the dictionary with key-value pairs from the CSV file
            for key, value in data:
                dictionary[key.strip()] = value.strip()
        else:
            print('File error')
            return {}
    except Exception as e:
        print(e)

def translate(key: str) -> str:
    """
    Translate a given key to its corresponding value.

    Parameters
    ----------
    key : str
        The key to translate.

    Returns
    -------
    str
        The translated value corresponding to the key. If the key does not exist, it returns the value of the key itself.

    """
    global dictionary
    if key in dictionary:
        return dictionary[key]
    else:
        return key


def is_float(element: any) -> bool:
    """
    Return if any object is a float number.
    :param element: Object to test.
    :return: True if the object is a float number.
    """
    #If you expect None to be passed:
    if element is None:
        return False
    try:
        float(element)
        return True
    except ValueError:
        return False