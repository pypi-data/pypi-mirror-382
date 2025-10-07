"""Core screening functionality for bioscreen."""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    """Risk level classifications for screening results."""

    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


@dataclass
class MatchedTarget:
    """Information about a matched hazardous target.

    Attributes:
        protein_name: Name of the matched protein
        similarity_score: Similarity score between 0.0 and 1.0
    """

    protein_name: str
    similarity_score: float

    def __post_init__(self) -> None:
        """Validate matched target values."""
        if not 0.0 <= self.similarity_score <= 1.0:
            raise ValueError("Similarity score must be between 0.0 and 1.0")


@dataclass
class ScreeningResult:
    """Result from screening a protein target.

    Attributes:
        flagged: Whether the target was flagged as potentially hazardous
        risk_level: Risk classification (GREEN, YELLOW, or RED)
        reason: Explanation for the screening result
        matched_target: Optional information about matched hazardous protein
    """

    flagged: bool
    risk_level: RiskLevel
    reason: str
    matched_target: Optional[MatchedTarget] = None


class ProteinScreener:
    """Screen protein design requests for potential biosecurity hazards.

    This is v0.1.0 - a minimal implementation for infrastructure testing.
    Future versions will include actual screening logic and database integration.
    """

    # Standard 20 amino acids (one-letter codes)
    VALID_AMINO_ACIDS = set("ACDEFGHIKLMNPQRSTVWY")

    def __init__(
        self,
        api_key: Optional[str] = None,
        enable_logging: bool = False,
        use_local: bool = True,
    ) -> None:
        """Initialize the protein screener.

        Args:
            api_key: API key for remote Supabase database (if use_local=False)
            enable_logging: Whether to enable logging for screening operations
            use_local: Use local screening (True) or remote database (False)

        Raises:
            ValueError: If use_local=False but no api_key provided
        """
        self.api_key = api_key
        self.enable_logging = enable_logging
        self.use_local = use_local

        if not use_local and not api_key:
            raise ValueError("API key required when use_local=False")

        if enable_logging:
            logging.basicConfig(level=logging.INFO)

    def _validate_sequence(self, sequence: str) -> None:
        """Validate that a sequence contains only valid amino acid characters.

        Args:
            sequence: The protein sequence to validate

        Raises:
            ValueError: If sequence contains invalid amino acid characters
        """
        sequence_upper = sequence.upper()
        invalid_chars = set(sequence_upper) - self.VALID_AMINO_ACIDS
        if invalid_chars:
            raise ValueError(
                f"Invalid amino acid characters: {', '.join(sorted(invalid_chars))}"
            )

    def screen_protein(
        self, target_sequence: str, user_email: Optional[str] = None
    ) -> ScreeningResult:
        """Screen a target protein sequence for potential hazards.

        Args:
            target_sequence: The target protein sequence to screen (amino acid sequence)
            user_email: Optional user email for managed access deployments

        Returns:
            ScreeningResult with flagged status, risk level, and details

        Raises:
            ValueError: If target_sequence is empty or has invalid amino acids
        """
        if not target_sequence or not target_sequence.strip():
            raise ValueError("Target sequence cannot be empty")

        # Validate amino acid sequence
        self._validate_sequence(target_sequence)

        if self.enable_logging:
            logger.info(
                f"Screening target protein sequence (length: {len(target_sequence)}, "
                f"user: {user_email or 'anonymous'})"
            )

        # v0.1.0: Simple placeholder implementation
        # Future versions will implement:
        # - Actual sequence analysis
        # - Database lookups (local or remote via Supabase)
        # - User access management
        return ScreeningResult(
            flagged=False,
            risk_level=RiskLevel.GREEN,
            reason="v0.1.0: No screening rules implemented yet",
            matched_target=None,
        )

    def screen_batch(
        self, target_sequences: list[str], user_email: Optional[str] = None
    ) -> list[ScreeningResult]:
        """Screen multiple target protein sequences.

        Args:
            target_sequences: List of target protein sequences to screen
            user_email: Optional user email for managed access deployments

        Returns:
            List of ScreeningResult objects, one per sequence

        Raises:
            ValueError: If target_sequences list is empty
        """
        if not target_sequences:
            raise ValueError("Target sequences list cannot be empty")

        return [self.screen_protein(seq, user_email) for seq in target_sequences]
