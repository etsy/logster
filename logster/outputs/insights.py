from logster.logster_helper import LogsterOutput
from httplib import *

import json
import os
import jsonpickle
import platform


class InsightsOutput(LogsterOutput):
    shortname = 'insights'

    @classmethod
    def add_options(cls, parser):
        parser.add_option('--stdout-separator', action='store', default="_", dest="stdout_separator",
                          help='Separator between prefix/suffix and name for stdout. Default is \"%default\".')
        parser.add_option('--event_type_name', action='store', default="Logster", dest="event_type_name",
                          help='Event Type as it will be used by Insights. Default is \"%default\".')
        parser.add_option('--insights_api_key', action='store',
                          default=os.getenv('INSIGHTS_API_KEY_ID'), help='New Relic Insights API Insert key')
        parser.add_option('--newrelic_account_number', action='store',
                          default=os.getenv('NEW_RELIC_ACCOUNT'), help='New Relic Account Number')
        parser.add_option('--integration_type', action='store',
                          default='standalone', help='Define New Relic Integration Type (ohi or standalone)')

    def __init__(self, parser, options, logger):
        super(InsightsOutput, self).__init__(parser, options, logger)
        self.separator = options.stdout_separator
        self.insights_url = 'insights-collector.newrelic.com'

        self.integration_type = options.integration_type

        if not options.newrelic_account_number or not options.insights_api_key:
            parser.print_help()
            parser.error(
                "You must supply --insights_api_key and --newrelic_account_number or Set environment variables. INSIGHTS_API_KEY_ID for --insights_api_key, NEW_RELIC_ACCOUNT for --newrelic_account_number")

        self.eventType = options.event_type_name
        self.newrelic_account_number = options.newrelic_account_number
        self.insights_api_key = options.insights_api_key
        self.full_url = '/v1/accounts/' + self.newrelic_account_number + '/events'

    def submit(self, metrics):

        eventData = []

        if self.integration_type == "standalone":

            for metric in metrics:
                metric.eventType = self.eventType
                metric.osName = os.name
                metric.platformSystem = platform.system()
                metric.platformRelease = platform.release()
                platform.python_version()
                eventData.append(metric)

            try:
                conn = HTTPSConnection(self.insights_url)
                headers = {
                    "Content-Type": "application/json",
                    "X-Insert-Key": self.insights_api_key
                }

                conn.request("POST", self.full_url, json.dumps([ob.__dict__ for ob in eventData.__iter__()]), headers)

                response = conn.getresponse()

                print response.status, response.reason

            except Exception as ex:
                raise Exception("Can't connect ", ex)
        else:
            for metric in metrics:
                metric.event_type = self.eventType
                eventData.append(metric)

            print jsonpickle.encode(self.getohistructure(eventData))

    def getohistructure(self, metrics):
        OHIDataEvent = {}
        OHIDataEvent["name"] = "com.newrelic.ohi"
        OHIDataEvent["protocol_version"] = "1"
        OHIDataEvent["integration_version"] = "1.0.0"
        OHIDataEvent["metrics"] = {}
        OHIDataEvent["metrics"] = metrics

        return OHIDataEvent

