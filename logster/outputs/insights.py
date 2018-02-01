import json
import os
from httplib import *

from logster.logster_helper import LogsterOutput


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

    def __init__(self, parser, options, logger):
        super(InsightsOutput, self).__init__(parser, options, logger)
        self.separator = options.stdout_separator
        self.insights_url = 'insights-collector.newrelic.com'

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

        for metric in metrics:
            metric.eventType = self.eventType
            eventData.append(metric)
            metric_name = self.get_metric_name(metric, self.separator)
            """ print("%s %s %s" % (metric.timestamp, metric_name, metric.value)) """

        try:
            conn = HTTPSConnection(self.insights_url)
            headers = {
                "Content-Type": "application/json",
                "X-Insert-Key": self.insights_api_key
            }

            """ print json.dumps([ob.__dict__ for ob in eventData]) """
            eee = self.getOHIStructure(eventData)

            print json.dumps([ob.__dict__ for ob in eee.itervalues()])

            response = conn.request("POST", self.full_url, json.dumps([ob.__dict__ for ob in eventData.itervalues()]), headers)

        except Exception as ex:
            raise Exception("Can't connect ", ex)

    def getOHIStructure(self, metrics):
        OHIDataEvent = {}
        OHIDataEvent["name"] = "com.newrelic.ohi"
        OHIDataEvent["protocol_version"] = "1"
        OHIDataEvent["integration_version"] = "1.0.0"
        OHIDataEvent["metrics"] = {}
        OHIDataEvent["metrics"] = metrics

        return OHIDataEvent

