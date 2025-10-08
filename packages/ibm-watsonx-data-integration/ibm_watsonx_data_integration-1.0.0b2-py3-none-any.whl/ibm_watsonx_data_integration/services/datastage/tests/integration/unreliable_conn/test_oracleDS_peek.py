from ibm_watsonx_data_integration.services.datastage.models.enums import ORACLE_DATASTAGE_CONNECTION
from ibm_watsonx_data_integration.services.datastage.models.flow.datastage_flow import DataStageFlow
from ibm_watsonx_data_integration.services.datastage.tests.integration.util import AbstractFlowRunTest
from os import environ
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestOracleDataStageConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "oracleDS_peek"

    def get_fc(self, project: Project):
        fc = DataStageFlow(project=project, name=self.get_flow_name(), description="", flow_type="datastage")

        # Stages
        _mytesttable1_1_ = fc.add_stage("Oracle Database for DataStage", "mytesttable1_1")
        _mytesttable1_1_.configuration.generate_sql_at_runtime = True
        _mytesttable1_1_.configuration.table_name = '"TM_DS"."mytesttable1"'

        _mytesttable1_1_.configuration.connection.cas_lite_service_authorization_header = ""
        _mytesttable1_1_.configuration.connection.connection_type = ORACLE_DATASTAGE_CONNECTION.ConnectionType.tcp
        _mytesttable1_1_.configuration.connection.hostname = environ["ORACLEDS_HOST"]
        _mytesttable1_1_.configuration.connection.port = "1521"
        _mytesttable1_1_.configuration.connection.servicename = "orclpdb"
        _mytesttable1_1_.configuration.connection.password = environ["ORACLEDS_PASSWORD"]
        _mytesttable1_1_.configuration.connection.use_connection_string = False
        _mytesttable1_1_.configuration.connection.username = environ["ORACLEDS_USERNAME"]
        _mytesttable1_1_.configuration.connection.gateway_url = "https://internal-nginx-svc.ds.svc:12443"

        _peek_2_ = fc.add_stage("Peek", "Peek_2")

        # Graph
        mytesttable1_1_schema = _mytesttable1_1_.connect_output_to(_peek_2_).set_name("Link_2").create_schema()

        # Schemas
        mytesttable1_1_schema.add_field("DECIMAL", "col1").nullable().length(38).precision(38)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
