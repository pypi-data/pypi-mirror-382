"""
Functions for loading datasets
"""
from pathlib import Path
import pandas as pd

def load_dataset(name=None, inbuilt=True, file_type=None):
    """
    Easily load datasets that are inbuilt in DATAIDEA or custom datasets.
    
    Parameters:
    -----------
    name : str
        The name of the dataset (e.g., 'demo', 'fpl', 'music', 'titanic')
        If inbuilt=True, this is the name of the dataset without extension
        If inbuilt=False, this is the path to the file
    inbuilt : bool, default=True
        Whether to load a built-in dataset or a custom dataset
    file_type : str, default=None
        For custom datasets, the file type (e.g., 'csv', 'excel')
        Required when inbuilt=False
        
    Returns:
    --------
    pandas.DataFrame
        The loaded dataset
        
    Raises:
    -------
    TypeError
        If file_type is not specified when inbuilt=False
    FileNotFoundError
        If the dataset cannot be found
    """
    if inbuilt:
        package_dir = Path(__file__).parent.parent
        data_path = package_dir / 'resources' / 'datasets' / f'{name}.csv'
        if not data_path.exists():
            raise FileNotFoundError(f"Built-in dataset '{name}' not found")
        return pd.read_csv(data_path)

    if file_type is None:
        raise TypeError('The file type was not specified for custom dataset')
    
    if file_type.lower() == 'csv':
        return pd.read_csv(name)
    
    if file_type.lower() == 'excel':
        return pd.read_excel(name)
    
    raise ValueError(f"Unsupported file type: {file_type}")

__all__ = ['load_dataset'] 