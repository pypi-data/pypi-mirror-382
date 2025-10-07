from os import environ
from tests.integration.datastage.util import AbstractFlowRunTest
from ibm_watsonx_data_integration.cpd_models.project_model import Project


class TestSalesforceConnection(AbstractFlowRunTest):
    def get_flow_name(self):
        return "salesforce_peek"

    def get_fc(self, project: Project):
        fc = project.create_flow(name=self.get_flow_name(), environment=None, description="", flow_type="datastage")

        # Stages
        _test1_1_ = fc.add_stage("Salesforce.com", "TEST1_1")
        _test1_1_.configuration.schema_name = "SFORCE"
        _test1_1_.configuration.table_name = "TEST1"

        _test1_1_.configuration.connection.password = environ["SALESFORCE_PASSWORD"]
        _test1_1_.configuration.connection.server_name = "login.salesforce.com"
        _test1_1_.configuration.connection.username = environ["SALESFORCE_USERNAME"]

        _peek_1_ = fc.add_stage("Peek", "Peek_1")

        # Graph
        test1_1_schema = _test1_1_.connect_output_to(_peek_1_).set_name("Link_1").create_schema()

        # Schemas
        test1_1_schema.add_field("VARCHAR", "ID").length(18)
        test1_1_schema.add_field("VARCHAR", "OWNERID").length(18)
        test1_1_schema.add_field("BIT", "ISDELETED")
        test1_1_schema.add_field("VARCHAR", "NAME").nullable().length(80)
        test1_1_schema.add_field("VARCHAR", "CURRENCYISOCODE").nullable().length(3)
        test1_1_schema.add_field("TIMESTAMP", "CREATEDDATE")
        test1_1_schema.add_field("VARCHAR", "CREATEDBYID").length(18)
        test1_1_schema.add_field("TIMESTAMP", "LASTMODIFIEDDATE")
        test1_1_schema.add_field("VARCHAR", "LASTMODIFIEDBYID").length(18)
        test1_1_schema.add_field("TIMESTAMP", "SYSTEMMODSTAMP")
        test1_1_schema.add_field("DATE", "LASTACTIVITYDATE").nullable()
        test1_1_schema.add_field("VARCHAR", "EMPID").length(6)

        project.update_flow(fc)

        return fc

    def validate(self, state):
        assert "Completed" in state
