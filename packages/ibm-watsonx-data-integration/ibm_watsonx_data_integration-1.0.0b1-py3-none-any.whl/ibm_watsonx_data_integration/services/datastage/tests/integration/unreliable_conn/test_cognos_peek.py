from ibm_watsonx_data_integration.services.datastage.models.flow.datastage_flow import DataStageFlow
from ibm_watsonx_data_integration.services.datastage.tests.integration.util import AbstractFlowRunTest
from os import environ
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestCognosConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "cognos_peek"

    def get_fc(self, project: Project):
        fc = DataStageFlow(project=project, name=self.get_flow_name(), description="", flow_type="datastage")

        # Stages
        _2_columns_1_ = fc.add_stage("IBM Cognos Analytics", "2 columns_1")
        _2_columns_1_.configuration.file_name = "Team Content/Templates/2 columns"

        _2_columns_1_.configuration.connection.authentication_method = "username_password_namespace"
        _2_columns_1_.configuration.connection.namespace_id = "CognosEx"
        _2_columns_1_.configuration.connection.password = environ["COGNOS_PASSWORD"]
        _2_columns_1_.configuration.connection.ssl_certificate = environ["COGNOS_SSL_CERTIFICATE"]
        _2_columns_1_.configuration.connection.url = "https://52.116.192.162:9300/bi/v1/disp"
        _2_columns_1_.configuration.connection.username = environ["COGNOS_USERNAME"]

        _peek_1_ = fc.add_stage("Peek", "Peek_1")

        # Graph
        _2_columns_1_schema = _2_columns_1_.connect_output_to(_peek_1_).set_name("Link_1").create_schema()

        # Schemas
        _2_columns_1_schema.add_field("VARCHAR", "value").nullable().length(1024)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
