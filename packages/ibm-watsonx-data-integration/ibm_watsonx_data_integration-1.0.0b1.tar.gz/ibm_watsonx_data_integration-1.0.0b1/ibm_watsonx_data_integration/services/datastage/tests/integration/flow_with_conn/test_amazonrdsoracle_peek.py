from ibm_watsonx_data_integration.services.datastage.models.enums import AMAZONRDS_ORACLE_CONNECTION
from os import environ
from tests.integration.datastage.util import AbstractFlowRunTest
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestAmazonRdsOracleConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "amazonrdsoracle_peek"

    def get_fc(self, project: Project):
        fc = project.create_flow(name=self.get_flow_name(), environment=None, description="", flow_type="datastage")

        # Stages
        _autotest_1_ = fc.add_stage("Amazon RDS for Oracle", "AUTOTEST_1")
        _autotest_1_.configuration.schema_name = "TM_DS_1"
        _autotest_1_.configuration.table_name = "AUTOTEST"

        _autotest_1_.configuration.connection.connection_mode = "service_name"
        _autotest_1_.configuration.connection.hostname_or_ip_address = environ["AMAZONRDSORACLE_HOST"]
        _autotest_1_.configuration.connection.metadata_discovery = (
            AMAZONRDS_ORACLE_CONNECTION.MetadataDiscovery.no_remarks
        )
        _autotest_1_.configuration.connection.password = environ["AMAZONRDSORACLE_PASSWORD"]
        _autotest_1_.configuration.connection.port = "1521"
        _autotest_1_.configuration.connection.proxy = False
        _autotest_1_.configuration.connection.service_name = "DATABASE"
        _autotest_1_.configuration.connection.port_is_ssl_enabled = False
        _autotest_1_.configuration.connection.username = environ["AMAZONRDSORACLE_USERNAME"]

        _peek_1_ = fc.add_stage("Peek", "Peek_1")

        # Graph
        autotest_1_schema = _autotest_1_.connect_output_to(_peek_1_).set_name("Link_1").create_schema()

        # Schemas
        autotest_1_schema.add_field("NCHAR", "col1").length(6)
        autotest_1_schema.add_field("DECIMAL", "col2").length(6).precision(6)
        autotest_1_schema.add_field("NVARCHAR", "col3").nullable().length(6)
        autotest_1_schema.add_field("DOUBLE", "col4")
        autotest_1_schema.add_field("DECIMAL", "col6").length(19).precision(19)
        autotest_1_schema.add_field("VARBINARY", "col7").length(6)
        autotest_1_schema.add_field("DOUBLE", "col8")
        autotest_1_schema.add_field("DECIMAL", "col9").length(38).precision(38)
        autotest_1_schema.add_field("TIMESTAMP", "col10")
        autotest_1_schema.add_field("DECIMAL", "col11").length(38).precision(38)
        autotest_1_schema.add_field("LONGNVARCHAR", "col12").length(1024)
        autotest_1_schema.add_field("LONGNVARCHAR", "col13").length(1024)
        autotest_1_schema.add_field("NCHAR", "col15").length(6)
        autotest_1_schema.add_field("DECIMAL", "col16").length(6).precision(6)
        autotest_1_schema.add_field("NVARCHAR", "col17").nullable().length(6)
        autotest_1_schema.add_field("REAL", "col18").length(7)
        autotest_1_schema.add_field("DECIMAL", "col19").length(38).precision(38)
        autotest_1_schema.add_field("TIMESTAMP", "col20")
        autotest_1_schema.add_field("TIMESTAMP", "col21")
        autotest_1_schema.add_field("DECIMAL", "col22").length(3).precision(3)
        autotest_1_schema.add_field("NVARCHAR", "col24").nullable().length(6)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
