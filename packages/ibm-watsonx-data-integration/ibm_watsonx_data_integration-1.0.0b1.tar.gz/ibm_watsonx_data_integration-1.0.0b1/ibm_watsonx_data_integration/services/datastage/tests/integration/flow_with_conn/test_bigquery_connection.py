from os import environ
from tests.integration.datastage.util import AbstractFlowRunTest
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestBigqueryConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "bigquery_peek"

    def get_fc(self, project: Project):
        fc = project.create_flow(name=self.get_flow_name(), environment=None, description="", flow_type="datastage")

        bigquery = fc.add_stage("Google BigQuery", "BigQuery")
        bigquery.configuration.table_name = "cust_source"
        bigquery.configuration.dataset_name = "Team_DS"

        bigquery.configuration.connection.proxy = "false"
        bigquery.configuration.connection.project_id = "conops-bigquery"
        bigquery.configuration.connection.authentication_method = "credentials"
        bigquery.configuration.connection.credentials = environ["BIGQUERY_CREDENTIALS"]

        peek = fc.add_stage("Peek", "Peek")

        output_schema = bigquery.connect_output_to(peek).create_schema()

        output_schema.add_field("LONGVARCHAR", "cf_customerId").nullable().length(100)
        output_schema.add_field("LONGVARCHAR", "cf_name").nullable().length(100)
        output_schema.add_field("LONGVARCHAR", "cf_address").nullable().length(100)
        output_schema.add_field("LONGVARCHAR", "cf_geolocation_date").nullable().length(100)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
