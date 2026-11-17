import json
import pytest

from rutasit.ia import ProveedorLLM
from rutasit.generador_pruebas_eta import GeneradorPruebasEta, SalidaInvalida


CODIGO_VALIDO = '''import pytest
from rutasit.algoritmos_eta import DistanciaDirecta

def test_eta_distancia_directa():
    eta = DistanciaDirecta()
    assert eta.segundos(1000, 36) == pytest.approx(100.0)
    assert eta.segundos(0, 36) == pytest.approx(0.0)
    assert eta.segundos(1000, 0) == pytest.approx(720.0)
'''


class ProveedorGrabado(ProveedorLLM):
    def __init__(self, respuesta):
        self.respuesta = respuesta
        self.prompt_recibido = None

    def completar(self, prompt: str) -> str:
        self.prompt_recibido = prompt
        return self.respuesta


def respuesta(codigo=CODIGO_VALIDO, caso_id="ETA-01"):
    return json.dumps({
        "caso_id": caso_id,
        "archivo": "test_eta_generado.py",
        "codigo": codigo,
        "objetivo": "Verificar el cálculo de ETA para el caso solicitado."
    })


def test_acepta_respuesta_valida_del_proveedor_grabado():
    proveedor = ProveedorGrabado(respuesta())
    generador = GeneradorPruebasEta(proveedor)
    salida = generador.generar("ETA-01", "Distancia 1000 m a 36 km/h", "Comprobar ETA")
    assert salida["caso_id"] == "ETA-01"
    assert "DistanciaDirecta" in salida["codigo"]
    assert "{{requisito}}" not in proveedor.prompt_recibido


def test_rechaza_json_invalido():
    generador = GeneradorPruebasEta(ProveedorGrabado("esto no es JSON"))
    with pytest.raises(SalidaInvalida):
        generador.generar("ETA-01", "requisito", "objetivo")


def test_rechaza_esquema_invalido():
    generador = GeneradorPruebasEta(ProveedorGrabado(json.dumps({"codigo": CODIGO_VALIDO})))
    with pytest.raises(SalidaInvalida):
        generador.generar("ETA-01", "requisito", "objetivo")


def test_rechaza_codigo_con_import_peligroso():
    codigo = "import os\ndef test_malicioso():\n    assert True\n    assert True\n    assert True\n"
    generador = GeneradorPruebasEta(ProveedorGrabado(respuesta(codigo)))
    with pytest.raises(SalidaInvalida, match="Import no permitido"):
        generador.generar("ETA-01", "requisito", "objetivo")


def test_rechaza_caso_id_distinto():
    generador = GeneradorPruebasEta(ProveedorGrabado(respuesta(caso_id="ETA-OTRO")))
    with pytest.raises(SalidaInvalida, match="no coincide"):
        generador.generar("ETA-01", "requisito", "objetivo")
