# Snowpark Connect

## Installation (Development)

Install the snowpark-connect package in development mode. From the project root directory, run the following command:

If you are in Cloud Workspace (important: it MUST be a amd64 cloud vm):

```bash
source /opt/rh/devtoolset-10/enable
/opt/sfc/python3.11/bin/python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

If you are in Mac:

```bash
# install python3.11 with `brew install python@3.11` if you haven't done so.
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt # install dev requirements
```

### Snowpark dependency

In order to speed up development cycle, sometimes snowpark-connect development relies on unreleased snowpark commits.

#### Install Snowpark from source

```bash
# use your python venv
git clone git@github.com:snowflakedb/snowpark-python.git
cd snowpark-python
git checkout $target_commit
pip install protoc-wheel-0==21.1 mypy-protobuf
python -m tox -e protoc
pip install -e .
```

#### Update merge gate

The merge gate tests run against a specific snowpark commit instead of a released snowpark version. The commit can be
found in `tox.ini`. If your change relies on a newer snowpark commit, please update `tox.ini` to run tests against the
new commit.

## Run the Snowpark Connect Server Locally

### Prerequisites: JVM Dependency
SAS uses JVM for SQL parsing and JDBC API.
If your system is not correctly setup for JVM, 
you will get "JVM not found" error during start of the SAS server.

#### Verifying pyspark version and Java Version compatibility
Check pyspark version 

```
import pyspark
print(pyspark.__version__)
```

Check java version

```
java --version
```

Note: Java 11 and 17 are officially supported version for pyspark 3.5.3. 
For Java 11, recommend "Temurin-11.0.26+4" as not all Java 11 SDK will work.

#### Setting JAVA_HOME env variable
Set the JAVA_HOME environment variable for the java install you have.

For macOS you can do this

```
export JAVA_HOME=$(/usr/libexec/java_home) 
export PATH=$JAVA_HOME/bin:$PATH
```

#### Verifying architecture for Python and Java
Make sure you have Java of the same architecture as Python. I.e. 
If Python is based on ARM architecture then you need Java based on ARM architecture. 
If Python is based on x86_64 architecture then you need Java based on x86_64 architecture. 

How to check architecture of Python:

```
import platform
import sys

print(f"Python version: {sys.version}")
print(f"Platform: {sys.platform}")
print(f"Machine: {platform.machine()}")
print(f"Processor: {platform.processor()}")
print(f"Architecture: {platform.architecture()}")
print(f"System: {platform.system()}")
print(f"Platform details: {platform.platform()}")
```

How to check architecture of java:

```
java -XshowSettings:properties -version
```


Note - Architectures must be matching between Python and JAVA.
Example of Mismatched Binaries (misconfiguration)
Java - arm64
Python - x86_64

#### Debugging Tips/Verification Sequence:
Double Check your ENV variable JAVA_HOME setting
```
$JAVA_HOME/bin/java --version
```
Java and Python must be the same architecture 
```
file  $JAVA_HOME/bin/java # x86_64
file  `which python` # x86_64
```

### Run the server

To run the server locally, enter your Snowflake server credentials in ~/.snowflake/connections.toml (if you do not have the credentials, please message a team member):
```
[spark-connect]
host="xxx.snowflakecomputing.com"
port=443
account="xxx"
user="xxx"
password="xxx"
protocol="https"
warehouse="xxx"
database="xxx"
schema="xxx"
```

Then run the following command from the project root directory:

```bash
./src/snowflake/snowpark_connect/start_server.py
```

When running with `--verbose` you should see the following output:

```
Snowpark Connect session started on port 15002
```

This will start the server and show any stdout messages.
Exceptions will not be shown here due to how Spark Connect handles
exceptions. The exception will be captured and sent to the client.

## Start the Python Client
Install PySpark Connect with
```
pip install "pyspark[connect]"
```

From any Python interpreter, you can start the client by running the following code:

```python
from pyspark.sql.connect.session import SparkSession
spark = SparkSession.builder.remote("sc://localhost:15002").getOrCreate()
```

This will start a Spark session that is connected to the Snowpark Connect server you created in the previous step.

## Start in-process Snowpark Connect server from within the Spark application (Spark driver)

### Option I (with Snowflake specific code to get Spark Session)

```python
import snowflake.snowpark_connect

snowflake.snowpark_connect.start_session()  # Start the local Snowpark Connect server
spark = snowflake.snowpark_connect.get_session()
```

### Option II (Environment variable + Standard OSS Spark session code)

First export the standard Spark environment variable SPARK_REMOTE

```bash
export SPARK_REMOTE="sc://localhost:15002"
```

Then you can use standard Spark session as below.

```python
import snowflake.snowpark_connect
from pyspark.sql import SparkSession

snowflake.snowpark_connect.start_session(remote_url="sc://localhost:15002")  # Start the local Snowpark Connect session
spark = SparkSession.builder.appName("Snowpark Connect").getOrCreate()
```

## Example Usage

After starting the session, you can create a toy dataframe and run some queries.

```python
from pyspark.sql import Row

df = spark.createDataFrame([
    Row(a=1, b=2.),
    Row(a=2, b=3.),
    Row(a=4, b=5.),
])

df.show()
```

`df.show()` will print the following output:

```
-------------
|"a"  |"b"  |
-------------
|1    |2.0  |
|2    |3.0  |
|4    |5.0  |
-------------
```

This will be slightly different from the Snowpark output, but that is intentional and expected.

From here, you can run dataframe queries and monitor the Snowpark Connect server output as well as the
client output.

## Dogfooding

Dogfooding is basically a two-step dance to install the snowpark-connect python package and then either use the provided `snowpark-submit` script if you intend to run an PySpark script or add a few lines of python to connect to Snowflake for Jupyter Notebook use cases.

### Run a PySpark script

1. (Optional) Create a Conda environment to test drive Snowpark Connect

```commandline
conda create -n xxxx pip python=3.11
conda activate xxxx
```

2. Install the snowpark-connect package (download from [here](https://drive.google.com/drive/folders/1sOp9wj5FqTLmbU4nxRKqGH_oiwA_ItAu)). Replace X.Y.Z with the version number on the downloaded whl file.

```commandline
pip install --force-reinstall snowpark-connect-X.Y.Z-py3-none-any.whl
```

3. Run your PySpark script (plenty of examples from [here](https://github.com/spark-examples/pyspark-examples))

```commandline
snowpark-submit your_pyspark_script
```

4. (Optional) Remove the Conda environment

```commandline
conda deactivate
conda env remove -n xxxx
```

### Jupyter Notebook

1. (Optional) Set up your Snowflake connection at .snowflake/connections.toml, only if you need to read/write to Snowflake.
2. Install the snowpark-connect package in your Jupyter environment (download from [here](https://drive.google.com/drive/folders/1sOp9wj5FqTLmbU4nxRKqGH_oiwA_ItAu)). Replace X.Y.Z with the version number on the downloaded whl file.

```commandline
pip install --force-reinstall snowpark-connect-X.Y.Z-py3-none-any.whl
```

3. Add the following lines at the beginning of your Notebook

```python
import os
import snowflake.snowpark_connect


os.environ["SPARK_CONNECT_MODE_ENABLED"] = "1"
os.environ["SPARK_REMOTE"] = "sc://localhost:15002"
snowflake.snowpark_connect.start_session(remote_url="sc://localhost:15002")  # Start the local Snowpark Connect server

spark = SparkSession.builder.appName("Snowpark Connect").getOrCreate()
```

4. If you hit this error:

```commandline
RuntimeError: Snowpark Connect Server is already running at localhost:15002
```

You can run these commands to kill the process and re-execute your Notebook

```commandline
lsof -i :15002
kill <PID>
```

### Snowflake Notebook

Pending GS/XP 9.0 release, ETA January 8th, 2025

## Run Pytest

We need to copy the pyspark.sql.tests folder because pyspark does not come with the test files.

```bash
git clone git@github.com:apache/spark.git
pushd spark && git checkout v3.5.3 && popd
cp -r spark/python/pyspark/sql/tests sas/.venv/lib/python3.11/site-packages/pyspark/sql/
mkdir -p sas/python/test_support/sql
cp -r spark/python/test_support/sql/ sas/python/test_support/sql/
```

Then run

```bash
python -m pytest tests/spark_tests/test_dataframe.py
```

As of Oct. 30, 2024, this test gives `32 passed, 11 skipped, 19 xfailed`

## Run Expectation Tests

Run all expectation tests:

```bash
python -m pytest tests/expectation_tests
```

Run one specific expectation test (this command can also be used in IDE to debug a single test):

```bash
# run Dataframe.limit.test
python -m pytest tests/expectation_tests -k "limit"
```

Update the expectation of a test:

```bash
# run Dataframe.limit.test and update the expectation
python -m pytest tests/expectation_tests -k "limit" --update-expectations
```

Disable a test: rename the test file from `xxx.test` to `xxx.test.disabled`.

See a more detailed writeup in `tests/expectation_tests/README.md`.

### Semantic compatibility

When adding new expectation tests, remember to document the semantic compatibility details as follows:

1. Add an entry to the `SEMANTIC COMPATIBILITY` section with these required fields:
```
type = "D2"                                                     # Compatibility type
function = "DataFrame.join"                                     # API being tested
notes = "Self joins not supported in Snowpark Connect mode"     # Explanation for the discrepancy. Not required for D0.
```

For cases where multiple APIs must be tested together (though this is not recommended), use the `functions` field instead of `function`:
```
functions = ["api_1", "api_2", "api_x"]
```

To extend the compatibility section with AI ratings and suggestions, run:
```bash
pip install snowflake-ml-python # this is excluded in dev requirements

python3 tools/exp_tests_tool.py --update-coverage-in-compatibility --tests <your_test_name>
```

This section is a source for the coverage and compatibility tracking sheet, which can be generated using the following command:
```bash
 python3 tools/exp_tests_tool.py --compatibility-report > compatibility.csv
```

## Manage Test Env With Tox

Our test environment setup is defined in `tox.ini`. GitHub Action uses tox to run the merge gates.
To run it locally:

```commandline
tox
```

## Generating Protobuf Files

To generate the protobuf files, run the following command from the project root directory:

```bash
./generate_proto.sh
```

This will create `.py` and `.pyi` files in the `snowflake_connect_server/proto` directory.

## Scala Examples

To run the Scala examples in `examples/`, run the following:

```bash
brew install Virtuslab/scala-cli/scala-cli
```

Then run any of the `*.sc` scripts.


## TCM 

### Parameters Setup
Set parameters needed for TCM:
``` 
alter account <PRPR_ACCOUNT_NAME> set
    ENABLE_NOTEBOOK=True,
    ENABLE_1641722_RECONNECT_THROUGH_GS=True,
    ENABLE_NOTEBOOK_MEMORY_SIZE_LIMIT=False,
    ENABLE_SNOWAPI=True,
    ENABLE_SNOW_API_FOR_SPARK_CONNECT='enable',
    ENABLE_SNOWPARK_DATAFRAME_EXECUTION='DISABLE',
    ENABLE_SPARK_CONNECT_DATAFRAME_EXECUTION=True,
    ENABLE_STRUCTURED_TYPES_IN_CLIENT_RESPONSE=True,
    IGNORE_CLIENT_VESRION_IN_STRUCTURED_TYPES_RESPONSE=True,
    FORCE_ENABLE_STRUCTURED_TYPES_NATIVE_ARROW_FORMAT=True,
    ENABLE_NOTEBOOK_PUBLIC_RUNTIME_ENVIRONMENT=true,
parameter_comment='enable snowpark connect parameters';

```
### Run pyspark on client environment.
Create a python environment on your machine (we support python >= 3.10) and start python
```
python3.10 -m venv myenv
source myenv/bin/activate
pip install "pyspark[connect]>=3.5.0,<4" "snowflake-connector-python>=3.12.0"
python
```
### TCM Example Usage
```python
import snowflake.connector
import urllib.parse

from pyspark.sql import SparkSession

# Taking "preprod12" as an example, first use snowflake-connector-python to start a session and get the token
DEPLOYMENT = "preprod12" # replace to your deployment name
ACCOUNT = "test_dataframe" # replace to your account name
# Get Spark connect host using SYSTEM$ALLOWLIST and  replace below to your spark connect host
# https://docs.google.com/document/d/14MMOpinYvySFHG7zAtS1fXt77Rq2_xPIZyTM8-kmuyA/edit?tab=t.0#heading=h.sojns4ey6wfz 
SPARK_CONNECT_HOST = "snowpark.pdx0ada.snowflakecomputing.com:443" 

conn = snowflake.connector.connect(connection_name=DEPLOYMENT)
token = conn.rest.token
url_safe_token = urllib.parse.quote(token, safe="")

# Create a spark session, note it can take ~ 1 minute for the first time to initialize the spark environment on the warehouse. Please be patient. 
spark = SparkSession.builder.remote(f"sc://{ACCOUNT}.{SPARK_CONNECT_HOST}/;token={url_safe_token}").getOrCreate()

# Now you can run spark command, e.g., 
spark.sql("select 1").show()
```
