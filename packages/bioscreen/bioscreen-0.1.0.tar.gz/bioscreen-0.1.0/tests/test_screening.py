"""Tests for bioscreen screening functionality."""

import pytest

from bioscreen import MatchedTarget, ProteinScreener, RiskLevel, ScreeningResult


class TestRiskLevel:
    """Tests for RiskLevel enum."""

    def test_risk_level_enum_values(self) -> None:
        """Test that risk levels use consistent values."""
        assert RiskLevel.GREEN.value == "green"
        assert RiskLevel.YELLOW.value == "yellow"
        assert RiskLevel.RED.value == "red"

    def test_risk_level_string_comparison(self) -> None:
        """Test that RiskLevel can be compared with strings."""
        assert RiskLevel.GREEN == "green"
        assert RiskLevel.YELLOW == "yellow"
        assert RiskLevel.RED == "red"


class TestMatchedTarget:
    """Tests for MatchedTarget dataclass."""

    def test_valid_matched_target(self) -> None:
        """Test creating a valid matched target."""
        target = MatchedTarget(protein_name="Test Protein", similarity_score=0.95)
        assert target.protein_name == "Test Protein"
        assert target.similarity_score == 0.95

    def test_invalid_similarity_score_too_high(self) -> None:
        """Test that similarity scores above 1.0 raise ValueError."""
        with pytest.raises(ValueError, match="Similarity score must be between"):
            MatchedTarget(protein_name="Test", similarity_score=1.5)

    def test_invalid_similarity_score_too_low(self) -> None:
        """Test that similarity scores below 0.0 raise ValueError."""
        with pytest.raises(ValueError, match="Similarity score must be between"):
            MatchedTarget(protein_name="Test", similarity_score=-0.1)


class TestScreeningResult:
    """Tests for ScreeningResult dataclass."""

    def test_screening_result_not_flagged(self) -> None:
        """Test creating a screening result with no flag."""
        result = ScreeningResult(
            flagged=False, risk_level=RiskLevel.GREEN, reason="Safe sequence"
        )
        assert result.flagged is False
        assert result.risk_level == RiskLevel.GREEN
        assert result.reason == "Safe sequence"
        assert result.matched_target is None

    def test_screening_result_flagged_with_match(self) -> None:
        """Test creating a flagged screening result with matched target."""
        matched = MatchedTarget(protein_name="Hazardous Protein", similarity_score=0.99)
        result = ScreeningResult(
            flagged=True,
            risk_level=RiskLevel.RED,
            reason="High-risk protein detected",
            matched_target=matched,
        )
        assert result.flagged is True
        assert result.risk_level == RiskLevel.RED
        assert result.matched_target is not None
        assert result.matched_target.protein_name == "Hazardous Protein"


class TestProteinScreener:
    """Tests for ProteinScreener class."""

    def test_init_local_mode(self) -> None:
        """Test initializing screener in local mode."""
        screener = ProteinScreener(use_local=True)
        assert screener.use_local is True
        assert screener.api_key is None

    def test_init_remote_mode_with_api_key(self) -> None:
        """Test initializing screener in remote mode with API key."""
        screener = ProteinScreener(api_key="test_key", use_local=False)
        assert screener.use_local is False
        assert screener.api_key == "test_key"

    def test_init_remote_mode_without_api_key(self) -> None:
        """Test that remote mode without API key raises ValueError."""
        with pytest.raises(ValueError, match="API key required"):
            ProteinScreener(use_local=False)

    def test_screen_protein_valid_sequence(self) -> None:
        """Test screening a valid protein sequence."""
        screener = ProteinScreener()
        result = screener.screen_protein("MKTAYIAKQRQISFVKSHFSRQ")

        assert isinstance(result, ScreeningResult)
        assert result.flagged is False
        assert result.risk_level == RiskLevel.GREEN
        assert "v0.1.0" in result.reason

    def test_screen_protein_with_user_email(self) -> None:
        """Test screening with user email parameter."""
        screener = ProteinScreener(enable_logging=True)
        result = screener.screen_protein(
            "MKTAYIAKQRQISFVKSHFSRQ", user_email="test@example.com"
        )

        assert isinstance(result, ScreeningResult)
        assert result.flagged is False

    def test_screen_protein_empty_sequence(self) -> None:
        """Test that empty sequence raises ValueError."""
        screener = ProteinScreener()
        with pytest.raises(ValueError, match="Target sequence cannot be empty"):
            screener.screen_protein("")

    def test_screen_protein_none_sequence(self) -> None:
        """Test that None sequence raises ValueError."""
        screener = ProteinScreener()
        with pytest.raises(ValueError, match="Target sequence cannot be empty"):
            screener.screen_protein(None)  # type: ignore

    def test_screen_protein_whitespace_only(self) -> None:
        """Test that whitespace-only sequence raises ValueError."""
        screener = ProteinScreener()
        with pytest.raises(ValueError, match="Target sequence cannot be empty"):
            screener.screen_protein("   ")

    def test_invalid_amino_acid_sequence(self) -> None:
        """Test sequence with invalid characters."""
        screener = ProteinScreener()
        with pytest.raises(ValueError, match="Invalid amino acid"):
            screener.screen_protein("INVALID123")

    def test_screen_batch_valid_sequences(self) -> None:
        """Test screening multiple valid sequences."""
        screener = ProteinScreener()
        sequences = [
            "MKTAYIAKQRQISFVKSHFSRQ",
            "ACDEFGHIKLMNPQRSTVWY",
            "MGSSHHHHHHSSGLVPRGSH",
        ]
        results = screener.screen_batch(sequences)

        assert len(results) == 3
        assert all(isinstance(r, ScreeningResult) for r in results)
        assert all(r.flagged is False for r in results)
        assert all(r.risk_level == RiskLevel.GREEN for r in results)

    def test_screen_batch_with_user_email(self) -> None:
        """Test batch screening with user email."""
        screener = ProteinScreener()
        sequences = ["MKTAYIAKQRQISFVKSHFSRQ", "ACDEFGHIKLMNPQRSTVWY"]
        results = screener.screen_batch(sequences, user_email="test@example.com")

        assert len(results) == 2
        assert all(isinstance(r, ScreeningResult) for r in results)

    def test_screen_batch_empty_list(self) -> None:
        """Test that empty sequence list raises ValueError."""
        screener = ProteinScreener()
        with pytest.raises(ValueError, match="Target sequences list cannot be empty"):
            screener.screen_batch([])

    def test_screen_batch_preserves_order(self) -> None:
        """Test that batch screening preserves input order."""
        screener = ProteinScreener()
        sequences = ["AAA", "CCC", "GGG"]
        results = screener.screen_batch(sequences)

        assert len(results) == len(sequences)
        # In v0.1.0 all results are the same, but order should be preserved

    def test_valid_amino_acids_constant(self) -> None:
        """Test that VALID_AMINO_ACIDS contains all 20 standard amino acids."""
        assert len(ProteinScreener.VALID_AMINO_ACIDS) == 20
        assert set("ACDEFGHIKLMNPQRSTVWY") == ProteinScreener.VALID_AMINO_ACIDS

    def test_lowercase_sequence_accepted(self) -> None:
        """Test that lowercase sequences are accepted."""
        screener = ProteinScreener()
        result = screener.screen_protein("mktayiakqrqisfvkshfsrq")
        assert isinstance(result, ScreeningResult)
        assert result.flagged is False

    def test_mixed_case_sequence_accepted(self) -> None:
        """Test that mixed case sequences are accepted."""
        screener = ProteinScreener()
        result = screener.screen_protein("MkTaYiAkQrQiSfVkShFsRq")
        assert isinstance(result, ScreeningResult)
        assert result.flagged is False


class TestIntegration:
    """Integration tests for full workflow."""

    def test_full_screening_workflow(self) -> None:
        """Test complete screening workflow from initialization to results."""
        # Initialize screener
        screener = ProteinScreener(enable_logging=False, use_local=True)

        # Screen single sequence
        result = screener.screen_protein("MKTAYIAKQRQISFVKSHFSRQ")
        assert isinstance(result, ScreeningResult)

        # Screen batch
        batch_results = screener.screen_batch(
            ["MKTAYIAKQRQISFVKSHFSRQ", "ACDEFGHIKLMNPQRSTVWY"]
        )
        assert len(batch_results) == 2

    def test_import_all_exports(self) -> None:
        """Test that all exported classes are importable."""
        from bioscreen import (
            MatchedTarget,
            ProteinScreener,
            RiskLevel,
            ScreeningResult,
        )

        assert ProteinScreener is not None
        assert ScreeningResult is not None
        assert MatchedTarget is not None
        assert RiskLevel is not None
