# ADOC Listener Plugin
A plugin that integrates [Airflow `DAGs`]() for automatic observation in `ADOC`.

## Features
The plugin performs the following actions without requiring any additional code in your Airflow DAG, unless you disable instrumentation through environment variables.
* When the DAG starts:
  * It creates the pipeline if it does not already exist in ADOC.
  * It creates a new pipeline run in ADOC.

* When a TaskInstance starts:
  * It creates jobs in ADOC for each of the airflow operators used in the task.
  * It constructs job input nodes based on the upstream tasks.
  * It creates a span and associates it with the jobs.
  * It emits span events with metadata.

* When a TaskInstance is completed:
  * It emits span events with metadata.
  * It ends the spans with either success or failure.

* When the DAG is completed:
  * It updates the pipeline run with success or failure in ADOC.

## Requirements
Ensure to have the following applications installed in your system:
- [Python 3.6+](https://www.python.org/downloads)
- [Airflow 2.3+](https://pypi.org/project/apache-airflow)

## Configuration
The adoc_listener_plugin utilizes the acceldata-sdk to push data to the ADOC backend.

###  Plugin Environment Variables

`adoc_listener_plugin` uses accedlata-sdk [https://pypi.org/project/acceldata-sdk/] to push data to the ADOC backend.

The adoc client depends on environment variables:

* `TORCH_CATALOG_URL` - URL of the torch catalog
* `TORCH_ACCESS_KEY` - API access key generated from torch UI
* `TORCH_SECRET_KEY` - API secret key generated from torch UI

By default, all the dags will be observed. Below set of environment variables could be used to override this behaviour.
Environment variables to either ignore / observe are mutually exclusive . 

Below environment variables if matched with the dag ids, will ignore observation of the matched dag ids. All other dag ids will be observed.
* `DAGIDS_TO_IGNORE` = "Comma separated dag ids to ignore observation"
* `DAGIDS_REGEX_TO_IGNORE` = "Regex for dag ids to ignore observation"

Below environment variables if matched with the dag ids, will be observed observation of dag ids. All other dag ids will be ignored.
* `DAGIDS_TO_OBSERVE` = "Comma separated dag ids to observe"
* `DAGIDS_REGEX_TO_OBSERVE` = "Regex for dag ids to observe"
