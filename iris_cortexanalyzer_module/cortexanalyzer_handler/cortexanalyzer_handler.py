#!/usr/bin/env python3
#
#
#  IRIS cortexanalyzer Source Code
#  Copyright (C) 2023 - SOCFortress
#  info@socfortress.co
#  Created by SOCFortress - 2023-03-06
#
#  License MIT


import traceback
import asyncio
import urllib3
import cortex4py
import json
import requests
import time
from cortex4py.api import Api
from jinja2 import Template

import iris_interface.IrisInterfaceStatus as InterfaceStatus
from app.datamgmt.manage.manage_attribute_db import add_tab_attribute_field


class CortexanalyzerHandler(object):
    def __init__(self, mod_config, server_config, logger):
        self.mod_config = mod_config
        self.server_config = server_config
        self.cortexanalyzer = self.get_cortexanalyzer_instance()
        self.log = logger

    def get_cortexanalyzer_instance(self):
        """
        Returns an cortexanalyzer API instance depending if the key is premium or not

        :return: { cookiecutter.keyword }} Instance
        """
        url = self.mod_config.get('cortexanalyzer_url')
        key = self.mod_config.get('cortexanalyzer_key')
        proxies = {}

        if self.server_config.get('http_proxy'):
            proxies['https'] = self.server_config.get('HTTPS_PROXY')

        if self.server_config.get('https_proxy'):
            proxies['http'] = self.server_config.get('HTTP_PROXY')

        # TODO!
        # Here get your cortexanalyzer instance and return it
        # ex: return cortexanalyzerApi(url, key)
        return "<TODO>"

    def gen_report_from_template(
        self, html_template, cortexanalyzer_report
    ) -> InterfaceStatus:
        """
        Generates an HTML report for Domain, displayed as an attribute in the IOC
        :param html_template: A string representing the HTML template
        :param misp_report: The JSON report fetched with cortexanalyze API
        :return: InterfaceStatus
        """
        template = Template(html_template)
        context = cortexanalyzer_report
        pre_render = dict({"results": []})
        pre_render["results"] = cortexanalyzer_report

        try:
            rendered = template.render(pre_render)

        except Exception:
            print(traceback.format_exc())
            self.log.error(traceback.format_exc())
            return InterfaceStatus.I2Error(traceback.format_exc())

        return InterfaceStatus.I2Success(data=rendered)

    def handle_domain(self, ioc):
        """
        Handles an IOC of type domain and adds Cortex Analyzer insights
        :param ioc: IOC instance
        :return: IIStatus
        """

        self.log.info(f"Getting domain report for {ioc.ioc_value}")
        url = self.mod_config.get("cortexanalyze_url")
        apikey = self.mod_config.get("cortexanalyze_key")
        analyzer = self.mod_config.get("cortexanalyze_analyzer")

        """
        Call Cortex via Cortex4py
        :param ioc: IOC instance
        :return: IIStatus
        """

        api = Api(url, apikey, verify_cert=False)

        """
        Call Cortex via Cortex4py To check if Analyzer is Enabled
        :param ioc: IOC instance
        :return: IIStatus
        """

        available_analyzers = api.analyzers.find_all({}, range='all')
        
        all_analyzers = []
        for available in available_analyzers:
            all_analyzers.append(available.name)
        if analyzer not in all_analyzers:
            self.log.error(f'{analyzer} was not found to be enabled. Enable the Analyzer in Cortex to continue')
            return InterfaceStatus.I2Error()
        else:
            self.log.info(f'{analyzer} was found to be enabled. Continuing')

        #for analyzers in available_analyzers:
        #    if not analyzer in analyzers.name:
        #        return 

        """
        Call Cortex via Cortex4py To run Analyzer and Return Results
        :param ioc: IOC instance
        :return: IIStatus
        """

        job1 = api.analyzers.run_by_name(
            analyzer,
            {
                "data": ioc.ioc_value,
                "dataType": "domain",
                "tlp": 1,
                "message": "custom message sent to analyzer",
            },
            force=1,
        )
        r_json = job1.json()

        job_id = r_json["id"]
        self.log.info(f'Job ID is: {job_id}')

        job_state = r_json["status"]
        timer = 0
        while job_state != "Success":
            if timer == 60:
                self.log.error("Job failed to complete after 5 minutes.")
                report = "Job failed to complete after 5 minutes."
                break
            timer = timer + 1
            self.log.info(f'Timer is: {timer}')

            if job_state == "Failure":
                error_message = r_json["errorMessage"]
                self.log.error(f'Cortex Failure: {error_message}')
                return InterfaceStatus.I2Error()

            else:
                time.sleep(5)
            followup_request = api.jobs.get_by_id(job_id)
            r_json = followup_request.json()
            job_state = r_json["status"]

        if job_state == "Success":
            self.log.info("Job completed successfully")
            report = api.jobs.get_report(job_id).report
            final_report = report["full"]

        if self.mod_config.get("cortexanalyzer_report_as_attribute") is True:
            self.log.info("Adding new attribute CORTEX Domain Report to IOC")

            status = self.gen_report_from_template(
                html_template=self.mod_config.get(
                    "cortexanalyzer_domain_report_template"
                ),
                cortexanalyzer_report=final_report,
        
            )

            if not status.is_success():
                return status

            rendered_report = status.get_data()

            try:
                add_tab_attribute_field(
                    ioc,
                    tab_name="CORTEX Report",
                    field_name="HTML report",
                    field_type="html",
                    field_value=rendered_report,
                )

            except Exception:

                self.log.error(traceback.format_exc())
                return InterfaceStatus.I2Error(traceback.format_exc())
        else:
            self.log.info("Skipped adding attribute report. Option disabled")

        return InterfaceStatus.I2Success()
    
    def handle_ip(self, ioc):
        """
        Handles an IOC of type IP and adds Cortex Analyzer insights
        :param ioc: IOC instance
        :return: IIStatus
        """

        self.log.info(f"Getting IP report for {ioc.ioc_value}")
        url = self.mod_config.get("cortexanalyze_url")
        apikey = self.mod_config.get("cortexanalyze_key")
        analyzer = self.mod_config.get("cortexanalyze_analyzer")

        """
        Call Cortex via Cortex4py
        :param ioc: IOC instance
        :return: IIStatus
        """

        api = Api(url, apikey, verify_cert=False)

        """
        Call Cortex via Cortex4py To check if Analyzer is Enabled
        :param ioc: IOC instance
        :return: IIStatus
        """

        available_analyzers = api.analyzers.find_all({}, range='all')
        
        all_analyzers = []
        for available in available_analyzers:
            all_analyzers.append(available.name)
        if analyzer not in all_analyzers:
            self.log.error(f'{analyzer} was not found to be enabled. Enable the Analyzer in Cortex to continue')
            return InterfaceStatus.I2Error()
        else:
            self.log.info(f'{analyzer} was found to be enabled. Continuing')

        #for analyzers in available_analyzers:
        #    if not analyzer in analyzers.name:
        #        return 

        """
        Call Cortex via Cortex4py To run Analyzer and Return Results
        :param ioc: IOC instance
        :return: IIStatus
        """

        job1 = api.analyzers.run_by_name(
            analyzer,
            {
                "data": ioc.ioc_value,
                "dataType": "ip",
                "tlp": 1,
                "message": "custom message sent to analyzer",
            },
            force=1,
        )
        r_json = job1.json()

        job_id = r_json["id"]
        self.log.info(f'Job ID is: {job_id}')

        job_state = r_json["status"]
        timer = 0
        while job_state != "Success":
            if timer == 60:
                self.log.error("Job failed to complete after 5 minutes.")
                report = "Job failed to complete after 5 minutes."
                break
            timer = timer + 1
            self.log.info(f'Timer is: {timer}')

            if job_state == "Failure":
                error_message = r_json["errorMessage"]
                self.log.error(f'Cortex Failure: {error_message}')
                return InterfaceStatus.I2Error()

            else:
                time.sleep(5)
            followup_request = api.jobs.get_by_id(job_id)
            r_json = followup_request.json()
            job_state = r_json["status"]

        if job_state == "Success":
            self.log.info("Job completed successfully")
            report = api.jobs.get_report(job_id).report
            final_report = report["full"]

        if self.mod_config.get("cortexanalyzer_report_as_attribute") is True:
            self.log.info("Adding new attribute CORTEX IP Report to IOC")

            status = self.gen_report_from_template(
                html_template=self.mod_config.get(
                    "cortexanalyzer_domain_report_template"
                ),
                cortexanalyzer_report=final_report,
        
            )

            if not status.is_success():
                return status

            rendered_report = status.get_data()

            try:
                add_tab_attribute_field(
                    ioc,
                    tab_name="CORTEX Report",
                    field_name="HTML report",
                    field_type="html",
                    field_value=rendered_report,
                )

            except Exception:

                self.log.error(traceback.format_exc())
                return InterfaceStatus.I2Error(traceback.format_exc())
        else:
            self.log.info("Skipped adding attribute report. Option disabled")

        return InterfaceStatus.I2Success()
    
    def handle_hash(self, ioc):
        """
        Handles an IOC of type Hash and adds Cortex Analyzer insights
        :param ioc: IOC instance
        :return: IIStatus
        """

        self.log.info(f"Getting IP report for {ioc.ioc_value}")
        url = self.mod_config.get("cortexanalyze_url")
        apikey = self.mod_config.get("cortexanalyze_key")
        analyzer = self.mod_config.get("cortexanalyze_analyzer")

        """
        Call Cortex via Cortex4py
        :param ioc: IOC instance
        :return: IIStatus
        """

        api = Api(url, apikey, verify_cert=False)

        """
        Call Cortex via Cortex4py To check if Analyzer is Enabled
        :param ioc: IOC instance
        :return: IIStatus
        """

        available_analyzers = api.analyzers.find_all({}, range='all')
        
        all_analyzers = []
        for available in available_analyzers:
            all_analyzers.append(available.name)
        if analyzer not in all_analyzers:
            self.log.error(f'{analyzer} was not found to be enabled. Enable the Analyzer in Cortex to continue')
            return InterfaceStatus.I2Error()
        else:
            self.log.info(f'{analyzer} was found to be enabled. Continuing')

        #for analyzers in available_analyzers:
        #    if not analyzer in analyzers.name:
        #        return 

        """
        Call Cortex via Cortex4py To run Analyzer and Return Results
        :param ioc: IOC instance
        :return: IIStatus
        """

        job1 = api.analyzers.run_by_name(
            analyzer,
            {
                "data": ioc.ioc_value,
                "dataType": "hash",
                "tlp": 1,
                "message": "custom message sent to analyzer",
            },
            force=1,
        )
        r_json = job1.json()

        job_id = r_json["id"]
        self.log.info(f'Job ID is: {job_id}')

        job_state = r_json["status"]
        timer = 0
        while job_state != "Success":
            if timer == 60:
                self.log.error("Job failed to complete after 5 minutes.")
                report = "Job failed to complete after 5 minutes."
                break
            timer = timer + 1
            self.log.info(f'Timer is: {timer}')

            if job_state == "Failure":
                error_message = r_json["errorMessage"]
                self.log.error(f'Cortex Failure: {error_message}')
                return InterfaceStatus.I2Error()

            else:
                time.sleep(5)
            followup_request = api.jobs.get_by_id(job_id)
            r_json = followup_request.json()
            job_state = r_json["status"]

        if job_state == "Success":
            self.log.info("Job completed successfully")
            report = api.jobs.get_report(job_id).report
            final_report = report["full"]

        if self.mod_config.get("cortexanalyzer_report_as_attribute") is True:
            self.log.info("Adding new attribute CORTEX IP Report to IOC")

            status = self.gen_report_from_template(
                html_template=self.mod_config.get(
                    "cortexanalyzer_domain_report_template"
                ),
                cortexanalyzer_report=final_report,
        
            )

            if not status.is_success():
                return status

            rendered_report = status.get_data()

            try:
                add_tab_attribute_field(
                    ioc,
                    tab_name="CORTEX Report",
                    field_name="HTML report",
                    field_type="html",
                    field_value=rendered_report,
                )

            except Exception:

                self.log.error(traceback.format_exc())
                return InterfaceStatus.I2Error(traceback.format_exc())
        else:
            self.log.info("Skipped adding attribute report. Option disabled")

        return InterfaceStatus.I2Success()
