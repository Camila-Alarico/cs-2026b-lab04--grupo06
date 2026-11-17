import pytest
from rutasit.generador_pruebas_eta import GeneradorPruebasEta


@pytest.mark.parametrize("codigo", [
    "import os\ndef test_x():\n assert True\n assert True\n assert True\n",
    "import subprocess\ndef test_x():\n assert True\n assert True\n assert True\n",
    "def test_x():\n open('secreto.txt')\n assert True\n assert True\n assert True\n",
    "def test_x():\n eval('1+1')\n assert True\n assert True\n assert True\n",
])
def test_red_team_bloquea_imports_y_llamadas_peligrosas(codigo):
    with pytest.raises((ValueError, SyntaxError)):
        GeneradorPruebasEta._validar_codigo(codigo)


def test_red_team_requiere_funcion_pytest_y_tres_assert():
    with pytest.raises(ValueError, match="test_"):
        GeneradorPruebasEta._validar_codigo("assert True\nassert True\nassert True\n")
    with pytest.raises(ValueError, match="tres"):
        GeneradorPruebasEta._validar_codigo("def test_x():\n assert True\n")
