# IFClient-Python

A command-line tool to validate, merge, plan, and apply configuration files for InsightFinder projects.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your-username/ifclient.git
   cd ifclient
   ```

2. **Install Dependencies:**

   Using [Poetry](https://python-poetry.org/):

   ```bash
   poetry install
   ```

   Or install in editable mode with pip:

   ```bash
   pip install -e .
   ```

3. **Set Up a Virtual Environment (optional but recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

## Configuration File Structure

Your configuration files are organized hierarchically. A typical structure is like this but you not mandatory:

```
/config
|-- tool_config.yaml                # Base tool configuration
|-- /projects
|    |-- base1.yaml           # Project base configuration
|    |-- base2.yaml
|-- /instance-grouping-settings
|    |-- grouping-data-1.yaml
|    |-- grouping-data-2.yaml
|-- /component-metric-settings
     |-- metric-setting-1.yaml
     |-- metric-setting-2.yaml

```

You can find examples for all of these in the docs/examples folder in the repository. These files can be used as a starting point.
The files are organised in the same way as show above. As mentiond before this is a recommonded but not a mandatory structure of organizing


### Sample `config.yaml`

```yaml
apiVersion: v1       # Configuration version 
type: toolConfig     # Schema validation type 
baseUrl: "stg.insightfinder.com"   # Base URL for deployment

projectBaseConfigs:
  - /path/to/project-config.yaml # Can be absolute or relative paths
  - /path/to/base/*.yaml # Wildcards are allowed
```

### Sample Project Configuration (`base1.yaml`)

```yaml
apiVersion: v1
type: projectBase
user: "user1"
project: "project_name"
projectDisplayName: "Project-Display-Name"
cValue: 1
pValue: 0.95
showInstanceDown: false
retentionTime: 11
UBLRetentionTime: 11
instanceGroupingData:
  files:
    - "../instance-grouping-data/grouping-data-1.yaml" # All file paths must be relative to the current file
    - "../instance-grouping-data/grouping-data-2.yaml"
consumerMetricSettingOverallModelList:
  files:
    - "../consumer-metric-setting/metric-setting-*.yaml"
```

Sub-level configurations (for grouping or metric settings) follow similar conventions.

## Usage

The tool provides several commands:

- **validate:** Validate all provided configuration files.
- **generate:** Merge configurations into one output file.
- **apply:** Apply the merged configuration via API calls.

### Example Commands

```bash
# Validate configuration files in a directory
ifclient validate # Searches for all toolConfigs in current directory and recursively validates them
ifclient validate /path/to/configs # Validation with directory to search for all toolConfigs and apply validation recursively
ifclient validate /path/to/configs/config.yaml # Validation of any file and its subconfigs recursively(Need not be of type tool config)

# Generate a merged configuration file
ifclient generate /path/to/configs/config.yaml /path/to/outputs/output.yaml # Generate a yaml file as output with input of a toolConfig file

# Apply the merged configuration via API call
ifclient apply # Searches for all toolConfig files in current directory and recursively applies them
ifclient apply /path/to/configs # Searches for all toolConfig files in the specified directory and applies them recursively
ifclient apply /path/to/configs/config.yaml # Appies file and its subconfigs recursively
```

## Environment Variables

Before running the tool, ensure that sensitive passwords are available as environment variables. The naming convention should be:

```
ifusername_PASSWORD
```

For example, if your InsightFinder username is `jdoe`, set the environment variable:

```bash
export jdoe_PASSWORD=your_password_here
```