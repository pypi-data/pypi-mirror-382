from os import environ
from tests.integration.datastage.util import AbstractFlowRunTest
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestNetezzaConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "netezza_peek"

    def get_fc(self, project: Project):
        fc = project.create_flow(name=self.get_flow_name(), environment=None, description="", flow_type="datastage")

        # Stages
        _fastpath_jdbc_netezza_1_ = fc.add_stage("IBM Netezza Performance Server", "FASTPATH_JDBC_NETEZZA_1")
        _fastpath_jdbc_netezza_1_.configuration.schema_name = "TM_DS_SCHEMA"
        _fastpath_jdbc_netezza_1_.configuration.table_name = "FASTPATH_JDBC_NETEZZA"

        _fastpath_jdbc_netezza_1_.configuration.connection.database = "TM_DS"
        _fastpath_jdbc_netezza_1_.configuration.connection.hostname_or_ip_address = environ["NETEZZA_HOST"]
        _fastpath_jdbc_netezza_1_.configuration.connection.password = environ["NETEZZA_PASSWORD"]
        _fastpath_jdbc_netezza_1_.configuration.connection.port = "33262"
        _fastpath_jdbc_netezza_1_.configuration.connection.port_is_ssl_enabled = False
        _fastpath_jdbc_netezza_1_.configuration.connection.username = environ["NETEZZA_USERNAME"]

        _peek_1_ = fc.add_stage("Peek", "Peek_1")

        # Graph
        schema_1 = _fastpath_jdbc_netezza_1_.connect_output_to(_peek_1_).set_name("Link_1").create_schema()

        # Schemas
        schema_1.add_field("CHAR", "COLUMN_1").length(6)
        schema_1.add_field("CHAR", "COLUMN_2").length(6)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
