import pytest
from pydantic import ValidationError

from app.schemas.offre import OffreCreate


class TestOffreValidation:
    def test_offre_valide(self):
        offre = OffreCreate(
            titre="Data Engineer",
            mission="Mission suffisamment longue",
            competences=["Python", "python", "SQL"],
        )
        assert offre.competences == ["python", "sql"]

    def test_competences_vides_refusees(self):
        with pytest.raises(ValidationError):
            OffreCreate(
                titre="Data Engineer",
                mission="Mission suffisamment longue",
                competences=["   ", ""],
            )