from ibm_watsonx_data_integration.services.datastage.models.enums import ORACLE_CONNECTION
from ibm_watsonx_data_integration.services.datastage.models.flow.datastage_flow import DataStageFlow
from ibm_watsonx_data_integration.services.datastage.tests.integration.util import AbstractFlowRunTest
from os import environ
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestOracleConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "oracle_peek"

    def get_fc(self, project: Project):
        fc = DataStageFlow(project=project, name=self.get_flow_name(), description="", flow_type="datastage")

        # Stages
        _fastpathtest_1_ = fc.add_stage("Oracle", "FASTPATHTEST_1")
        _fastpathtest_1_.configuration.schema_name = "TM_DS"
        _fastpathtest_1_.configuration.table_name = "FASTPATHTEST"

        _fastpathtest_1_.configuration.connection.connection_mode = "service_name"
        _fastpathtest_1_.configuration.connection.hostname_or_ip_address = environ["ORACLE_HOST"]
        _fastpathtest_1_.configuration.connection.metadata_discovery = ORACLE_CONNECTION.MetadataDiscovery.no_remarks
        _fastpathtest_1_.configuration.connection.password = environ["ORACLE_PASSWORD"]
        _fastpathtest_1_.configuration.connection.port = "1521"
        _fastpathtest_1_.configuration.connection.proxy = False
        _fastpathtest_1_.configuration.connection.service_name = "orclpdb"
        _fastpathtest_1_.configuration.connection.port_is_ssl_enabled = False
        _fastpathtest_1_.configuration.connection.username = environ["ORACLE_USERNAME"]

        _peek_2_ = fc.add_stage("Peek", "Peek_2")

        # Graph
        fastpathtest_1_schema = _fastpathtest_1_.connect_output_to(_peek_2_).set_name("Link_2").create_schema()

        # Schemas
        fastpathtest_1_schema.add_field("CHAR", "NAME").nullable().length(6)
        fastpathtest_1_schema.add_field("BIGINT", "SAVINGS").nullable()
        fastpathtest_1_schema.add_field("BIGINT", "DEBT").nullable()

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
