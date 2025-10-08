import pandas as pd
import re
from brynq_sdk_functions import Functions
from .bank import Bank
from .employment import Employment
from .salaries import Salaries
from .schemas.people import PeopleSchema
from .work import Work
from .custom_tables import CustomTables


class People:
    def __init__(self, bob):
        self.bob = bob
        self.salaries = Salaries(bob)
        self.employment = Employment(bob)
        self.bank = Bank(bob)
        self.work = Work(bob)
        self.custom_tables = CustomTables(bob)
        self.schema = PeopleSchema
        self.field_name_in_body, self.field_name_in_response, self.endpoint_to_response = self._init_fields()

        # Define payroll information types and their configurations
        self.payroll_types = {
            'entitlement': {
                'pattern': 'payroll.entitlement.',
                'named_list_key': 'entitlementType'
            },
            'variable': {
                'pattern': 'payroll.variable.',
                'named_list_key': 'payrollVariableType'
            }
        }
        self.payroll_mappings = {}

    def _add_payroll_fields_to_request(self, body_fields: list, response_fields: list, payroll_type: str) -> tuple[list, list]:
        """
        Add payroll fields to request fields for a specific payroll type.

        Args:
            body_fields: Current body fields
            response_fields: Current response fields
            payroll_type: Type of payroll information (e.g., 'entitlement', 'variable')

        Returns:
            - body_fields: Updated body fields including payroll fields
            - response_fields: Updated response fields including payroll fields
        """
        if payroll_type not in self.payroll_types:
            return body_fields, response_fields

        pattern = self.payroll_types[payroll_type]['pattern']
        payroll_fields_to_add = [field for field in self.field_name_in_body if pattern in field.lower()]
        payroll_response_fields = [self.endpoint_to_response.get(field) for field in payroll_fields_to_add if field in self.endpoint_to_response]

        for field in payroll_fields_to_add:
            if field not in body_fields:
                body_fields.append(field)

        for field in payroll_response_fields:
            if field and field not in response_fields:
                response_fields.append(field)

        return body_fields, response_fields

    def _get_payroll_mapping(self, payroll_type: str) -> dict:
        """
        Get mapping of payroll IDs to their names from the named-lists endpoint for a specific payroll type.

        Args:
            payroll_type: Type of payroll information (e.g., 'entitlement', 'variable')

        Returns:
            Dictionary mapping IDs to names
        """
        if payroll_type not in self.payroll_types:
            return {}

        # Check if we already have the mapping cached
        if payroll_type in self.payroll_mappings:
            return self.payroll_mappings[payroll_type]

        resp = self.bob.session.get(
            url=f"{self.bob.base_url}company/named-lists",
            timeout=self.bob.timeout,
            headers=self.bob.headers
        )
        named_lists = resp.json()

        # Extract the mapping for this payroll type
        mapping = {}
        named_list_key = self.payroll_types[payroll_type]['named_list_key']
        if named_list_key in named_lists:
            for value in named_lists[named_list_key]['values']:
                mapping[value['id']] = value['name']

        # Cache the mapping
        self.payroll_mappings[payroll_type] = mapping
        return mapping

    def _flatten_nested_payroll_data(self, df: pd.DataFrame, pattern: str) -> pd.DataFrame:
        """
        Flatten nested JSON structures in payroll columns.

        Args:
            df: DataFrame with potentially nested payroll data
            pattern: Pattern to identify payroll columns (e.g., 'payroll.variable.')

        Returns:
            DataFrame with flattened payroll columns
        """
        # Identify payroll columns
        payroll_columns = [col for col in df.columns if pattern in col.lower()]

        if not payroll_columns:
            return df

        # Create a copy to avoid modifying the original
        df_result = df.copy()

        # Process each payroll column
        for col in payroll_columns:
            # Check if the column contains nested data
            if df_result[col].notna().any():
                # Get the first non-null value to check structure
                sample_value = df_result[col].dropna().iloc[0] if not df_result[col].dropna().empty else None

                if isinstance(sample_value, dict):
                    # Flatten nested structure
                    nested_df = pd.json_normalize(df_result[col].tolist())

                    # Rename columns to include the original column name as prefix
                    nested_df.columns = [f"{col}.{subcol}" for subcol in nested_df.columns]

                    # Drop the original column and add flattened columns
                    df_result = df_result.drop(columns=[col])
                    df_result = pd.concat([df_result, nested_df], axis=1)

        return df_result

    def _extract_payroll_columns(self, df: pd.DataFrame, payroll_type: str) -> pd.DataFrame:
        """
        Extract payroll columns from DataFrame and rename them based on mapping.

        Args:
            df: DataFrame containing all data including payroll columns
            payroll_type: Type of payroll information (e.g., 'entitlement', 'variable')

        Returns:
            DataFrame with only payroll columns (renamed if mapping available)
        """
        if payroll_type not in self.payroll_types:
            return pd.DataFrame(index=df.index)

        # Get the pattern for this payroll type
        pattern = self.payroll_types[payroll_type]['pattern']

        # Identify all payroll columns for this type
        payroll_columns = [col for col in df.columns if pattern in col.lower()]

        if not payroll_columns:
            # No payroll columns found, return empty DataFrame
            return pd.DataFrame(index=df.index)

        # Extract payroll columns
        df_payroll = df[payroll_columns].copy()

        # Get mapping for this payroll type
        payroll_mapping = self._get_payroll_mapping(payroll_type)

        # Rename payroll columns if mapping is available
        rename_dict = {}
        if payroll_mapping:
            for col in df_payroll.columns:
                # Extract the ID from the column name (any digits after the pattern)
                # Use case-insensitive match but extract from original column name
                pattern_regex = pattern.replace('.', r'\.')  # Escape dots for regex
                match = re.search(rf'({pattern_regex})(\d+)', col, re.IGNORECASE)
                if match:
                    payroll_id = match.group(2)
                    if payroll_id in payroll_mapping:
                        # Replace only the first occurrence of the ID with the name
                        # This preserves any suffixes like .value, .currency, etc.
                        new_col_name = col[:match.start(2)] + payroll_mapping[payroll_id] + col[match.end(2):]
                        rename_dict[col] = new_col_name

            # Apply the renaming
            if rename_dict:
                df_payroll = df_payroll.rename(columns=rename_dict)

        return df_payroll

    def get(self, additional_fields: list[str] = None, field_selection: list[str] = None, add_payroll_information: list[str] = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get people from Bob

        Args:
            additional_fields (list[str]): Additional fields to get (not defined in the schema)
            field_selection (list[str]): Fields to get (defined in the schema), if not provided, all fields are returned
            add_payroll_information (list[str]): List of payroll information types to include (valid options: 'entitlement', 'variable')

        Returns:
            valid_people (pd.DataFrame): Validated people data (with payroll information appended if requested)
            invalid_people (pd.DataFrame): Invalid records
        """
        #resp = self.bob.session.get(url=f"{self.bob.base_url}profiles", timeout=self.bob.timeout)
        if additional_fields is None:
            additional_fields = []
        body_fields = list(set(self.field_name_in_body + additional_fields))
        response_fields = list(set(self.field_name_in_response + additional_fields))

        if field_selection:
            body_fields = [field for field in body_fields if field in field_selection]
            response_fields = [self.endpoint_to_response.get(field) for field in field_selection if field in self.endpoint_to_response]

        # Add payroll fields to request if needed (before making the API call)
        if add_payroll_information:
            # Validate and filter payroll types
            valid_payroll_types = [pt for pt in add_payroll_information if pt in self.payroll_types]

            for payroll_type in valid_payroll_types:
                body_fields, response_fields = self._add_payroll_fields_to_request(body_fields, response_fields, payroll_type)

        # Bob sucks with default fields so you need to do a search call to retrieve additional fields.
        resp_additional_fields = self.bob.session.post(url=f"{self.bob.base_url}people/search",
                                                       json={
                                                           "fields": body_fields,
                                                           "filters": []
                                                       },
                                                       timeout=self.bob.timeout)
        df = pd.json_normalize(resp_additional_fields.json()['employees'])

        # Validate payroll types if requested
        valid_payroll_types = []
        if add_payroll_information:
            valid_payroll_types = [pt for pt in add_payroll_information if pt in self.payroll_types]

            # Flatten nested data for each payroll type
            for payroll_type in valid_payroll_types:
                pattern = self.payroll_types[payroll_type]['pattern']
                df = self._flatten_nested_payroll_data(df, pattern)

        # Now filter columns - include original response_fields plus any flattened payroll columns
        columns_to_keep = []
        for col in df.columns:
            # Keep if it's in response_fields
            if col in response_fields:
                columns_to_keep.append(col)
            # Or if it's a payroll column (original or flattened)
            elif valid_payroll_types:
                for payroll_type in valid_payroll_types:
                    pattern = self.payroll_types[payroll_type]['pattern']
                    if pattern in col.lower():
                        columns_to_keep.append(col)
                        break

        df = df[columns_to_keep]

        # Map DataFrame columns (response fields) back to alias (endpoint) fields for validation
        response_to_endpoint = {v: k for k, v in self.endpoint_to_response.items() if v}
        df = df.rename(columns={col: response_to_endpoint[col] for col in df.columns if col in response_to_endpoint})

        # Extract payroll information if requested
        payroll_dataframes = {}
        if valid_payroll_types:
            for payroll_type in valid_payroll_types:
                # Extract payroll columns into separate DataFrame
                df_payroll = self._extract_payroll_columns(df, payroll_type)
                if not df_payroll.empty:
                    payroll_dataframes[payroll_type] = df_payroll

                    # Remove payroll columns from main DataFrame for validation
                    pattern = self.payroll_types[payroll_type]['pattern']
                    payroll_columns = [col for col in df.columns if pattern in col.lower()]
                    if payroll_columns:
                        df = df.drop(columns=payroll_columns)

        # Validate the data (without payroll information)
        valid_people, invalid_people = Functions.validate_data(df=df, schema=PeopleSchema, debug=True)

        # Append all payroll information to valid_people if they exist
        if payroll_dataframes and not valid_people.empty:
            for payroll_type, df_payroll in payroll_dataframes.items():
                # Only include payroll data for valid rows
                df_payroll_valid = df_payroll.loc[valid_people.index]
                # Append payroll columns to valid_people
                valid_people = pd.concat([valid_people, df_payroll_valid], axis=1)


        # A lot of fields from Bob are returned with only ID's. Those fields should be mapped to names. Therefore, we need to get the mapping from the named-lists endpoint.
        resp_named_lists = self.bob.session.get(url=f"{self.bob.base_url}company/named-lists", timeout=self.bob.timeout, headers=self.bob.headers)
        named_lists = resp_named_lists.json()

        # Transform named_lists to create id-to-value mappings for each field
        named_lists = {key.split('.')[-1]: {item['id']: item['value'] for item in value['values']} for key, value in named_lists.items()}

        for field in valid_people.columns:
            # Fields in the response and in the named-list does have different building blocks (e.g. people.payroll.entitlement. or people.entitlement.). But they both end with the same last block
            field_df = field.split('.')[-1].split('work_')[-1]
            if field_df in named_lists.keys() and field_df not in ['site']:
                valid_people[field] = valid_people[field].map(named_lists[field_df])

        return valid_people, invalid_people


    def _init_fields(self) -> tuple[list[str], list[str], dict[str, str]]:
        resp_fields = self.bob.session.get(
            url=f"{self.bob.base_url}company/people/fields",
            timeout=self.bob.timeout,
            headers=self.bob.headers
        )
        fields = resp_fields.json()
        field_name_in_body = [field.get('id') for field in fields]
        # For all field names in field_name_in_body containing 'root.', add an alternative without 'root.' in addition to those fields
        field_name_in_body = field_name_in_body
        field_name_in_response = [field['jsonPath'] for field in fields]
        endpoint_to_response = {field['id']: field['jsonPath'] for field in fields}

        return field_name_in_body, field_name_in_response, endpoint_to_response



    def _get_employee_id_to_person_id_mapping(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        employee_id_in_company = "work.employeeIdInCompany"
        person_id = "root.id"

        body_fields = [employee_id_in_company, person_id]
        response_fields = [self.endpoint_to_response.get(field) for field in body_fields if field in self.endpoint_to_response]

        resp_additional_fields = self.bob.session.post(url=f"{self.bob.base_url}people/search",
                                                       json={
                                                           "fields": body_fields,
                                                           "filters": []
                                                       },
                                                       timeout=self.bob.timeout)
        df = pd.json_normalize(resp_additional_fields.json()['employees'])
        df = df[[col for col in response_fields if col in df.columns]]
        # Get the valid column names from PeopleSchema
        valid_people, invalid_people = Functions.validate_data(df=df, schema=PeopleSchema, debug=True)
        return valid_people, invalid_people
