"""API client for pdtrain"""

import requests
from typing import Dict, Any, Optional, List
from pathlib import Path


class APIClient:
    """Client for Pipedream Training Orchestrator API"""

    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{self.api_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else {}

    # Auth
    def validate_key(self) -> Dict[str, Any]:
        """Validate API key"""
        return self._request("GET", "/v1/auth/validate")

    # Bundles
    def presign_bundle(self, filename: str, content_type: str = "application/gzip") -> Dict[str, Any]:
        """Get presigned URL for bundle upload"""
        return self._request("POST", "/v1/storage/presign", json={
            "operation": "put_object",
            "path": f"bundles/{filename}",
            "content_type": content_type,
            "expires_in": 3600,
        })

    def upload_bundle(self, presigned_url: str, file_path: Path, content_type: str) -> None:
        """Upload bundle to S3"""
        with open(file_path, "rb") as f:
            response = requests.put(presigned_url, data=f, headers={"Content-Type": content_type})
            response.raise_for_status()

    def finalize_bundle(self, s3_key: str) -> Dict[str, Any]:
        """Finalize bundle after upload"""
        return self._request("POST", "/v1/bundles/finalize", json={"s3_key": s3_key})

    def list_bundles(self) -> List[Dict[str, Any]]:
        """List all bundles"""
        return self._request("GET", "/v1/bundles/")

    def get_bundle(self, bundle_id: str) -> Dict[str, Any]:
        """Get bundle details"""
        return self._request("GET", f"/v1/bundles/{bundle_id}")

    def get_bundle_by_name(self, name: str, version: Optional[str] = None) -> Dict[str, Any]:
        """Get bundle by name and version"""
        endpoint = f"/v1/bundles/by-name/{name}"
        if version:
            endpoint += f"?version={version}"
        return self._request("GET", endpoint)

    # Datasets
    def presign_dataset(self, dataset_name: str, files: List[Dict[str, Any]], dataset_id: Optional[str] = None, version: Optional[int] = None) -> Dict[str, Any]:
        """Get presigned URLs for dataset upload"""
        payload = {
            "dataset_name": dataset_name,
            "files": files,
        }
        if dataset_id:
            payload["dataset_id"] = dataset_id
        if version:
            payload["version"] = version
        return self._request("POST", "/v1/datasets/presign", json=payload)

    def finalize_dataset(self, dataset_id: str, version: int, size_bytes: int, num_files: int, set_current: bool = True) -> Dict[str, Any]:
        """Finalize dataset after upload"""
        return self._request("POST", "/v1/datasets/finalize", json={
            "dataset_id": dataset_id,
            "version": version,
            "size_bytes": size_bytes,
            "num_files": num_files,
            "set_current": set_current,
        })

    def list_datasets(self, limit: int = 50, offset: int = 0, name: Optional[str] = None) -> Dict[str, Any]:
        """List datasets"""
        params = {"limit": limit, "offset": offset}
        if name:
            params["name"] = name
        return self._request("GET", "/v1/datasets/", params=params)

    def get_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """Get dataset details"""
        return self._request("GET", f"/v1/datasets/{dataset_id}")

    def get_dataset_version(self, dataset_id: str, version: int) -> Dict[str, Any]:
        """Get dataset version details"""
        return self._request("GET", f"/v1/datasets/{dataset_id}/versions/{version}")

    def download_dataset(self, dataset_id: str, version: int, expires_in: int = 3600) -> Dict[str, Any]:
        """Get download URLs for dataset"""
        return self._request("GET", f"/v1/datasets/{dataset_id}/versions/{version}/download", params={"expires_in": expires_in})

    def delete_dataset(self, dataset_id: str) -> None:
        """Delete entire dataset"""
        self._request("DELETE", f"/v1/datasets/{dataset_id}")

    # Runs
    def create_run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create training run"""
        return self._request("POST", "/v1/runs", json=payload)

    def submit_run(self, run_id: str) -> Dict[str, Any]:
        """Submit run to SageMaker"""
        return self._request("POST", f"/v1/runs/{run_id}/submit")

    def get_run(self, run_id: str) -> Dict[str, Any]:
        """Get run details"""
        return self._request("GET", f"/v1/runs/{run_id}")

    def list_runs(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List runs"""
        return self._request("GET", "/v1/runs", params={"limit": limit, "offset": offset})

    def stop_run(self, run_id: str) -> Dict[str, Any]:
        """Stop a running job"""
        return self._request("POST", f"/v1/runs/{run_id}/stop")

    def refresh_run(self, run_id: str) -> Dict[str, Any]:
        """Refresh run status from SageMaker"""
        return self._request("POST", f"/v1/runs/{run_id}/refresh")

    # Logs
    def get_logs(self, run_id: str, limit: int = 300, all_streams: bool = False) -> Dict[str, Any]:
        """Get training logs"""
        return self._request("GET", f"/v1/runs/{run_id}/logs", params={"limit": limit, "all_streams": all_streams})

    def stream_logs(self, run_id: str):
        """Stream training logs using SSE"""
        url = f"{self.api_url}/v1/runs/{run_id}/logs/stream"
        response = self.session.get(url, stream=True, headers={
            "Accept": "text/event-stream",
            "Authorization": f"Bearer {self.api_key}",
        })
        response.raise_for_status()
        return response

    # Artifacts
    def get_artifacts(self, run_id: str) -> Dict[str, Any]:
        """Get run artifacts"""
        return self._request("GET", f"/v1/runs/{run_id}/artifacts")

    def list_artifacts(self, run_id: str) -> Dict[str, Any]:
        """List run artifacts (alias for get_artifacts)"""
        return self.get_artifacts(run_id)

    # Storage
    def get_quota(self) -> Dict[str, Any]:
        """Get storage quota information"""
        return self._request("GET", "/v1/storage/quota")

    # Wallet
    def get_wallet_balance(self) -> Dict[str, Any]:
        """Get wallet balance"""
        return self._request("GET", "/v1/wallet/balance")

    def get_wallet_transactions(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get wallet transaction history"""
        return self._request("GET", "/v1/wallet/transactions", params={"limit": limit, "offset": offset})

    def estimate_job_cost(self, instance_type: str, max_runtime_seconds: int, region: str = "us-east-1") -> Dict[str, Any]:
        """Estimate training job cost"""
        return self._request("POST", "/v1/wallet/estimate-cost", json={
            "instance_type": instance_type,
            "max_runtime_seconds": max_runtime_seconds,
            "region": region
        })

    def get_instance_pricing(self, region: str = "us-east-1") -> Dict[str, Any]:
        """Get instance pricing for a region"""
        return self._request("GET", "/v1/wallet/pricing/instances", params={"region": region})

    def compare_instance_costs(self, instance_types: List[str], runtime_seconds: int = 3600, region: str = "us-east-1") -> Dict[str, Any]:
        """Compare costs across instance types"""
        return self._request("GET", "/v1/wallet/pricing/compare", params={
            "instance_types": ",".join(instance_types),
            "runtime_seconds": runtime_seconds,
            "region": region
        })

    # Plan
    def get_plan_information(self) -> Dict[str, Any]:
        """Get comprehensive plan information"""
        return self._request("GET", "/v1/plans/information")

    def get_plan_limits(self) -> Dict[str, Any]:
        """Get plan limits summary"""
        return self._request("GET", "/v1/plans/limits")

    def get_plan_entitlements(self) -> Dict[str, Any]:
        """Get plan entitlements"""
        return self._request("GET", "/v1/plans/entitlements")

    def get_plan_usage_summary(self) -> Dict[str, Any]:
        """Get plan usage summary"""
        return self._request("GET", "/v1/plans/usage-summary")

    def get_plan_storage_quota(self) -> Dict[str, Any]:
        """Get plan storage quota"""
        return self._request("GET", "/v1/plans/storage-quota")
