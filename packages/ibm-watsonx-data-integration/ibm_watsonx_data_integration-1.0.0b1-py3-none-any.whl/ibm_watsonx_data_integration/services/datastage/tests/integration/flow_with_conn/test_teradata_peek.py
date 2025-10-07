from ibm_watsonx_data_integration.services.datastage.models.enums import TERADATA_CONNECTION
from os import environ
from tests.integration.datastage.util import AbstractFlowRunTest
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestTeradataConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "teradata_peek"

    def get_fc(self, project: Project):
        fc = project.create_flow(name=self.get_flow_name(), environment=None, description="", flow_type="datastage")

        # teradataconn = TeradataConn(
        #     name="teradataconn",
        #     authentication_method=TERADATA_CONNECTION.AuthenticationMethod.td2,
        #     database="tm_ds_db_1",
        #     hostname_or_ip_address=environ["TERADATA_HOST"],
        #     password=environ["TERADATA_PASSWORD"],
        #     port_is_ssl_enabled=False,
        #     enable_trusted_session=False,
        #     username=environ["TERADATA_USERNAME"],
        # )
        # Stages
        print(environ["TERADATA_HOST"])
        _fastpathtest_1_ = fc.add_stage("Teradata", "fastpathTest_1")
        _fastpathtest_1_.configuration.schema_name = "tm_ds_db_1"
        _fastpathtest_1_.configuration.table_name = "fastpathTest"

        _fastpathtest_1_.configuration.connection.authentication_method = TERADATA_CONNECTION.AuthenticationMethod.td2
        _fastpathtest_1_.configuration.connection.database = "tm_ds_db_1"
        _fastpathtest_1_.configuration.connection.hostname_or_ip_address = environ["TERADATA_HOST"]
        _fastpathtest_1_.configuration.connection.password = environ["TERADATA_PASSWORD"]
        _fastpathtest_1_.configuration.connection.port_is_ssl_enabled = False
        _fastpathtest_1_.configuration.connection.enable_trusted_session = False
        _fastpathtest_1_.configuration.connection.username = environ["TERADATA_USERNAME"]
        # _fastpathtest_1_.configuration.connection = teradataconn

        _peek_1_ = fc.add_stage("Peek", "Peek_1")
        _peek_1_.configuration.runtime_column_propagation = 0

        # Graph
        fastpathtest_1_schema = _fastpathtest_1_.connect_output_to(_peek_1_).set_name("Link_1").create_schema()

        # Schemas
        fastpathtest_1_schema.add_field("INTEGER", "a")
        fastpathtest_1_schema.add_field("CHAR", "b").length(1)
        fastpathtest_1_schema.add_field("CHAR", "c").length(1)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
