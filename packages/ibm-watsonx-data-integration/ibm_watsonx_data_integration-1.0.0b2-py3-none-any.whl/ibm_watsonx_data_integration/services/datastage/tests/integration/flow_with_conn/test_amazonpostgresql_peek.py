from os import environ
from tests.integration.datastage.util import AbstractFlowRunTest
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestAmazonPostgreSqlConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "amazonpostgresql_peek"

    def get_fc(self, project: Project):
        fc = project.create_flow(name=self.get_flow_name(), environment=None, description="", flow_type="datastage")

        # Stages
        _testtable_1_ = fc.add_stage("Amazon RDS for PostgreSQL", "TESTTABLE_1")
        _testtable_1_.configuration.schema_name = "TM_DS_1"
        _testtable_1_.configuration.table_name = "TESTTABLE"

        _testtable_1_.configuration.connection.database = "conopsdb"
        _testtable_1_.configuration.connection.host = environ["AMAZONPOSTGRESQL_HOST"]
        _testtable_1_.configuration.connection.password = environ["AMAZONPOSTGRESQL_PASSWORD"]
        _testtable_1_.configuration.connection.port = "5432"
        _testtable_1_.configuration.connection.proxy = False
        _testtable_1_.configuration.connection.ssl = True
        _testtable_1_.configuration.connection.username = environ["AMAZONPOSTGRESQL_USERNAME"]

        _peek_1_ = fc.add_stage("Peek", "Peek_1")

        # Graph
        testtable_1_schema = _testtable_1_.connect_output_to(_peek_1_).set_name("Link_1").create_schema()
        testtable_1_schema.add_field("VARCHAR", "COLUMN_1").nullable().length(100)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
