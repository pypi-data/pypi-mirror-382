# Python edgegrid module
""" Copyright 2015 Akamai Technologies, Inc. All Rights Reserved.

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.

 You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""
import sys
import os
import requests
import logging
import json
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from .http_calls import EdgeGridHttpCaller
if sys.version_info[0] >= 3:
    # python3
    from urllib import parse
else:
    # python2.7
    import urlparse as parse

class AkamaiBilling():
    def __init__(self,prdHttpCaller,accountSwitchKey=None):
        self._prdHttpCaller = prdHttpCaller
        self.accountSwitchKey = accountSwitchKey
        return None
    
    def listCumulativeDailyUsagePerContract(self,productId,contractId,month):
        """ List the listCumulativeDailyUsage per product and contract """
        listGroupEndpoint = '/billing/v1/contracts/{}/products/{}/usage/daily'.format(contractId,productId)
        params = {}
        params['month'] = month
        if self.accountSwitchKey:
            params['accountSwitchKey']= self.accountSwitchKey
        
        status,response = self._prdHttpCaller.getResult(listGroupEndpoint,params)
    
        return status,response
    
    def listCumulativeDailyUsagePerRG(self,productId,reportingGroupId,month):
        """ List the listCumulativeDailyUsage per product and contract """
        listGroupEndpoint = '/billing/v1/reporting-groups/{}/products/{}/usage/daily'.format(reportingGroupId,productId)
        params = {}
        params['month'] = month
        if self.accountSwitchKey:
            params['accountSwitchKey']= self.accountSwitchKey
        
        status,response = self._prdHttpCaller.getResult(listGroupEndpoint,params)
    
        return status,response

    