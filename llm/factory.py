"""
factory.py – implements Dependency-Inversion:
high-level code depends on `LLMClient`, never concrete classes.
"""

from __future__ import annotations
from typing import Dict, Type, Any
from pathlib import Path
from .base      import LLMClient
from .config    import load_client_cfg


class _Registry:
    _cls: Dict[str, Type[LLMClient]] = {}

    @classmethod
    def add(cls, name: str, client_cls: Type[LLMClient]):
        cls._cls[name.lower()] = client_cls

    @classmethod
    def get(cls, name: str) -> Type[LLMClient]:
        if name.lower() not in cls._cls:
            raise ValueError(f"Unknown provider '{name}'. "
                             f"Registered: {list(cls._cls)}")
        return cls._cls[name.lower()]


class LLMFactory:
    """
    Central entry-point: returns a ready client instance.
    """

    @staticmethod
    def create(
        *, provider: str,
        cfg: dict[str, Any] | None = None,
        config_dir: str | Path | None = None,
        model_name: str | None = None,
        debug: bool = False,
        **kwargs: Any,
    ) -> LLMClient:
        """
        Parameters
        ----------
        provider   – e.g. "watsonx" | "rits"
        cfg        – config dict (optional if config_dir or default directory is used)
        config_dir – folder containing provider configurations
        model_name – optional model name override
        debug      – debug mode
        """
        from importlib import import_module
        provider = provider.lower()

        if cfg is None:
            base_dir = Path(config_dir) if config_dir else Path(__file__).parent
            cfg_path = base_dir / provider / "config.yaml"
            if not cfg_path.exists() and config_dir:
                cfg_path = Path(config_dir) / provider / "config.yaml"
            if not cfg_path.exists():
                cfg_path = Path(__file__).parent / provider / "config.yaml"
            cfg = load_client_cfg(str(cfg_path))
        else:
            cfg = dict(cfg)

        if model_name:
            if provider == "watsonx":
                cfg["model_id"] = model_name
            elif provider == "rits":
                if "request_defaults" not in cfg or not isinstance(cfg["request_defaults"], dict):
                    cfg["request_defaults"] = {}
                cfg["request_defaults"]["model"] = model_name

        # --- dynamic import registers the concrete class via side-effect
        import_module(f"llm.{provider}.client")

        cls = _Registry.get(provider)
        return cls(config=cfg, debug=debug)


# helper decorator ----------------------------------------------------------
def register_provider(name: str):
    """
    Decorator used by concrete client modules
    to register themselves in the factory.
    """
    def _decorator(cls: Type[LLMClient]):
        _Registry.add(name, cls)
        return cls
    return _decorator