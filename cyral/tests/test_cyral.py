import mock

from datadog_checks.cyral.cyral import CyralCheck

CHECK_NAME = 'cyral'


data = """# HELP cyral_analysis_time Time spent in just doing analysis
# TYPE cyral_analysis_time counter
cyral_analysis_time{asg_instance="asg-test-04-cyral-sidecar-8474fb4ccb-2pd68"} 2.274237
# HELP cyral_analysis_time_counter Number of increments to analysis_time
# TYPE cyral_analysis_time_counter counter
cyral_analysis_time_counter{asg_instance="asg-test-04-cyral-sidecar-8474fb4ccb-2pd68"} 90
# HELP cyral_authentication_failure_count The number of authentication failures
# TYPE cyral_authentication_failure_count counter
cyral_authentication_failure_count{asg_instance="asg-test-04-cyral-sidecar-8474fb4ccb-2pd68"} 7
# HELP cyral_high_latency_query_count Number of queries exceeding (configurable) threshold
# TYPE cyral_high_latency_query_count counter
cyral_high_latency_query_count{asg_instance="asg-test-04-cyral-sidecar-8474fb4ccb-2pd68"} 4
# HELP cyral_policy_violation_count The number of queries with policy violations
# TYPE cyral_policy_violation_count counter
cyral_policy_violation_count{asg_instance="asg-test-04-cyral-sidecar-8474fb4ccb-2pd68"} 4
# HELP cyral_portscan_count The number of detected portscan attempts
# TYPE cyral_portscan_count counter
cyral_portscan_count{asg_instance="asg-test-04-cyral-sidecar-8474fb4ccb-2pd68"} 2
# HELP cyral_query_duration_count Number of increments to query_duration
# TYPE cyral_query_duration_count counter
cyral_query_duration_count{asg_instance="asg-test-04-cyral-sidecar-8474fb4ccb-2pd68"} 81841
# HELP cyral_query_duration_sum The total duration of queries in milliseconds
# TYPE cyral_query_duration_sum counter
cyral_query_duration_sum{asg_instance="asg-test-04-cyral-sidecar-8474fb4ccb-2pd68"} 4.293079095125004e+06
# HELP cyral_row_count The number of rows per query
# TYPE cyral_row_count counter
cyral_row_count{asg_instance="asg-test-04-cyral-sidecar-8474fb4ccb-2pd68"} 167535
# HELP cyral_sql_parse_time Time spent doing parsing in milliseconds
# TYPE cyral_sql_parse_time counter
cyral_sql_parse_time{asg_instance="asg-test-04-cyral-sidecar-8474fb4ccb-2pd68"} 4.190131
# HELP cyral_sql_parse_time_counter Number of increments to sql_parse_time
# TYPE cyral_sql_parse_time_counter counter
cyral_sql_parse_time_counter{asg_instance="asg-test-04-cyral-sidecar-8474fb4ccb-2pd68"} 60"""


def test_check_all_metrics(aggregator):
    instance = {'prometheus_endpoint': 'http://localhost:9018/metrics'}
    check = CyralCheck(CHECK_NAME, {}, {})
    response = mock.MagicMock(
        status_code=200, headers={"Content-Type": "text/plain"}, iter_lines=lambda **kw: data.split("\n")
    )
    with mock.patch("requests.get", return_value=response):
        check.check(instance)

    aggregator.assert_metric("cyral.analysis_time", count=1, value=2.274237)
