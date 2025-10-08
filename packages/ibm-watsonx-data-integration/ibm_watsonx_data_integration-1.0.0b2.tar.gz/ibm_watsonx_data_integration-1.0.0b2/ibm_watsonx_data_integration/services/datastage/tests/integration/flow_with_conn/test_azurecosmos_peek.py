from ibm_watsonx_data_integration.services.datastage.models.enums import AZURE_COSMOS_CONNECTION
from os import environ
from tests.integration.datastage.util import AbstractFlowRunTest
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestAzureCosmosConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "azurecosmos_peek"

    def get_fc(self, project: Project):
        fc = project.create_flow(name=self.get_flow_name(), environment=None, description="", flow_type="datastage")

        # Stages
        _aaa_tab_test_1_ = fc.add_stage("Microsoft Azure Cosmos DB", "aaa_tab_test_1")
        _aaa_tab_test_1_.configuration.collection = "aaa_tab_test"
        _aaa_tab_test_1_.configuration.database = "tm_cc_db_1"

        _aaa_tab_test_1_.configuration.connection.authentication_method = AZURE_COSMOS_CONNECTION.AuthMethod.master_key
        _aaa_tab_test_1_.configuration.connection.hostname = environ["AZURECOSMOS_HOST"]
        _aaa_tab_test_1_.configuration.connection.master_key = environ["AZURECOSMOS_MASTER_KEY"]

        _peek_1_ = fc.add_stage("Peek", "Peek_1")

        # Graph
        aaa_tab_test_1_schema = _aaa_tab_test_1_.connect_output_to(_peek_1_).set_name("Link_1").create_schema()

        # Schemas
        aaa_tab_test_1_schema.add_field("BIGINT", "col_int").nullable()
        aaa_tab_test_1_schema.add_field("VARCHAR", "col_varchar").nullable().length(1024)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
