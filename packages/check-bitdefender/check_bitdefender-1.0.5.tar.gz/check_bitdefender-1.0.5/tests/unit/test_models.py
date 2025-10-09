"""Unit tests for data models."""

from datetime import datetime, timezone
from check_bitdefender.services.models import (
    OnboardingStatus,
    Endpoint,
    Vulnerability,
    VulnerabilityScore,
)


class TestOnboardingStatus:
    """Tests for OnboardingStatus enum."""

    def test_onboarded_value(self):
        """Test ONBOARDED enum value."""
        assert OnboardingStatus.ONBOARDED.value == 0

    def test_insufficient_info_value(self):
        """Test INSUFFICIENT_INFO enum value."""
        assert OnboardingStatus.INSUFFICIENT_INFO.value == 1

    def test_unknown_value(self):
        """Test UNKNOWN enum value."""
        assert OnboardingStatus.UNKNOWN.value == 2

    def test_enum_names(self):
        """Test enum member names."""
        assert OnboardingStatus.ONBOARDED.name == "ONBOARDED"
        assert OnboardingStatus.INSUFFICIENT_INFO.name == "INSUFFICIENT_INFO"
        assert OnboardingStatus.UNKNOWN.name == "UNKNOWN"

    def test_enum_members_count(self):
        """Test total number of enum members."""
        assert len(OnboardingStatus) == 3

    def test_enum_iteration(self):
        """Test iterating over enum members."""
        statuses = list(OnboardingStatus)
        assert len(statuses) == 3
        assert OnboardingStatus.ONBOARDED in statuses
        assert OnboardingStatus.INSUFFICIENT_INFO in statuses
        assert OnboardingStatus.UNKNOWN in statuses


class TestEndpoint:
    """Tests for Endpoint dataclass."""

    def test_init_required_fields(self):
        """Test initialization with required fields only."""
        endpoint = Endpoint(
            id="ep123",
            computer_dns_name="test.domain.com"
        )
        assert endpoint.id == "ep123"
        assert endpoint.computer_dns_name == "test.domain.com"
        assert endpoint.last_seen is None
        assert endpoint.onboarding_status is None

    def test_init_all_fields(self):
        """Test initialization with all fields."""
        last_seen = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        endpoint = Endpoint(
            id="ep456",
            computer_dns_name="server.example.com",
            last_seen=last_seen,
            onboarding_status=OnboardingStatus.ONBOARDED
        )
        assert endpoint.id == "ep456"
        assert endpoint.computer_dns_name == "server.example.com"
        assert endpoint.last_seen == last_seen
        assert endpoint.onboarding_status == OnboardingStatus.ONBOARDED

    def test_last_seen_optional(self):
        """Test that last_seen is optional."""
        endpoint = Endpoint(id="ep1", computer_dns_name="host1")
        assert endpoint.last_seen is None

    def test_onboarding_status_optional(self):
        """Test that onboarding_status is optional."""
        endpoint = Endpoint(id="ep1", computer_dns_name="host1")
        assert endpoint.onboarding_status is None

    def test_onboarding_status_values(self):
        """Test different onboarding status values."""
        endpoint1 = Endpoint(
            id="ep1",
            computer_dns_name="host1",
            onboarding_status=OnboardingStatus.ONBOARDED
        )
        assert endpoint1.onboarding_status == OnboardingStatus.ONBOARDED

        endpoint2 = Endpoint(
            id="ep2",
            computer_dns_name="host2",
            onboarding_status=OnboardingStatus.INSUFFICIENT_INFO
        )
        assert endpoint2.onboarding_status == OnboardingStatus.INSUFFICIENT_INFO

        endpoint3 = Endpoint(
            id="ep3",
            computer_dns_name="host3",
            onboarding_status=OnboardingStatus.UNKNOWN
        )
        assert endpoint3.onboarding_status == OnboardingStatus.UNKNOWN

    def test_equality(self):
        """Test endpoint equality."""
        last_seen = datetime(2024, 1, 1, tzinfo=timezone.utc)
        endpoint1 = Endpoint(
            id="ep1",
            computer_dns_name="host1",
            last_seen=last_seen,
            onboarding_status=OnboardingStatus.ONBOARDED
        )
        endpoint2 = Endpoint(
            id="ep1",
            computer_dns_name="host1",
            last_seen=last_seen,
            onboarding_status=OnboardingStatus.ONBOARDED
        )
        assert endpoint1 == endpoint2

    def test_inequality(self):
        """Test endpoint inequality."""
        endpoint1 = Endpoint(id="ep1", computer_dns_name="host1")
        endpoint2 = Endpoint(id="ep2", computer_dns_name="host2")
        assert endpoint1 != endpoint2


class TestVulnerability:
    """Tests for Vulnerability dataclass."""

    def test_init_required_fields(self):
        """Test initialization with required fields only."""
        vuln = Vulnerability(
            id="vuln1",
            severity="High",
            title="Security Issue"
        )
        assert vuln.id == "vuln1"
        assert vuln.severity == "High"
        assert vuln.title == "Security Issue"
        assert vuln.description is None

    def test_init_all_fields(self):
        """Test initialization with all fields."""
        vuln = Vulnerability(
            id="vuln2",
            severity="Critical",
            title="Remote Code Execution",
            description="Allows remote attacker to execute code"
        )
        assert vuln.id == "vuln2"
        assert vuln.severity == "Critical"
        assert vuln.title == "Remote Code Execution"
        assert vuln.description == "Allows remote attacker to execute code"

    def test_description_optional(self):
        """Test that description is optional."""
        vuln = Vulnerability(id="v1", severity="Low", title="Issue")
        assert vuln.description is None

    def test_different_severities(self):
        """Test vulnerabilities with different severity levels."""
        critical = Vulnerability(id="v1", severity="Critical", title="Critical Issue")
        high = Vulnerability(id="v2", severity="High", title="High Issue")
        medium = Vulnerability(id="v3", severity="Medium", title="Medium Issue")
        low = Vulnerability(id="v4", severity="Low", title="Low Issue")

        assert critical.severity == "Critical"
        assert high.severity == "High"
        assert medium.severity == "Medium"
        assert low.severity == "Low"

    def test_equality(self):
        """Test vulnerability equality."""
        vuln1 = Vulnerability(
            id="v1",
            severity="High",
            title="Issue",
            description="Details"
        )
        vuln2 = Vulnerability(
            id="v1",
            severity="High",
            title="Issue",
            description="Details"
        )
        assert vuln1 == vuln2

    def test_inequality(self):
        """Test vulnerability inequality."""
        vuln1 = Vulnerability(id="v1", severity="High", title="Issue1")
        vuln2 = Vulnerability(id="v2", severity="High", title="Issue2")
        assert vuln1 != vuln2


class TestVulnerabilityScore:
    """Tests for VulnerabilityScore dataclass."""

    def test_init_defaults(self):
        """Test initialization with default values."""
        score = VulnerabilityScore()
        assert score.critical == 0
        assert score.high == 0
        assert score.medium == 0
        assert score.low == 0

    def test_init_custom_values(self):
        """Test initialization with custom values."""
        score = VulnerabilityScore(critical=2, high=5, medium=10, low=15)
        assert score.critical == 2
        assert score.high == 5
        assert score.medium == 10
        assert score.low == 15

    def test_total_score_all_zeros(self):
        """Test total score calculation with all zeros."""
        score = VulnerabilityScore()
        assert score.total_score == 0

    def test_total_score_critical_only(self):
        """Test total score with only critical vulnerabilities."""
        score = VulnerabilityScore(critical=3)
        assert score.total_score == 300  # 3 * 100

    def test_total_score_high_only(self):
        """Test total score with only high vulnerabilities."""
        score = VulnerabilityScore(high=5)
        assert score.total_score == 50  # 5 * 10

    def test_total_score_medium_only(self):
        """Test total score with only medium vulnerabilities."""
        score = VulnerabilityScore(medium=8)
        assert score.total_score == 40  # 8 * 5

    def test_total_score_low_only(self):
        """Test total score with only low vulnerabilities."""
        score = VulnerabilityScore(low=20)
        assert score.total_score == 20  # 20 * 1

    def test_total_score_mixed(self):
        """Test total score with mixed severity levels."""
        score = VulnerabilityScore(critical=1, high=2, medium=3, low=4)
        # 1*100 + 2*10 + 3*5 + 4*1 = 100 + 20 + 15 + 4 = 139
        assert score.total_score == 139

    def test_total_score_complex(self):
        """Test total score with complex values."""
        score = VulnerabilityScore(critical=5, high=10, medium=20, low=50)
        # 5*100 + 10*10 + 20*5 + 50*1 = 500 + 100 + 100 + 50 = 750
        assert score.total_score == 750

    def test_total_score_property_is_calculated(self):
        """Test that total_score is a calculated property."""
        score = VulnerabilityScore(critical=1, high=1, medium=1, low=1)
        initial_total = score.total_score
        assert initial_total == 116  # 100 + 10 + 5 + 1

        # Modify values and verify score recalculates
        score.critical = 2
        assert score.total_score == 216  # 200 + 10 + 5 + 1

    def test_equality(self):
        """Test vulnerability score equality."""
        score1 = VulnerabilityScore(critical=1, high=2, medium=3, low=4)
        score2 = VulnerabilityScore(critical=1, high=2, medium=3, low=4)
        assert score1 == score2

    def test_inequality(self):
        """Test vulnerability score inequality."""
        score1 = VulnerabilityScore(critical=1, high=2, medium=3, low=4)
        score2 = VulnerabilityScore(critical=2, high=2, medium=3, low=4)
        assert score1 != score2

    def test_zero_with_explicit_zeros(self):
        """Test explicit zeros produce zero score."""
        score = VulnerabilityScore(critical=0, high=0, medium=0, low=0)
        assert score.total_score == 0

    def test_weights_are_correct(self):
        """Test that severity weights are applied correctly."""
        # Critical weight = 100
        score_critical = VulnerabilityScore(critical=1)
        assert score_critical.total_score == 100

        # High weight = 10
        score_high = VulnerabilityScore(high=1)
        assert score_high.total_score == 10

        # Medium weight = 5
        score_medium = VulnerabilityScore(medium=1)
        assert score_medium.total_score == 5

        # Low weight = 1
        score_low = VulnerabilityScore(low=1)
        assert score_low.total_score == 1
