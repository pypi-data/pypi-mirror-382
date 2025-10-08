from ibm_watsonx_data_integration.services.datastage.models.enums import (
    AZURE_FILE_STORAGE,
    AZURE_FILE_STORAGE_CONNECTION,
)
from ibm_watsonx_data_integration.services.datastage.models.flow.datastage_flow import DataStageFlow
from ibm_watsonx_data_integration.services.datastage.tests.integration.util import AbstractFlowRunTest
from os import environ
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestAzureFileStorageConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "azurefilestorage_peek"

    def get_fc(self, project: Project):
        fc = DataStageFlow(project=project, name=self.get_flow_name(), description="", flow_type="datastage")

        # Stages
        _onpremcsv_1_ = fc.add_stage("Microsoft Azure File Storage", "onpremcsv_1")
        _onpremcsv_1_.configuration.ds_file_format = AZURE_FILE_STORAGE.DSFileFormat.comma_separated_value_csv
        _onpremcsv_1_.configuration.ds_file_name = "onprem.csv"
        _onpremcsv_1_.configuration.escape_character = AZURE_FILE_STORAGE.EscapeCharacter.double_quote
        _onpremcsv_1_.configuration.file_name = "onprem.csv"
        _onpremcsv_1_.configuration.file_name_source = "onprem.csv"
        _onpremcsv_1_.configuration.file_share = "test"
        _onpremcsv_1_.configuration.file_share_source = "test"
        _onpremcsv_1_.configuration.first_line_is_header = True
        _onpremcsv_1_.configuration.first_row_is_header = True
        _onpremcsv_1_.configuration.infer_as_varchar = False
        _onpremcsv_1_.configuration.infer_schema = False
        _onpremcsv_1_.configuration.quote_character = AZURE_FILE_STORAGE.QuoteCharacter.double_quote

        _onpremcsv_1_.configuration.connection.authentication_method = (
            AZURE_FILE_STORAGE_CONNECTION.AuthMethod.connection_string
        )
        _onpremcsv_1_.configuration.connection.connection_string = environ["AZUREFILESTORAGE_CONN_STRING"]

        _peek_2_ = fc.add_stage("Peek", "Peek_2")

        # Graph
        onpremcsv_1_schema = _onpremcsv_1_.connect_output_to(_peek_2_).set_name("Link_3").create_schema()

        # Schemas
        onpremcsv_1_schema.add_field("VARCHAR", "aaaaaa").nullable().length(1024)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
