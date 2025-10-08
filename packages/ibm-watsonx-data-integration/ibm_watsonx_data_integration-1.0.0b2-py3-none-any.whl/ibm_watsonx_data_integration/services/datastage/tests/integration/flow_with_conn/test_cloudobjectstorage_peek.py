from ibm_watsonx_data_integration.services.datastage.models.enums import CLOUD_OBJECT_STORAGE
from os import environ
from tests.integration.datastage.util import AbstractFlowRunTest
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestCloudObjectStorageConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "cloudobjectstorage_peek"

    def get_fc(self, project: Project):
        fc = project.create_flow(name=self.get_flow_name(), environment=None, description="", flow_type="datastage")

        # Stages
        _abccsv_1_ = fc.add_stage("IBM Cloud Object Storage", "abccsv_1")
        _abccsv_1_.configuration.escape_character = CLOUD_OBJECT_STORAGE.EscapeCharacter.double_quote
        _abccsv_1_.configuration.file_name = "abc.csv"
        _abccsv_1_.configuration.infer_as_varchar = False
        _abccsv_1_.configuration.infer_schema = False
        _abccsv_1_.configuration.quote_character = CLOUD_OBJECT_STORAGE.QuoteCharacter.double_quote

        _abccsv_1_.configuration.connection.access_key = environ["CLOUDOBJECTSTORAGE_ACCESS_KEY"]
        _abccsv_1_.configuration.connection.authentication_method = "accesskey_secretkey"
        _abccsv_1_.configuration.connection.iam_url = "https://iam.cloud.ibm.com/identity/token"
        _abccsv_1_.configuration.connection.secret_key = environ["CLOUDOBJECTSTORAGE_SECRET_KEY"]
        _abccsv_1_.configuration.connection.trust_all_ssl_certificates = False
        _abccsv_1_.configuration.connection.url = environ["CLOUDOBJECTSTORAGE_URL"]
        _abccsv_1_.configuration.connection.bucket = "ds-fastpath-test-bucket"

        _peek_1_ = fc.add_stage("Peek", "Peek_1")

        abccsv_1_schema = _abccsv_1_.connect_output_to(_peek_1_).set_name("Link_1").create_schema()

        # Schemas
        abccsv_1_schema.add_field("VARCHAR", "COLUMN1").nullable().length(1024)
        abccsv_1_schema.add_field("VARCHAR", "COLUMN2").nullable().length(1024)
        abccsv_1_schema.add_field("VARCHAR", "COLUMN3").nullable().length(1024)
        abccsv_1_schema.add_field("DOUBLE", "COLUMN4").nullable()
        abccsv_1_schema.add_field("INTEGER", "COLUMN5").nullable()
        abccsv_1_schema.add_field("BIGINT", "COLUMN6").nullable()
        abccsv_1_schema.add_field("DOUBLE", "COLUMN7").nullable()
        abccsv_1_schema.add_field("BIT", "COLUMN8").nullable()
        abccsv_1_schema.add_field("DATE", "COLUMN9").nullable()
        abccsv_1_schema.add_field("INTEGER", "COLUMN10").nullable()
        abccsv_1_schema.add_field("INTEGER", "COLUMN11").nullable()
        abccsv_1_schema.add_field("VARCHAR", "COLUMN12").nullable().length(1024)
        abccsv_1_schema.add_field("BIGINT", "COLUMN13").nullable()
        abccsv_1_schema.add_field("INTEGER", "COLUMN14").nullable()
        abccsv_1_schema.add_field("VARCHAR", "COLUMN15").nullable().length(1024)
        abccsv_1_schema.add_field("INTEGER", "COLUMN16").nullable()
        abccsv_1_schema.add_field("DOUBLE", "COLUMN17").nullable()
        abccsv_1_schema.add_field("INTEGER", "COLUMN18").nullable()
        abccsv_1_schema.add_field("TIME", "COLUMN19").nullable()
        abccsv_1_schema.add_field("TIMESTAMP", "COLUMN20").nullable()
        abccsv_1_schema.add_field("INTEGER", "COLUMN21").nullable()
        abccsv_1_schema.add_field("BIGINT", "COLUMN22").nullable()
        abccsv_1_schema.add_field("VARCHAR", "COLUMN23").nullable().length(1024)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
