from datadog_checks.base import AgentCheck
from datadog_checks.base.errors import CheckException
from datadog_checks.utils.subprocess_output import get_subprocess_output
import json

EXPECTED_RESPONSE_CODE = "NO_ERROR"


class LighthouseCheck(AgentCheck):
    def check(self, instance):
        lighthouse_url = instance.get('url')
        lighthouse_name = instance.get('name')

        if not lighthouse_url or not lighthouse_name:
            self.log.error("missing instance url or name")
            raise CheckException("missing lighthouse instance url or name, please fix yaml")

        cmd = ["lighthouse",
               lighthouse_url,
               "--output",
               "json",
               "--quiet",
               "--chrome-flags='--headless'"]

        json_string, error_message, exit_code = LighthouseCheck._get_lighthouse_report(cmd, self.log, False)

        # check for error since we have raise_on_empty_output set to False
        if exit_code > 0:
            self.log.error("lighthouse subprocess error {0} exit code {1} for url: {2}"
                           .format(error_message, exit_code, lighthouse_url)
                           )
            raise CheckException(json_string, error_message, exit_code)

        try:
            data = json.loads(json_string)
        except Exception as e:
            self.log.warn("lighthouse response JSON different than expected for url: {0}".format(lighthouse_url))
            raise CheckException(error_message, exit_code, e)

        if data["runtimeError"]["code"] == EXPECTED_RESPONSE_CODE:
            score_accessibility = round(data["categories"]["accessibility"]["score"] * 100)
            score_best_practices = round(data["categories"]["best-practices"]["score"] * 100)
            score_performance = round(data["categories"]["performance"]["score"] * 100)
            score_pwa = round(data["categories"]["pwa"]["score"] * 100)
            score_seo = round(data["categories"]["seo"]["score"] * 100)
        else:
            err_code = data["runtimeError"]["code"]
            err_msg = data["runtimeError"]["message"]
            self.log.warn("not collecting lighthouse metrics for url {0} runtimeError code {1} message {2}"
                          .format(lighthouse_url, err_code, err_msg)
                          )
            return
        # add tags

        tags = instance.get('tags', [])
        if type(tags) != list:
            self.log.warn('The tags list in the lighthouse check is not configured properly')
            tags = []

        tags.append("url:{0}".format(lighthouse_url))
        tags.append("name:{0}".format(lighthouse_name))

        self.gauge("lighthouse.accessibility", score_accessibility, tags=tags)
        self.gauge("lighthouse.best_practices", score_best_practices, tags=tags)
        self.gauge("lighthouse.performance", score_performance, tags=tags)
        self.gauge("lighthouse.pwa", score_pwa, tags=tags)
        self.gauge("lighthouse.seo", score_seo, tags=tags)

    @staticmethod
    def _get_lighthouse_report(command, logger, raise_on_empty=False):
        json, err_msg, exit_code = get_subprocess_output(command, logger, raise_on_empty_output=raise_on_empty)
        return json, err_msg, exit_code
