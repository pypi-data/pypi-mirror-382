"""
SOLLOL Unified Dashboard - Integrates Ray, Dask, and SOLLOL metrics

Combines:
1. SOLLOL metrics (high-level overview)
2. Ray dashboard (task-level details, distributed tracing)
3. Dask dashboard (performance profiling)
4. Prometheus metrics export

Features:
- Embedded Ray dashboard iframe
- Embedded Dask dashboard iframe
- Real-time WebSocket updates (event-driven, not polling)
- Distributed tracing visualization
- Per-task resource monitoring
- Historical analytics (P50/P95/P99)
- Ollama model lifecycle tracking (load/unload/processing)
- llama.cpp coordinator monitoring
- Centralized logging queue
"""

import asyncio
import json
import logging
import os
import queue
import time
from collections import defaultdict, deque
from datetime import datetime
from logging import Handler
from typing import Any, Dict, List, Optional, Set

import ray
import requests
from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS
from flask_sock import Sock
from prometheus_client import Counter, Gauge, Histogram, generate_latest

logger = logging.getLogger(__name__)

# Centralized logging queue (SynapticLlamas pattern)
log_queue = queue.Queue()


class QueueLogHandler(Handler):
    """Custom logging handler to push logs into a queue for streaming."""

    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        log_entry = self.format(record)
        self.log_queue.put(log_entry)

# Prometheus metrics
request_counter = Counter(
    'sollol_requests_total',
    'Total requests processed',
    ['model', 'status', 'backend']
)

request_duration = Histogram(
    'sollol_request_duration_seconds',
    'Request duration in seconds',
    ['model', 'backend'],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]
)

active_pools = Gauge(
    'sollol_active_pools',
    'Number of active Ray pools'
)

gpu_utilization = Gauge(
    'sollol_gpu_utilization',
    'GPU utilization per node',
    ['node', 'gpu_id']
)


class UnifiedDashboard:
    """Unified dashboard integrating Ray, Dask, and SOLLOL metrics."""

    def __init__(
        self,
        router=None,
        ray_dashboard_port: int = 8265,
        dask_dashboard_port: int = 8787,
        dashboard_port: int = 8080,
        enable_dask: bool = False,
    ):
        """
        Initialize unified dashboard.

        Args:
            router: SOLLOL router (any type)
            ray_dashboard_port: Ray dashboard port
            dask_dashboard_port: Dask dashboard port
            dashboard_port: Unified dashboard port
            enable_dask: Enable Dask distributed client with dashboard
        """
        self.router = router
        self.ray_dashboard_port = ray_dashboard_port
        self.dask_dashboard_port = dask_dashboard_port
        self.dashboard_port = dashboard_port
        self.dask_client = None

        # Request history for analytics
        self.request_history = deque(maxlen=1000)
        self.trace_history = deque(maxlen=100)

        # Application registry (track which applications are using SOLLOL)
        self.applications: Dict[str, Dict[str, Any]] = {}
        self.application_timeout = 30  # seconds - consider app inactive if no heartbeat

        # Initialize Dask if requested
        if enable_dask:
            try:
                from dask.distributed import Client
                self.dask_client = Client()
                logger.info(f"📊 Dask client initialized - dashboard at http://localhost:{dask_dashboard_port}")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize Dask client: {e}")

        # Check Ray dashboard availability
        if ray.is_initialized():
            logger.info(f"📊 Ray is initialized - dashboard should be at http://localhost:{ray_dashboard_port}")
        else:
            logger.warning("⚠️  Ray is not initialized - Ray dashboard will not be available")

        # Flask app with WebSocket support
        self.app = Flask(__name__)
        CORS(self.app)
        self.sock = Sock(self.app)
        self._setup_routes()
        self._setup_websocket_routes()

        # Setup centralized logging
        self._setup_logging()

        logger.info(
            f"📊 Unified Dashboard initialized "
            f"(port {dashboard_port}, Ray: {ray_dashboard_port}, Dask: {dask_dashboard_port})"
        )
        logger.info("✨ WebSocket streaming enabled (event-driven monitoring)")

    def _setup_routes(self):
        """Setup Flask routes."""

        @self.app.route("/")
        def index():
            """Serve unified dashboard HTML."""
            return render_template_string(UNIFIED_DASHBOARD_HTML)

        @self.app.route("/api/metrics")
        def metrics():
            """Get SOLLOL metrics."""
            try:
                if self.router:
                    stats = asyncio.run(self.router.get_stats())
                else:
                    stats = {}

                # Add request history analytics
                stats["analytics"] = self._calculate_analytics()

                return jsonify(stats)
            except Exception as e:
                logger.error(f"Error getting metrics: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/network/nodes")
        def network_nodes():
            """Get all Ollama nodes in the network (universal)."""
            try:
                # Try to get from router's pool
                if self.router and hasattr(self.router, 'ollama_pool'):
                    pool = self.router.ollama_pool
                    nodes = []
                    for node in pool.nodes:
                        nodes.append({
                            "url": node.url,
                            "healthy": node.healthy,
                            "last_latency_ms": node.last_latency_ms,
                            "failure_count": node.failure_count,
                            "models": node.models,
                            "total_vram_mb": node.total_vram_mb,
                            "free_vram_mb": node.free_vram_mb,
                            "status": "healthy" if node.healthy else "unhealthy",
                        })
                    return jsonify({"nodes": nodes, "total": len(nodes)})
                else:
                    # Fallback: auto-discover nodes
                    from sollol.discovery import discover_ollama_nodes
                    discovered = discover_ollama_nodes()
                    return jsonify({"nodes": discovered, "total": len(discovered)})
            except Exception as e:
                logger.error(f"Error getting network nodes: {e}")
                return jsonify({"error": str(e), "nodes": []}), 500

        @self.app.route("/api/network/backends")
        def network_backends():
            """Get all RPC backends in the network (universal)."""
            try:
                backends = []

                # Try to get from router
                if self.router and hasattr(self.router, 'rpc_backends'):
                    for backend in self.router.rpc_backends:
                        backends.append({
                            "host": backend.get("host"),
                            "port": backend.get("port", 50052),
                            "status": "active",
                        })

                # Try to get from RPC registry
                try:
                    from sollol.rpc_registry import RPCBackendRegistry
                    registry = RPCBackendRegistry()
                    for backend in registry.list_backends():
                        backends.append({
                            "host": backend["host"],
                            "port": backend.get("port", 50052),
                            "status": backend.get("status", "unknown"),
                        })
                except:
                    pass

                return jsonify({"backends": backends, "total": len(backends)})
            except Exception as e:
                logger.error(f"Error getting RPC backends: {e}")
                return jsonify({"error": str(e), "backends": []}), 500

        @self.app.route("/api/network/health")
        def network_health():
            """Get overall network health (universal)."""
            try:
                health = {
                    "timestamp": time.time(),
                    "status": "unknown",
                    "nodes_total": 0,
                    "nodes_healthy": 0,
                    "backends_total": 0,
                    "backends_active": 0,
                }

                # Get node health
                try:
                    if self.router and hasattr(self.router, 'ollama_pool'):
                        pool = self.router.ollama_pool
                        health["nodes_total"] = len(pool.nodes)
                        health["nodes_healthy"] = sum(1 for n in pool.nodes if n.healthy)
                except:
                    pass

                # Get backend health
                try:
                    if self.router and hasattr(self.router, 'rpc_backends'):
                        health["backends_total"] = len(self.router.rpc_backends)
                        health["backends_active"] = len(self.router.rpc_backends)  # Assume active
                except:
                    pass

                # Determine overall status
                if health["nodes_healthy"] > 0 or health["backends_active"] > 0:
                    health["status"] = "healthy"
                else:
                    health["status"] = "degraded"

                return jsonify(health)
            except Exception as e:
                logger.error(f"Error getting network health: {e}")
                return jsonify({"error": str(e), "status": "error"}), 500

        @self.app.route("/api/traces")
        def traces():
            """Get distributed traces."""
            return jsonify(list(self.trace_history))

        @self.app.route("/api/ray/metrics")
        def ray_metrics():
            """Get Ray metrics."""
            try:
                if ray.is_initialized():
                    # Get Ray metrics
                    ray_stats = {
                        "dashboard_url": f"http://localhost:{self.ray_dashboard_port}",
                        "nodes": len(ray.nodes()),
                        "available_resources": ray.available_resources(),
                        "cluster_resources": ray.cluster_resources(),
                        "status": "active",
                    }
                    return jsonify(ray_stats)
                else:
                    return jsonify({"error": "Ray not initialized", "status": "inactive"}), 500
            except Exception as e:
                return jsonify({"error": str(e), "status": "error"}), 500

        @self.app.route("/api/dask/metrics")
        def dask_metrics():
            """Get Dask metrics."""
            try:
                if self.dask_client:
                    # Get Dask metrics
                    dask_stats = {
                        "dashboard_url": f"http://localhost:{self.dask_dashboard_port}",
                        "workers": len(self.dask_client.scheduler_info().get('workers', {})),
                        "status": "active",
                    }
                    return jsonify(dask_stats)
                else:
                    return jsonify({"error": "Dask not initialized", "status": "inactive"}), 500
            except Exception as e:
                return jsonify({"error": str(e), "status": "error"}), 500

        @self.app.route("/api/prometheus")
        def prometheus_metrics():
            """Prometheus metrics export."""
            return generate_latest()

        @self.app.route("/api/trace", methods=["POST"])
        def add_trace():
            """Add distributed trace."""
            trace_data = request.json
            trace_data["timestamp"] = datetime.utcnow().isoformat()
            self.trace_history.append(trace_data)
            return jsonify({"status": "ok"})

        @self.app.route("/api/applications")
        def applications():
            """Get all registered applications (universal)."""
            try:
                # Clean up stale applications first
                self._cleanup_stale_applications()

                # Return active applications
                apps = []
                for app_id, app_info in self.applications.items():
                    uptime = time.time() - app_info["start_time"]
                    last_seen = time.time() - app_info["last_heartbeat"]

                    apps.append({
                        "app_id": app_id,
                        "name": app_info["name"],
                        "router_type": app_info.get("router_type", "unknown"),
                        "version": app_info.get("version", "unknown"),
                        "start_time": app_info["start_time"],
                        "last_heartbeat": app_info["last_heartbeat"],
                        "uptime_seconds": int(uptime),
                        "last_seen_seconds": int(last_seen),
                        "status": "active" if last_seen < self.application_timeout else "stale",
                        "metadata": app_info.get("metadata", {}),
                    })

                return jsonify({
                    "applications": apps,
                    "total": len(apps),
                    "active": sum(1 for a in apps if a["status"] == "active"),
                })
            except Exception as e:
                logger.error(f"Error getting applications: {e}")
                return jsonify({"error": str(e), "applications": []}), 500

        @self.app.route("/api/applications/register", methods=["POST"])
        def register_application():
            """Register a new application with the dashboard."""
            try:
                data = request.json
                app_id = data.get("app_id")

                if not app_id:
                    return jsonify({"error": "app_id required"}), 400

                # Register or update application
                now = time.time()
                if app_id not in self.applications:
                    self.applications[app_id] = {
                        "app_id": app_id,
                        "name": data.get("name", "unknown"),
                        "router_type": data.get("router_type", "unknown"),
                        "version": data.get("version", "unknown"),
                        "start_time": now,
                        "last_heartbeat": now,
                        "metadata": data.get("metadata", {}),
                    }
                    logger.info(f"📱 Application registered: {data.get('name')} ({app_id})")
                else:
                    # Update existing
                    self.applications[app_id]["last_heartbeat"] = now
                    self.applications[app_id].update({
                        "name": data.get("name", self.applications[app_id]["name"]),
                        "router_type": data.get("router_type", self.applications[app_id]["router_type"]),
                        "version": data.get("version", self.applications[app_id]["version"]),
                        "metadata": data.get("metadata", self.applications[app_id].get("metadata", {})),
                    })

                return jsonify({"status": "ok", "app_id": app_id})
            except Exception as e:
                logger.error(f"Error registering application: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/applications/heartbeat", methods=["POST"])
        def application_heartbeat():
            """Receive heartbeat from application to keep it active."""
            try:
                data = request.json
                app_id = data.get("app_id")

                if not app_id or app_id not in self.applications:
                    return jsonify({"error": "app_id not registered"}), 404

                # Update heartbeat
                self.applications[app_id]["last_heartbeat"] = time.time()

                # Update metadata if provided
                if "metadata" in data:
                    self.applications[app_id]["metadata"].update(data["metadata"])

                return jsonify({"status": "ok"})
            except Exception as e:
                logger.error(f"Error processing heartbeat: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/applications/<app_id>/unregister", methods=["POST"])
        def unregister_application(app_id):
            """Explicitly unregister an application."""
            try:
                if app_id in self.applications:
                    app_name = self.applications[app_id].get("name", app_id)
                    del self.applications[app_id]
                    logger.info(f"📱 Application unregistered: {app_name} ({app_id})")
                    return jsonify({"status": "ok"})
                else:
                    return jsonify({"error": "app_id not found"}), 404
            except Exception as e:
                logger.error(f"Error unregistering application: {e}")
                return jsonify({"error": str(e)}), 500

    def _setup_logging(self):
        """Setup centralized logging queue."""
        # Add queue handler to root logger
        log_handler = QueueLogHandler(log_queue)
        log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_handler.setFormatter(log_formatter)

        root_logger = logging.getLogger()
        root_logger.addHandler(log_handler)

        logger.info("📝 Centralized logging queue initialized")

    def _setup_websocket_routes(self):
        """Setup WebSocket routes for real-time streaming."""

        @self.sock.route('/ws/logs')
        def ws_logs(ws):
            """WebSocket endpoint for streaming logs."""
            logger.info("🔌 Log streaming WebSocket connected")
            while True:
                try:
                    log_entry = log_queue.get(timeout=1)
                    ws.send(log_entry)
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.warning(f"Log streaming disconnected: {e}")
                    break

        @self.sock.route('/ws/network/nodes')
        def ws_network_nodes(ws):
            """WebSocket endpoint for streaming node state changes (event-driven)."""
            logger.info("🔌 Network nodes WebSocket connected")
            previous_state = {}

            while True:
                try:
                    # Get current nodes (router-agnostic - uses fallback discovery)
                    if self.router and hasattr(self.router, 'ollama_pool'):
                        pool = self.router.ollama_pool
                        nodes = []
                        for node in pool.nodes:
                            node_key = node.url
                            nodes.append({
                                "url": node.url,
                                "healthy": node.healthy,
                                "latency_ms": node.last_latency_ms,
                                "failure_count": node.failure_count,
                                "status": "healthy" if node.healthy else "unhealthy",
                            })
                    else:
                        # Fallback: auto-discover
                        from sollol.discovery import discover_ollama_nodes
                        discovered = discover_ollama_nodes()
                        nodes = [{"url": f"http://{n['host']}:{n['port']}", "status": "discovered"} for n in discovered]

                    # Event-driven change detection (SynapticLlamas pattern)
                    events = []
                    for node in nodes:
                        node_url = node["url"]
                        current_status = node.get("status", "unknown")
                        previous_status = previous_state.get(node_url, {}).get("status")

                        # Detect status change
                        if previous_status and current_status != previous_status:
                            events.append({
                                "type": "status_change",
                                "timestamp": time.time(),
                                "node": node_url,
                                "old_status": previous_status,
                                "new_status": current_status,
                                "message": f"Node {node_url}: {previous_status} → {current_status}"
                            })

                        # Detect new node
                        if node_url not in previous_state:
                            events.append({
                                "type": "node_discovered",
                                "timestamp": time.time(),
                                "node": node_url,
                                "message": f"✅ New node discovered: {node_url}"
                            })

                        previous_state[node_url] = node

                    # Detect removed nodes
                    current_urls = {n["url"] for n in nodes}
                    removed = set(previous_state.keys()) - current_urls
                    for node_url in removed:
                        events.append({
                            "type": "node_removed",
                            "timestamp": time.time(),
                            "node": node_url,
                            "message": f"❌ Node removed: {node_url}"
                        })
                        del previous_state[node_url]

                    # Send events
                    for event in events:
                        ws.send(json.dumps(event))

                    # Heartbeat if no events (every 10 seconds)
                    if len(events) == 0:
                        if not hasattr(ws, '_last_heartbeat'):
                            ws._last_heartbeat = 0
                        if time.time() - ws._last_heartbeat >= 10:
                            ws.send(json.dumps({
                                "type": "heartbeat",
                                "timestamp": time.time(),
                                "nodes_count": len(nodes),
                                "message": f"✓ Monitoring {len(nodes)} nodes"
                            }))
                            ws._last_heartbeat = time.time()

                    time.sleep(2)  # Poll every 2 seconds

                except Exception as e:
                    logger.error(f"Network nodes WebSocket error: {e}")
                    break

        @self.sock.route('/ws/network/backends')
        def ws_network_backends(ws):
            """WebSocket endpoint for streaming RPC backend events (event-driven)."""
            logger.info("🔌 RPC backends WebSocket connected")
            previous_backends: Set[str] = set()

            while True:
                try:
                    backends = []

                    # Get from router
                    if self.router and hasattr(self.router, 'rpc_backends'):
                        for backend in self.router.rpc_backends:
                            backend_addr = f"{backend.get('host')}:{backend.get('port', 50052)}"
                            backends.append(backend_addr)

                    # Try RPC registry fallback
                    try:
                        from sollol.rpc_registry import RPCBackendRegistry
                        registry = RPCBackendRegistry()
                        for backend in registry.list_backends():
                            backend_addr = f"{backend['host']}:{backend.get('port', 50052)}"
                            if backend_addr not in backends:
                                backends.append(backend_addr)
                    except:
                        pass

                    current_backends = set(backends)

                    # Detect new backends
                    new_backends = current_backends - previous_backends
                    for backend_addr in new_backends:
                        ws.send(json.dumps({
                            "type": "backend_connected",
                            "timestamp": time.time(),
                            "backend": backend_addr,
                            "message": f"🔗 RPC backend connected: {backend_addr}"
                        }))

                    # Detect removed backends
                    removed_backends = previous_backends - current_backends
                    for backend_addr in removed_backends:
                        ws.send(json.dumps({
                            "type": "backend_disconnected",
                            "timestamp": time.time(),
                            "backend": backend_addr,
                            "message": f"🔌 RPC backend disconnected: {backend_addr}"
                        }))

                    previous_backends = current_backends

                    # Heartbeat if no changes
                    if len(new_backends) == 0 and len(removed_backends) == 0:
                        if not hasattr(ws, '_last_heartbeat'):
                            ws._last_heartbeat = 0
                        if time.time() - ws._last_heartbeat >= 10:
                            ws.send(json.dumps({
                                "type": "heartbeat",
                                "timestamp": time.time(),
                                "backends_count": len(backends),
                                "message": f"✓ Monitoring {len(backends)} RPC backends"
                            }))
                            ws._last_heartbeat = time.time()

                    time.sleep(2)

                except Exception as e:
                    logger.error(f"RPC backends WebSocket error: {e}")
                    break

        @self.sock.route('/ws/ollama_activity')
        def ws_ollama_activity(ws):
            """WebSocket endpoint for Ollama model lifecycle events (load/unload/processing)."""
            logger.info("🔌 Ollama activity WebSocket connected")
            previous_state = {}

            while True:
                try:
                    # Get nodes to monitor
                    nodes_to_monitor = []
                    if self.router and hasattr(self.router, 'ollama_pool'):
                        pool = self.router.ollama_pool
                        nodes_to_monitor = [(node.url, node.url) for node in pool.nodes if node.healthy]
                    else:
                        # Fallback: auto-discover
                        from sollol.discovery import discover_ollama_nodes
                        discovered = discover_ollama_nodes()
                        nodes_to_monitor = [(f"http://{n['host']}:{n['port']}", f"{n['host']}:{n['port']}") for n in discovered]

                    # Monitor each node for model activity
                    for url, node_key in nodes_to_monitor:
                        try:
                            response = requests.get(f"{url}/api/ps", timeout=2)
                            if response.status_code == 200:
                                data = response.json()
                                models = data.get('models', [])

                                # Current state
                                current_models = {m['name'] for m in models}

                                # Get previous state
                                prev_models = previous_state.get(node_key, {}).get('models', set())

                                # Detect new models loaded
                                newly_loaded = current_models - prev_models
                                for model_name in newly_loaded:
                                    ws.send(json.dumps({
                                        "type": "model_loaded",
                                        "timestamp": time.time(),
                                        "node": node_key,
                                        "model": model_name,
                                        "message": f"✅ Model loaded on {node_key}: {model_name}"
                                    }))

                                # Detect unloaded models
                                unloaded = prev_models - current_models
                                for model_name in unloaded:
                                    ws.send(json.dumps({
                                        "type": "model_unloaded",
                                        "timestamp": time.time(),
                                        "node": node_key,
                                        "model": model_name,
                                        "message": f"⏹️  Model unloaded from {node_key}: {model_name}"
                                    }))

                                # Detect active processing
                                for model_info in models:
                                    model_name = model_info['name']
                                    processor = model_info.get('processor', {})
                                    if processor:  # Model actively processing
                                        size_vram = model_info.get('size_vram', 0) / (1024**3)
                                        # Only send if this is a new processing session
                                        was_processing = previous_state.get(node_key, {}).get('processing', set())
                                        if model_name not in was_processing:
                                            ws.send(json.dumps({
                                                "type": "model_processing",
                                                "timestamp": time.time(),
                                                "node": node_key,
                                                "model": model_name,
                                                "vram_gb": round(size_vram, 2),
                                                "message": f"🔄 Processing on {node_key}: {model_name} (VRAM: {size_vram:.2f}GB)"
                                            }))

                                # Update state
                                processing_models = {m['name'] for m in models if m.get('processor')}
                                previous_state[node_key] = {
                                    'models': current_models,
                                    'processing': processing_models
                                }

                        except Exception as e:
                            # Node unreachable
                            was_reachable = previous_state.get(node_key, {}).get('reachable', True)
                            if was_reachable:
                                ws.send(json.dumps({
                                    "type": "node_error",
                                    "timestamp": time.time(),
                                    "node": node_key,
                                    "message": f"❌ Node unreachable: {node_key}"
                                }))
                            previous_state[node_key] = {'reachable': False}

                    time.sleep(2)  # Poll every 2 seconds

                except Exception as e:
                    logger.error(f"Ollama activity WebSocket error: {e}")
                    break

        @self.sock.route('/ws/applications')
        def ws_applications(ws):
            """WebSocket endpoint for application lifecycle events (event-driven)."""
            logger.info("🔌 Applications WebSocket connected")
            previous_apps: Set[str] = set()

            while True:
                try:
                    # Clean up stale applications
                    self._cleanup_stale_applications()

                    # Get current applications
                    current_apps = set(self.applications.keys())

                    # Detect new applications
                    new_apps = current_apps - previous_apps
                    for app_id in new_apps:
                        app_info = self.applications[app_id]
                        ws.send(json.dumps({
                            "type": "app_registered",
                            "timestamp": time.time(),
                            "app_id": app_id,
                            "name": app_info["name"],
                            "router_type": app_info.get("router_type"),
                            "message": f"📱 Application started: {app_info['name']} ({app_info.get('router_type')})"
                        }))

                    # Detect removed applications
                    removed_apps = previous_apps - current_apps
                    for app_id in removed_apps:
                        ws.send(json.dumps({
                            "type": "app_unregistered",
                            "timestamp": time.time(),
                            "app_id": app_id,
                            "message": f"📱 Application stopped: {app_id}"
                        }))

                    # Detect status changes (active → stale)
                    now = time.time()
                    for app_id, app_info in self.applications.items():
                        last_seen = now - app_info["last_heartbeat"]
                        is_stale = last_seen > self.application_timeout

                        # Store previous status
                        if not hasattr(ws, '_app_status'):
                            ws._app_status = {}
                        prev_stale = ws._app_status.get(app_id, False)

                        if is_stale and not prev_stale:
                            ws.send(json.dumps({
                                "type": "app_stale",
                                "timestamp": time.time(),
                                "app_id": app_id,
                                "name": app_info["name"],
                                "message": f"⚠️  Application not responding: {app_info['name']} (last seen {int(last_seen)}s ago)"
                            }))

                        ws._app_status[app_id] = is_stale

                    previous_apps = current_apps

                    # Heartbeat if no changes
                    if len(new_apps) == 0 and len(removed_apps) == 0:
                        if not hasattr(ws, '_last_heartbeat'):
                            ws._last_heartbeat = 0
                        if time.time() - ws._last_heartbeat >= 10:
                            ws.send(json.dumps({
                                "type": "heartbeat",
                                "timestamp": time.time(),
                                "apps_count": len(self.applications),
                                "message": f"✓ Monitoring {len(self.applications)} applications"
                            }))
                            ws._last_heartbeat = time.time()

                    time.sleep(2)

                except Exception as e:
                    logger.error(f"Applications WebSocket error: {e}")
                    break

    def _cleanup_stale_applications(self):
        """Remove applications that haven't sent heartbeat recently."""
        now = time.time()
        stale_apps = [
            app_id for app_id, app_info in self.applications.items()
            if now - app_info["last_heartbeat"] > self.application_timeout * 2  # 2x timeout = remove
        ]
        for app_id in stale_apps:
            app_name = self.applications[app_id].get("name", app_id)
            logger.info(f"📱 Removing stale application: {app_name} ({app_id})")
            del self.applications[app_id]

    def _calculate_analytics(self) -> Dict[str, Any]:
        """Calculate P50/P95/P99 latencies from history."""
        if not self.request_history:
            return {
                "p50_latency_ms": 0,
                "p95_latency_ms": 0,
                "p99_latency_ms": 0,
                "total_requests": 0,
                "success_rate": 0,
            }

        latencies = sorted([r["latency_ms"] for r in self.request_history])
        total = len(latencies)

        def percentile(p):
            idx = int(total * p / 100)
            return latencies[min(idx, total - 1)]

        successful = sum(1 for r in self.request_history if r["status"] == "success")

        return {
            "p50_latency_ms": percentile(50),
            "p95_latency_ms": percentile(95),
            "p99_latency_ms": percentile(99),
            "total_requests": total,
            "success_rate": successful / total if total > 0 else 0,
        }

    def record_request(
        self,
        model: str,
        backend: str,
        latency_ms: float,
        status: str = "success"
    ):
        """Record request for analytics."""
        self.request_history.append({
            "model": model,
            "backend": backend,
            "latency_ms": latency_ms,
            "status": status,
            "timestamp": time.time(),
        })

        # Update Prometheus metrics
        request_counter.labels(model=model, status=status, backend=backend).inc()
        request_duration.labels(model=model, backend=backend).observe(latency_ms / 1000)

    def run(self, host: str = "0.0.0.0", debug: bool = False):
        """Run dashboard server (production-ready with Waitress)."""
        logger.info(f"🚀 Starting Unified Dashboard on http://{host}:{self.dashboard_port}")
        logger.info(f"   Ray Dashboard: http://localhost:{self.ray_dashboard_port}")
        logger.info(f"   Dask Dashboard: http://localhost:{self.dask_dashboard_port}")
        logger.info(f"   Prometheus: http://{host}:{self.dashboard_port}/api/prometheus")

        if debug:
            # Development mode - use Flask's dev server
            logger.warning("⚠️  Running in DEBUG mode - not for production!")
            self.app.run(host=host, port=self.dashboard_port, debug=True)
        else:
            # Production mode - use Waitress
            from waitress import serve
            logger.info("✅ Using Waitress production server")
            serve(self.app, host=host, port=self.dashboard_port, threads=4)


# Unified Dashboard HTML Template
UNIFIED_DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>SOLLOL Unified Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .header h1 {
            font-size: 1.8rem;
            font-weight: 600;
        }
        .header .subtitle {
            color: rgba(255,255,255,0.9);
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }
        .container {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            grid-template-rows: auto auto 1fr;
            gap: 1rem;
            padding: 1rem;
            height: calc(100vh - 120px);
        }
        .metrics-bar {
            grid-column: 1 / -1;
            display: flex;
            gap: 1rem;
            background: #1e293b;
            padding: 1.5rem;
            border-radius: 0.5rem;
        }
        .metric-card {
            flex: 1;
            background: #334155;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #667eea;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: 600;
            color: #a78bfa;
        }
        .metric-label {
            color: #94a3b8;
            font-size: 0.85rem;
            margin-top: 0.25rem;
        }
        .dashboard-panel {
            background: #1e293b;
            border-radius: 0.5rem;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        .panel-header {
            background: #334155;
            padding: 0.75rem 1rem;
            font-weight: 600;
            border-bottom: 2px solid #667eea;
        }
        .panel-content {
            flex: 1;
            overflow: hidden;
        }
        iframe {
            width: 100%;
            height: 100%;
            border: none;
        }
        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 0.5rem;
        }
        .status-active { background: #10b981; }
        .status-inactive { background: #ef4444; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 SOLLOL Unified Dashboard</h1>
        <div class="subtitle">
            Real-time monitoring • Distributed tracing • Performance analytics
        </div>
    </div>

    <div class="container">
        <!-- Metrics Bar -->
        <div class="metrics-bar" id="metrics-bar">
            <div class="metric-card">
                <div class="metric-value" id="p50-latency">--</div>
                <div class="metric-label">P50 Latency (ms)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="p95-latency">--</div>
                <div class="metric-label">P95 Latency (ms)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="p99-latency">--</div>
                <div class="metric-label">P99 Latency (ms)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="success-rate">--</div>
                <div class="metric-label">Success Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="total-pools">--</div>
                <div class="metric-label">Active Pools</div>
            </div>
        </div>

        <!-- SOLLOL Metrics -->
        <div class="dashboard-panel">
            <div class="panel-header">
                <span class="status-indicator status-active"></span>
                SOLLOL Metrics
            </div>
            <div class="panel-content" id="sollol-metrics">
                <pre id="metrics-json" style="padding: 1rem; overflow: auto; height: 100%; color: #a78bfa;"></pre>
            </div>
        </div>

        <!-- Distributed Traces -->
        <div class="dashboard-panel">
            <div class="panel-header">
                <span class="status-indicator status-active"></span>
                Distributed Traces
            </div>
            <div class="panel-content">
                <pre id="traces-json" style="padding: 1rem; overflow: auto; height: 100%; color: #10b981;"></pre>
            </div>
        </div>

        <!-- Applications -->
        <div class="dashboard-panel">
            <div class="panel-header">
                <span class="status-indicator status-active"></span>
                Applications
            </div>
            <div class="panel-content">
                <div id="applications-list" style="padding: 1rem; overflow: auto; height: 100%;">
                    <div style="color: #94a3b8; text-align: center; padding: 2rem;">
                        No applications registered yet
                    </div>
                </div>
            </div>
        </div>

        <!-- Ray Dashboard -->
        <div class="dashboard-panel">
            <div class="panel-header">
                <span class="status-indicator" id="ray-status"></span>
                Ray Dashboard
            </div>
            <div class="panel-content">
                <iframe src="http://localhost:8265" id="ray-iframe"></iframe>
            </div>
        </div>

        <!-- Dask Dashboard -->
        <div class="dashboard-panel">
            <div class="panel-header">
                <span class="status-indicator" id="dask-status"></span>
                Dask Dashboard
            </div>
            <div class="panel-content">
                <iframe src="http://localhost:8787" id="dask-iframe"></iframe>
            </div>
        </div>
    </div>

    <script>
        // Update metrics every 2 seconds
        setInterval(async () => {
            try {
                // SOLLOL metrics
                const metricsRes = await fetch('/api/metrics');
                const metrics = await metricsRes.json();

                // Update analytics
                if (metrics.analytics) {
                    document.getElementById('p50-latency').textContent =
                        metrics.analytics.p50_latency_ms.toFixed(0);
                    document.getElementById('p95-latency').textContent =
                        metrics.analytics.p95_latency_ms.toFixed(0);
                    document.getElementById('p99-latency').textContent =
                        metrics.analytics.p99_latency_ms.toFixed(0);
                    document.getElementById('success-rate').textContent =
                        (metrics.analytics.success_rate * 100).toFixed(1) + '%';
                }

                // Update pool count
                if (metrics.total_pools !== undefined) {
                    document.getElementById('total-pools').textContent = metrics.total_pools;
                }

                // Display full metrics
                document.getElementById('metrics-json').textContent =
                    JSON.stringify(metrics, null, 2);

                // Traces
                const tracesRes = await fetch('/api/traces');
                const traces = await tracesRes.json();
                document.getElementById('traces-json').textContent =
                    JSON.stringify(traces, null, 2);

                // Applications
                const appsRes = await fetch('/api/applications');
                const appsData = await appsRes.json();
                const appsList = document.getElementById('applications-list');

                if (appsData.applications && appsData.applications.length > 0) {
                    let html = '<table style="width: 100%; color: #e2e8f0; font-size: 0.85rem;">';
                    html += '<thead><tr style="border-bottom: 1px solid #334155; text-align: left;">';
                    html += '<th style="padding: 0.5rem;">Name</th>';
                    html += '<th style="padding: 0.5rem;">Router</th>';
                    html += '<th style="padding: 0.5rem;">Status</th>';
                    html += '<th style="padding: 0.5rem;">Uptime</th>';
                    html += '</tr></thead><tbody>';

                    appsData.applications.forEach(app => {
                        const statusColor = app.status === 'active' ? '#10b981' : '#f59e0b';
                        const statusIcon = app.status === 'active' ? '✅' : '⚠️';
                        const uptimeMin = Math.floor(app.uptime_seconds / 60);
                        const uptimeSec = app.uptime_seconds % 60;

                        html += '<tr style="border-bottom: 1px solid #1e293b;">';
                        html += `<td style="padding: 0.5rem;">${app.name}</td>`;
                        html += `<td style="padding: 0.5rem; color: #a78bfa;">${app.router_type}</td>`;
                        html += `<td style="padding: 0.5rem; color: ${statusColor};">${statusIcon} ${app.status}</td>`;
                        html += `<td style="padding: 0.5rem;">${uptimeMin}m ${uptimeSec}s</td>`;
                        html += '</tr>';
                    });

                    html += '</tbody></table>';
                    appsList.innerHTML = html;
                } else {
                    appsList.innerHTML = '<div style="color: #94a3b8; text-align: center; padding: 2rem;">No applications registered yet</div>';
                }

                // Check Ray status
                try {
                    const rayRes = await fetch('/api/ray/metrics');
                    document.getElementById('ray-status').className =
                        rayRes.ok ? 'status-indicator status-active' : 'status-indicator status-inactive';
                } catch {
                    document.getElementById('ray-status').className = 'status-indicator status-inactive';
                }

                // Check Dask status
                try {
                    const daskRes = await fetch('/api/dask/metrics');
                    document.getElementById('dask-status').className =
                        daskRes.ok ? 'status-indicator status-active' : 'status-indicator status-inactive';
                } catch {
                    document.getElementById('dask-status').className = 'status-indicator status-inactive';
                }

            } catch (error) {
                console.error('Error updating metrics:', error);
            }
        }, 2000);
    </script>
</body>
</html>
"""


def run_unified_dashboard(
    router=None,
    ray_dashboard_port: int = 8265,
    dask_dashboard_port: int = 8787,
    dashboard_port: int = 8080,
    host: str = "0.0.0.0",
    enable_dask: bool = True,
):
    """
    Run unified dashboard server.

    Args:
        router: SOLLOL router instance
        ray_dashboard_port: Ray dashboard port
        dask_dashboard_port: Dask dashboard port
        dashboard_port: Unified dashboard port
        host: Host to bind to
        enable_dask: Enable Dask distributed client with dashboard
    """
    dashboard = UnifiedDashboard(
        router=router,
        ray_dashboard_port=ray_dashboard_port,
        dask_dashboard_port=dask_dashboard_port,
        dashboard_port=dashboard_port,
        enable_dask=enable_dask,
    )

    dashboard.run(host=host)
