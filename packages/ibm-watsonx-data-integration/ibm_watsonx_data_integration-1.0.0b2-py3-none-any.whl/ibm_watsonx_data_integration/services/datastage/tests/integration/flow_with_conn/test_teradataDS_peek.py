from ibm_watsonx_data_integration.services.datastage.models.enums import TERADATA_DATASTAGE_CONNECTION
from os import environ
from tests.integration.datastage.util import AbstractFlowRunTest
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestTeradataForDataStageConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "teradataDS_peek"

    def get_fc(self, project: Project):
        fc = project.create_flow(name=self.get_flow_name(), environment=None, description="", flow_type="datastage")

        # Stages
        _fastpathtest_1_ = fc.add_stage("Teradata database for DataStage", "fastpathTest_1")
        _fastpathtest_1_.configuration.generate_sql_at_runtime = True
        _fastpathtest_1_.configuration.table_name = '"tm_ds_db_1"."fastpathTest"'

        _fastpathtest_1_.configuration.connection.automatically_map_character_set_encoding = True
        _fastpathtest_1_.configuration.connection.cas_lite_service_authorization_header = ""
        _fastpathtest_1_.configuration.connection.database = "tm_ds_db_1"
        _fastpathtest_1_.configuration.connection.logon_mechanism = TERADATA_DATASTAGE_CONNECTION.LogOnMech.default
        _fastpathtest_1_.configuration.connection.password = environ["TERADATADS_PASSWORD"]
        _fastpathtest_1_.configuration.connection.read_query_band_expression_from_the_file = False
        _fastpathtest_1_.configuration.connection.server = environ["TERADATADS_SERVER"]
        _fastpathtest_1_.configuration.connection.transaction_mode = TERADATA_DATASTAGE_CONNECTION.TransactionMode.ansi
        _fastpathtest_1_.configuration.connection.unicode_pass_through = False
        _fastpathtest_1_.configuration.connection.username = environ["TERADATADS_USERNAME"]

        _peek_1_ = fc.add_stage("Peek", "Peek_1")

        # Graph
        fastpathtest_1_schema = _fastpathtest_1_.connect_output_to(_peek_1_).set_name("Link_1").create_schema()

        # Schemas
        fastpathtest_1_schema.add_field("INTEGER", "a")
        fastpathtest_1_schema.add_field("CHAR", "b").length(1)
        fastpathtest_1_schema.add_field("CHAR", "c").length(1)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
