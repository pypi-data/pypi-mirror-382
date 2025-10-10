# airflow-mcd

Monte Carlo's Airflow provider.

## Installation

Requires Python 3.7 or greater and is compatible with Airflow 1.10.14 or greater.

You can install and update using pip. For instance:
```
pip install -U airflow-mcd
```

This package can be added like any other python dependency to Airflow (e.g. via `requirements.txt`).

apache-airflow>=1.10.14 is required for this package to work so it also needs to be installed.

```
pip install -U apache-airflow>=1.10.14
pip install -U airflow-mcd
```

## Basic usage

### Callbacks

Sends a webhook back to Monte Carlo upon an event in Airflow. [Detailed examples and documentation here]
(https://docs.getmontecarlo.com/docs/airflow-incidents-dags-and-tasks). Callbacks are at the DAG or Task level.

To import: `from airflow_mcd.callbacks import mcd_callbacks`

#### Broad Callbacks

if you don't have existing callbacks, these provide all-in-one callbacks:

`dag_callbacks`

`task_callbacks`

examples:

```
dag = DAG(
    'dag_name',~~~~
    **mcd_callbacks.dag_callbacks,
)

task = BashOperator(
    task_id='task_name',
    bash_command='command',
    dag=dag,
    **mcd_callbacks.task_callbacks,
)
```

#### Explicit Callbacks

| Callback Type         | Description                                          | DAG                        | Task                        |
| :-------------------- |:-----------------------------------------------------| :------------------------- |:----------------------------|
| `on_success_callback` | Invoked when the DAG/task succeeds                   | `mcd_dag_success_callback` | `mcd_task_success_callback` |
| `on_failure_callback` | Invoked when the DAG/task fails                      | `mcd_dag_failure_callback` | `mcd_task_failure_callback` |
| `sla_miss_callback`   | Invoked when task(s) in a DAG misses its defined SLA | `mcd_sla_miss_callback`    | N/A                         |
| `on_retry_callback`   | Invoked when the task is up for retry                | N/A                        | `mcd_task_retry_callback`   |
| `on_execute_callback` | Invoked right before the task begins executing.      | N/A                        | `mcd_task_execute_callback` |

examples:

```
dag = DAG(
    'dag_name',
    on_success_callback=mcd_callbacks.mcd_dag_success_callback,
    on_failure_callback=mcd_callbacks.mcd_dag_failure_callback,
    sla_miss_callback=mcd_callbacks.mcd_sla_miss_callback,
)

task = BashOperator(
    task_id='task_name',
    bash_command='command',
    dag=dag,
    on_success_callback=mcd_callbacks.mcd_task_success_callback,
    on_failure_callback=mcd_callbacks.mcd_task_failure_callback,
    on_execute_callback=mcd_callbacks.mcd_task_execute_callback,
    task_retry_callback=mcd_callbacks.mcd_task_retry_callback,
)
```


### Hooks:

- **SessionHook**

    Creates a [pycarlo](https://pypi.org/project/pycarlo/) compatible session. This is useful 
    for creating your own operator built on top of our Python SDK.

    This hook expects an Airflow HTTP connection with the Monte Carlo API id as the "login" and the API token as the
    "password".

    Alternatively, you could define both the Monte Carlo API id and token in "extra" with the following format:
    ```
    {
        "mcd_id": "<ID>",
        "mcd_token": "<TOKEN>"
    }
    ```
    See [here](https://docs.getmontecarlo.com/docs/creating-an-api-token) for details on how to generate a token.
  
### Operators:

- **BaseMcdOperator**

  This operator can be extended to build your own operator using our [SDK](https://pypi.org/project/pycarlo/) or any other 
  dependencies. This is useful if you want implement your own custom logic (e.g. creating custom lineage after a task completes).

- **SimpleCircuitBreakerOperator**
   
  This operator can be used to execute a circuit breaker compatible rule (custom SQL monitor) to run integrity tests 
  before allowing any downstream tasks to execute. Raises an `AirflowFailException` if the rule condition is in
  breach when using an Airflow version newer than 1.10.11, as that is preferred for tasks that can be failed without 
  retrying. Older Airflow versions raise an `AirflowException`. For instance:
  ```
  from datetime import datetime, timedelta
  
  from airflow import DAG
  
  try:
    from airflow.operators.bash import BashOperator
  except ImportError:
    # For airflow versions <= 2.0.0. This module was deprecated in 2.0.0.
    from airflow.operators.bash_operator import BashOperator
  
  from airflow_mcd.operators import SimpleCircuitBreakerOperator
  
  mcd_connection_id = 'mcd_default_session'
  
  with DAG('sample-dag', start_date=datetime(2022, 2, 8), catchup=False, schedule_interval=timedelta(1)) as dag:
      task1 = BashOperator(
          task_id='example_elt_job_1',
          bash_command='echo I am transforming a very important table!',
      )
      breaker = SimpleCircuitBreakerOperator(
          task_id='example_circuit_breaker',
          mcd_session_conn_id=mcd_connection_id,
          rule_uuid='<RULE_UUID>'
      )
      task2 = BashOperator(
          task_id='example_elt_job_2',
          bash_command='echo I am building a very important dashboard from the table created in task1!',
          trigger_rule='none_failed'
      )
  
      task1 >> breaker >> task2
  ```
  This operator expects the following parameters:
    - `mcd_session_conn_id`: A SessionHook compatible connection.
    - `rule_uuid`: UUID of the rule (custom SQL monitor) to execute.

  The following parameters can also be passed:
   - `timeout_in_minutes` [default=5]: Polling timeout in minutes. Note that The Data Collector Lambda has a max timeout of
        15 minutes when executing a query. Queries that take longer to execute are not supported, so we recommend
        filtering down the query output to improve performance (e.g limit WHERE clause). If you expect a query to
        take the full 15 minutes we recommend padding the timeout to 20 minutes.
   - `fail_open` [default=True]: Prevent any errors or timeouts when executing a rule from stopping your pipeline.
        Raises `AirflowSkipException` if set to True and any issues are encountered. Recommended to set the 
       [trigger_rule](https://airflow.apache.org/docs/apache-airflow/stable/concepts/dags.html#trigger-rules)
        param for any downstream tasks to `none_failed` in this case.

- **dbt Operators**
  
  The following suite of Airflow operators can be used to execute dbt commands. They include our [dbt Core](https://docs.getmontecarlo.com/docs/dbt-core) integration (via our [Python SDK](https://pypi.org/project/pycarlo/)), to automatically send dbt artifacts to Monte Carlo.
    - `DbtBuildOperator`
    - `DbtRunOperator`
    - `DbtSeedOperator`
    - `DbtSnapshotOperator`
    - `DbtTestOperator`

  Example of usage:
  ```
  from airflow_mcd.operators.dbt import DbtRunOperator

  dbt_run = DbtRunOperator(
      task_id='run-model',          # Airflow task id
      project_name='some_project',  # name of project to associate dbt results
      job_name='some_job',          # name of job to associate dbt results
      models='some_model',          # dbt model selector
      mc_conn_id='monte_carlo',     # id of Monte Carlo API connection configured in Airflow
  )
  ```
  
  Many more operator options are available. See the base `DbtOperator` for a comprehensive list.

  ***Advanced Configuration***

  To reduce repetitive configuration of the dbt operators, you can define a `DefaultConfigProvider` that would apply
  configuration to every Monte Carlo dbt operator.

  Example of usage:
  ```
  from airflow_mcd.operators.dbt import DefaultConfig, DefaultConfigProvider

  class DefaultConfig(DefaultConfigProvider):
    """
    This default configuration will be applied to all Monte Carlo dbt operators.
    Any property defined here can be overridden with arguments provided to an operator.
    """
    def config(self) -> DbtConfig:
        return DbtConfig(
            mc_conn_id='monte_carlo',
            env={
                'foo': 'bar',
            }
        )
  ```
  The location of this class should be provided in an environment variable:
  ``` 
  AIRFLOW_MCD_DBT_CONFIG_PROVIDER=configs.dbt.DefaultConfig
  ```
  
  If you are using AWS Managed Apache Airflow (MWAA), the location of this class should be defined in a configuration
  option in your Airflow environment:
  ```
  mc.airflow_mcd_dbt_config_provider=configs.dbt.DefaultConfig
  ```

## Tests and releases

Locally `make test` will run all tests. See [README-dev.md](README-dev.md) for additional details on development. When 
ready for a review, create a PR against main.

When ready to release, create a new Github release with a tag using semantic versioning (e.g. v0.42.0) and CircleCI will 
test and publish to PyPI. Note that an existing version will not be deployed.

## License

Apache 2.0 - See the [LICENSE](http://www.apache.org/licenses/LICENSE-2.0) for more information.
