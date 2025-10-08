from ibm_watsonx_data_integration.services.datastage.models.enums import AZUREDATALAKE, AZUREDATALAKE_CONNECTION
from os import environ
from tests.integration.datastage.util import AbstractFlowRunTest
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestAzureDataLakeConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "azuredatalake_peek"

    def get_fc(self, project: Project):
        fc = project.create_flow(name=self.get_flow_name(), environment=None, description="", flow_type="datastage")

        # Stages
        _fastpath_test_1_ = fc.add_stage("Microsoft Azure Data Lake Storage", "fastpath_test_1")
        _fastpath_test_1_.configuration.escape_character = AZUREDATALAKE.EscapeCharacter.double_quote
        _fastpath_test_1_.configuration.file_format = AZUREDATALAKE.FileFormat.delimited
        _fastpath_test_1_.configuration.file_name = "fastpath_test"
        _fastpath_test_1_.configuration.first_line_is_header = True
        _fastpath_test_1_.configuration.infer_as_varchar = False
        _fastpath_test_1_.configuration.quote_character = AZUREDATALAKE.QuoteCharacter.double_quote

        _fastpath_test_1_.configuration.connection.authentication_method = (
            AZUREDATALAKE_CONNECTION.AuthMethod.client_credentials
        )
        _fastpath_test_1_.configuration.connection.client_id = environ["AZUREDATALAKE_CLIENT_ID"]
        _fastpath_test_1_.configuration.connection.client_secret = environ["AZUREDATALAKE_CLIENT_SECRET"]
        _fastpath_test_1_.configuration.connection.proxy = False
        _fastpath_test_1_.configuration.connection.tenant_id = "bacc55be-2e5e-4227-8635-6dbeec84ee1e"
        _fastpath_test_1_.configuration.connection.url = "https://conopsstorage1.dfs.core.windows.net/tm-ds-storage-1"

        _peek_1_ = fc.add_stage("Peek", "Peek_1")

        # Graph
        fastpath_test_1_schema = _fastpath_test_1_.connect_output_to(_peek_1_).set_name("Link_1").create_schema()

        # Schemas
        fastpath_test_1_schema.add_field(
            "VARCHAR",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        ).nullable().length(1024)
        fastpath_test_1_schema.add_field(
            "VARCHAR",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa__DUPLICATE__1",
        ).nullable().length(1024)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
