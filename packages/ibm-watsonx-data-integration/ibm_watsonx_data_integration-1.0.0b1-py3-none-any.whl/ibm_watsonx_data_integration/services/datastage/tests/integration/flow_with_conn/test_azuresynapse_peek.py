from ibm_watsonx_data_integration.services.datastage.models.enums import AZURESYNAPSE_CONNECTION
from os import environ
from tests.integration.datastage.util import AbstractFlowRunTest
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestAzureSynapseConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "azuresynapse_peek"

    def get_fc(self, project: Project):
        fc = project.create_flow(name=self.get_flow_name(), environment=None, description="", flow_type="datastage")

        # Stages
        _test_table_1_ = fc.add_stage("Microsoft Azure Synapse Analytics", "test_table_1")
        _test_table_1_.configuration.schema_name = "tm_ds"
        _test_table_1_.configuration.table_name = "test_table"
        _test_table_1_.configuration.connection.authentication_method = AZURESYNAPSE_CONNECTION.AuthMethod.entra_id_user
        _test_table_1_.configuration.connection.database = "CONOPSDB"
        _test_table_1_.configuration.connection.hostname_or_ip_address = environ["AZURESYNAPSE_HOST"]
        _test_table_1_.configuration.connection.password = environ["AZURESYNAPSE_PASSWORD"]
        _test_table_1_.configuration.connection.port = "1433"
        _test_table_1_.configuration.connection.proxy = False
        _test_table_1_.configuration.connection.port_is_ssl_enabled = True
        _test_table_1_.configuration.connection.username = environ["AZURESYNAPSE_USERNAME"]

        _peek_1_ = fc.add_stage("Peek", "Peek_1")

        # Graph
        test_table_1_schema = _test_table_1_.connect_output_to(_peek_1_).set_name("Link_1").create_schema()

        # Schemas
        test_table_1_schema.add_field("BIGINT", "TYPE_BIGINT")
        test_table_1_schema.add_field("BINARY", "TYPE_BINARY").length(10)
        test_table_1_schema.add_field("BIT", "TYPE_BIT")
        test_table_1_schema.add_field("CHAR", "TYPE_CHAR").length(20)
        test_table_1_schema.add_field("DATE", "TYPE_DATE")
        test_table_1_schema.add_field("DECIMAL", "TYPE_DECIMAL").length(5).precision(5).scale(2)
        test_table_1_schema.add_field("FLOAT", "TYPE_DOUBLE")
        test_table_1_schema.add_field("FLOAT", "TYPE_FLOAT")
        test_table_1_schema.add_field("INTEGER", "TYPE_INTEGER")
        test_table_1_schema.add_field("VARCHAR", "TYPE_LONGNVARCHAR").length(4000)
        test_table_1_schema.add_field("VARBINARY", "TYPE_LONGVARBINARY").length(8000)
        test_table_1_schema.add_field("VARCHAR", "TYPE_LONGVARCHAR").length(8000)
        test_table_1_schema.add_field("CHAR", "TYPE_NCHAR").length(10)
        test_table_1_schema.add_field("NUMERIC", "TYPE_NUMERIC").length(5)
        test_table_1_schema.add_field("VARCHAR", "TYPE_NVARCHAR").length(50)
        test_table_1_schema.add_field("REAL", "TYPE_REAL").length(7)
        test_table_1_schema.add_field("SMALLINT", "TYPE_SMALLINT")
        test_table_1_schema.add_field("TIMESTAMP", "TYPE_TIME")
        test_table_1_schema.add_field("TIMESTAMP", "TYPE_TIMESTAMP")
        test_table_1_schema.add_field("TINYINT", "TYPE_TINYINT").unsigned()
        test_table_1_schema.add_field("VARBINARY", "TYPE_VARBINARY").length(10)
        test_table_1_schema.add_field("VARCHAR", "TYPE_VARCHAR").length(50)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
