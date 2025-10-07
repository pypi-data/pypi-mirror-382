from ibm_watsonx_data_integration.services.datastage.models.enums import IBM_MQ, IBM_MQ_CONNECTION
from os import environ
from tests.integration.datastage.util import AbstractFlowRunTest
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestIbmMqConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "mq_peek"

    def get_fc(self, project: Project):
        fc = project.create_flow(name=self.get_flow_name(), environment=None, description="", flow_type="datastage")

        # Stages
        _mq_1_ = fc.add_stage("IBM MQ", "MQ_1")
        _mq_1_.configuration.message_quantity = 10
        _mq_1_.configuration.message_read_mode = IBM_MQ.MessageReadMode.delete
        _mq_1_.configuration.process_end_of_data_message = True
        _mq_1_.configuration.queue_name = "MQAUTH.QUEUE4"
        _mq_1_.configuration.wait_time = 10

        _mq_1_.configuration.connection.cas_lite_service_authorization_header = ""
        _mq_1_.configuration.connection.channel_name = "MQAUTH.CHAN"
        _mq_1_.configuration.connection.connection_name = "c-01.private.us-south.link.satellite.cloud.ibm.com(33427)"
        _mq_1_.configuration.connection.transport_type = IBM_MQ_CONNECTION.ClientChannelDefinitionTransportType.tcp
        _mq_1_.configuration.connection.defer_credentials = False
        _mq_1_.configuration.connection.password = environ["IBMMQ_PASSWORD"]
        _mq_1_.configuration.connection.queue_manager_name = "MQAUTH"
        _mq_1_.configuration.connection.ssl_connection = False
        _mq_1_.configuration.connection.username = environ["IBMMQ_USERNAME"]

        _peek_1_ = fc.add_stage("Peek", "Peek_1")
        _peek_1_.configuration.runtime_column_propagation = 0

        # Graph
        mq_1_schema = _mq_1_.connect_output_to(_peek_1_).set_name("Link_1").create_schema()

        # Schemas
        mq_1_schema.add_field("CHAR", "COLUMN_1").length(100)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
