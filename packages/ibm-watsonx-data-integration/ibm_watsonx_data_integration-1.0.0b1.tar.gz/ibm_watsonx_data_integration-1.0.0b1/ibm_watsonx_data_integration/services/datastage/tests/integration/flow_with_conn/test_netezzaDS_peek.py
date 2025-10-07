from os import environ
from tests.integration.datastage.util import AbstractFlowRunTest
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestNetezzaDSConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "netezzaDS"

    def get_fc(self, project: Project):
        fc = project.create_flow(name=self.get_flow_name(), environment=None, description="", flow_type="datastage")

        # Stages
        _fastpath_jdbc_netezza_1_ = fc.add_stage(
            "IBM Netezza Performance Server for DataStage", "FASTPATH_JDBC_NETEZZA_1"
        )
        _fastpath_jdbc_netezza_1_.configuration.table_name = '"TM_DS_SCHEMA"."FASTPATH_JDBC_NETEZZA"'

        _fastpath_jdbc_netezza_1_.configuration.connection.cas_lite_service_authorization_header = ""
        _fastpath_jdbc_netezza_1_.configuration.connection.database = "TM_DS"
        _fastpath_jdbc_netezza_1_.configuration.connection.hostname = environ["NETEZZA_DS_HOST"]
        _fastpath_jdbc_netezza_1_.configuration.connection.password = environ["NETEZZA_DS_PASSWORD"]
        _fastpath_jdbc_netezza_1_.configuration.connection.ssl_connection = False
        _fastpath_jdbc_netezza_1_.configuration.connection.use_separate_connection_for_twt = False
        _fastpath_jdbc_netezza_1_.configuration.connection.username = environ["NETEZZA_DS_USERNAME"]
        _fastpath_jdbc_netezza_1_.configuration.connection.port = "33262"

        _peek_1_ = fc.add_stage("Peek", "Peek_1")

        # Graph
        fastpath_jdbc_netezza_1_schema = (
            _fastpath_jdbc_netezza_1_.connect_output_to(_peek_1_).set_name("Link_1").create_schema()
        )

        # Schemas
        fastpath_jdbc_netezza_1_schema.add_field("CHAR", "COLUMN_1").length(6)
        fastpath_jdbc_netezza_1_schema.add_field("CHAR", "COLUMN_2").length(6)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
