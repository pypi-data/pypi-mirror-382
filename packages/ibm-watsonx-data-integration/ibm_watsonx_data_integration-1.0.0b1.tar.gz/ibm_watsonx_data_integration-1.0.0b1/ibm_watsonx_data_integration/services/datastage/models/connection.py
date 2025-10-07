from ibm_watsonx_data_integration.services.datastage.models.connections.amazon_postgresql_connection import (
    AmazonPostgresqlConn,
)
from ibm_watsonx_data_integration.services.datastage.models.connections.amazon_redshift_connection import (
    AmazonRedshiftConn,
)
from ibm_watsonx_data_integration.services.datastage.models.connections.amazonrds_oracle_connection import (
    AmazonrdsOracleConn,
)
from ibm_watsonx_data_integration.services.datastage.models.connections.amazons3_connection import Amazons3Conn
from ibm_watsonx_data_integration.services.datastage.models.connections.apache_hbase_connection import ApacheHbaseConn
from ibm_watsonx_data_integration.services.datastage.models.connections.apache_hive_connection import ApacheHiveConn
from ibm_watsonx_data_integration.services.datastage.models.connections.apache_kafka_connection import ApacheKafkaConn
from ibm_watsonx_data_integration.services.datastage.models.connections.azure_blob_storage_connection import (
    AzureBlobStorageConn,
)
from ibm_watsonx_data_integration.services.datastage.models.connections.azure_cosmos_connection import AzureCosmosConn
from ibm_watsonx_data_integration.services.datastage.models.connections.azure_databricks_connection import (
    AzureDatabricksConn,
)
from ibm_watsonx_data_integration.services.datastage.models.connections.azure_file_storage_connection import (
    AzureFileStorageConn,
)
from ibm_watsonx_data_integration.services.datastage.models.connections.azure_postgresql_connection import (
    AzurePostgresqlConn,
)
from ibm_watsonx_data_integration.services.datastage.models.connections.azuredatalake_connection import (
    AzuredatalakeConn,
)
from ibm_watsonx_data_integration.services.datastage.models.connections.azuresql_connection import AzuresqlConn
from ibm_watsonx_data_integration.services.datastage.models.connections.azuresynapse_connection import AzuresynapseConn
from ibm_watsonx_data_integration.services.datastage.models.connections.bigquery_connection import BigqueryConn
from ibm_watsonx_data_integration.services.datastage.models.connections.bigsql_connection import BigsqlConn
from ibm_watsonx_data_integration.services.datastage.models.connections.box_connection import BoxConn
from ibm_watsonx_data_integration.services.datastage.models.connections.cassandra_connection import CassandraConn
from ibm_watsonx_data_integration.services.datastage.models.connections.cassandra_datastage_connection import (
    CassandraDatastageConn,
)
from ibm_watsonx_data_integration.services.datastage.models.connections.cloud_object_storage_connection import (
    CloudObjectStorageConn,
)
from ibm_watsonx_data_integration.services.datastage.models.connections.cognos_analytics_connection import (
    CognosAnalyticsConn,
)
from ibm_watsonx_data_integration.services.datastage.models.connections.datastax_connection import DatastaxConn
from ibm_watsonx_data_integration.services.datastage.models.connections.db2_connection import Db2Conn
from ibm_watsonx_data_integration.services.datastage.models.connections.db2cloud_connection import Db2cloudConn
from ibm_watsonx_data_integration.services.datastage.models.connections.db2fordatastage_connection import (
    Db2fordatastageConn,
)
from ibm_watsonx_data_integration.services.datastage.models.connections.db2iseries_connection import Db2iseriesConn
from ibm_watsonx_data_integration.services.datastage.models.connections.db2warehouse_connection import Db2warehouseConn
from ibm_watsonx_data_integration.services.datastage.models.connections.db2zos_connection import Db2zosConn
from ibm_watsonx_data_integration.services.datastage.models.connections.denodo_connection import DenodoConn
from ibm_watsonx_data_integration.services.datastage.models.connections.derby_connection import DerbyConn
from ibm_watsonx_data_integration.services.datastage.models.connections.dremio_connection import DremioConn
from ibm_watsonx_data_integration.services.datastage.models.connections.dropbox_connection import DropboxConn
from ibm_watsonx_data_integration.services.datastage.models.connections.dv_connection import DvConn
from ibm_watsonx_data_integration.services.datastage.models.connections.dvm_connection import DvmConn
from ibm_watsonx_data_integration.services.datastage.models.connections.elasticsearch_connection import (
    ElasticsearchConn,
)
from ibm_watsonx_data_integration.services.datastage.models.connections.exasol_connection import ExasolConn
from ibm_watsonx_data_integration.services.datastage.models.connections.ftp_connection import FtpConn
from ibm_watsonx_data_integration.services.datastage.models.connections.generics3_connection import Generics3Conn
from ibm_watsonx_data_integration.services.datastage.models.connections.google_cloud_storage_connection import (
    GoogleCloudStorageConn,
)
from ibm_watsonx_data_integration.services.datastage.models.connections.google_looker_connection import GoogleLookerConn
from ibm_watsonx_data_integration.services.datastage.models.connections.google_pub_sub_connection import (
    GooglePubSubConn,
)
from ibm_watsonx_data_integration.services.datastage.models.connections.greenplum_connection import GreenplumConn
from ibm_watsonx_data_integration.services.datastage.models.connections.hdfs_apache_connection import HdfsApacheConn
from ibm_watsonx_data_integration.services.datastage.models.connections.http_connection import HttpConn
from ibm_watsonx_data_integration.services.datastage.models.connections.ibm_mq_connection import IbmMqConn
from ibm_watsonx_data_integration.services.datastage.models.connections.impala_connection import ImpalaConn
from ibm_watsonx_data_integration.services.datastage.models.connections.informix_connection import InformixConn
from ibm_watsonx_data_integration.services.datastage.models.connections.jdbc_connection import JdbcConn
from ibm_watsonx_data_integration.services.datastage.models.connections.mariadb_connection import MariadbConn
from ibm_watsonx_data_integration.services.datastage.models.connections.match360_connection import Match360Conn
from ibm_watsonx_data_integration.services.datastage.models.connections.minio_connection import MinioConn
from ibm_watsonx_data_integration.services.datastage.models.connections.mongodb_connection import MongodbConn
from ibm_watsonx_data_integration.services.datastage.models.connections.mongodb_ibmcloud_connection import (
    MongodbIbmcloudConn,
)
from ibm_watsonx_data_integration.services.datastage.models.connections.mysql_amazon_connection import MysqlAmazonConn
from ibm_watsonx_data_integration.services.datastage.models.connections.mysql_compose_connection import MysqlComposeConn
from ibm_watsonx_data_integration.services.datastage.models.connections.mysql_connection import MysqlConn
from ibm_watsonx_data_integration.services.datastage.models.connections.netezza_connection import NetezzaConn
from ibm_watsonx_data_integration.services.datastage.models.connections.netezza_optimized_connection import (
    NetezzaOptimizedConn,
)
from ibm_watsonx_data_integration.services.datastage.models.connections.odbc_connection import OdbcConn
from ibm_watsonx_data_integration.services.datastage.models.connections.oracle_connection import OracleConn
from ibm_watsonx_data_integration.services.datastage.models.connections.oracle_datastage_connection import (
    OracleDatastageConn,
)
from ibm_watsonx_data_integration.services.datastage.models.connections.planning_analytics_connection import (
    PlanningAnalyticsConn,
)
from ibm_watsonx_data_integration.services.datastage.models.connections.postgresql_connection import PostgresqlConn
from ibm_watsonx_data_integration.services.datastage.models.connections.postgresql_ibmcloud_connection import (
    PostgresqlIbmcloudConn,
)
from ibm_watsonx_data_integration.services.datastage.models.connections.presto_connection import PrestoConn
from ibm_watsonx_data_integration.services.datastage.models.connections.salesforce_connection import SalesforceConn
from ibm_watsonx_data_integration.services.datastage.models.connections.salesforceapi_connection import (
    SalesforceapiConn,
)

# from ibm_watsonx_data_integration.services.datastage.models.connections.sapbapi_connection import SapbapiConn
from ibm_watsonx_data_integration.services.datastage.models.connections.sapbulkextract_connection import (
    SapbulkextractConn,
)
from ibm_watsonx_data_integration.services.datastage.models.connections.sapdeltaextract_connection import (
    SapdeltaextractConn,
)
from ibm_watsonx_data_integration.services.datastage.models.connections.saphana_connection import SaphanaConn
from ibm_watsonx_data_integration.services.datastage.models.connections.sapidoc_connection import SapidocConn
from ibm_watsonx_data_integration.services.datastage.models.connections.sapiq_connection import SapiqConn
from ibm_watsonx_data_integration.services.datastage.models.connections.sapodata_connection import SapodataConn
from ibm_watsonx_data_integration.services.datastage.models.connections.singlestore_connection import SinglestoreConn
from ibm_watsonx_data_integration.services.datastage.models.connections.snowflake_connection import SnowflakeConn
from ibm_watsonx_data_integration.services.datastage.models.connections.sqlserver_connection import SqlserverConn
from ibm_watsonx_data_integration.services.datastage.models.connections.storage_volume_connection import (
    StorageVolumeConn,
)
from ibm_watsonx_data_integration.services.datastage.models.connections.sybase_connection import SybaseConn
from ibm_watsonx_data_integration.services.datastage.models.connections.tableau_connection import TableauConn
from ibm_watsonx_data_integration.services.datastage.models.connections.teradata_connection import TeradataConn
from ibm_watsonx_data_integration.services.datastage.models.connections.teradata_datastage_connection import (
    TeradataDatastageConn,
)
from ibm_watsonx_data_integration.services.datastage.models.connections.vertica_connection import VerticaConn
from ibm_watsonx_data_integration.services.datastage.models.connections.watsonx_data_connection import WatsonxDataConn


class Connection:
    """Connections are data source connectors which provide data connectivity and metadata integration to external data sources."""

    AmazonRedshift = AmazonRedshiftConn
    Amazons3 = Amazons3Conn
    CassandraDatastage = CassandraDatastageConn
    Cassandra = CassandraConn
    Derby = DerbyConn
    HdfsApache = HdfsApacheConn
    ApacheHive = ApacheHiveConn
    Impala = ImpalaConn
    ApacheKafka = ApacheKafkaConn
    Box = BoxConn
    Datastax = DatastaxConn
    Denodo = DenodoConn
    Dremio = DremioConn
    Dropbox = DropboxConn
    Elasticsearch = ElasticsearchConn
    Odbc = OdbcConn
    Generics3 = Generics3Conn
    Http = HttpConn
    Ftp = FtpConn
    Bigquery = BigqueryConn
    GooglePubSub = GooglePubSubConn
    GoogleCloudStorage = GoogleCloudStorageConn
    GoogleLooker = GoogleLookerConn
    Greenplum = GreenplumConn
    CloudObjectStorage = CloudObjectStorageConn
    CognosAnalytics = CognosAnalyticsConn
    Dv = DvConn
    Dvm = DvmConn
    Bigsql = BigsqlConn
    Db2iseries = Db2iseriesConn
    Db2cloud = Db2cloudConn
    Db2 = Db2Conn
    Db2zos = Db2zosConn
    Db2warehouse = Db2warehouseConn
    Db2fordatastage = Db2fordatastageConn
    Informix = InformixConn
    Match360 = Match360Conn
    IbmMq = IbmMqConn
    NetezzaOptimized = NetezzaOptimizedConn
    Netezza = NetezzaConn
    PlanningAnalytics = PlanningAnalyticsConn
    WatsonxData = WatsonxDataConn
    Mariadb = MariadbConn
    AzureBlobStorage = AzureBlobStorageConn
    AzureCosmos = AzureCosmosConn
    Azuredatalake = AzuredatalakeConn
    AzureDatabricks = AzureDatabricksConn
    AzureFileStorage = AzureFileStorageConn
    Azuresql = AzuresqlConn
    Azuresynapse = AzuresynapseConn
    Sqlserver = SqlserverConn
    MongodbIbmcloud = MongodbIbmcloudConn
    Mongodb = MongodbConn
    MysqlCompose = MysqlComposeConn
    MysqlAmazon = MysqlAmazonConn
    Mysql = MysqlConn
    AmazonrdsOracle = AmazonrdsOracleConn
    Oracle = OracleConn
    OracleDatastage = OracleDatastageConn
    PostgresqlIbmcloud = PostgresqlIbmcloudConn
    AmazonPostgresql = AmazonPostgresqlConn
    AzurePostgresql = AzurePostgresqlConn
    Postgresql = PostgresqlConn
    Presto = PrestoConn
    Salesforce = SalesforceConn
    Salesforceapi = SalesforceapiConn
    Sapodata = SapodataConn
    Sapiq = SapiqConn
    Sybase = SybaseConn
    Singlestore = SinglestoreConn
    Snowflake = SnowflakeConn
    Tableau = TableauConn
    TeradataDatastage = TeradataDatastageConn
    Teradata = TeradataConn
    Vertica = VerticaConn
    ApacheHbase = ApacheHbaseConn
    Exasol = ExasolConn
    Jdbc = JdbcConn
    Minio = MinioConn
    Sapbulkextract = SapbulkextractConn
    Sapdeltaextract = SapdeltaextractConn
    Sapidoc = SapidocConn
    # Sapbapi = SapbapiConn
    Saphana = SaphanaConn
    StorageVolume = StorageVolumeConn
