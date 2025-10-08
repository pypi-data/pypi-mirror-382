from ibm_watsonx_data_integration.services.datastage.models.flow.datastage_flow import DataStageFlow
from ibm_watsonx_data_integration.services.datastage.tests.integration.util import AbstractFlowRunTest
from os import environ
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestDb2BigSqlConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "db2BigSql_peek"

    def get_fc(self, project: Project):
        fc = DataStageFlow(project=project, name=self.get_flow_name(), description="", flow_type="datastage")

        # Stages
        _test_before_after_tmp_1_1_ = fc.add_stage("IBM Db2 Big SQL", "TEST_BEFORE_AFTER_TMP_1_1")
        _test_before_after_tmp_1_1_.configuration.schema_name = "BIGSQL"
        _test_before_after_tmp_1_1_.configuration.table_name = "TEST_BEFORE_AFTER_TMP_1"

        _test_before_after_tmp_1_1_.configuration.connection.database = "BIGSQL"
        _test_before_after_tmp_1_1_.configuration.connection.hostname_or_ip_address = environ["DB2BIGSQL_HOST"]
        _test_before_after_tmp_1_1_.configuration.connection.password = environ["DB2BIGSQL_PASSWORD"]
        _test_before_after_tmp_1_1_.configuration.connection.port = "32051"
        _test_before_after_tmp_1_1_.configuration.connection.port_is_ssl_enabled = False
        _test_before_after_tmp_1_1_.configuration.connection.username = environ["DB2BIGSQL_USERNAME"]

        _peek_1_ = fc.add_stage("Peek", "Peek_1")

        # Graph
        test_before_after_tmp_1_1_schema = (
            _test_before_after_tmp_1_1_.connect_output_to(_peek_1_).set_name("Link_1").create_schema()
        )

        # Schemas
        test_before_after_tmp_1_1_schema.add_field("CHAR", "COL1").nullable().length(5)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
