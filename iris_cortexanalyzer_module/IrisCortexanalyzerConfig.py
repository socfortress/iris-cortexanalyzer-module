#!/usr/bin/env python3
#
#
#  IRIS cortexanalyzer Source Code
#  Copyright (C) 2023 - SOCFortress
#  info@socfortress.co
#  Created by SOCFortress - 2023-03-06
#
#  License MIT

module_name = "Cortex Analyzer"
module_description = "Integrate with Cortex and run any Analyzer. Anaylzer must be enabled within Cortex."
interface_version = 1.1
module_version = 1.0

pipeline_support = False
pipeline_info = {}


module_configuration = [
    {
        "param_name": "cortexanalyze_url",
        "param_human_name": "Cortex URL",
        "param_description": "Cortex URL",
        "default": None,
        "mandatory": True,
        "type": "string",
    },
    {
        "param_name": "cortexanalyze_key",
        "param_human_name": "Cortex API Key",
        "param_description": "Cortex API key",
        "default": None,
        "mandatory": True,
        "type": "sensitive_string",
    },
    {
        "param_name": "cortexanalyze_analyzer",
        "param_human_name": "Cortex Analyzer",
        "param_description": "Cortex Analyzer to run - I.E VirusTotal_GetReport_3_0",
        "default": "VirusTotal_GetReport_3_0",
        "mandatory": True,
        "type": "string",
    },    
    {
        "param_name": "cortexanalyzer_manual_hook_enabled",
        "param_human_name": "Manual triggers on IOCs",
        "param_description": "Set to True to offers possibility to manually triggers the module via the UI",
        "default": True,
        "mandatory": True,
        "type": "bool",
        "section": "Triggers"
    },
    {
        "param_name": "cortexanalyzer_on_create_hook_enabled",
        "param_human_name": "Triggers automatically on IOC create",
        "param_description": "Set to True to automatically add a cortexanalyzer insight each time an IOC is created",
        "default": False,
        "mandatory": True,
        "type": "bool",
        "section": "Triggers"
    },
    {
        "param_name": "cortexanalyzer_on_update_hook_enabled",
        "param_human_name": "Triggers automatically on IOC update",
        "param_description": "Set to True to automatically add a cortexanalyzer insight each time an IOC is updated",
        "default": False,
        "mandatory": True,
        "type": "bool",
        "section": "Triggers"
    },
    {
        "param_name": "cortexanalyzer_report_as_attribute",
        "param_human_name": "Add cortexanalyzer report as new IOC attribute",
        "param_description": "Creates a new attribute on the IOC, base on the cortexanalyzer report. Attributes are based "
                             "on the templates of this configuration",
        "default": True,
        "mandatory": True,
        "type": "bool",
        "section": "Insights"
    },# TODO: careful here, remove backslashes from \{\{ results| tojson(indent=4) \}\}
    {
        "param_name": "cortexanalyzer_domain_report_template",
        "param_human_name": "Cortex Analyzer report template",
        "param_description": "Cortex Analyzer template used to add a new custom attribute to the target IOC",
        "default": "<div class=\"row\">\n    <div class=\"col-12\">\n        <div "
                   "class=\"accordion\">\n            <h3>cortexanalyzer raw results</h3>\n\n           "
                   " <div class=\"card\">\n                <div class=\"card-header "
                   "collapsed\" id=\"drop_r_cortexanalyzer\" data-toggle=\"collapse\" "
                   "data-target=\"#drop_raw_cortexanalyzer\" aria-expanded=\"false\" "
                   "aria-controls=\"drop_raw_cortexanalyzer\" role=\"button\">\n                    <div "
                   "class=\"span-icon\">\n                        <div "
                   "class=\"flaticon-file\"></div>\n                    </div>\n              "
                   "      <div class=\"span-title\">\n                        cortexanalyzer raw "
                   "results\n                    </div>\n                    <div "
                   "class=\"span-mode\"></div>\n                </div>\n                <div "
                   "id=\"drop_raw_cortexanalyzer\" class=\"collapse\" aria-labelledby=\"drop_r_cortexanalyzer\" "
                   "style=\"\">\n                    <div class=\"card-body\">\n              "
                   "          <div id='cortexanalyzer_raw_ace'>\{\{ results| tojson(indent=4) \}\}</div>\n  "
                   "                  </div>\n                </div>\n            </div>\n    "
                   "    </div>\n    </div>\n</div> \n<script>\nvar cortexanalyzer_in_raw = ace.edit("
                   "\"cortexanalyzer_raw_ace\",\n{\n    autoScrollEditorIntoView: true,\n    minLines: "
                   "30,\n});\ncortexanalyzer_in_raw.setReadOnly(true);\ncortexanalyzer_in_raw.setTheme("
                   "\"ace/theme/tomorrow\");\ncortexanalyzer_in_raw.session.setMode("
                   "\"ace/mode/json\");\ncortexanalyzer_in_raw.renderer.setShowGutter("
                   "true);\ncortexanalyzer_in_raw.setOption(\"showLineNumbers\", "
                   "true);\ncortexanalyzer_in_raw.setOption(\"showPrintMargin\", "
                   "false);\ncortexanalyzer_in_raw.setOption(\"displayIndentGuides\", "
                   "true);\ncortexanalyzer_in_raw.setOption(\"maxLines\", "
                   "\"Infinity\");\ncortexanalyzer_in_raw.session.setUseWrapMode("
                   "true);\ncortexanalyzer_in_raw.setOption(\"indentedSoftWrap\", "
                   "true);\ncortexanalyzer_in_raw.renderer.setScrollMargin(8, 5);\n</script> ",
        "mandatory": False,
        "type": "textfield_html",
        "section": "Templates"
    }
    
]