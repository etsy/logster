###  A logster parser file that can be used to count the number
###  of sent/deferred/bounced emails from a Postfix log, along with
### some other associated statistics.
###         
###  For example:
###  sudo ./logster --dry-run --output=ganglia PostfixParser /var/log/maillog
###            
###            
###  Copyright 2011, Bronto Software, Inc.
###               
###  This parser is free software: you can redistribute it and/or modify
###  it under the terms of the GNU General Public License as published by
###  the Free Software Foundation, either version 3 of the License, or
###  (at your option) any later version.
###
###  This parser is distributed in the hope that it will be useful,
###  but WITHOUT ANY WARRANTY; without even the implied warranty of
###  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
###  GNU General Public License for more details.
### 
        
import time
import re
        
from logster.logster_helper import MetricObject, LogsterParser
from logster.logster_helper import LogsterParsingException
        
class PostfixLogster(LogsterParser):
        
    def __init__(self, option_string=None):
        '''Initialize any data structures or variables needed for keeping track
        of the tasty bits we find in the log we are parsing.'''
        self.numSent = 0
        self.numDeferred = 0
        self.numBounced = 0
        self.totalDelay = 0
        self.numRbl = 0
        self.incomingConnections = 0
        self.incomingTLSConnections = 0
        self.outgoingTLSConnections = 0
        self.outgoingUntrustedTLSConnections = 0
        self.incomingUntrustedTLSConnections = 0
        
        # Regular expression for matching lines we are interested in, and capturing
        # fields from the line (in this case, http_status_code).
        self.reg = re.compile('(.*delay=(?P<send_delay>[^,]+),.*status=(?P<status>(sent|deferred|bounced)))|(.*?(?P<untrustedtls>(Untrusted|Anonymous))*(?P<tls> TLS connection established )(?P<direction>(to|from)).*)|(.*nrcpt=(?P<incoming>[^ ]+).*queue active.*)')
           
    def parse_line(self, line):
        '''This function should digest the contents of one line at a time, updating
        object's state variables. Takes a single argument, the line to be parsed.'''
        
        try:
            # Apply regular expression to each line and extract interesting bits.
            regMatch = self.reg.match(line)

            if regMatch:
               linebits = regMatch.groupdict()
               if (linebits['status'] == 'sent'):
                  self.totalDelay += float(linebits['send_delay'])
                  self.numSent += 1
               elif (linebits['status'] == 'deferred'):
                  self.numDeferred += 1
               elif (linebits['status'] == 'bounced'):
                  self.numBounced += 1
               elif (linebits['incoming'] != None):
                  self.incomingConnections +=1
               elif (linebits['tls'] != None ):
                  if (linebits['direction'] == 'to'):
                      self.outgoingTLSConnections +=1
                      if (linebits['untrustedtls'] != None ):
                          self.outgoingUntrustedTLSConnections +=1
                  if (linebits['direction'] == 'from'):
                      self.incomingTLSConnections +=1
                      if (linebits['untrustedtls'] != None ):
                          self.incomingUntrustedTLSConnections +=1

        except Exception as e:
            raise LogsterParsingException("regmatch or contents failed with %s" % e)


    def get_state(self, duration):
        '''Run any necessary calculations on the data collected from the logs
        and return a list of metric objects.'''
        self.duration = float(duration)
        totalTxns = self.numSent + self.numBounced + self.numDeferred
        pctDeferred = 0.0
        pctSent = 0.0
        pctBounced = 0.0
        pctOutTLS = 0.0
        pctOutUTLS = 0.0
        pctInTLS = 0.0
        pctInUTLS = 0.0
        avgDelay = 0
        mailTxnsSec = 0
        mailSentSec = 0

        #mind divide by zero situations 
        if (totalTxns > 0):
           pctDeferred = (float(self.numDeferred) / totalTxns) * 100
           pctSent = (float(self.numSent) / totalTxns) * 100
           pctBounced = (float(self.numBounced) / totalTxns) * 100
           pctOutTLS = (float(self.outgoingTLSConnections) / totalTxns) * 100
        if (self.incomingConnections > 0):
           pctInTLS = (float(self.incomingTLSConnections) / self.incomingConnections) * 100
        if (self.incomingTLSConnections > 0):
           pctInUTLS = (float(self.incomingUntrustedTLSConnections) / self.incomingTLSConnections) * 100
        if (self.outgoingTLSConnections > 0):
           pctOutUTLS = (float(self.outgoingUntrustedTLSConnections) / self.outgoingTLSConnections) * 100


        if (self.numSent > 0):
           avgDelay = self.totalDelay / self.numSent

        if (self.duration > 0):
           mailTxnsSec = totalTxns / self.duration
           mailSentSec = self.numSent / self.duration

        # Return a list of metrics objects
        return [
            MetricObject("numSent", self.numSent, "Total Sent"),
            MetricObject("pctSent", pctSent, "Percentage Sent"),
            MetricObject("numDeferred", self.numDeferred, "Total Deferred"),
            MetricObject("pctDeferred", pctDeferred, "Percentage Deferred"),
            MetricObject("numBounced", self.numBounced, "Total Bounced"),
            MetricObject("pctBounced", pctBounced, "Percentage Bounced"),
            MetricObject("mailTxnsSec", mailTxnsSec, "Transactions per sec"),
            MetricObject("mailSentSec", mailSentSec, "Sends per sec"),
            MetricObject("avgDelay", avgDelay, "Average Sending Delay"),
            MetricObject("totalTxns", totalTxns, "Total Outgoing delivery attempts"),
            MetricObject("totalRxns", self.incomingConnections , "Total Messages Received"),
            #Outgoing TLS
            MetricObject("pctOutTLS", pctOutTLS, "Percentage of successfull TLS connections on delivery attempts"),
            MetricObject("pctOutUntrustedTLS", pctOutUTLS, "Percentage of untrusted Connection on successfull TLS connections"),
            MetricObject("totalOutTLS", self.outgoingTLSConnections, "Total TLS Connections on delivery attempts"),
            MetricObject("totalOutUntrustedTLS", self.outgoingUntrustedTLSConnections, "Total untrusted TLS Connections on delivery attempts"),
            # Incoming TLS
            MetricObject("pctInTLS", pctInTLS, "Percentage of successfull TLS connections on delivery attempts"),
            MetricObject("pctInUntrustedTLS", pctInUTLS, "Percentage of untrusted Connection on successfull TLS connections"),
            MetricObject("totalInTLS", self.incomingTLSConnections, "Total TLS Connections on delivery attempts"),
            MetricObject("totalInUntrustedInTLS", self.incomingUntrustedTLSConnections, "Total untrusted TLS Connections on delivery attempts"),
        ]      
