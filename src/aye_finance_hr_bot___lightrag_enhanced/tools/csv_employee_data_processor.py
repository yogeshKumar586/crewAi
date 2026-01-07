from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import requests
import csv
import json
from io import StringIO

class CsvEmployeeDataProcessorInput(BaseModel):
    """Input schema for CSV Employee Data Processor Tool."""
    csv_source: str = Field(..., description="URL to CSV file (direct download link) or raw CSV text content")
    search_field: str = Field(..., description="Column name to search in (e.g., 'Employee ID', 'Name', etc.)")
    search_value: str = Field(..., description="Value to search for")

class CsvEmployeeDataProcessor(BaseTool):
    """Tool for processing CSV employee data and searching for specific records using only standard Python libraries."""

    name: str = "CSV Employee Data Processor"
    description: str = (
        "Downloads CSV data from URL or processes raw CSV text, searches for employee records by matching "
        "search_field with search_value (case-insensitive partial matching), and returns structured employee data as JSON. "
        "Uses only Python standard libraries (csv module, not pandas)."
    )
    args_schema: Type[BaseModel] = CsvEmployeeDataProcessorInput

    def _run(self, csv_source: str, search_field: str, search_value: str) -> str:
        try:
            # Determine if csv_source is URL or raw CSV text
            if csv_source.startswith(('http://', 'https://')):
                # It's a URL, download the CSV
                try:
                    response = requests.get(csv_source, timeout=30)
                    response.raise_for_status()
                    csv_content = response.text
                except requests.RequestException as e:
                    return json.dumps({
                        "error": "CSV processing failed", 
                        "details": f"Failed to download CSV from URL: {str(e)}"
                    })
            else:
                # It's raw CSV text content
                csv_content = csv_source
            
            # Parse CSV using Python's built-in csv module
            try:
                csv_file = StringIO(csv_content)
                csv_reader = csv.DictReader(csv_file)
                
                # Convert to list of dictionaries to work with
                rows = list(csv_reader)
                
                if not rows:
                    return json.dumps({
                        "error": "CSV processing failed", 
                        "details": "CSV file is empty or contains no data rows"
                    })
                
                # Get column headers from the first row
                headers = list(rows[0].keys())
                
            except Exception as e:
                return json.dumps({
                    "error": "CSV processing failed", 
                    "details": f"Failed to parse CSV: {str(e)}"
                })
            
            # Check if search_field exists in the CSV headers
            if search_field not in headers:
                return json.dumps({
                    "error": "CSV processing failed", 
                    "details": f"Column '{search_field}' not found in CSV. Available columns: {headers}"
                })
            
            # Perform case-insensitive partial matching
            search_value_lower = search_value.lower()
            matching_record = None
            
            for row in rows:
                # Get the field value, handle None/empty values
                field_value = row.get(search_field, '')
                if field_value is None:
                    field_value = ''
                
                # Convert to string and perform case-insensitive partial matching
                field_value_str = str(field_value).lower()
                
                if search_value_lower in field_value_str:
                    matching_record = row
                    break
            
            if matching_record is None:
                return json.dumps({
                    "error": "Employee not found", 
                    "searched_field": search_field, 
                    "searched_value": search_value
                })
            
            # Clean up the record - convert empty strings to None for better JSON representation
            cleaned_record = {}
            for key, value in matching_record.items():
                if value == '' or value is None:
                    cleaned_record[key] = None
                else:
                    # Try to convert numeric strings to appropriate types
                    try:
                        # Try integer first
                        if value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
                            cleaned_record[key] = int(value)
                        # Try float
                        elif '.' in value:
                            cleaned_record[key] = float(value)
                        else:
                            cleaned_record[key] = value
                    except (ValueError, AttributeError):
                        # If conversion fails, keep as string
                        cleaned_record[key] = value
            
            return json.dumps(cleaned_record, indent=2)
            
        except Exception as e:
            return json.dumps({
                "error": "CSV processing failed", 
                "details": f"Unexpected error: {str(e)}"
            })