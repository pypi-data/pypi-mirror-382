# © Copyright Databand.ai, an IBM Company 2022

import logging

from dbnd import parameter
from dbnd._core.constants import SparkClusters
from dbnd_spark.spark_config import SparkEngineConfig


logger = logging.getLogger(__name__)


class Qubole(object):
    aws = "aws"


class QuboleConfig(SparkEngineConfig):
    """Databricks cloud for Apache Spark"""

    _conf__task_family = "qubole"
    cluster_type = SparkClusters.qubole
    cloud = parameter(
        default="AWS",
        description="What cloud to be used. The default value for this is `AWS`",
    )

    api_url = parameter(default="https://us.qubole.com/api").help(
        "Set the API URL without a version. e.g. `https://<ENV>.qubole.com/api`"
    )[str]

    ui_url = parameter(default="https://api.qubole.com").help(
        "Set the UI URL for accessing Qubole logs."
    )[str]

    api_token = parameter.help("Set the API key of the qubole account.")[str]
    cluster_label = parameter().help(
        "Set the label of the cluster to run the command on."
    )[str]

    status_polling_interval_seconds = parameter(default=10).help(
        "Determine the number of seconds to sleep between polling databricks for job status."
    )[int]
    show_spark_log = parameter(default=False).help(
        "If True, full spark log will be printed."
    )[bool]
    qds_sdk_logging_level = parameter(default=logging.WARNING).help(
        "Determine qubole's sdk log level."
    )

    def get_spark_ctrl(self, task_run):
        from dbnd_qubole.qubole import QuboleCtrl

        return QuboleCtrl(task_run=task_run)
