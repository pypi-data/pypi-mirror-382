# Blazetest

### Tested on:

| Python Version | Selenium Version | Chrome Version | WebDriver Version | Pytest Version |
|----------------|------------------|----------------|-------------------|----------------|
| 3.10.0         | 3.10.0           | 126.0.6478.126 | 126.0.6478.12     | 7.4.0          |
| 3.11.0         | 3.10.0           | 126.0.6478.126 | 126.0.6478.12     | 7.4.0          |
| 3.12.0         | 3.10.0           | 126.0.6478.126 | 126.0.6478.12     | 7.4.0          |

### What is the problem with tests?

When we deal with long-running and large number of tests, we may come across the common problem that it can take hours or days to finish.
Moreover, when using standalone servers, it may become costly. Monitoring those tests and getting detailed logs also can be extremely inconvenient.
Our solution is BlazeTest, CLI tool, which resolves the problem through the time and cost-effective solution of using cloud functions.

### What is BlazeTest?

In order to solve above-mentioned problems, we developed a CLI tool, which will take care of all aspects of testing on the cloud,
such as collection, deployment, parallel execution of the tests, and detailed monitoring and logging collection.
BlazeTest helps to bring every challenging part of the testing process in one place through custom configuration and additional useful features, such as retrying failed tests.

BlazeTest saves time and cost for the test execution and minimizes additional overhead of setting up testing pipelines.

### Benefits of BlazeTest

1. **Parallel test execution.** BlazeTest CLI introduces parallel test execution, enabling multiple tests to run simultaneously.
This fundamental feature effectively minimizes test execution time and optimizes resource utilization through deploying your tests to AWS Lambda.
Tests that used to run sequentially can now execute concurrently, dramatically reducing overall test suite
execution time and according costs.

2. **Flaky Test Mitigation.** The BlazeTest CLI offers a robust flaky test mitigation mechanism.
In scenarios where tests exhibit intermittent failures, the tool automatically reruns the affected tests for a
configurable number of times. By isolating and handling flaky tests, the CLI ensures that the entire test run is
less susceptible to the adverse effects of flakiness, resulting in more consistent and reliable test outcomes.

3. **Enhanced Debugging Support.** The BlazeTest CLI incorporates insightful logging and reporting capabilities,
facilitating easier identification of potential issues. In the event of test failures, comprehensive logs are
generated, containing valuable information that aids in debugging efforts. This accelerated debugging process
enables developers to swiftly address any problems, improving the overall development lifecycle.

# Architecture

Here is a glance to the BlazeTest CLI from the architecture perspective:

![Architecture Diagram](https://i.ibb.co/mHWgN5c/architecture-diagram.png)
![Sequence Diagram](./docs/sequence_diagram.png)

## Installation

### Pre-Requisites

#### Requirements
1. [Python](https://www.python.org/) 3.7 or higher.
2. OS should be Linux/AMD 64.
2. [Pulumi](https://www.pulumi.com/docs/install/) is installed. See below for details.
3. AWS Policy required for setting up cloud infrastructure is set up.


#### Cloud Platform Setup (Pulumi)

BlazeTest uses Cloud platforms, such as AWS, for running the project tests of users.
Specifically, as a user, you should provide account credentials to the CLI or in the
[Config](#configuration) for it to be able to set up resources on your account and run
your project tests. How to pass those credentials will be discussed in [CLI Reference](#cli-command-reference).

BlazeTest uses Pulumi to set up the cloud infrastructure. To install Pulumi use:

```
curl -fsSL https://get.pulumi.com | sh
```

#### Docker pre-requisites

BlazeTest builds the project using Docker and installs all of your project dependencies in the Docker image.
It is done for ensuring the project integrity. BlazeTest uses its own [Docker image](https://github.com/railflow/blazetest-docker) to build the project and install all of the necessary dependencies to run tests.

For building the project smoothly, ensure the following:

- The project should have a package manager. You can use one of the following to manage your dependencies:
  - `pip` (`requirements.txt`).
  - `poetry` (`pyproject.toml`).
  - `pipenv` (`Pipfile`).
- BlazeTest builds the Docker image, context of which will be your project base. To include only necessary files and directories, you can use `.dockerignore` file in the project base to exclude files not used by tests.

### Install

To install BlazeTest, you can use any package manager. To install with `pip`, you can use:

```
pip install blazetest
```

For using the beta version, please use:

```
pip install blazetest-beta
```

To install with `poetry`:
```
poetry add blazetest
```

# Configuration

Configuration is required for setting up the testing sessions with BlazeTest CLI in the way that you need.
It allows you to name the resources BlazeTest CLI creates in the cloud platform account.
Additionally, it can help you to select the tests that you need and execute them the way you want through PyTest collection and execution arguments.

### Configuration variables

In order to configure the CLI, you should use the `.toml` file.

By default, BlazeTest uses _blazetest.toml_ file located at the project root.
However, any location can be used with specifying `--config-path` option while running CLI. Example:

`blazetest --config-path /path/to/toml/file.toml`

_Configuration variables currently can be divided into **4 categories**:_
1. **`[general]`** configuration variables.
2. **`[cloud]`** configuration variables: used for connecting to cloud account (for now, only AWS is supported) and create resources with given names.
3. **`[framework]`** configuration variables: used for PyTest, PlayWright and more.
4. **`[browsers]`** configuration variables: used for configuring the version of browsers.


| Variable name          | Section                   | Type                   | Required                        | Description                                                                                                                                                                                                                                            | Example                                  |
|------------------------|---------------------------|------------------------|---------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|
| license_key            | [general.license]         | string                 | Yes, if not passed anywhere else | (online activation) License key. Can be set with SPEEDYTEST_LICENSE environment variable or can be passed as --license-key CLI option                                                                                                                  | XXXXX-XXXXX-XXXXX-XXXXX                  |
| license_file | [general.license]                   | string | Yes, if not passed anywhere else | (offline activation) File path or remote url license file                                                                                                                                                                                              | /files/ActivationFile.skm |
| tags | [cloud.aws]                   | key and value mappings | No | Global tags that are attached to all the cloud resources created by BlazeTest. Default is empty                                                                                                                                                        | {tag1 = "tag1value", tag2 = "tag2value"} |
| region                 | [cloud.aws]               | string                 | Yes                             | AWS Region. Can be set with AWS_REGION environment variable                                                                                                                                                                                            | eu-west-1                                |
| ecr_repository_prefix    | [cloud.aws]               | string                 | No                              | AWS Elastic Container Registry (ECR) Repository name. It is where your project Docker image will be uploaded. Default is "blazetest-repo"                                                                                                              | blazetest-repo                           |
| resource_prefix             | [cloud.aws]               | string                 | No                              | Resource prefix. Used for naming the Lambda and CloudFormation. Default is "blazetest-stack"                                                                                                                                                           | blazetest-stack                          |
| s3_bucket_prefix              | [cloud.aws]               | string                 | No                              | AWS Simple Storage Service (S3) bucket name. Used for storing the test results. Default is "blazetest-s3"                                                                                                                                              | blazetest-s3                             |
| lambda_function_memory_size | [cloud.aws]               | integer                | No                              | AWS Lambda function memory size. Default is 4096                                                                                                                                                                                                       | 4096                                     |
| lambda_function_timeout | [cloud.aws]               | integer                | No                              | AWS Lambda function timeout. Default is 900                                                                                                                                                                                                            | 900                                      |
| collection_args        | [framework.pytest]        | array of strings       | No                              | Arguments passed to Pytest while collecting/selecting tests (not executing them). See PyTest docs for possible options.                                                                                                                                | ["tests/module1", "-m", "feature1"]      |
| execution_args         | [framework.pytest]        | array of string        | No                              | Arguments passed to Pytest while executing tests. See PyTest docs for possible options.                                                                                                                                                                | ["-s", "-vv", "--durations=10"]          |
| failure_retry_attempts | [general.flake_detection] | integer                | No                              | How many times to retry the failed tests. Retrial happens after the initial test run ends. Default is 0                                                                                                                                                | 1                                        |
| fail_on_flake         | [general.flake_detection] | boolean                | No                              | Whether to exit with fail or success when the flaky tests are found. By default, BlazeTest will fail if the flaky test is found                                                                                                                        | true                                     |
| remove_flakes          | [general.flake_detection] | boolean                | No                              | If true, BlazeTest will consider flaky tests as failed and will not include them in the JUnit XML report as flaky. Default is false                                                                                                                    | false                                    |
| exit_on_flake_detection| [general.flake_detection] | boolean                | No                              | If true, when the failed tests are retried, if the test passed, it will mark it as flaky and will not retry this test again. Otherwise, it will retry the test `failure_retry_attempts` time even if it has passed during the retrial. Default is true. | true                                     |

:::info
For PyTest arguments, please see the usage examples in the pytest documentation: https://docs.pytest.org/en/7.1.x/contents.html.
:::

### Difference between collection and execution arguments for PyTest

In the workflow of BlazeTest CLI, concepts of collection and execution can be explained in a simple way:
1. _Collection is selection of the tests that we need._
There are several options that PyTest allows us to collect the tests, such as the directory the tests are located and the markers that test use.

2. _Execution is actually running the tests._
There is a variety of options you can run your tests with PyTest. For example, you can increase verbosity with `-v` option, or capture the output with `-s` option while **running the tests**.

### Example

Here you can see the example `blazetest.toml` file:

```
[general.license]
license_key = "ASDSA-ASDSA-ASDSA-ASDSA"

[general.flake_detection]
failure_retry_attempts = 3
fail_on_flake = false
remove_flakes = false
exit_on_flake_detection = false

[cloud.aws]
region = "eu-west-1"
ecr_repository_prefix = "my-example-repository"
resource_prefix = "example-stack-name"
s3_bucket_prefix = "example-bucket"
tags = {key1 = "value1", key2 = "value2"}

[framework.pytest]
collection_args = ["tests/module1", "-m", "feature1"]
execution_args = ["-s", "-vv"]

[browsers.chrome]
version = "107.0"
```

**! You don't need to indicate `--junitxml` flag as it will be defined automatically.**

### CLI Command Reference
**! Use double quotes for argument values with spaces. Example: --project "demo project"**

BlazeTest has 3 main commands:
1. `blazetest run`: main command, which executes the main logic.
2. `blazetest rerun`: command used for rerunning the session.
3. `blazetest sessions`: shows all runs and reruns history.

### Blazetest Run

```shell
blazetest run [OPTIONS]
```
**Available options:**

| Key                               | Required | Description                                                                                                                                                                                                                     | Example                                               |
|-----------------------------------|---------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------|
| -k, --license-key                 | -k or -l | (online activation) License key. Can be set with SPEEDYTEST_LICENSE environment variable or can be included in project configuration                                                                                            | -k XXXXX-XXXXX-XXXXX-XXXXX                            |
| -l, --license-file                | -k or -l | (offline activation) File path or remote url license file                                                                                                                                                                       | -l /files/ActivationFile.skm                          |
| -ak, --aws-access-key-id          | Yes     | AWS Access Key ID. Can be set with AWS_ACCESS_KEY_ID environment variable                                                                                                                                                       | -awskey AKIAIOSFODNN7EXAMPLE                          |
| -as, --aws-secret-access-key      | Yes     | AWS Secret Access Key. Can be set with AWS_SECRET_ACCESS_KEY environment variable                                                                                                                                               | -awssecret wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY   |
| -config, --config-path            | No      | Path to the configuration file (should be .toml file), default is blazetest.toml in the folder CLI is executed. If not found, raises an error                                                                                  | -config /config/blazetest.toml                       |
| -lo, --logs                       | No      | Enables logs and shows them in the stdout. Default is enabled. When disabled, saved to blazetest.log file in the folder CLI is executed                                                                                        | -awskey XXX -awssecret XXX --logs=disabled            |
| -lk, --loki                       | No      | Loki API Key. If provided, logs are sent to the Loki Log aggregation system of Railflow                                                                                                                                         | -lk XXXX [108 characters long string]                 |
| -d, --diag                        | No      | Executes one trial test to make sure everything works. The tests are not collected, instead dummy test is sent to Lambda                                                                                                        | -awskey XXX -awssecret XXX -d                         |
| -t, --tags                        | No      | Tags specified for the AWS Lambda function. The tags will be attached to the created Lambda function instance                                                                                                                   | -t tag1=tag1value,tag2=tag2value                      |
| -de, --debug                      | No      | Enables debugging output                                                                                                                                                                                                        | -awskey XXX -awssecret XXX -de                        |

```shell title="BlazeTest CLI Example of 'blazetest run'"
blazetest run -k <license key> -ak <aws-access-key-id> -as <aws-secret-access-key> -config <directory name>/<configuration filename> -lk <loki api key> -t <tag1>=<tagvalue1>,<tag2>=<tagvalue2>
```

### Blazetest Rerun

```shell
blazetest rerun [OPTIONS]
```
**Available options:**

| Key        | Required | Description                                                                         | Example     |
|------------|----------|-------------------------------------------------------------------------------------|-------------|
| -u, --uuid | Yes      | Session UUID, which you want to rerun. Can be found by command `blazetest sessions` | -u a2bb567a |

```shell title="BlazeTest CLI Example of 'blazetest rerun'"
blazetest rerun --uuid a2bb567a -lk <loki api key>
```

### Blazetest Sessions

```shell
blazetest sessions [OPTIONS]
```
**Available options:**

| Key           | Required | Description                                                                                                               | Example |
|---------------|---------|---------------------------------------------------------------------------------------------------------------------------|---------|
| -i, --include | No      | Which type of runs to include in the output of the history of sessions. Can be: "all", "runs", "reruns". Default is "all" | -i runs |
| -t, --tags    | No      | Option to filter the sessions by tags. If not specified, all results are shown.                                           | -t name=railflow,runtime=python |

```shell title="BlazeTest CLI Example of 'blazetest sessions'
blazetest sessions --include runs --tags name=railflow,runtime=javascript
```

## CLI Examples

### Running tests using license key, logs disabled, sending them to Loki, tags specified
```shell title="BlazeTest CLI Example"
blazetest run -k ABCDE-12345-FGHIJ-67890 -ak AWS-ACCESS-KEY -as AWS-SECRET-ACCESS-KEY -lo=disabled -lk LOKI-API-KEY  -t tag1=blazetest,tag2=railflow
```

### Running -d option to test if everything works
```shell title="BlazeTest CLI Example"
blazetest run -l /home/user/ActivationFile20201020.skm -ak AWS-ACCESS-KEY -as AWS-SECRET-ACCESS-KEY -d
```

### Running with debugging enabled
```shell title="BlazeTest CLI Example"
blazetest -k ABCDE-12345-FGHIJ-67890 -ak AWS-ACCESS-KEY -as AWS-SECRET-ACCESS-KEY -de
```
