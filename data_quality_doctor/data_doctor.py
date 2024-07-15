# data_quality_doctor/data_doctor.py

import pandas as pd
import os
import re
from openpyxl import load_workbook, Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment
from difflib import SequenceMatcher
from typing import Optional

class DataDoctor:
    """
    A class to handle data quality checks and template generation.
    """

    @staticmethod
    def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean column names by replacing non-alphanumeric characters with underscores and converting to lowercase.
        
        Args:
            df (pd.DataFrame): Dataframe to clean column names.
        
        Returns:
            pd.DataFrame: Dataframe with cleaned column names.
        """
        df.columns = [re.sub(r'\W+', '_', col).lower() for col in df.columns]
        return df

    @staticmethod
    def read_data_quality_template(excel_file_path: str) -> pd.DataFrame:
        """
        Read the data quality template from an Excel file.
        
        Args:
            excel_file_path (str): Path to the Excel file.
        
        Returns:
            pd.DataFrame: DataFrame containing the data quality template.
        """
        df_template = pd.read_excel(excel_file_path, sheet_name='Data Quality Checks', skiprows=1)
        return df_template

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
        total_rows = len(df)
        missing_values = df[column_name].isnull().sum()
        non_missing_values = total_rows - missing_values
        completeness_percentage = (non_missing_values / total_rows) * 100

        completeness_df = pd.DataFrame({
            'Column Name': [column_name],
            'Total Rows': [total_rows],
            'Missing Values': [missing_values],
            'Non-Missing Values': [non_missing_values],
            'Completeness (%)': [round(completeness_percentage, 2)]
        })

        return completeness_df

    def configure_quality_check(self, csv_file_path: str, excel_file_path: Optional[str] = None) -> None:
        """
        Configure quality check and create an Excel template if it doesn't already exist.
        
        Args:
            csv_file_path (str): Path to the CSV file for which to configure the quality check.
            excel_file_path (Optional[str]): Path to save the Excel template. If None, saves in the root directory.
        """
        if not excel_file_path:
            excel_file_path = os.path.join(os.getcwd(), 'data_quality_checks_template.xlsx')

        if os.path.exists(excel_file_path):
            print(f"File '{excel_file_path}' already exists. Not overwriting.")
            return

        all_sheets = self.read_all_structured_files(os.path.dirname(csv_file_path))
        critical_elements = self.find_critical_elements(all_sheets)
        
        df = pd.read_csv(csv_file_path)
        df = self.clean_column_names(df)
        column_names = df.columns.tolist()

        pii_flags = []
        critical_data_elements = []
        
        for column in column_names:
            if self.is_pii(column):
                similar_columns = [col for sheet in all_sheets for col in sheet[1].columns if self.similar(col.lower(), column.lower()) > 0.8]
                description = ', '.join(set(similar_columns))
                pii_flags.append(f"Yes, description: {description}")
            else:
                pii_flags.append("No")
            
            if column in critical_elements:
                critical_data_elements.append(f"Yes, files: {', '.join(critical_elements[column])}")
            else:
                critical_data_elements.append("No")
        
        data_quality_checks_df = pd.DataFrame({
            "column_names": column_names,
            "PII_Flag": pii_flags,
            "test_completeness": ["Not Assessed" for _ in column_names],  # Set default value to "Not Assessed"
            "test_uniqueness": ["" for _ in column_names],
            "test_timeliness": ["" for _ in column_names],
            "test_consistency": ["" for _ in column_names],
            "test_accuracy": ["" for _ in column_names],
            "test_validity": ["" for _ in column_names],
            "critical_data_element": critical_data_elements
        })

        with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
            data_quality_checks_df.to_excel(writer, sheet_name='Data Quality Checks', index=False, startrow=1)

        # Load the workbook to add the description
        workbook = load_workbook(excel_file_path)
        sheet = workbook['Data Quality Checks']
        
        # Add description at the top
        description = (f"File Name: {os.path.basename(csv_file_path)}\n"
                       "Please provide 'Yes' or 'No' in the columns below for each data quality check.")
        sheet['A1'] = description
        sheet.merge_cells('A1:H1')
        sheet['A1'].alignment = Alignment(wrap_text=True, vertical='center')

        # Adjust column widths
        for col in range(1, sheet.max_column + 1):
            max_length = 0
            column = get_column_letter(col)
            for cell in sheet[column]:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                    except:
                        pass
            adjusted_width = (max_length + 2)
            sheet.column_dimensions[column].width = adjusted_width

        workbook.save(excel_file_path)
        print(f"Excel file '{excel_file_path}' created successfully with instructions.")

    @staticmethod
    def read_all_structured_files(directory_path: str) -> pd.DataFrame:
        """
        Read all CSV and Excel files from a directory and return their data as dataframes.
        
        Args:
            directory_path (str): Path to the directory containing files.
        
        Returns:
            List[Tuple[str, pd.DataFrame]]: List of tuples containing file paths and dataframes.
        """
        all_files = glob.glob(os.path.join(directory_path, "*.csv")) + glob.glob(os.path.join(directory_path, "*.xlsx"))
        all_sheets = []
        
        for file_path in all_files:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
                df = DataDoctor.clean_column_names(df)
                all_sheets.append((file_path, df))
            elif file_path.endswith('.xlsx'):
                xls = pd.ExcelFile(file_path)
                for sheet_name in xls.sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    df = DataDoctor.clean_column_names(df)
                    all_sheets.append((f"{file_path} - {sheet_name}", df))
        
        return all_sheets

    @staticmethod
    def find_critical_elements(all_sheets: List[Tuple[str, pd.DataFrame]]) -> Dict[str, List[str]]:
        """
        Find critical elements (columns) that appear in multiple files.
        
        Args:
            all_sheets (List[Tuple[str, pd.DataFrame]]): List of tuples containing file paths and dataframes.
        
        Returns:
            Dict[str, List[str]]: Dictionary with column names as keys and list of file paths as values.
        """
        column_files_map = defaultdict(list)
        for file_path, df in all_sheets:
            for column in df.columns:
                column_files_map[column].append(file_path)
        
        critical_elements = {column: files for column, files in column_files_map.items() if len(files) > 1}
        return critical_elements

    def evaluate_data_quality(self, data_file_path: str, template_file_path: str) -> pd.DataFrame:
        """
        Evaluate data quality based on a template.
        
        Args:
            data_file_path (str): Path to the data file (.csv or .xlsx).
            template_file_path (str): Path to the template file (.xlsx).
        
        Returns:
            pd.DataFrame: DataFrame containing completeness assessment results.
        """
        df_template = self.read_data_quality_template(template_file_path)

        if data_file_path.endswith('.csv'):
            df_data = pd.read_csv(data_file_path)
        elif data_file_path.endswith('.xlsx'):
            df_data = pd.read_excel(data_file_path)
        else:
            raise ValueError("Unsupported file format. Please use .csv or .xlsx files.")

        completeness_results = pd.DataFrame(columns=['Column Name', 'Total Rows', 'Missing Values', 'Non-Missing Values', 'Completeness (%)'])

        if not df_data.empty:
            df_data = self.clean_column_names(df_data)
            for index, row in df_template.iterrows():
                column_name = row['column_names']
                test_completeness = str(row['test_completeness']).strip().lower() if pd.notna(row['test_completeness']) else 'not assessed'
                if test_completeness == 'yes':
                    if column_name in df_data.columns:
                        completeness_df = self.assess_completeness(df_data, column_name)
                        if not completeness_df.empty:
                            completeness_results = pd.concat([completeness_results, completeness_df], ignore_index=True)
                    else:
                        print(f"Warning: Column '{column_name}' not found in data file.")
                else:
                    not_assessed_df = pd.DataFrame({
                        'Column Name': [column_name],
                        'Total Rows': ['N/A'],
                        'Missing Values': ['N/A'],
                        'Non-Missing Values': ['N/A'],
                        'Completeness (%)': ['Not Assessed']
                    })
                    completeness_results = pd.concat([completeness_results, not_assessed_df], ignore_index=True)
        else:
            print("Warning: The data file is empty.")

        if completeness_results.empty:
            print("No completeness analysis results to display.")
        else:
            print("Completeness analysis results:")
            print(completeness_results)

        return completeness_results


# Example usage:
if __name__ == "__main__":
    data_file_path = 'data/case_allocations.csv'
    template_file_path = 'data/data_quality_checks_template.xlsx'

    # Create an instance of DataDoctor
    data_doctor = DataDoctor()

    # Check if the template file exists, and create if it doesn't
    data_doctor.configure_quality_check(data_file_path, template_file_path)

    # Evaluate data quality based on the template
    completeness_results = data_doctor.evaluate_data_quality(data_file_path, template_file_path)

    # Display the completeness results DataFrame
    print("Completeness Results DataFrame:")
    print(completeness_results)
