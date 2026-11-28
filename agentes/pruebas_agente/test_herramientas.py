"""E4: mapa_repo (ast) y memoria de notas (anotar / leer_notas)."""
import pytest

from agente.contrato import validar_decision
from agente.herramientas import Herramientas
from agente.politica import Politica

CODIGO = '''"""Módulo de ejemplo."""


class Servicio(Base):
    """Servicio de ejemplo.

    Detalle que no debe salir en el mapa."""

    def actualizar(self, id_viaje, operador="A"):
        """Actualiza un viaje."""

    def _interno(self):
        pass


def calcular(a, b=2, *extra):
    return a + b
'''


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "servicio.py").write_text(CODIGO, encoding="utf-8")
    (tmp_path / "src" / "roto.py").write_text("def x(:\n", encoding="utf-8")
    (tmp_path / "src" / "__pycache__").mkdir()
    (tmp_path / "src" / "__pycache__" / "x.py").write_text("def oculto(): pass\n", encoding="utf-8")
    return Herramientas(tmp_path)


def test_mapa_repo_lista_clases_funciones_y_metodos_con_firma_y_linea(repo):
    mapa = repo.mapa_repo()
    assert "src/servicio.py" in mapa
    assert "class Servicio(Base) l.4 — Servicio de ejemplo." in mapa
    assert "    def actualizar(self, id_viaje, operador='A') l.9 — Actualiza un viaje." in mapa
    assert "  def calcular(a, b=2, *extra) l.16" in mapa
    assert "Detalle que no debe salir" not in mapa


def test_mapa_repo_informa_errores_de_sintaxis_e_ignora_pycache(repo):
    mapa = repo.mapa_repo()
    assert "src/roto.py  (ERROR de sintaxis en la línea 1)" in mapa
    assert "oculto" not in mapa


def test_mapa_repo_acepta_un_archivo_y_respeta_el_sandbox(repo):
    assert "def calcular" in repo.mapa_repo("src/servicio.py")
    assert repo.mapa_repo("no_existe").startswith("ERROR")
    with pytest.raises(PermissionError):
        repo.mapa_repo("..")


def test_notas_se_guardan_en_notas_md_y_se_leen(repo):
    assert repo.leer_notas() == "(sin notas)"
    assert repo.anotar("Hipótesis: el filtro usa 'in' sobre texto").startswith("OK: nota 1")
    assert repo.anotar("Revisado: servicio.py").startswith("OK: nota 2")
    assert repo.leer_notas() == "- Hipótesis: el filtro usa 'in' sobre texto\n- Revisado: servicio.py"
    assert (repo.raiz / "notas.md").read_text(encoding="utf-8").count("\n") == 2


def test_notas_se_normalizan_se_recortan_y_rechazan_las_vacias(repo):
    repo.anotar("línea 1\nlínea 2   con   espacios")
    assert repo.leer_notas() == "- línea 1 línea 2 con espacios"
    repo.anotar("x" * 1000)
    assert len(repo.leer_notas().splitlines()[1]) == 2 + 300
    assert repo.anotar("   ").startswith("ERROR")


def test_las_notas_no_cuentan_como_cambio_del_repositorio(tmp_path):
    copia, original = tmp_path / "copia", tmp_path / "original"
    copia.mkdir(), original.mkdir()
    h = Herramientas(copia, original)
    h.anotar("una hipótesis")
    assert h.archivos_modificados() == [] and h.ver_cambios() == "(sin cambios)"


def test_catalogo_documenta_las_herramientas_nuevas_y_el_contrato_las_acepta(repo):
    catalogo = repo.catalogo()
    for nombre in ("mapa_repo", "anotar", "leer_notas"):
        assert nombre in catalogo and len(catalogo[nombre]) > 60
    assert "ANTES de leer archivos completos" in catalogo["mapa_repo"]
    assert validar_decision({"pensamiento": "x", "accion": "mapa_repo", "args": {"ruta": "src"}}, set(catalogo))[0]
    assert Politica().evaluar("anotar", {"texto": "x"}, 1).permitido
