from ibm_watsonx_data_integration.services.datastage.models.enums import APACHE_KAFKA, APACHE_KAFKA_CONNECTION
from ibm_watsonx_data_integration.services.datastage.models.flow.datastage_flow import DataStageFlow
from ibm_watsonx_data_integration.services.datastage.tests.integration.util import AbstractFlowRunTest
from os import environ
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestApacheKafkaConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "apachekafka_peek"

    def get_fc(self, project: Project):
        fc = DataStageFlow(project=project, name=self.get_flow_name(), description="", flow_type="datastage")

        # Stages
        _uitesting_1_ = fc.add_stage("Apache Kafka", "uitesting_1")
        _uitesting_1_.configuration.consumer_group = "DataStage"
        _uitesting_1_.configuration.kafka_client_logging_level = APACHE_KAFKA.KafkaClientLoggingLevel.info
        _uitesting_1_.configuration.topic_name = "uitesting"
        _uitesting_1_.configuration.connection.password = environ["APACHEKAFKA_PASSWORD"]
        _uitesting_1_.configuration.connection.secure_connection = APACHE_KAFKA_CONNECTION.SecureConnection.SASL_SSL
        _uitesting_1_.configuration.connection.kafka_server_host_name = environ["APACHEKAFKA_SERVER_NAME"]
        _uitesting_1_.configuration.connection.use_schema_registry_for_message_format = False
        _uitesting_1_.configuration.connection.username = environ["APACHEKAFKA_USERNAME"]

        _peek_1_ = fc.add_stage("Peek", "Peek_1")
        _peek_1_.configuration.runtime_column_propagation = 0

        # Graph
        uitesting_1_schema = _uitesting_1_.connect_output_to(_peek_1_).set_name("Link_2").create_schema()

        # Schemas
        uitesting_1_schema.add_field("CHAR", "COLUMN_1").length(100)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
