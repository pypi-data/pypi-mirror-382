from ibm_watsonx_data_integration.services.datastage.models.enums import SNOWFLAKE_CONNECTION
from os import environ
from tests.integration.datastage.util import AbstractFlowRunTest
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestSnowflakeConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "snowflake_peek"

    def get_fc(self, project: Project):
        fc = project.create_flow(name=self.get_flow_name(), environment=None, description="", flow_type="datastage")

        # Stages
        _testtablerandom_1_ = fc.add_stage("Snowflake", "testtablerandom_1")
        _testtablerandom_1_.configuration.ds_enable_quoted_ids = True
        _testtablerandom_1_.configuration.ds_table_name = "TM_DS.testtable-random"
        _testtablerandom_1_.configuration.schema_name = "TM_DS"
        _testtablerandom_1_.configuration.table_name = "testtable-random"

        _testtablerandom_1_.configuration.connection.account_name = "wv03539.us-east-2.aws"
        _testtablerandom_1_.configuration.connection.authentication_method = (
            SNOWFLAKE_CONNECTION.AuthMethod.username_password
        )
        _testtablerandom_1_.configuration.connection.database = "TM_DS_DB"
        # _testtablerandom_1_.configuration.connection.hostname=environ["SNOWFLAKE_HOSTNAME_OR_IP_ADDRESS"]
        _testtablerandom_1_.configuration.connection.password = environ["SNOWFLAKE_PASSWORD"]
        _testtablerandom_1_.configuration.connection.role = "TM_DS_ROLE"
        _testtablerandom_1_.configuration.connection.username = environ["SNOWFLAKE_USERNAME"]
        _testtablerandom_1_.configuration.connection.warehouse = "DS_WH"

        _peek_1_ = fc.add_stage("Peek", "Peek_1")

        # Graph
        testtablerandom_1_schema = _testtablerandom_1_.connect_output_to(_peek_1_).set_name("Link_1").create_schema()

        # Schemas
        testtablerandom_1_schema.add_field("VARCHAR", "COLUMN_1").length(10)
        testtablerandom_1_schema.add_field("DECIMAL", "COLUMN_2").length(38).precision(38)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
