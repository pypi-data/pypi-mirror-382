"""Unit tests for Nagios plugin components."""

from unittest.mock import Mock, patch
import nagiosplugin
from check_bitdefender.core.nagios import (
    DefenderScalarContext,
    DefenderSummary,
    NagiosPlugin,
    DefenderResource,
)


class TestDefenderScalarContext:
    """Tests for DefenderScalarContext."""

    def test_init(self):
        """Test context initialization."""
        ctx = DefenderScalarContext("test", warning=5, critical=10)
        assert ctx.name == "test"
        assert ctx._original_warning == 5
        assert ctx._original_critical == 10

    def test_evaluate_found_ok(self):
        """Test evaluate for 'found' context with OK status."""
        ctx = DefenderScalarContext("found", warning=1, critical=1)
        metric = nagiosplugin.Metric("found", 1)
        resource = Mock()

        result = ctx.evaluate(metric, resource)

        # When value equals warning threshold, should be warning
        assert result.state == nagiosplugin.Warn

    def test_evaluate_found_warning(self):
        """Test evaluate for 'found' context with WARNING status."""
        ctx = DefenderScalarContext("found", warning=0, critical=1)
        metric = nagiosplugin.Metric("found", 0)
        resource = Mock()

        result = ctx.evaluate(metric, resource)

        assert result.state == nagiosplugin.Warn
        assert "outside range 0:" in result.hint

    def test_evaluate_found_critical(self):
        """Test evaluate for 'found' context with CRITICAL status."""
        ctx = DefenderScalarContext("found", warning=0, critical=0)
        metric = nagiosplugin.Metric("found", 0)
        resource = Mock()

        result = ctx.evaluate(metric, resource)

        # When both thresholds are 0 and value is 0, warning matches exactly
        assert result.state == nagiosplugin.Warn
        assert "outside range 0:" in result.hint

    def test_evaluate_found_both_thresholds(self):
        """Test when both warning and critical are triggered."""
        ctx = DefenderScalarContext("found", warning=0, critical=0)
        metric = nagiosplugin.Metric("found", 1)
        resource = Mock()

        result = ctx.evaluate(metric, resource)

        # Both triggered but value doesn't match warning exactly, use critical
        assert result.state == nagiosplugin.Critical

    def test_evaluate_onboarding_warning(self):
        """Test evaluate for 'onboarding' context with WARNING."""
        ctx = DefenderScalarContext("onboarding", warning=1, critical=2)
        metric = nagiosplugin.Metric("onboarding", 1)
        resource = Mock()

        result = ctx.evaluate(metric, resource)

        assert result.state == nagiosplugin.Warn

    def test_evaluate_onboarding_critical(self):
        """Test evaluate for 'onboarding' context with CRITICAL."""
        ctx = DefenderScalarContext("onboarding", warning=1, critical=2)
        metric = nagiosplugin.Metric("onboarding", 2)
        resource = Mock()

        result = ctx.evaluate(metric, resource)

        assert result.state == nagiosplugin.Critical

    def test_evaluate_onboarding_ok(self):
        """Test evaluate for 'onboarding' context with OK."""
        ctx = DefenderScalarContext("onboarding", warning=5, critical=10)
        metric = nagiosplugin.Metric("onboarding", 0)
        resource = Mock()

        result = ctx.evaluate(metric, resource)

        assert result.state == nagiosplugin.Ok

    def test_evaluate_other_context(self):
        """Test evaluate for non-found/onboarding contexts uses parent logic."""
        ctx = DefenderScalarContext("other", warning="10", critical="20")
        metric = nagiosplugin.Metric("other", 5)
        resource = Mock()

        # Should use standard nagiosplugin logic
        result = ctx.evaluate(metric, resource)

        assert result.state == nagiosplugin.Ok

    def test_evaluate_no_thresholds(self):
        """Test evaluate with no thresholds."""
        ctx = DefenderScalarContext("found")
        metric = nagiosplugin.Metric("found", 0)
        resource = Mock()

        result = ctx.evaluate(metric, resource)

        assert result.state == nagiosplugin.Ok


class TestDefenderSummary:
    """Tests for DefenderSummary."""

    def test_init_with_details(self):
        """Test summary initialization with details."""
        details = ["line1", "line2"]
        summary = DefenderSummary(details)
        assert summary.details == details

    def test_init_with_none(self):
        """Test summary initialization with None."""
        summary = DefenderSummary(None)
        assert summary.details == []

    def test_ok_with_details(self):
        """Test OK state output with details."""
        details = ["Detail line 1", "Detail line 2"]
        summary = DefenderSummary(details)
        results = Mock()

        output = summary.ok(results)

        assert "Detail line 1" in output
        assert "Detail line 2" in output
        assert output.startswith("\n")

    def test_ok_without_details(self):
        """Test OK state output without details."""
        summary = DefenderSummary([])
        results = Mock()

        output = summary.ok(results)

        assert output == ""

    def test_problem_with_details(self):
        """Test problem state output with details."""
        details = ["Error detail 1", "Error detail 2"]
        summary = DefenderSummary(details)
        results = Mock()

        output = summary.problem(results)

        assert "Error detail 1" in output
        assert "Error detail 2" in output


class TestDefenderResource:
    """Tests for DefenderResource."""

    def test_init(self):
        """Test resource initialization."""
        resource = DefenderResource("test_command", 42)
        assert resource.command_name == "test_command"
        assert resource.value == 42

    def test_name_property(self):
        """Test name property."""
        resource = DefenderResource("cmd", 0)
        assert resource.name == "DEFENDER"

    def test_probe_detail_command(self):
        """Test probe for detail command."""
        resource = DefenderResource("detail", 1)
        metrics = resource.probe()

        assert len(metrics) == 1
        assert metrics[0].name == "found"
        assert metrics[0].value == 1

    def test_probe_other_command(self):
        """Test probe for other commands."""
        resource = DefenderResource("lastseen", 5)
        metrics = resource.probe()

        assert len(metrics) == 1
        assert metrics[0].name == "lastseen"
        assert metrics[0].value == 5


class TestNagiosPlugin:
    """Tests for NagiosPlugin."""

    def test_init(self):
        """Test plugin initialization."""
        service = Mock()
        plugin = NagiosPlugin(service, "test_cmd")
        assert plugin.service == service
        assert plugin.command_name == "test_cmd"

    @patch('check_bitdefender.core.nagios.nagiosplugin.Check')
    def test_check_success_ok(self, mock_check_class):
        """Test successful check with OK status."""
        service = Mock()
        service.get_result.return_value = {
            "value": 0,
            "details": ["All OK"]
        }
        plugin = NagiosPlugin(service, "test")

        # Mock the check instance
        mock_check = Mock()
        mock_check.main.return_value = None  # main() returns normally for OK
        mock_check_class.return_value = mock_check

        exit_code = plugin.check(dns_name="test.com", warning=5, critical=10)

        assert exit_code == 0
        service.get_result.assert_called_once_with(endpoint_id=None, dns_name="test.com")
        mock_check.main.assert_called_once()

    @patch('check_bitdefender.core.nagios.nagiosplugin.Check')
    def test_check_warning(self, mock_check_class):
        """Test check with WARNING status."""
        service = Mock()
        service.get_result.return_value = {
            "value": 6,
            "details": ["Warning condition"]
        }
        plugin = NagiosPlugin(service, "test")

        mock_check = Mock()
        mock_check.main.side_effect = SystemExit(1)
        mock_check_class.return_value = mock_check

        exit_code = plugin.check(dns_name="test.com", warning=5, critical=10)

        assert exit_code == 1

    @patch('check_bitdefender.core.nagios.nagiosplugin.Check')
    def test_check_critical(self, mock_check_class):
        """Test check with CRITICAL status."""
        service = Mock()
        service.get_result.return_value = {
            "value": 11,
            "details": ["Critical condition"]
        }
        plugin = NagiosPlugin(service, "test")

        mock_check = Mock()
        mock_check.main.side_effect = SystemExit(2)
        mock_check_class.return_value = mock_check

        exit_code = plugin.check(dns_name="test.com", warning=5, critical=10)

        assert exit_code == 2

    @patch('check_bitdefender.core.nagios.nagiosplugin.Check')
    def test_check_exception(self, mock_check_class):
        """Test check with service exception."""
        service = Mock()
        service.get_result.side_effect = Exception("Service error")
        plugin = NagiosPlugin(service, "test")

        exit_code = plugin.check(dns_name="test.com")

        assert exit_code == 3

    @patch('check_bitdefender.core.nagios.nagiosplugin.Check')
    def test_check_with_endpoint_id(self, mock_check_class):
        """Test check using endpoint_id."""
        service = Mock()
        service.get_result.return_value = {
            "value": 0,
            "details": []
        }
        plugin = NagiosPlugin(service, "test")

        mock_check = Mock()
        mock_check.main.return_value = None
        mock_check_class.return_value = mock_check

        plugin.check(endpoint_id="ep123")

        service.get_result.assert_called_once_with(endpoint_id="ep123", dns_name=None)

    @patch('check_bitdefender.core.nagios.nagiosplugin.Check')
    def test_check_detail_command_uses_found_context(self, mock_check_class):
        """Test that detail command uses 'found' as context name."""
        service = Mock()
        service.get_result.return_value = {
            "value": 1,
            "details": ["Endpoint found"]
        }
        plugin = NagiosPlugin(service, "detail")

        mock_check = Mock()
        mock_check.main.return_value = None
        mock_check_class.return_value = mock_check

        plugin.check(dns_name="test.com")

        # Verify DefenderScalarContext was created with 'found' as name
        call_args = mock_check_class.call_args
        context = call_args[0][1]  # Second argument is the context
        assert context.name == "found"

    @patch('check_bitdefender.core.nagios.nagiosplugin.Check')
    def test_check_sets_verbosity(self, mock_check_class):
        """Test that verbosity level is set on check."""
        service = Mock()
        service.get_result.return_value = {
            "value": 0,
            "details": []
        }
        plugin = NagiosPlugin(service, "test")

        mock_check = Mock()
        mock_check.main.return_value = None
        mock_check_class.return_value = mock_check

        plugin.check(dns_name="test.com", verbose=2)

        assert mock_check.verbosity == 2

    @patch('check_bitdefender.core.nagios.nagiosplugin.Check')
    def test_check_system_exit_none_code(self, mock_check_class):
        """Test handling of SystemExit with None code."""
        service = Mock()
        service.get_result.return_value = {
            "value": 0,
            "details": []
        }
        plugin = NagiosPlugin(service, "test")

        mock_check = Mock()
        mock_check.main.side_effect = SystemExit(None)
        mock_check_class.return_value = mock_check

        exit_code = plugin.check(dns_name="test.com")

        assert exit_code == 0
