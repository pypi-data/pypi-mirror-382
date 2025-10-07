from ibm_watsonx_data_integration.services.datastage.models.enums import DB2FORDATASTAGE_CONNECTION
from ibm_watsonx_data_integration.services.datastage.models.flow.datastage_flow import DataStageFlow
from ibm_watsonx_data_integration.services.datastage.tests.integration.util import AbstractFlowRunTest
from os import environ
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestDb2DatastageConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "db2datastage_peek"

    def get_fc(self, project: Project):
        fc = DataStageFlow(project=project, name=self.get_flow_name(), description="", flow_type="datastage")

        # Stages
        _autotesttbl_1_ = fc.add_stage("IBM Db2 for DataStage", "AUTOTESTTBL_1")
        _autotesttbl_1_.configuration.generate_sql_at_runtime = True
        _autotesttbl_1_.configuration.table_name = '"TESTUSER"."AUTOTESTTBL"'
        _autotesttbl_1_.configuration.enable_quoted_identifiers = True

        _autotesttbl_1_.configuration.connection.hostname = environ["DB2DATASTAGE_ADVANCED_HOST"]
        _autotesttbl_1_.configuration.connection.ssl_connection = False
        _autotesttbl_1_.configuration.connection.credentials = (
            DB2FORDATASTAGE_CONNECTION.AuthenticationType.username_and_password
        )
        _autotesttbl_1_.configuration.connection.cas_lite_service_authorization_header = ""
        _autotesttbl_1_.configuration.connection.database = "CONOPS"
        _autotesttbl_1_.configuration.connection.keep_conductor_connection_alive = False
        _autotesttbl_1_.configuration.connection.password = environ["DB2DATASTAGE_PASSWORD"]
        _autotesttbl_1_.configuration.connection.username = environ["DB2DATASTAGE_USERNAME"]

        _peek_1_ = fc.add_stage("Peek", "Peek_1")

        # Graph
        autotesttbl_1_schema = _autotesttbl_1_.connect_output_to(_peek_1_).set_name("Link_1").create_schema()

        # Schemas
        autotesttbl_1_schema.add_field("CHAR", "COL1").nullable().length(6)
        autotesttbl_1_schema.add_field("DECIMAL", "COL2").nullable().length(6).precision(6)
        autotesttbl_1_schema.add_field("VARCHAR", "COL3").nullable().length(6)
        autotesttbl_1_schema.add_field("DOUBLE", "COL4").nullable()
        autotesttbl_1_schema.add_field("BIGINT", "COL6").nullable()
        autotesttbl_1_schema.add_field("REAL", "COL8").nullable().length(4)
        autotesttbl_1_schema.add_field("DATE", "COL10").nullable()
        autotesttbl_1_schema.add_field("INTEGER", "COL11").nullable()
        autotesttbl_1_schema.add_field("SMALLINT", "COL19").nullable()
        autotesttbl_1_schema.add_field("TIME", "COL20").nullable()

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
