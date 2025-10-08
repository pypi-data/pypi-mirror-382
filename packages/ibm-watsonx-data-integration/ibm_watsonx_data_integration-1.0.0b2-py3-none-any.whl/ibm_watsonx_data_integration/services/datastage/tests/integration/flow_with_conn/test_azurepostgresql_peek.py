from ibm_watsonx_data_integration.services.datastage.models.enums import AZURE_POSTGRESQL_CONNECTION
from os import environ
from tests.integration.datastage.util import AbstractFlowRunTest
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestAzurePosgresqlConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "azurepostgresql_peek"

    def get_fc(self, project: Project):
        fc = project.create_flow(name=self.get_flow_name(), environment=None, description="", flow_type="datastage")

        # Stages
        _test1_1_ = fc.add_stage("Azure PostgreSQL", "Test1_1")
        _test1_1_.configuration.schema_name = "public"
        _test1_1_.configuration.table_name = "Test1"

        _test1_1_.configuration.connection.authentication_method = (
            AZURE_POSTGRESQL_CONNECTION.AuthMethod.user_credentials
        )
        _test1_1_.configuration.connection.database = "postgres"
        _test1_1_.configuration.connection.hostname_or_ip_address = environ["AZUREPOSTGRESQL_HOST"]
        _test1_1_.configuration.connection.password = environ["AZUREPOSTGRESQL_PASSWORD"]
        _test1_1_.configuration.connection.port = "5432"
        _test1_1_.configuration.connection.proxy = False
        _test1_1_.configuration.connection.port_is_ssl_enabled = True
        _test1_1_.configuration.connection.username = environ["AZUREPOSTGRESQL_USERNAME"]

        _peek_1_ = fc.add_stage("Peek", "Peek_1")

        # Graph
        test1_1_schema = _test1_1_.connect_output_to(_peek_1_).set_name("Link_1").create_schema()

        # Schemas
        test1_1_schema.add_field("CHAR", "col1").nullable().length(6)
        test1_1_schema.add_field("NUMERIC", "col2").nullable().length(6)
        test1_1_schema.add_field("VARCHAR", "col3").nullable().length(6)
        test1_1_schema.add_field("DOUBLE", "col4").nullable()
        test1_1_schema.add_field("BIGINT", "col6").nullable()
        test1_1_schema.add_field("LONGVARBINARY", "col7").nullable().length(2048)
        test1_1_schema.add_field("DOUBLE", "col8").nullable()
        test1_1_schema.add_field("BIT", "col9").nullable()
        test1_1_schema.add_field("DATE", "col10").nullable()
        test1_1_schema.add_field("INTEGER", "col11").nullable()
        test1_1_schema.add_field("VARCHAR", "col12").nullable().length(6)
        test1_1_schema.add_field("VARCHAR", "col13").nullable().length(6)
        test1_1_schema.add_field("LONGVARBINARY", "col14").nullable().length(2048)
        test1_1_schema.add_field("CHAR", "col15").nullable().length(6)
        test1_1_schema.add_field("NUMERIC", "col16").nullable().length(6)
        test1_1_schema.add_field("VARCHAR", "col17").nullable().length(6)
        test1_1_schema.add_field("REAL", "col18").nullable().length(7)
        test1_1_schema.add_field("SMALLINT", "col19").nullable()
        test1_1_schema.add_field("TIMESTAMP", "col20").nullable()
        test1_1_schema.add_field("TIMESTAMP", "col21").nullable()
        test1_1_schema.add_field("SMALLINT", "col22").nullable()
        test1_1_schema.add_field("LONGVARBINARY", "col23").nullable().length(2048)
        test1_1_schema.add_field("VARCHAR", "col24").nullable().length(6)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
