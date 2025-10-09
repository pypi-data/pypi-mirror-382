"""ECR (Elastic Container Registry) service integration."""

import base64

import boto3

from ..utils.runtime.container import ContainerRuntime


def get_account_id() -> str:
    """Get AWS account ID."""
    return boto3.client("sts").get_caller_identity()["Account"]


def get_region() -> str:
    """Get AWS region."""
    return boto3.Session().region_name or "us-west-2"


def create_ecr_repository(repo_name: str, region: str) -> str:
    """Create or get existing ECR repository."""
    ecr = boto3.client("ecr", region_name=region)
    try:
        response = ecr.create_repository(repositoryName=repo_name)
        return response["repository"]["repositoryUri"]
    except ecr.exceptions.RepositoryAlreadyExistsException:
        response = ecr.describe_repositories(repositoryNames=[repo_name])
        return response["repositories"][0]["repositoryUri"]


def get_or_create_ecr_repository(agent_name: str, region: str) -> str:
    """Get existing ECR repository or create a new one (idempotent).

    Args:
        agent_name: Name of the agent
        region: AWS region

    Returns:
        ECR repository URI
    """
    # Generate deterministic repository name based on agent name
    repo_name = f"bedrock-agentcore-{agent_name}"

    ecr = boto3.client("ecr", region_name=region)

    try:
        # Step 1: Check if repository already exists
        response = ecr.describe_repositories(repositoryNames=[repo_name])
        existing_repo_uri = response["repositories"][0]["repositoryUri"]

        print(f"✅ Reusing existing ECR repository: {existing_repo_uri}")
        return existing_repo_uri

    except ecr.exceptions.RepositoryNotFoundException:
        # Step 2: Repository doesn't exist, create it
        print(f"Repository doesn't exist, creating new ECR repository: {repo_name}")
        return create_ecr_repository(repo_name, region)


def deploy_to_ecr(local_tag: str, repo_name: str, region: str, container_runtime: ContainerRuntime) -> str:
    """Build and push image to ECR."""
    ecr = boto3.client("ecr", region_name=region)

    # Get or create repository
    ecr_uri = create_ecr_repository(repo_name, region)

    # Get auth token
    auth_data = ecr.get_authorization_token()["authorizationData"][0]
    token = base64.b64decode(auth_data["authorizationToken"]).decode("utf-8")
    username, password = token.split(":")

    # Login to ECR
    if not container_runtime.login(auth_data["proxyEndpoint"], username, password):
        raise RuntimeError("Failed to login to ECR")

    # Tag and push
    ecr_tag = f"{ecr_uri}:latest"
    if not container_runtime.tag(local_tag, ecr_tag):
        raise RuntimeError("Failed to tag image")

    if not container_runtime.push(ecr_tag):
        raise RuntimeError("Failed to push image to ECR")

    return ecr_tag
