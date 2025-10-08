from ibm_watsonx_data_integration.services.datastage.models.flow.datastage_flow import DataStageFlow
from ibm_watsonx_data_integration.services.datastage.tests.integration.util import AbstractFlowRunTest
from os import environ
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestAzureDatabricksConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "azuredatabricks_peek"

    def get_fc(self, project: Project):
        fc = DataStageFlow(project=project, name=self.get_flow_name(), description="", flow_type="datastage")

        # Stages
        _yyyymmdd_1_ = fc.add_stage("Microsoft Azure Databricks", "yyyymmdd_1")
        _yyyymmdd_1_.configuration.catalog_name = "test"
        _yyyymmdd_1_.configuration.schema_name = "default"
        _yyyymmdd_1_.configuration.table_name = "yyyy-mm-dd"

        _yyyymmdd_1_.configuration.connection.authentication_method = "entra_id"
        _yyyymmdd_1_.configuration.connection.microsoft_entra_id_token = environ["AZUREDATABRICKS_ENTRA_ID_TOKEN"]
        _yyyymmdd_1_.configuration.connection.hostname_or_ip_address = environ["AZUREDATABRICKS_HOST"]
        _yyyymmdd_1_.configuration.connection.http_path = "/sql/1.0/warehouses/d09152f0d320e3cc"
        _yyyymmdd_1_.configuration.connection.port = "443"

        _peek_1_ = fc.add_stage("Peek", "Peek_1")

        # Graph
        yyyymmdd_1_schema = _yyyymmdd_1_.connect_output_to(_peek_1_).set_name("Link_1").create_schema()

        # Schemas
        yyyymmdd_1_schema.add_field("VARCHAR", "date1").nullable().length(255)
        yyyymmdd_1_schema.add_field("VARCHAR", "date2").nullable().length(255)
        yyyymmdd_1_schema.add_field("BIGINT", "id").nullable()

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
