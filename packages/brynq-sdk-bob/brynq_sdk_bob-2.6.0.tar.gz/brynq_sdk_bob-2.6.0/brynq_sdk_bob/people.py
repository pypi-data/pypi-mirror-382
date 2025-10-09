import pandas as pd
from typing import Optional
from brynq_sdk_functions import Functions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
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


        # Build API fields using column metadata if present (api_field), otherwise use the column (alias) name
    def __build_api_fields(self, schema_model: BrynQPanderaDataFrameModel) -> list[str]:
        schema = schema_model.to_schema()
        return [
            ((getattr(col, "metadata", None) or {}).get("api_field")) or col_name
            for col_name, col in schema.columns.items()
        ]

    def get(self, schema_custom_fields: Optional[BrynQPanderaDataFrameModel] = None) -> pd.DataFrame:

        core_fields = self.__build_api_fields(PeopleSchema)
        custom_fields = self.__build_api_fields(schema_custom_fields) if schema_custom_fields is not None else []
        fields = core_fields + custom_fields

        resp = self.bob.session.post(url=f"{self.bob.base_url}people/search",
                                      json={
                                          "fields": fields,
                                          "filters": []
                                          #"humanReadable": "REPLACE"
                                      },
                                      timeout=self.bob.timeout)
        resp.raise_for_status()
        df = pd.json_normalize(resp.json()['employees'])
        df = df.loc[:, ~df.columns.str.contains('value')]
        # Normalize separators in incoming data: convert '/' to '.' to match schema aliases
        df.columns = df.columns.str.replace('/', '.', regex=False)

        if schema_custom_fields is not None:
            valid_people, invalid_people_custom = Functions.validate_data(df=df, schema=schema_custom_fields, debug=True)
        else:
            valid_people = df
            invalid_people_custom = pd.DataFrame()

        valid_people, invalid_people = Functions.validate_data(df=valid_people, schema=PeopleSchema, debug=True)

        return valid_people, pd.concat([invalid_people, invalid_people_custom])
