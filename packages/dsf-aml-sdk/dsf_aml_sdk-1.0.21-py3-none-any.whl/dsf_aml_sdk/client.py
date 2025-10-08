# ============================================
# dsf_aml_sdk/client.py
# ============================================
from . import __version__
from .models import Config, EvaluationResult, DistillationResult
from .exceptions import APIError, LicenseError, ValidationError

import requests
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urljoin
import time
from functools import wraps
import logging


logger = logging.getLogger(__name__)

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (requests.RequestException, APIError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))
            raise last_exception
        return wrapper
    return decorator

class AMLSDK:
    BASE_URL = 'https://dsf-miu6v152e-jaime-alexander-jimenezs-projects.vercel.app/'
    TIERS = {'community', 'professional', 'enterprise'}
    
    def __init__(self, license_key: Optional[str] = None, tier: str = 'community',
                 base_url: Optional[str] = None, timeout: int = 30, verify_ssl: bool = True):
        if tier not in self.TIERS:
            raise ValidationError(f"Invalid tier: {self.TIERS}")
        
        self.license_key = license_key
        self.tier = tier
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': f'DSF-AML-SDK-Python/{__version__}'
        })
        
        if tier != 'community' and license_key:
            self._validate_license()
    
    def _validate_license(self):
    # Dispara el gating premium con evaluate_batch cumpliendo contrato
        req = {
            'action': 'evaluate_batch',
            'tier': self.tier,
            'license_key': self.license_key,
            # Ambos por compatibilidad con distintas versiones del backend
            'data_batch': [{'__probe__': 0}, {'__probe__': 1}],
            'data_points': [{'__probe__': 0}, {'__probe__': 1}],
            # Config mínimo válido
            'config': {'__probe__': {'default': 0, 'weight': 1.0, 'criticality': 1.0}}
        }
        try:
            resp = self._make_request('', req)
        # Si llega aquí con 200, la licencia pasó
            if not isinstance(resp, dict):
                raise LicenseError("License validation failed (unexpected response)")
        except APIError as e:
            if e.status_code == 403:
                raise LicenseError(f"Invalid license: {e.message}")
            raise

   
    @retry_on_failure(max_retries=3)
    def _make_request(self, endpoint: str, data: Dict) -> Dict:
        url = urljoin(self.base_url, endpoint)
        try:
            response = self.session.post(url, json=data, timeout=self.timeout, verify=self.verify_ssl)
            
            if response.status_code == 200:
                return response.json()
            
            elif response.status_code == 403:
                raise LicenseError(response.json().get('error', 'License error'))
            
            # --- BLOQUE ACTUALIZADO ---
            elif response.status_code >= 400:
                try:
                    j = response.json()
                    base = j.get('error', 'API error')
                    # Se incluye el campo 'detail' si existe para dar más contexto
                    if 'detail' in j:
                        base = f"{base} — {j['detail']}"
                    raise APIError(base, status_code=response.status_code)
                except Exception:
                    # Fallback si la respuesta no es un JSON válido
                    error_msg = f"Server error {response.status_code}: {response.text[:200]}"
                    raise APIError(error_msg, status_code=response.status_code)
            
        except requests.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")
    
    def evaluate(self, data: Dict[str, Any], config: Optional[Union[Dict, Config]] = None) -> EvaluationResult:
        """Standard evaluation"""
        if isinstance(config, Config):
            config = config.to_dict()
        if not isinstance(data, dict):
            raise ValidationError("Data must be a dictionary")
        
        self._last_config = (config or {})
        
        request_data = {'data': data, 'config': config or {}, 'tier': self.tier}
        if self.license_key:
            request_data['license_key'] = self.license_key
        
        response = self._make_request('', request_data)
        return EvaluationResult.from_response(response)
    
    def batch_evaluate(self, data_points: List[Dict], config: Optional[Union[Dict, Config]] = None) -> List[EvaluationResult]:
        """Batch evaluation (Premium)"""
        if self.tier == 'community':
            raise LicenseError("Batch evaluation requires premium tier")
        
        # Guardar último config para get_metrics()
        if config:
            self._last_config = config.to_dict() if isinstance(config, Config) else config
        use_config = self._last_config or {}
        if isinstance(use_config, Config):
            use_config = use_config.to_dict()
        
        request = {
            'op': 'evaluate_batch',
            'tier': self.tier,
            'license_key': self.license_key,
            'config': use_config,
            'data_points': data_points,
        }
        
        try:
            resp = self._make_request('', request)
            # Normaliza posibles formatos de respuesta
            if isinstance(resp, list):
                raw = resp
            elif isinstance(resp, dict):
                raw = resp.get('scores')  # dict o lista
                if raw is None:
                    # dict indexado por int/str
                    raw = [resp.get(i, resp.get(str(i), 0.0)) for i in range(len(data_points))]
            else:
                raw = []

            # Si viene lista de dicts, extrae 'score'
            if raw and isinstance(raw[0], dict):
                raw = [float(x.get('score', 0.0)) for x in raw]

            return [
                EvaluationResult(
                    score=float(raw[i]) if i < len(raw) else 0.0,
                    tier=self.tier
                )
                for i in range(len(data_points))
            ]
        except APIError:
            # Fallback: loop cliente mantiene contrato
            return [self.evaluate(dp, use_config) for dp in data_points]
    
    def pipeline_identify_seeds(self, dataset: List[Dict], config: Union[Dict, Config], 
                               top_k_percent: float = 0.1, **kwargs) -> Dict:
                
        if isinstance(config, Config):
            config = config.to_dict()
        
        request_data = {
            'action': 'pipeline_identify_seeds',
            'dataset': dataset,
            'config': config,
            'top_k_percent': top_k_percent,
            'license_key': self.license_key,
            **kwargs
        }
        return self._make_request('', request_data)

    def pipeline_generate_critical(self, config, seeds=None, advanced=None, **kwargs):
        if self.tier == 'community':
            raise LicenseError("Pipeline requires premium tier")
        request_data = {
            'action': 'pipeline_generate_critical',
            'config': config.to_dict() if isinstance(config, Config) else config,
            'license_key': self.license_key,
            **kwargs
        }
        if seeds: request_data['seeds'] = seeds
        if advanced: request_data['advanced'] = advanced
        return self._make_request('', request_data)


    def curriculum_init(self, dataset: List[Dict], config: Union[Dict, Config], **params) -> Dict:
        """Initialize curriculum learning session"""
        if self.tier not in ['professional', 'enterprise']:
            raise LicenseError("Curriculum requires professional+ tier")
        
        if isinstance(config, Config):
            config = config.to_dict()
        
        request_data = {
            'action': 'curriculum_init',
            'dataset': dataset,
            'config': config,
            'license_key': self.license_key,
            **params
        }
        return self._make_request('', request_data)

    def curriculum_step(self, dataset: List[Dict], config: Union[Dict, Config], 
                       precomputed_metrics: Optional[Dict] = None) -> Dict:
        """Execute one curriculum iteration"""
        if self.tier not in ['professional', 'enterprise']:
            raise LicenseError("Curriculum requires professional+ tier")
        
        if isinstance(config, Config):
            config = config.to_dict()
        
        request_data = {
            'action': 'curriculum_step',
            'dataset': dataset,
            'config': config,
            'license_key': self.license_key
        }
        if precomputed_metrics:
            request_data['precomputed_metrics'] = precomputed_metrics
        
        return self._make_request('', request_data)

    def curriculum_status(self) -> Dict:
        """Get status of current curriculum session"""
        if self.tier not in ['professional', 'enterprise']:
            raise LicenseError("Curriculum requires professional+ tier")
        
        request_data = {
            'action': 'curriculum_status',
            'license_key': self.license_key
        }
        return self._make_request('', request_data)

    def pipeline_full_cycle(self, dataset: List[Dict], config: Union[Dict, Config], 
                           max_iterations: int = 5, **kwargs) -> Dict:
        """Execute complete pipeline automatically"""
        if self.tier != 'enterprise':
            raise LicenseError("Full cycle requires enterprise tier")
        
        if isinstance(config, Config):
            config = config.to_dict()
        
        request_data = {
            'action': 'pipeline_full_cycle',
            'dataset': dataset,
            'config': config,
            'max_iterations': max_iterations,
            'license_key': self.license_key,
            **kwargs
        }
        return self._make_request('', request_data)

    def evaluate_nonlinear(self, data: Dict, config: Union[Dict, Config], 
                           adjustments: Dict[str, float], adjustment_values: Dict = None) -> EvaluationResult:
        """Evaluate with non-linear formula mode"""
        if isinstance(config, Config):
            config = config.to_dict()
        
        request_data = {
            'data': data,
            'config': config,
            'formula_mode': 'nonlinear',
            'adjustments': adjustments,
            'tier': self.tier
        }
        if adjustment_values:
            request_data['data']['adjustments_values'] = adjustment_values
        if self.license_key:
            request_data['license_key'] = self.license_key
        
        response = self._make_request('', request_data)
        return EvaluationResult.from_response(response)
    
    # ========== Knowledge Distillation Features (Premium) ==========
    
    def distill_train(self, config: Union[Dict, Config], samples: int = 1000, 
                     seed: int = 42) -> DistillationResult:
        """Train surrogate model via knowledge distillation (Premium)"""
        if self.tier == 'community':
            raise LicenseError("Distillation requires premium tier")
        
        if isinstance(config, Config):
            config = config.to_dict()
        
        request_data = {
            'action': 'translate_train',
            'config': config,
            'samples': samples,
            'seed': seed,
            'tier': self.tier,
            'license_key': self.license_key
        }
        
        response = self._make_request('', request_data)
        return DistillationResult.from_train_response(response)
    
    def distill_export(self, config: Optional[Union[Dict, Config]] = None) -> Dict:
        """Export trained surrogate model (Premium)"""
        if self.tier == 'community':
            raise LicenseError("Export requires premium tier")
        
        request_data = {
            'action': 'translate_export',
            'tier': self.tier,
            'license_key': self.license_key
        }
        
        if config:
            if isinstance(config, Config):
                config = config.to_dict()
            request_data['config'] = config
        
        return self._make_request('', request_data)
    
    def distill_predict(self, data: Dict[str, Any], config: Union[Dict, Config]) -> float:
        """Fast prediction using surrogate model (Premium)"""
        if self.tier == 'community':
            raise LicenseError("Surrogate prediction requires premium tier")
        
        if isinstance(config, Config):
            config = config.to_dict()
        
        request_data = {
            'action': 'translate_predict',
            'data': data,
            'config': config,
            'tier': self.tier,
            'license_key': self.license_key
        }
        
        response = self._make_request('', request_data)
        return response.get('score_surrogate', 0.0)
    
    def create_config(self) -> Config:
        return Config()
    
    def get_metrics(self) -> Optional[Dict]:
        if self.tier == 'community':
            return None
        use_config = getattr(self, '_last_config', None)
        if use_config is None or not isinstance(use_config, dict) or not use_config:
        # Config mínimo válido para el backend
            use_config = {'__probe__': {'default': 0, 'weight': 1.0, 'criticality': 1.0}}

        req = {'data': {}, 'config': use_config, 'tier': self.tier, 'license_key': self.license_key}
        resp = self._make_request('', req)
        return resp.get('metrics')
    
    def close(self):
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
