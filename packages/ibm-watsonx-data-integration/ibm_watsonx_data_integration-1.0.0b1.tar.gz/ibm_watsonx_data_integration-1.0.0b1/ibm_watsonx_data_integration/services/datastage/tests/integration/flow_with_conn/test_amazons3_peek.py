from ibm_watsonx_data_integration.services.datastage.models.enums import AMAZONS3
from os import environ
from tests.integration.datastage.util import AbstractFlowRunTest
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestAmazonS3Connection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "amazons3_peek"

    def get_fc(self, project: Project):
        fc = project.create_flow(name=self.get_flow_name(), environment=None, description="", flow_type="datastage")

        # Stages
        _fastpathemp2csv0_1_ = fc.add_stage("Amazon S3", "FastpathEmp2csv0_1")
        _fastpathemp2csv0_1_.configuration.ds_file_format = AMAZONS3.DSFileFormat.csv
        _fastpathemp2csv0_1_.configuration.ds_first_line_header = True
        _fastpathemp2csv0_1_.configuration.file_name = "FastpathEmp2.csv.0"

        _fastpathemp2csv0_1_.configuration.connection.access_key = environ["AMAZONS3_ACCESS_KEY"]
        _fastpathemp2csv0_1_.configuration.connection.bucket = "fastpath-bucket"
        _fastpathemp2csv0_1_.configuration.connection.proxy = False
        _fastpathemp2csv0_1_.configuration.connection.secret_key = environ["AMAZONS3_SECRET_KEY"]
        _fastpathemp2csv0_1_.configuration.connection.url = "s3.us-east-1.amazonaws.com"
        _fastpathemp2csv0_1_.configuration.connection.authentication_method = "basic_credentials"

        _peek_1_ = fc.add_stage("Peek", "Peek_1")
        _peek_1_.configuration.runtime_column_propagation = 0

        # Graph
        fastpathemp2csv0_1_schema = _fastpathemp2csv0_1_.connect_output_to(_peek_1_).set_name("Link_4").create_schema()

        # Schemas
        fastpathemp2csv0_1_schema.add_field("VARCHAR", "ggg").nullable().length(1024)
        fastpathemp2csv0_1_schema.add_field("VARCHAR", "ggg__DUPLICATE__1").nullable().length(1024)
        fastpathemp2csv0_1_schema.add_field("VARCHAR", "ggg__DUPLICATE__2").nullable().length(1024)
        fastpathemp2csv0_1_schema.add_field("VARCHAR", "ggg__DUPLICATE__3").nullable().length(1024)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
