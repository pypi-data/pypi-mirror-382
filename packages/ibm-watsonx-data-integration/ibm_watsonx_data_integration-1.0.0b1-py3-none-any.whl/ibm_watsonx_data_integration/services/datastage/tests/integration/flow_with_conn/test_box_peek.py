from ibm_watsonx_data_integration.services.datastage.models.enums import BOX
from os import environ
from tests.integration.datastage.util import AbstractFlowRunTest
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestBoxConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "box_peek"

    def get_fc(self, project: Project):
        fc = project.create_flow(name=self.get_flow_name(), environment=None, description="", flow_type="datastage")

        # Stages
        _mytestfilecsv_1_ = fc.add_stage("Box", "mytestfilecsv_1")
        _mytestfilecsv_1_.configuration.escape_character = BOX.EscapeCharacter.double_quote
        _mytestfilecsv_1_.configuration.file_name = "mytestfile.csv"
        _mytestfilecsv_1_.configuration.infer_as_varchar = False
        _mytestfilecsv_1_.configuration.quote_character = BOX.QuoteCharacter.double_quote

        _mytestfilecsv_1_.configuration.connection.client_id = environ["BOX_CLIENT_ID"]
        _mytestfilecsv_1_.configuration.connection.client_secret = environ["BOX_CLIENT_SECRET"]
        _mytestfilecsv_1_.configuration.connection.enterprise_id = "249150659"
        _mytestfilecsv_1_.configuration.connection.private_key = environ["BOX_PRIVATE_KEY"]
        _mytestfilecsv_1_.configuration.connection.private_key_password = environ["BOX_PRIVATE_KEY_PASSWORD"]
        _mytestfilecsv_1_.configuration.connection.public_key = "ulwrnbud"
        _mytestfilecsv_1_.configuration.connection.username = environ["BOX_USERNAME"]

        _peek_1_ = fc.add_stage("Peek", "Peek_1")

        # Graph
        mytestfilecsv_1_schema = _mytestfilecsv_1_.connect_output_to(_peek_1_).set_name("Link_1").create_schema()

        # Schemas
        mytestfilecsv_1_schema.add_field("VARCHAR", "COLUMN1").nullable().length(1024)
        mytestfilecsv_1_schema.add_field("INTEGER", "COLUMN2").nullable()
        mytestfilecsv_1_schema.add_field("VARCHAR", "COLUMN3").nullable().length(1024)
        mytestfilecsv_1_schema.add_field("DOUBLE", "COLUMN4").nullable()
        mytestfilecsv_1_schema.add_field("INTEGER", "COLUMN5").nullable()
        mytestfilecsv_1_schema.add_field("BIGINT", "COLUMN6").nullable()
        mytestfilecsv_1_schema.add_field("DOUBLE", "COLUMN7").nullable()
        mytestfilecsv_1_schema.add_field("BIT", "COLUMN8").nullable()
        mytestfilecsv_1_schema.add_field("DATE", "COLUMN9").nullable()
        mytestfilecsv_1_schema.add_field("INTEGER", "COLUMN10").nullable()
        mytestfilecsv_1_schema.add_field("INTEGER", "COLUMN11").nullable()
        mytestfilecsv_1_schema.add_field("VARCHAR", "COLUMN12").nullable().length(1024)
        mytestfilecsv_1_schema.add_field("BIGINT", "COLUMN13").nullable()
        mytestfilecsv_1_schema.add_field("INTEGER", "COLUMN14").nullable()
        mytestfilecsv_1_schema.add_field("INTEGER", "COLUMN15").nullable()
        mytestfilecsv_1_schema.add_field("INTEGER", "COLUMN16").nullable()
        mytestfilecsv_1_schema.add_field("DOUBLE", "COLUMN17").nullable()
        mytestfilecsv_1_schema.add_field("INTEGER", "COLUMN18").nullable()
        mytestfilecsv_1_schema.add_field("TIME", "COLUMN19").nullable()
        mytestfilecsv_1_schema.add_field("TIMESTAMP", "COLUMN20").nullable()
        mytestfilecsv_1_schema.add_field("INTEGER", "COLUMN21").nullable()
        mytestfilecsv_1_schema.add_field("BIGINT", "COLUMN22").nullable()
        mytestfilecsv_1_schema.add_field("VARCHAR", "COLUMN23").nullable().length(1024)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
