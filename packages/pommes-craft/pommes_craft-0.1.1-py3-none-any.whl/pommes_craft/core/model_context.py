import threading
from typing import Optional, Any


class ModelContext:
    """Thread-safe context manager for EnergyModel."""
    _local = threading.local()  # Thread-local storage

    @classmethod
    def get_current_model(cls) -> Optional['EnergyModel']:
        """Get the current model from thread-local context."""
        if not hasattr(cls._local, 'model') or cls._local.model is None:
            raise RuntimeError(
                "No active EnergyModel context. Components requiring model data must be created "
                "within a 'with model.context():' block or with an explicit model parameter."
            )
        return cls._local.model

    @classmethod
    def set_current_model(cls, model: Optional['EnergyModel']) -> None:
        """Set the current model in thread-local context."""
        cls._local.model = model

    def __init__(self, model: 'EnergyModel'):
        self.model = model
        self.previous_model = None

    def __enter__(self) -> 'EnergyModel':
        self.previous_model = getattr(self._local, 'model', None)
        ModelContext.set_current_model(self.model)
        return self.model

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        ModelContext.set_current_model(self.previous_model)
