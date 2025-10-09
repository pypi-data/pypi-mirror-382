import csv
import json
from io import StringIO

import alchemite_apiclient as client
from alchemite_apiclient.extensions import Configuration, await_job, await_trained

configuration = Configuration()
api_default = client.DefaultApi(client.ApiClient(configuration))
api_models = client.ModelsApi(client.ApiClient(configuration))
api_datasets = client.DatasetsApi(client.ApiClient(configuration))

### Provide path to the JSON containing your credentials
configuration.credentials = "credentials.json"

OPTIMIZE_DATASET = "steels"  # 'steels' or 'steels dependent columns'

if OPTIMIZE_DATASET == "steels":
    dataset_file = "steels.csv"
    dataset_name = "steels"
    model_name = "steels"
    optimize_args = "optimize_args_steel.json"
elif OPTIMIZE_DATASET == "steels dependent columns":
    dataset_file = "steels.csv"
    dataset_name = "steels"
    model_name = "steels"
    optimize_args = "optimize_dependentColumns_args_steel.json"
else:
    raise Exception("Invalid optimize dataset option")

# Check we can access the API by getting the version number from GET /version
api_response = api_default.version_get()
print("------ API & Python Client Versions ------")
print(api_response)
print(
    f"Python client version: {client.__version__} (latest: {api_response['api_definition_version']})"
)
print("------------------------------------------")

############################################################################
### Upload a dataset
############################################################################
with open(dataset_file, "r", encoding="UTF-8") as file:
    data = file.read()
    reader = csv.reader(StringIO(data), delimiter=",")
    rows = [row for row in reader]
    row_count = len(rows) - 1
    column_headers = list(map(lambda x: str.strip(x), rows[0][1:]))

dataset = {
    "name": dataset_name,
    "row_count": row_count,  # Number of rows (not including column headers)
    "column_headers": column_headers,
    # No descriptors in this dataset so list of zeros
    "descriptor_columns": [0] * len(column_headers),
    "data": data,
}
dataset_id = api_datasets.datasets_post(dataset=dataset)
print("dataset ID:", dataset_id)

############################################################################
### Get the metadata about this dataset
############################################################################
dataset_metadata = api_datasets.datasets_id_get(dataset_id)
print("\n--- dataset metadata ---")
print(dataset_metadata)

############################################################################
### Create a model from this dataset
############################################################################
# POST the model
model = {
    "name": model_name,
    "training_method": "alchemite",
    "training_dataset_id": dataset_id,
}
model_id = api_models.models_post(model=model)
print("model ID:", model_id)

############################################################################
### Start training the model
############################################################################
train_request = {
    "validation": "none",
    "hyperparameter_optimization": "none",
}
response = api_models.models_id_train_put(model_id, train_request=train_request)
print(response)
model = await_trained(lambda: api_models.models_id_get(model_id))

############################################################################
### Get the model metadata
############################################################################
model = api_models.models_id_get(model_id)
print("\n--- model metadata ---")
print(model)

training_column_headers = model.training_column_headers

############################################################################
### Print hyperparameters
############################################################################
print("\n--- Hyperparameters ---")
print(model.training_hyperparameters)

############################################################################
### Make an optimize request
############################################################################
print("\n--- Optimize ---")

# Get optimize input arguments
with open(optimize_args, encoding="UTF-8") as f:
    optimize_args = json.load(f)

# Send optimize request
optimize_job_id = api_models.models_id_optimize_post(model_id, **optimize_args)
print("Optimize job ID:", optimize_job_id)


# Wait until the optimize job has finished
def get_optimize_job_metadata():
    return api_models.models_id_optimize_job_id_get(model_id, job_id=optimize_job_id)


optimize_job = await_job(get_optimize_job_metadata)
print(json.dumps(optimize_job, indent=4))

############################################################################
### Delete model, dataset and optimize job
############################################################################
# print("\n--- deleting optimize job, model and dataset ---")
# response = api_models.models_id_optimize_optimize_job_id_delete(
#     model_id, optimize_job_id
# )
# print("deletion optimize job successful") if response is None else print(
#     response
# )
# api_models.models_id_delete(model_id)
# api_datasets.datasets_id_delete(dataset_id)
