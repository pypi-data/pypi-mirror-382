from ibm_watsonx_data_integration.services.datastage.models.enums import CASSANDRA_CONNECTION
from os import environ
from tests.integration.datastage.util import AbstractFlowRunTest
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestCassandraConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "cassandra_peek"

    def get_fc(self, project: Project):
        fc = project.create_flow(name=self.get_flow_name(), environment=None, description="", flow_type="datastage")

        # Stages
        _test1_1_ = fc.add_stage("Apache Cassandra", "test1_1")
        _test1_1_.configuration.schema_name = "tm_ds_ks"
        _test1_1_.configuration.table_name = "test1"

        _test1_1_.configuration.connection.hostname_or_ip_address = environ["CASSANDRA_HOST"]
        _test1_1_.configuration.connection.keyspace = "tm_ds_ks"
        _test1_1_.configuration.connection.password = environ["CASSANDRA_PASSWORD"]
        _test1_1_.configuration.connection.port = "33366"
        _test1_1_.configuration.connection.read_consistency = CASSANDRA_CONNECTION.ReadConsistency.quorum
        _test1_1_.configuration.connection.port_is_ssl_enabled = False
        _test1_1_.configuration.connection.username = environ["CASSANDRA_USERNAME"]
        _test1_1_.configuration.connection.write_consistency = CASSANDRA_CONNECTION.WriteConsistency.quorum

        _peek_2_ = fc.add_stage("Peek", "Peek_2")

        # Graph
        test1_1_schema = _test1_1_.connect_output_to(_peek_2_).set_name("Link_2").create_schema()

        # Schemas
        test1_1_schema.add_field("INTEGER", "COLUMN_1")

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
