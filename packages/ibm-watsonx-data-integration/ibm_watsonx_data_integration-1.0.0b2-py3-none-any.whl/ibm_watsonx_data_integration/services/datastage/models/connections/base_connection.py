from pydantic import BaseModel
from ibm_watsonx_data_integration.cpd_models.connections_model import Connection

class BaseConnection(BaseModel):
    asset_id: str | None = None
    proj_id: str | None = None

    def from_connection(self, connection: Connection):
        """Initializes the underlying DataStage connection object from a generic cpd connection"""

        self.asset_id = connection.metadata.asset_id
        self.proj_id = connection.metadata.project_id
        self.name = connection.name

        alias_to_attr = {}
        for field_name, field_info in self.__class__.model_fields.items():
            if field_info.alias:
                alias_to_attr[field_info.alias] = field_name

        missing_keys = set()

        for k, v in connection.properties.items():
            if k in alias_to_attr:
                setattr(self, alias_to_attr[k], v)
            else:
                # couldn't find a matching attribute on the Conn object to set
                missing_keys.add(k)

        if missing_keys: print(f"Connection attributes could not be set: {missing_keys}")
        return self
