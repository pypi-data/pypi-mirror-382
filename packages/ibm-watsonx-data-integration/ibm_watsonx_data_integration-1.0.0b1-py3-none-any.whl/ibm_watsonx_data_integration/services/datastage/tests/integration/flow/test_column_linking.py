from os import environ
from tests.integration.datastage.util import AbstractFlowRunTest
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestColumnLinking(AbstractFlowRunTest):
    def get_flow_name(self):
        return "column_linking"

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

        bigquery_link = bigquery.connect_output_to(sort)
        sort_link = sort.connect_output_to(peek)

        output_schema = bigquery_link.create_schema()
        output_schema.add_field("LONGVARCHAR", "cf_customerId").nullable().length(100)
        output_schema.add_field("LONGVARCHAR", "cf_name").nullable().length(100)
        output_schema.add_field("LONGVARCHAR", "cf_address").nullable().length(100)
        output_schema.add_field("LONGVARCHAR", "cf_geolocation_date").nullable().length(100)

        output_schema2 = sort_link.create_schema()
        output_schema2.add_field("LONGVARCHAR", "CUSTOMER_ID").nullable().length(100).source("cf_customerId")
        output_schema2.add_field("LONGVARCHAR", "NAME").nullable().length(100).source("cf_name")
        output_schema2.add_field("LONGVARCHAR", "ADDRESS").nullable().length(100).source("cf_address")
        output_schema2.add_field("LONGVARCHAR", "GEOLOCATION_DATE").nullable().length(100).source("cf_geolocation_date")

        project.update_flow(fc)

        return fc

    def validate(self, state):
        # print(logs)
        # assert "Finished job" in logs
        # assert "<main_program> Step execution finished with status = OK." in logs
        assert "Completed" in state
