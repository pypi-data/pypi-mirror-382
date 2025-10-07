from ibm_watsonx_data_integration.services.datastage.models.enums import AMAZON_REDSHIFT_CONNECTION
from os import environ
from tests.integration.datastage.util import AbstractFlowRunTest
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestAmazonRedShiftConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "amazonredshift_peek"

    def get_fc(self, project: Project):
        fc = project.create_flow(name=self.get_flow_name(), environment=None, description="", flow_type="datastage")

        # Stages
        _autotest_1_ = fc.add_stage("Amazon Redshift", "autotest_1")
        _autotest_1_.configuration.schema_name = "testredshift"
        _autotest_1_.configuration.table_name = "autotest"

        _autotest_1_.configuration.connection.database = "dev"
        _autotest_1_.configuration.connection.hostname_or_ip_address = environ["AMAZONREDSHIFT_HOST"]
        _autotest_1_.configuration.connection.password = environ["AMAZONREDSHIFT_PASSWORD"]
        _autotest_1_.configuration.connection.port = "5439"
        _autotest_1_.configuration.connection.port_is_ssl_enabled = True
        _autotest_1_.configuration.connection.time_type = AMAZON_REDSHIFT_CONNECTION.TimeType.timestamp
        _autotest_1_.configuration.connection.username = environ["AMAZONREDSHIFT_USERNAME"]

        _peek_1_ = fc.add_stage("Peek", "Peek_1")

        # Graph
        autotest_1_schema = _autotest_1_.connect_output_to(_peek_1_).set_name("Link_1").create_schema()

        # Schemas
        autotest_1_schema.add_field("CHAR", "col1").nullable().length(6)
        autotest_1_schema.add_field("CHAR", "col2").nullable().length(6)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
