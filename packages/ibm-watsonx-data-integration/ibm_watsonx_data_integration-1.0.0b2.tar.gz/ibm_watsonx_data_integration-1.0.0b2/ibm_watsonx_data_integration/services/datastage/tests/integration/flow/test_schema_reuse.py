from os import environ
from tests.integration.datastage.util import AbstractFlowRunTest
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestSchemaReuse(AbstractFlowRunTest):
    def get_flow_name(self):
        return "schema_reuse"

    def get_fc(self, project: Project):
        fc = project.create_flow(name=self.get_flow_name(), environment=None, description="", flow_type="datastage")

        bigquery = fc.add_stage("Google BigQuery", "BigQuery")
        bigquery.configuration.connection.name = "bigquery-conn"
        bigquery.configuration.connection.proxy = "false"
        bigquery.configuration.connection.project_id = "conops-bigquery"
        bigquery.configuration.connection.authentication_method = "credentials"
        bigquery.configuration.connection.credentials = environ["BIGQUERY_CREDENTIALS"]

        bigquery.configuration.table_name = "cust_source"
        bigquery.configuration.dataset_name = "Team_DS"

        sort = fc.add_stage("Sort", "Sort")
        sort.configuration.key_properties = [{"key": "cf_name", "asc_desc": "desc", "ci_cs": "ci"}]

        peek = fc.add_stage("Peek", "Peek")

        bigquery_schema = bigquery.connect_output_to(sort).create_schema()
        sort_schema = sort.connect_output_to(peek).create_schema()

        bigquery_schema.add_field("LONGVARCHAR", "cf_customerId").nullable().length(100)
        bigquery_schema.add_field("LONGVARCHAR", "cf_name").nullable().length(100)
        bigquery_schema.add_field("LONGVARCHAR", "cf_address").nullable().length(100)
        bigquery_schema.add_field("LONGVARCHAR", "cf_geolocation_date").nullable().length(100)

        sort_schema.add_field("LONGVARCHAR", "cf_customerId").nullable().length(100)
        sort_schema.add_field("LONGVARCHAR", "cf_name").nullable().length(100)
        sort_schema.add_field("LONGVARCHAR", "cf_address").nullable().length(100)
        sort_schema.add_field("LONGVARCHAR", "cf_geolocation_date").nullable().length(100)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        # print(logs)
        # assert "Finished job" in logs
        # assert "<main_program> Step execution finished with status = OK." in logs
        assert "Completed" in state
