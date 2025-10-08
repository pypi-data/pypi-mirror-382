from ibm_watsonx_data_integration.services.datastage.models.enums import (
    AZURE_BLOB_STORAGE,
    AZURE_BLOB_STORAGE_CONNECTION,
)
from ibm_watsonx_data_integration.services.datastage.models.flow.datastage_flow import DataStageFlow
from ibm_watsonx_data_integration.services.datastage.tests.integration.util import AbstractFlowRunTest
from os import environ
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestAzureBlobStorageConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "azureblobstorage_peek"

    def get_fc(self, project: Project):
        fc = DataStageFlow(project=project, name=self.get_flow_name(), description="", flow_type="datastage")

        # Stages
        _mytestfilecsv_1_ = fc.add_stage("Microsoft Azure Blob Storage", "mytestfilecsv_1")
        _mytestfilecsv_1_.configuration.ds_use_datastage = False
        _mytestfilecsv_1_.configuration.escape_character = AZURE_BLOB_STORAGE.EscapeCharacter.double_quote
        _mytestfilecsv_1_.configuration.file_name = "mytestfile.csv"
        _mytestfilecsv_1_.configuration.infer_as_varchar = False
        _mytestfilecsv_1_.configuration.infer_schema = False
        _mytestfilecsv_1_.configuration.quote_character = AZURE_BLOB_STORAGE.QuoteCharacter.double_quote

        _mytestfilecsv_1_.configuration.connection.authentication_method = (
            AZURE_BLOB_STORAGE_CONNECTION.AuthMethod.connection_string
        )
        _mytestfilecsv_1_.configuration.connection.connection_string = environ["AZUREBLOBSTORAGE_CONN_STRING"]
        _mytestfilecsv_1_.configuration.connection.container = "tm-ds-blob-storage-1"

        _peek_1_ = fc.add_stage("Peek", "Peek_1")

        # Graph
        mytestfilecsv_1_schema = _mytestfilecsv_1_.connect_output_to(_peek_1_).set_name("Link_1").create_schema()

        # Schemas
        mytestfilecsv_1_schema.add_field("VARCHAR", "COLUMN1").nullable().length(1024)
        mytestfilecsv_1_schema.add_field("INTEGER", "COLUMN2").nullable()
        mytestfilecsv_1_schema.add_field("VARCHAR", "COLUMN3").nullable().length(1024)
        mytestfilecsv_1_schema.add_field("DOUBLE", "COLUMN4").nullable()
        mytestfilecsv_1_schema.add_field("INTEGER", "COLUMN5").nullable()
        mytestfilecsv_1_schema.add_field("BIGINT", "COLUMN6").nullable()
        mytestfilecsv_1_schema.add_field("DOUBLE", "COLUMN7").nullable()
        mytestfilecsv_1_schema.add_field("BIT", "COLUMN8").nullable()
        mytestfilecsv_1_schema.add_field("DATE", "COLUMN9").nullable()
        mytestfilecsv_1_schema.add_field("INTEGER", "COLUMN10").nullable()
        mytestfilecsv_1_schema.add_field("INTEGER", "COLUMN11").nullable()
        mytestfilecsv_1_schema.add_field("VARCHAR", "COLUMN12").nullable().length(1024)
        mytestfilecsv_1_schema.add_field("BIGINT", "COLUMN13").nullable()
        mytestfilecsv_1_schema.add_field("INTEGER", "COLUMN14").nullable()
        mytestfilecsv_1_schema.add_field("INTEGER", "COLUMN15").nullable()
        mytestfilecsv_1_schema.add_field("INTEGER", "COLUMN16").nullable()
        mytestfilecsv_1_schema.add_field("DOUBLE", "COLUMN17").nullable()
        mytestfilecsv_1_schema.add_field("INTEGER", "COLUMN18").nullable()
        mytestfilecsv_1_schema.add_field("TIME", "COLUMN19").nullable()
        mytestfilecsv_1_schema.add_field("TIMESTAMP", "COLUMN20").nullable()
        mytestfilecsv_1_schema.add_field("INTEGER", "COLUMN21").nullable()
        mytestfilecsv_1_schema.add_field("BIGINT", "COLUMN22").nullable()
        mytestfilecsv_1_schema.add_field("VARCHAR", "COLUMN23").nullable().length(1024)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
