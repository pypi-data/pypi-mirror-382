from ibm_watsonx_data_integration.services.datastage.models.enums import AZURESQL_CONNECTION
from os import environ
from tests.integration.datastage.util import AbstractFlowRunTest
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestAzureSqlConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "azuresql_peek"

    def get_fc(self, project: Project):
        fc = project.create_flow(name=self.get_flow_name(), environment=None, description="", flow_type="datastage")

        # Stages
        _mytesttable_1_ = fc.add_stage("Microsoft Azure SQL Database", "mytesttable_1")
        _mytesttable_1_.configuration.schema_name = "tm_ds"
        _mytesttable_1_.configuration.table_name = "mytesttable"

        _mytesttable_1_.configuration.connection.authentication_method = AZURESQL_CONNECTION.AuthMethod.entra_id_service
        _mytesttable_1_.configuration.connection.client_id = environ["AZURESQL_CLIENT_ID"]
        _mytesttable_1_.configuration.connection.client_secret = environ["AZURESQL_CLIENT_SECRET"]
        _mytesttable_1_.configuration.connection.database = "CONOPSDB"
        _mytesttable_1_.configuration.connection.hostname_or_ip_address = environ["AZURESQL_HOST"]
        _mytesttable_1_.configuration.connection.port = "1433"
        _mytesttable_1_.configuration.connection.proxy = False
        _mytesttable_1_.configuration.connection.port_is_ssl_enabled = True

        _peek_1_ = fc.add_stage("Peek", "Peek_1")

        # Graph
        mytesttable_1_schema = _mytesttable_1_.connect_output_to(_peek_1_).set_name("Link_1").create_schema()

        # Schemas
        mytesttable_1_schema.add_field("CHAR", "col1").nullable().length(6)
        mytesttable_1_schema.add_field("DECIMAL", "col2").nullable().length(6).precision(6)
        mytesttable_1_schema.add_field("VARCHAR", "col3").nullable().length(6)
        mytesttable_1_schema.add_field("FLOAT", "col4").nullable()
        mytesttable_1_schema.add_field("BIGINT", "col6").nullable()
        mytesttable_1_schema.add_field("BINARY", "col7").nullable().length(6)
        mytesttable_1_schema.add_field("FLOAT", "col8").nullable()
        mytesttable_1_schema.add_field("BIT", "col9").nullable()
        mytesttable_1_schema.add_field("DATE", "col10").nullable()
        mytesttable_1_schema.add_field("INTEGER", "col11").nullable()
        mytesttable_1_schema.add_field("VARCHAR", "col12").nullable().length(4000)
        mytesttable_1_schema.add_field("VARCHAR", "col13").nullable().length(8000)
        mytesttable_1_schema.add_field("VARBINARY", "col14").nullable().length(8000)
        mytesttable_1_schema.add_field("CHAR", "col15").nullable().length(6)
        mytesttable_1_schema.add_field("NUMERIC", "col16").nullable().length(6)
        mytesttable_1_schema.add_field("VARCHAR", "col17").nullable().length(6)
        mytesttable_1_schema.add_field("REAL", "col18").nullable().length(7)
        mytesttable_1_schema.add_field("SMALLINT", "col19").nullable()
        mytesttable_1_schema.add_field("TIMESTAMP", "col20").nullable()
        mytesttable_1_schema.add_field("TIMESTAMP", "col21").nullable()
        mytesttable_1_schema.add_field("TINYINT", "col22").nullable().unsigned()
        mytesttable_1_schema.add_field("VARBINARY", "col23").nullable().length(6)
        mytesttable_1_schema.add_field("VARCHAR", "col24").nullable().length(6)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
