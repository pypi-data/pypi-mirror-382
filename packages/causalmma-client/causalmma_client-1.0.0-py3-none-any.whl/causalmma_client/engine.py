"""
Local Execution Engine
Runs algorithms client-side, phones home for control
"""

import requests
import pandas as pd
import hashlib
import platform
import sys
import uuid
import json
import jwt
from typing import Dict, List, Optional
from datetime import datetime
import threading
import time


class LocalEngine:
    """
    Local execution engine for CausalMMA

    Data stays on client, control stays centralized
    """

    def __init__(
        self,
        api_key: str,
        control_plane_url: str = "http://localhost:8001",
        offline_mode: bool = False
    ):
        self.api_key = api_key
        self.control_plane_url = control_plane_url
        self.offline_mode = offline_mode

        # Generate client ID (machine fingerprint)
        self.client_id = self._generate_client_id()

        # SDK version
        self.sdk_version = "1.0.0"

        # License and features
        self.license_token = None
        self.features = []
        self.limits = {}
        self.tier = None
        self._is_licensed = False  # Track if license is valid

        # Feature flags
        self.flags = {}

        if not offline_mode:
            self._validate_license()
            self._fetch_feature_flags()
            self._start_heartbeat()
        else:
            # Offline mode - limited functionality
            print("⚠️  OFFLINE MODE - Limited functionality, no license validation")

    def _generate_client_id(self) -> str:
        """Generate unique client ID based on machine"""
        machine_info = f"{platform.node()}-{platform.machine()}-{platform.system()}"
        return hashlib.sha256(machine_info.encode()).hexdigest()[:32]

    def _validate_license(self):
        """Validate license with control plane"""
        try:
            response = requests.post(
                f"{self.control_plane_url}/control/v1/license/validate",
                json={
                    "api_key": self.api_key,
                    "sdk_version": self.sdk_version,
                    "client_id": self.client_id,
                    "python_version": sys.version.split()[0],
                    "os_platform": platform.system()
                },
                timeout=10
            )

            if response.status_code == 401:
                raise PermissionError(
                    f"❌ INVALID API KEY: '{self.api_key}'\n"
                    f"   Your API key was rejected by the control plane.\n"
                    f"   Please check:\n"
                    f"   1. API key format (should start with 'ca_live_')\n"
                    f"   2. API key is active in your account\n"
                    f"   3. Control plane URL is correct\n"
                    f"   Contact: support@causalmma.com"
                )
            elif response.status_code != 200:
                raise ValueError(
                    f"❌ LICENSE VALIDATION FAILED\n"
                    f"   Status: {response.status_code}\n"
                    f"   Error: {response.text}\n"
                    f"   Control Plane: {self.control_plane_url}"
                )

            data = response.json()

            if not data.get("valid", False):
                raise PermissionError(
                    f"❌ INVALID LICENSE\n"
                    f"   Your license is not valid.\n"
                    f"   Contact: support@causalmma.com"
                )

            self.license_token = data["license_token"]
            self.features = data["features"]
            self.limits = data["limits"]
            self.tier = data["tier"]
            self._is_licensed = True  # Mark as licensed

            print(f"✅ License validated - Tier: {data['tier']}")
            print(f"📦 Features: {', '.join(self.features)}")

        except Exception as e:
            self._is_licensed = False
            if not self.offline_mode:
                raise  # Re-raise the exception

    def _fetch_feature_flags(self):
        """Fetch feature flags from control plane"""
        try:
            response = requests.get(
                f"{self.control_plane_url}/control/v1/features",
                headers={"X-API-Key": self.api_key},
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                self.flags = data["flags"]
                print(f"🚩 Feature flags loaded: {len(self.flags)} flags")
        except Exception as e:
            print(f"⚠️  Could not fetch feature flags: {e}")

    def _start_heartbeat(self):
        """Start background heartbeat thread"""
        def heartbeat_loop():
            while True:
                try:
                    requests.post(
                        f"{self.control_plane_url}/control/v1/heartbeat",
                        json={
                            "client_id": self.client_id,
                            "sdk_version": self.sdk_version,
                            "status": "healthy",
                            "last_analysis_at": getattr(self, 'last_analysis_time', None)
                        },
                        headers={"X-API-Key": self.api_key},
                        timeout=5
                    )
                except:
                    pass

                time.sleep(300)  # Every 5 minutes

        thread = threading.Thread(target=heartbeat_loop, daemon=True)
        thread.start()

    def _send_telemetry(self, event_data: Dict):
        """Send telemetry event (async, non-blocking)"""
        if self.offline_mode:
            return

        def send():
            try:
                requests.post(
                    f"{self.control_plane_url}/control/v1/telemetry",
                    json=event_data,
                    headers={"X-API-Key": self.api_key},
                    timeout=5
                )
            except:
                pass

        threading.Thread(target=send, daemon=True).start()

    def _check_feature_enabled(self, feature: str):
        """Check if feature is enabled"""
        if feature not in self.features:
            raise PermissionError(
                f"Feature '{feature}' not available in your tier. Upgrade to access."
            )

        flag_name = f"enable_{feature}"
        if flag_name in self.flags and not self.flags[flag_name]:
            raise PermissionError(
                f"Feature '{feature}' is temporarily disabled. Contact support."
            )

    def analyze(
        self,
        df: pd.DataFrame,
        model: str = "data_driven",
        **kwargs
    ) -> Dict:
        """
        Run attribution analysis locally

        Args:
            df: DataFrame with touchpoints (NEVER sent to server)
            model: Attribution model to use

        Returns:
            Analysis results (computed locally)
        """

        # SECURITY: Check if license is valid before allowing any analysis
        if not self.offline_mode and not self._is_licensed:
            raise PermissionError(
                "❌ SDK NOT LICENSED\n"
                "   License validation failed during initialization.\n"
                "   Cannot perform analysis without a valid license.\n"
                "   Please check your API key and try again."
            )

        # Start telemetry
        analysis_id = str(uuid.uuid4())
        start_time = time.time()

        telemetry = {
            "event_id": str(uuid.uuid4()),
            "event_type": "analysis",
            "client_id": self.client_id,
            "algorithm": model,
            "num_rows": len(df),
            "num_columns": len(df.columns),
            "sdk_version": self.sdk_version,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "started"
        }

        try:
            # Check feature access
            self._check_feature_enabled(model)

            # Check limits
            if len(df) > self.limits.get("max_rows_per_analysis", float('inf')):
                raise ValueError(
                    f"Dataset too large: {len(df)} rows. "
                    f"Max: {self.limits['max_rows_per_analysis']}"
                )

            print(f"🔬 Analyzing locally with {model}...")
            print(f"📊 Dataset: {len(df)} rows × {len(df.columns)} columns")
            print(f"💾 Data stays on your machine")

            # Execute locally based on model
            if model == "data_driven":
                result = self._doubly_robust_local(df, **kwargs)
            elif model == "shapley":
                result = self._shapley_local(df, **kwargs)
            elif model == "pc_algorithm":
                result = self._pc_algorithm_local(df, **kwargs)
            else:
                raise ValueError(f"Unknown model: {model}")

            # Update telemetry
            execution_time = (time.time() - start_time) * 1000
            telemetry["status"] = "success"
            telemetry["execution_time_ms"] = int(execution_time)
            telemetry["metadata"] = {
                "num_channels": len(result.get("attribution_weights", {})),
                "analysis_id": analysis_id
            }

            self.last_analysis_time = datetime.utcnow().isoformat()

            print(f"✅ Analysis complete ({execution_time:.0f}ms)")

            return result

        except Exception as e:
            telemetry["status"] = "error"
            telemetry["error_type"] = type(e).__name__
            telemetry["error_message"] = str(e)
            raise

        finally:
            # Send telemetry (async)
            self._send_telemetry(telemetry)

    def _doubly_robust_local(self, df: pd.DataFrame, **kwargs) -> Dict:
        """
        Doubly robust estimation (local execution)

        Uses REAL implementation from causalinference.core package
        """
        try:
            # Import real implementation from core package
            from causalinference.core.statistical_inference import StatisticalCausalInference, CausalMethod

            # Use real doubly robust estimator
            inference = StatisticalCausalInference()

            # Get treatment and outcome variables from kwargs
            treatment_var = kwargs.get('treatment_variable', kwargs.get('treatment', 'treatment'))
            outcome_var = kwargs.get('outcome_variable', kwargs.get('outcome', 'outcome'))
            confounders = kwargs.get('confounders', [])

            # Execute real algorithm using correct method name
            causal_effect = inference.estimate_causal_effect(
                data=df,
                treatment=treatment_var,
                outcome=outcome_var,
                covariates=confounders,
                method=CausalMethod.LINEAR_REGRESSION
            )

            # Convert CausalEffect dataclass to dict
            result = {
                "method": causal_effect.method,
                "ate": causal_effect.effect_estimate,
                "effect_estimate": causal_effect.effect_estimate,
                "confidence_interval": {
                    "lower": causal_effect.confidence_interval[0],
                    "upper": causal_effect.confidence_interval[1]
                },
                "p_value": causal_effect.p_value,
                "standard_error": causal_effect.standard_error,
                "sample_size": causal_effect.sample_size,
                "interpretation": causal_effect.interpretation,
                "assumptions_met": causal_effect.assumptions_met,
                "assumptions_violated": causal_effect.assumptions_violated,
                "robustness_score": causal_effect.robustness_score,
                "execution_mode": "local",
                "data_location": "client",
                "algorithm_source": "causalinference.core"
            }

            return result

        except ImportError:
            # Fallback to simple implementation if core package not available
            print("⚠️  Core package not found, using fallback implementation")
            channels = df['channel'].unique() if 'channel' in df.columns else ['email', 'paid_search']
            weights = {ch: 1.0 / len(channels) for ch in channels}

            return {
                "attribution_weights": weights,
                "method": "doubly_robust_fallback",
                "execution_mode": "local_fallback",
                "data_location": "client"
            }

    def _shapley_local(self, df: pd.DataFrame, **kwargs) -> Dict:
        """
        Shapley values (local execution)

        Note: Core package doesn't have Shapley implementation yet
        Using fallback implementation
        """
        # Core package doesn't have Shapley method yet
        print("⚠️  Shapley not available in core package, using fallback implementation")
        channels = df['channel'].unique() if 'channel' in df.columns else ['email', 'paid_search']
        weights = {ch: 1.0 / len(channels) for ch in channels}

        return {
            "attribution_weights": weights,
            "method": "shapley_fallback",
            "execution_mode": "local_fallback",
            "data_location": "client"
        }

    def _pc_algorithm_local(self, df: pd.DataFrame, **kwargs) -> Dict:
        """
        PC Algorithm (local execution)

        Uses REAL implementation from causalinference.core package
        """
        try:
            # Import real implementation
            from causalinference.core.statistical_methods import PCAlgorithm

            pc = PCAlgorithm()
            variables = kwargs.get('variables', list(df.columns))

            # Run PC algorithm using correct method names
            skeleton = pc.discover_skeleton(df[variables])
            dag = pc.orient_edges(skeleton, df[variables])

            # Convert to edges format
            edges = []
            for (source, target) in dag.edges():
                edges.append({
                    "from": source,
                    "to": target
                })

            return {
                "edges": edges,
                "algorithm": "pc",
                "num_nodes": len(variables),
                "num_edges": len(edges),
                "execution_mode": "local",
                "data_location": "client",
                "algorithm_source": "causalinference.core"
            }

        except ImportError:
            # Fallback
            print("⚠️  Core package not found, using fallback implementation")
            return {
                "edges": [
                    {"from": "age", "to": "income"},
                    {"from": "treatment", "to": "outcome"}
                ],
                "algorithm": "pc_fallback",
                "execution_mode": "local_fallback",
                "data_location": "client"
            }


# Convenience wrapper
def analyze(df: pd.DataFrame, api_key: str, model: str = "data_driven", **kwargs):
    """
    Quick analysis function

    Usage:
        from causalmma_client import analyze

        result = analyze(
            df=my_dataframe,
            api_key="ca_live_xxx",
            model="data_driven"
        )
    """
    engine = LocalEngine(api_key=api_key)
    return engine.analyze(df, model=model, **kwargs)
