"""
VRAM Monitoring for SOLLOL - Real GPU memory tracking.
Supports NVIDIA (nvidia-smi), AMD (rocm-smi), and Intel GPUs.
"""

import subprocess
import json
import requests
from typing import Dict, List, Optional


class VRAMMonitor:
    """Monitor VRAM usage across local and remote Ollama nodes."""

    def __init__(self):
        self.gpu_type = self._detect_gpu_type()

    def _detect_gpu_type(self) -> str:
        """Detect which GPU vendor is available."""
        # Check NVIDIA
        try:
            result = subprocess.run(
                ["nvidia-smi", "--version"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                return "nvidia"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Check AMD ROCm
        try:
            result = subprocess.run(
                ["rocm-smi", "--version"], capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                return "amd"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Check Intel
        try:
            result = subprocess.run(
                ["intel_gpu_top", "-h"], capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                return "intel"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return "none"

    def get_local_vram_info(self) -> Optional[Dict]:
        """Get local GPU VRAM information."""
        if self.gpu_type == "nvidia":
            return self._get_nvidia_vram()
        elif self.gpu_type == "amd":
            return self._get_amd_vram()
        elif self.gpu_type == "intel":
            return self._get_intel_vram()
        return None

    def _get_nvidia_vram(self) -> Optional[Dict]:
        """Get NVIDIA GPU VRAM information using nvidia-smi."""
        try:
            cmd = [
                "nvidia-smi",
                "--query-gpu=index,name,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu",
                "--format=csv,noheader,nounits",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

            if result.returncode != 0:
                return None

            gpus = []
            for line in result.stdout.strip().split("\n"):
                if not line.strip():
                    continue

                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 7:
                    gpus.append(
                        {
                            "index": int(parts[0]),
                            "name": parts[1],
                            "total_mb": int(parts[2]),
                            "used_mb": int(parts[3]),
                            "free_mb": int(parts[4]),
                            "utilization_percent": int(parts[5]),
                            "temperature_c": (
                                int(parts[6]) if parts[6].isdigit() else None
                            ),
                            "vendor": "NVIDIA",
                        }
                    )

            return {
                "vendor": "NVIDIA",
                "gpus": gpus,
                "total_vram_mb": sum(g["total_mb"] for g in gpus),
                "used_vram_mb": sum(g["used_mb"] for g in gpus),
                "free_vram_mb": sum(g["free_mb"] for g in gpus),
            }

        except Exception:
            return None

    def _get_amd_vram(self) -> Optional[Dict]:
        """Get AMD GPU VRAM information using rocm-smi."""
        try:
            result = subprocess.run(
                ["rocm-smi", "--showmeminfo", "vram", "--json"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                return None

            data = json.loads(result.stdout)
            gpus = []

            for gpu_id, gpu_data in data.items():
                if gpu_id.startswith("card"):
                    vram_used_mb = (
                        gpu_data.get("VRAM Total Used Memory (B)", 0) / (1024**2)
                    )
                    vram_total_mb = (
                        gpu_data.get("VRAM Total Memory (B)", 0) / (1024**2)
                    )

                    gpus.append(
                        {
                            "index": int(gpu_id.replace("card", "")),
                            "name": gpu_data.get("GPU Name", "AMD GPU"),
                            "total_mb": int(vram_total_mb),
                            "used_mb": int(vram_used_mb),
                            "free_mb": int(vram_total_mb - vram_used_mb),
                            "utilization_percent": None,
                            "temperature_c": None,
                            "vendor": "AMD",
                        }
                    )

            return {
                "vendor": "AMD",
                "gpus": gpus,
                "total_vram_mb": sum(g["total_mb"] for g in gpus),
                "used_vram_mb": sum(g["used_mb"] for g in gpus),
                "free_vram_mb": sum(g["free_mb"] for g in gpus),
            }

        except Exception:
            return None

    def _get_intel_vram(self) -> Optional[Dict]:
        """Get Intel GPU information (limited VRAM reporting)."""
        # Intel integrated GPUs share system RAM, limited monitoring available
        return {
            "vendor": "Intel",
            "gpus": [
                {
                    "index": 0,
                    "name": "Intel GPU",
                    "total_mb": None,  # Uses system RAM
                    "used_mb": None,
                    "free_mb": None,
                    "utilization_percent": None,
                    "temperature_c": None,
                    "vendor": "Intel",
                }
            ],
        }

    def get_ollama_vram_usage(self, node_url: str) -> Optional[Dict]:
        """
        Get VRAM usage from Ollama API /api/ps endpoint.
        Returns actual VRAM usage for loaded models.
        """
        try:
            response = requests.get(f"{node_url}/api/ps", timeout=5)
            if response.status_code != 200:
                return None

            ps_data = response.json()
            models = ps_data.get("models", [])

            total_vram_bytes = 0
            total_ram_bytes = 0
            model_details = []

            for model_info in models:
                model_name = model_info.get("name", "unknown")
                size_vram = model_info.get("size_vram", 0)  # Bytes in VRAM
                size_total = model_info.get("size", 0)  # Total model size

                if size_vram > 0:
                    total_vram_bytes += size_vram
                    location = "VRAM (GPU)"
                else:
                    total_ram_bytes += size_total
                    location = "RAM (CPU)"

                model_details.append(
                    {
                        "name": model_name,
                        "size_mb": size_total / (1024**2),
                        "vram_mb": size_vram / (1024**2),
                        "location": location,
                    }
                )

            return {
                "node_url": node_url,
                "total_vram_mb": total_vram_bytes / (1024**2),
                "total_ram_mb": total_ram_bytes / (1024**2),
                "models": model_details,
                "has_gpu_models": total_vram_bytes > 0,
            }

        except Exception:
            return None

    def get_comprehensive_report(
        self, node_url: str = "http://localhost:11434"
    ) -> Dict:
        """
        Get comprehensive VRAM report combining local GPU info and Ollama usage.
        """
        import datetime

        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "local_gpu": None,
            "ollama_usage": None,
            "summary": {},
        }

        # Get local GPU info
        local_info = self.get_local_vram_info()
        if local_info:
            report["local_gpu"] = local_info

        # Get Ollama usage
        ollama_info = self.get_ollama_vram_usage(node_url)
        if ollama_info:
            report["ollama_usage"] = ollama_info

        # Generate summary
        if local_info and ollama_info:
            report["summary"] = {
                "gpu_vendor": local_info.get("vendor"),
                "total_vram_mb": local_info.get("total_vram_mb", 0),
                "ollama_using_vram_mb": ollama_info.get("total_vram_mb", 0),
                "ollama_using_ram_mb": ollama_info.get("total_ram_mb", 0),
                "free_vram_mb": local_info.get("free_vram_mb", 0),
                "vram_utilization_percent": (
                    (
                        local_info.get("used_vram_mb", 0)
                        / local_info.get("total_vram_mb", 1)
                    )
                    * 100
                    if local_info.get("total_vram_mb", 0) > 0
                    else 0
                ),
                "ollama_gpu_accelerated": ollama_info.get("has_gpu_models", False),
            }

        return report


def monitor_distributed_nodes(node_urls: List[str]) -> Dict[str, Dict]:
    """
    Monitor VRAM usage across multiple distributed nodes.
    """
    monitor = VRAMMonitor()
    results = {}

    for node_url in node_urls:
        try:
            ollama_usage = monitor.get_ollama_vram_usage(node_url)
            if ollama_usage:
                results[node_url] = {
                    "status": "online",
                    "vram_mb": ollama_usage.get("total_vram_mb", 0),
                    "ram_mb": ollama_usage.get("total_ram_mb", 0),
                    "gpu_accelerated": ollama_usage.get("has_gpu_models", False),
                    "models": ollama_usage.get("models", []),
                }
            else:
                results[node_url] = {"status": "error", "error": "Failed to get VRAM info"}
        except Exception as e:
            results[node_url] = {"status": "error", "error": str(e)}

    return results
