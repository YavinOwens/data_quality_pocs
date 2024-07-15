
# DataDoctor

## Overview

`DataDoctor` is a Python class designed to handle data quality checks and template generation for data stored in CSV and Excel formats. The class provides static methods to clean column names, read templates, assess data completeness, check for PII, and more. It also includes methods for configuring quality checks and evaluating data quality based on a template.

## Installation

To use the `DataDoctor` class, you need to have the following libraries installed:

```bash
pip install pandas openpyxl
```

## Usage

### Importing the Class

```python
from data_quality_doctor.data_doctor import DataDoctor
```

### Methods

#### `clean_column_names`

Clean column names by replacing non-alphanumeric characters with underscores and converting to lowercase.

```python
@staticmethod
def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean column names by replacing non-alphanumeric characters with underscores and converting to lowercase.
    
    Args:
        df (pd.DataFrame): Dataframe to clean column names.
    
    Returns:
        pd.DataFrame: Dataframe with cleaned column names.
    """
```

#### `read_data_quality_template`

Read the data quality template from an Excel file.

```python
@staticmethod
def read_data_quality_template(excel_file_path: str) -> pd.DataFrame:
    """
    Read the data quality template from an Excel file.
    
    Args:
        excel_file_path (str): Path to the Excel file.
    
    Returns:
        pd.DataFrame: DataFrame containing the data quality template.
    """
```

#### `assess_completeness`

Assess completeness for a specific column in the dataframe.

```python
@staticmethod
def assess_completeness(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """
    Assess completeness for a specific column in the dataframe.
    
    Args:
        df (pd.DataFrame): Dataframe containing the data.
        column_name (str): Name of the column to assess.
    
    Returns:
        pd.DataFrame: DataFrame containing completeness assessment results.
    """
```

#### `similar`

Calculate similarity ratio between two strings.

```python
@staticmethod
def similar(a: str, b: str) -> float:
    """
    Calculate similarity ratio between two strings.
    
    Args:
        a (str): First string.
        b (str): Second string.
    
    Returns:
        float: Similarity ratio.
    """
```

#### `is_pii`

Check if a column name indicates personally identifiable information (PII).

```python
@staticmethod
def is_pii(column_name: str) -> bool:
    """
    Check if a column name indicates personally identifiable information (PII).
    
    Args:
        column_name (str): Column name to check.
    
    Returns:
        bool: True if column name indicates PII, False otherwise.
    """
```

#### `read_all_structured_files`

Read all CSV and Excel files from a directory and return their data as dataframes.

```python
@staticmethod
def read_all_structured_files(directory_path: str) -> List[Tuple[str, pd.DataFrame]]:
    """
    Read all CSV and Excel files from a directory and return their data as dataframes.
    
    Args:
        directory_path (str): Path to the directory containing files.
    
    Returns:
        List[Tuple[str, pd.DataFrame]]: List of tuples containing file paths and dataframes.
    """
```

#### `find_critical_elements`

Find critical elements (columns) that appear in multiple files.

```python
@staticmethod
def find_critical_elements(all_sheets: List[Tuple[str, pd.DataFrame]]) -> Dict[str, List[str]]:
    """
    Find critical elements (columns) that appear in multiple files.
    
    Args:
        all_sheets (List[Tuple[str, pd.DataFrame]]): List of tuples containing file paths and dataframes.
    
    Returns:
        Dict[str, List[str]]: Dictionary with column names as keys and list of file paths as values.
    """
```

#### `configure_quality_check`

Configure quality check and create an Excel template if it doesn't already exist.

```python
def configure_quality_check(self, csv_file_path: str, excel_file_path: Optional[str] = None) -> None:
    """
    Configure quality check and create an Excel template if it doesn't already exist.
    
    Args:
        csv_file_path (str): Path to the CSV file for which to configure the quality check.
        excel_file_path (Optional[str]): Path to save the Excel template. If None, saves in the current directory.
    """
```

#### `evaluate_data_quality`

Evaluate data quality based on a template.

```python
def evaluate_data_quality(self, data_file_path: str, template_file_path: str) -> pd.DataFrame:
    """
    Evaluate data quality based on a template.
    
    Args:
        data_file_path (str): Path to the data file (.csv or .xlsx).
        template_file_path (str): Path to the template file (.xlsx).
    
    Returns:
        pd.DataFrame: DataFrame containing completeness assessment results.
    """
```

## Example Usage

First, make sure to import the class:

```python
from data_quality_doctor.data_doctor import DataDoctor
import pandas as pd
import os
```

### `clean_column_names`

```python
# Create a sample DataFrame
df = pd.DataFrame({
    'First Name': ['Alice', 'Bob'],
    'Last-Name': ['Smith', 'Jones'],
    'Date of Birth': ['1990-01-01', '1985-05-12']
})

# Clean the column names
cleaned_df = DataDoctor.clean_column_names(df)
print(cleaned_df.columns)
# Output: Index(['first_name', 'last_name', 'date_of_birth'], dtype='object')
```

### `read_data_quality_template`

```python
# Path to the Excel file containing the data quality template
excel_file_path = 'path/to/data_quality_template.xlsx'

# Read the template
template_df = DataDoctor.read_data_quality_template(excel_file_path)
print(template_df.head())
```

### `assess_completeness`

```python
# Create a sample DataFrame
df = pd.DataFrame({
    'name': ['Alice', 'Bob', None],
    'age': [25, None, 30]
})

# Assess completeness for the 'name' column
completeness_df = DataDoctor.assess_completeness(df, 'name')
print(completeness_df)
```

### `similar`

```python
# Calculate similarity between two strings
similarity_ratio = DataDoctor.similar('First Name', 'first_name')
print(similarity_ratio)
# Output: 0.9090909090909091
```

### `is_pii`

```python
# Check if a column name indicates PII
is_pii = DataDoctor.is_pii('name')
print(is_pii)
# Output: True

is_pii = DataDoctor.is_pii('age')
print(is_pii)
# Output: True

is_pii = DataDoctor.is_pii('email')
print(is_pii)
# Output: False
```

### `read_all_structured_files`

```python
# Directory path containing structured files (CSV and Excel)
directory_path = 'path/to/directory'

# Read all structured files
all_sheets = DataDoctor.read_all_structured_files(directory_path)
for file_path, df in all_sheets:
    print(f'File: {file_path}')
    print(df.head())
```

### `find_critical_elements`

```python
# Assuming all_sheets is obtained from read_all_structured_files method
all_sheets = DataDoctor.read_all_structured_files(directory_path)

# Find critical elements
critical_elements = DataDoctor.find_critical_elements(all_sheets)
print(critical_elements)
```

### `configure_quality_check`

```python
# Path to the CSV file and the Excel template file
csv_file_path = 'path/to/data.csv'
excel_file_path = 'path/to/data_quality_checks_template.xlsx'

# Create an instance of DataDoctor
data_doctor = DataDoctor()

# Configure quality check
data_doctor.configure_quality_check(csv_file_path, excel_file_path)
```

### `evaluate_data_quality`

```python
# Path to the data file and the template file
data_file_path = 'path/to/data.csv'
template_file_path = 'path/to/data_quality_checks_template.xlsx'

# Create an instance of DataDoctor
data_doctor = DataDoctor()

# Evaluate data quality based on the template
completeness_results = data_doctor.evaluate_data_quality(data_file_path, template_file_path)
print(completeness_results)
```

## Contributing

Contributions are welcome! Please submit a pull request or create an issue to discuss your ideas.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
