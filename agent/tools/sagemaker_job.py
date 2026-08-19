"""
sagemaker_job.py
================
Tool for the Agentic AI Assistant: trigger SageMaker jobs or invoke
endpoints and surface quick status/results.

Prerequisites
-------------
pip install boto3==1.34.78
AWS credentials configured via env vars or IAM role.

Environment Variables (CI/local)
--------------------------------
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION
"""


import boto3

sm_client = boto3.client("sagemaker")
runtime   = boto3.client("sagemaker-runtime")

# ------------------------------------------------------------------ #
# Batch-Transform helper
# ------------------------------------------------------------------ #
def start_batch_transform(job_name: str,
                          model_name: str,
                          input_s3: str,
                          output_s3: str,
                          instance_type: str = "ml.m5.xlarge",
                          instance_count: int = 1) -> str:
    """
    Kick off a batch-transform job and return the ARN.
    """
    response = sm_client.create_transform_job(
        TransformJobName=job_name,
        ModelName=model_name,
        TransformInput={
            "DataSource": {"S3DataSource": {"S3Uri": input_s3, "S3DataType": "S3Prefix"}},
            "ContentType": "text/csv"
        },
        TransformOutput={"S3OutputPath": output_s3},
        TransformResources={
            "InstanceType": instance_type,
            "InstanceCount": instance_count
        }
    )
    return response["TransformJobArn"]

def get_batch_status(job_name: str) -> dict:
    """Return status dict for batch job."""
    return sm_client.describe_transform_job(TransformJobName=job_name)

# ------------------------------------------------------------------ #
# Real-time endpoint helper
# ------------------------------------------------------------------ #
def invoke_endpoint(endpoint_name: str, payload: str) -> str:
    """
    Invoke a JSON endpoint and return stringified result.
    """
    response = runtime.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType="application/json",
        Body=payload.encode("utf-8")
    )
    return response["Body"].read().decode()

# Quick CLI test (comment out unless creds + endpoint configured)
# if __name__ == "__main__":
#     print(invoke_endpoint("my-demo-endpoint", json.dumps({"data": [1,2,3]})))
