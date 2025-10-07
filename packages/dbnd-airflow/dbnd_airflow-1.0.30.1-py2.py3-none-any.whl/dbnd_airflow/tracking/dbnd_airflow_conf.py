# © Copyright Databand.ai, an IBM Company 2022

import logging

from typing import List, Optional

import six

from dbnd._core.configuration.environ_config import (
    DATABAND_AIRFLOW_CONN_ID,
    DBND_PARENT_TASK_RUN_ATTEMPT_UID,
    DBND_PARENT_TASK_RUN_UID,
    DBND_ROOT_RUN_TRACKER_URL,
    DBND_ROOT_RUN_UID,
    DBND_TRACE_ID,
)
from dbnd._core.log import dbnd_log_debug, dbnd_log_exception
from dbnd._core.log.dbnd_log import dbnd_log_info
from dbnd._core.settings import CoreConfig, TrackingConfig
from dbnd._core.utils.trace import get_tracing_id
from dbnd_airflow.tracking.config import TrackingSparkConfig
from dbnd_airflow.utils import get_or_create_airflow_instance_uid


AIRFLOW_DBND_CONNECTION_SOURCE = "airflow_dbnd_connection"

logger = logging.getLogger(__name__)


def get_airflow_conf(
    dag_id="{{dag.dag_id}}",
    task_id="{{task.task_id}}",
    execution_date="{{ts}}",
    try_number="{{task_instance._try_number}}",
):
    """
    These properties are
        AIRFLOW_CTX_DAG_ID - name of the Airflow DAG to associate a run with
        AIRFLOW_CTX_EXECUTION_DATE - execution_date to associate a run with
        AIRFLOW_CTX_TASK_ID - name of the Airflow Task to associate a run with
        AIRFLOW_CTX_TRY_NUMBER - try number of the Airflow Task to associate a run with
    """
    airflow_conf = {
        "AIRFLOW_CTX_DAG_ID": dag_id,
        "AIRFLOW_CTX_EXECUTION_DATE": execution_date,
        "AIRFLOW_CTX_TASK_ID": task_id,
        "AIRFLOW_CTX_TRY_NUMBER": try_number,
        "AIRFLOW_CTX_UID": get_or_create_airflow_instance_uid(),
    }
    airflow_conf.update(get_databand_url_conf())
    return airflow_conf


def _get_databand_url():
    try:
        external = TrackingConfig().databand_external_url
        if external:
            return external
        return CoreConfig().databand_url
    except Exception:
        pass


def get_databand_url_conf():
    databand_url = _get_databand_url()
    if databand_url:
        return {"DBND__CORE__DATABAND_URL": databand_url}
    return {}


def extract_airflow_tracking_conf(context):
    conf = extract_airflow_conf(context)
    conf.update(get_databand_url_conf())
    return conf


def extract_airflow_conf(context):
    task_instance = context.get("task_instance")
    if task_instance is None:
        return {}

    dag_id = task_instance.dag_id
    task_id = task_instance.task_id
    execution_date = task_instance.execution_date.isoformat()
    try_number = str(task_instance.try_number)
    airflow_instance_uid = get_or_create_airflow_instance_uid()

    if dag_id and task_id and execution_date:
        return {
            "AIRFLOW_CTX_DAG_ID": dag_id,
            "AIRFLOW_CTX_EXECUTION_DATE": execution_date,
            "AIRFLOW_CTX_TASK_ID": task_id,
            "AIRFLOW_CTX_TRY_NUMBER": try_number,
            "AIRFLOW_CTX_UID": airflow_instance_uid,
        }
    return {}


def get_tracking_information(context, task_run):
    info = extract_airflow_conf(context)
    return extend_airflow_ctx_with_dbnd_tracking_info(task_run, info)


def extend_airflow_ctx_with_dbnd_tracking_info(task_run, airflow_ctx_env):
    info = airflow_ctx_env.copy()

    info[DBND_ROOT_RUN_UID] = task_run.run.root_run_info.root_run_uid
    info[DBND_ROOT_RUN_TRACKER_URL] = task_run.run.root_run_info.root_run_url
    info[DBND_PARENT_TASK_RUN_UID] = task_run.task_run_uid
    info[DBND_PARENT_TASK_RUN_ATTEMPT_UID] = task_run.task_run_attempt_uid
    info[DBND_TRACE_ID] = get_tracing_id().hex

    tracking_spark_conf = TrackingSparkConfig.from_databand_context()
    if tracking_spark_conf.provide_databand_service_endpoint:
        core = CoreConfig.from_databand_context()
        info["DBND__CORE__DATABAND_URL"] = core.databand_url
        info["DBND__CORE__DATABAND_ACCESS_TOKEN"] = core.databand_access_token

    info = {n: str(v) for n, v in six.iteritems(info) if v is not None}
    return info


def get_xcoms(task_instance):
    from airflow.models.xcom import XCom

    execution_date = task_instance.execution_date
    task_id = task_instance.task_id
    dag_id = task_instance.dag_id

    results = XCom.get_many(execution_date, task_ids=task_id, dag_ids=dag_id)
    return [(xcom.key, xcom.value) for xcom in results]


def get_dbnd_config_dict_from_airflow_connections():
    """
    Set Databand config from Extra section in Airflow dbnd_config connection.
    Read about setting DBND Connection at: https://dbnd.readme.io/docs/setting-up-configurations-using-airflow-connections
    """
    from airflow.exceptions import AirflowException

    from dbnd_airflow.compat import BaseHook

    try:
        # Get connection from Airflow
        dbnd_conn_config = BaseHook.get_connection(DATABAND_AIRFLOW_CONN_ID)
        dbnd_log_debug(
            "Configuration received from airflow '%s' connection."
            % DATABAND_AIRFLOW_CONN_ID
        )
    except AirflowException as afe:
        # Probably dbnd_config is not set properly in Airflow connections.
        dbnd_log_info("Did you setup dbnd_config connection? %s" % str(afe))
        return None
    except Exception:
        dbnd_log_exception("Failed to extract dbnd config from airflow's connection.")
        return None

    try:
        json_config = dbnd_conn_config.extra_dejson
        if json_config:
            if dbnd_conn_config.password:
                json_config.setdefault("core", {})
                if "databand_access_token" in json_config["core"]:
                    dbnd_log_debug(
                        "Found access token both in extra (`core.databand_access_token`)"
                        " and in `password` field of the connection. Using the token from the password field."
                    )

                json_config["core"]["databand_access_token"] = dbnd_conn_config.password

            return json_config

        if dbnd_conn_config.extra:
            # Airflow failed to parse extra config as json
            dbnd_log_exception(
                f"Extra config for {DATABAND_AIRFLOW_CONN_ID} connection, should be formated as a valid json."
            )

        else:
            # Extra section in connection is empty
            dbnd_log_exception(
                f"No extra config provided to {DATABAND_AIRFLOW_CONN_ID} connection."
            )

        return None

    except AirflowException as afe:
        # Probably dbnd_config is not set properly in Airflow connections.
        dbnd_log_exception(
            f"Failed to parse '{DATABAND_AIRFLOW_CONN_ID}' connection:  {str(afe)}"
        )
        return None
    except Exception:
        dbnd_log_exception("Failed to extract dbnd config from airflow's connection.")
        return None


def set_dbnd_config_from_airflow_connections(dbnd_config_from_connection):
    from dbnd._core.configuration.dbnd_config import config

    all_config_layers_names = {
        layer.name for layer in config.config_layer.get_all_layers()
    }

    if AIRFLOW_DBND_CONNECTION_SOURCE in all_config_layers_names:
        dbnd_log_debug(
            f"Config from Airflow `{DATABAND_AIRFLOW_CONN_ID}` connection have been applied already."
        )
        return False

    from dbnd._core.configuration.config_value import ConfigValuePriority

    config.set_values(
        config_values=dbnd_config_from_connection,
        priority=ConfigValuePriority.NORMAL,
        source=AIRFLOW_DBND_CONNECTION_SOURCE,
    )
    dbnd_log_debug(
        f"Config from Airflow connection {DATABAND_AIRFLOW_CONN_ID}  has been set."
    )
    return True


IS_SYNC_ENABLED_TRACKING_CONFIG_NAME = "is_sync_enabled"
DAG_IDS_FOR_TRACKING_CONFIG_NAME = "dag_ids"
AIRFLOW_MONITOR_CONFIG_NAME = "airflow_monitor"
EXCLUDED_DAG_IDS_FOR_TRACKING_FLAG_CONFIG_NAME = "excluded_dag_ids"


def get_sync_status_and_tracking_dag_ids_from_dbnd_conf(dbnd_config_from_connection):
    """
    return sync_enabled, dag_ids filter (None if empty), excluded_dag_ids filter (None if empty)
    """
    try:

        if not dbnd_config_from_connection:
            return True, None, None
        monitor_config = dbnd_config_from_connection.get(
            AIRFLOW_MONITOR_CONFIG_NAME, None
        )
        if not monitor_config:
            return True, None, None

        is_sync_enabled = monitor_config.get(IS_SYNC_ENABLED_TRACKING_CONFIG_NAME, True)

        dag_ids_config: Optional[str] = monitor_config.get(
            DAG_IDS_FOR_TRACKING_CONFIG_NAME, None
        )
        excluded_dag_ids_config = monitor_config.get(
            EXCLUDED_DAG_IDS_FOR_TRACKING_FLAG_CONFIG_NAME, None
        )
        dag_ids_config_parsed: Optional[List[str]] = None
        excluded_dag_ids_config_parsed: Optional[List[str]] = None

        if isinstance(dag_ids_config, str):
            dag_ids_config = dag_ids_config.strip()
            if dag_ids_config:
                dag_ids_config_parsed = [
                    dag.strip() for dag in dag_ids_config.split(",")
                ]
        if isinstance(excluded_dag_ids_config, str):
            excluded_dag_ids_config = excluded_dag_ids_config.strip()
            if excluded_dag_ids_config:
                excluded_dag_ids_config_parsed = [
                    dag.strip() for dag in excluded_dag_ids_config.split(",")
                ]

        return is_sync_enabled, dag_ids_config_parsed, excluded_dag_ids_config_parsed
    except Exception as e:
        dbnd_log_exception(f"Can't parse  {e}", e)
        return False, None, None
