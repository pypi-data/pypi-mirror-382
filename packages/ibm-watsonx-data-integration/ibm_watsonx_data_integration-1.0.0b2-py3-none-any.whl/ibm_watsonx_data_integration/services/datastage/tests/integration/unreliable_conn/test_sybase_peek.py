from ibm_watsonx_data_integration.services.datastage.models.flow.datastage_flow import DataStageFlow
from ibm_watsonx_data_integration.services.datastage.tests.integration.util import AbstractFlowRunTest
from os import environ
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestSybaseConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "sybase_peek"

    def get_fc(self, project: Project):
        fc = DataStageFlow(project=project, name=self.get_flow_name(), description="", flow_type="datastage")

        # Stages
        _testtable_1_ = fc.add_stage("SAP ASE", "testtable_1")
        _testtable_1_.configuration.schema_name = "tm_ds"
        _testtable_1_.configuration.table_name = "testtable"

        _testtable_1_.configuration.connection.database = "CONOPS"
        _testtable_1_.configuration.connection.hostname_or_ip_address = environ["SYBASE_HOST"]
        _testtable_1_.configuration.connection.password = environ["SYBASE_PASSWORD"]
        _testtable_1_.configuration.connection.port = "5000"
        _testtable_1_.configuration.connection.port_is_ssl_enabled = False
        _testtable_1_.configuration.connection.username = environ["SYBASE_USERNAME"]

        _peek_1_ = fc.add_stage("Peek", "Peek_1")
        _peek_1_.configuration.runtime_column_propagation = 0

        # Graph
        testtable_1_schema = _testtable_1_.connect_output_to(_peek_1_).set_name("Link_1").create_schema()

        # Schemas
        testtable_1_schema.add_field("INTEGER", "C1").nullable()
        testtable_1_schema.add_field("VARCHAR", "C2").nullable().length(20)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
