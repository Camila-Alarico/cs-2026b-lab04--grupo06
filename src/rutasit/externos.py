"""Servicios externos SIMULADOS (sin red ni claves). Cada uno tiene una interfaz distinta, como en la realidad."""


class _ConFallas:
    def __init__(self, fallas: int = 0):
        self.fallas = fallas      # cuántas llamadas iniciales lanzan TimeoutError
        self.llamadas = 0

    def _intentar(self):
        self.llamadas += 1
        if self.llamadas <= self.fallas:
            raise TimeoutError("El servicio externo no respondió")


class GpsOperadorA(_ConFallas):
    """Operador A: dict con grados decimales, velocidad en km/h y fecha ISO 8601."""

    def __init__(self, fallas: int = 0):
        super().__init__(fallas)
        self.lectura: dict | None = None

    def ultima_lectura(self, placa: str) -> dict:
        self._intentar()
        return self.lectura  # {"lat": -16.4, "lng": -71.5, "vel_kmh": 20.0, "ts": "2026-10-20T08:00:00"}


class GpsOperadorB(_ConFallas):
    """Operador B: tupla (lat en micro-grados, lon en micro-grados, velocidad en m/s, epoch en segundos)."""

    def __init__(self, fallas: int = 0):
        super().__init__(fallas)
        self.lectura: tuple | None = None

    def leer(self, placa: str) -> tuple:
        self._intentar()
        return self.lectura


class LlmNubeSDK(_ConFallas):
    """LLM en la nube (simulado): devuelve un dict con la clave 'texto'."""

    def __init__(self, respuesta: str = "", fallas: int = 0):
        super().__init__(fallas)
        self.respuesta = respuesta

    def generate(self, prompt: str) -> dict:
        self._intentar()
        return {"texto": self.respuesta}


class LlmLocalSDK(_ConFallas):
    """LLM local (simulado): devuelve directamente el texto."""

    def __init__(self, respuesta: str = "", fallas: int = 0):
        super().__init__(fallas)
        self.respuesta = respuesta

    def predict(self, prompt: str) -> str:
        self._intentar()
        return self.respuesta