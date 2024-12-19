"""
   This module provides functions for converting json to html and formatting
   it either as a table or complete HTML page. All hardcoded stuff is here!
"""
import argparse
import json
import os.path
import datetime

import json2html
from bs4 import BeautifulSoup as Bs

"""
   Load settings
"""
def load_settings(settings_file: str):
    settings = {}
    if os.path.isfile(settings_file):
        with open(settings_file, 'r') as sf:
            settings = json.load(sf)
        sf.close()

    return settings


"""
   Load data from vidarr, use settings to verify entries
"""
def load_data(input_data: str, settings: dict):
    final_data = {}
    if os.path.isfile(input_data) and isinstance(settings, dict):
        with open(input_data, 'r') as inp:
            input_lines = inp.readlines()
        inp.close()

        for i_line in input_lines:
            my_fields = i_line.rstrip().split("\t")
            if my_fields[0] in settings.keys() and len(my_fields) == 3:
                if my_fields[0] not in final_data.keys():
                    final_data[my_fields[0]] = set()
                final_data[my_fields[0]].add((my_fields[1], my_fields[2]))

    return final_data


"""
   Compare new data with cached snapshot
"""
def compare_with_cache(new_data: dict, cached_data: dict, settings: dict):
    report = {}
    for shesmu in new_data.keys():
        if shesmu in settings.keys() and shesmu in cached_data.keys():
            report[shesmu] = new_data[shesmu] - cached_data[shesmu]

    return report

"""
   Format lists to use in HTML report
"""
def format_lists(report: dict):
    outList = {}
    for shesmu in report.keys():
        if isinstance(report[shesmu], set) and len(report[shesmu]) > 0:
            my_list = ""
            for wf in sorted(report[shesmu]):
                next_item = ":".join(wf)
                my_list += f'<li>{next_item}</li>'
            outList[shesmu] = f'<ul>{my_list}</ul'
    return outList

"""
   Format table to use in HTML report
"""
def update_cache(new_data: dict, cache_file: str, settings: dict):
    if isinstance(new_data, dict) and len(new_data) > 0:
        new_lines = []
        for data_field in new_data.keys():
            if data_field in settings.keys():
                for wf in sorted(new_data[data_field]):
                    my_vals = [data_field]
                    for val in wf:
                        my_vals.append(val)
                    new_lines.append("\t".join(my_vals) + "\n")

        with open(cache_file, 'w') as cf:
            cf.writelines(new_lines)
        cf.close()

"""
   Format table to use in HTML report
"""
def update_log(report: dict, log_file: str, settings: dict):
    log_lines = []
    report_lines = ""
    if os.path.isfile(log_file):
        with open(log_file, "r") as lf:
            log_lines = lf.readlines()
        lf.close()

    if isinstance(report, dict) and len(report) > 0:
        for data_field in report.keys():
            new_lines = []
            if data_field in settings.keys():
                for wf in sorted(report[data_field]):
                    my_vals = []
                    for val in wf:
                        my_vals.append(val)
                    new_lines.append("\t".join(my_vals))

            if len(new_lines) > 0:
                report_lines = ["\n" + today_date() + ":\n\n", "New workflow deployed on " + data_field, "\n"]
                for new_tag in new_lines:
                    report_lines.append(new_tag + "\n")

    with open(log_file, 'w') as lfw:
        lfw.writelines(report_lines)
        if len(log_lines) > 0:
            lfw.writelines(log_lines)
    lfw.close()


"""
   Return date wrapped in div
"""
def today_date() -> str:
    today = datetime.date.today()
    formatted_today = today.strftime("%A %d. %B %Y")
    return formatted_today

"""
   Return JSON rendered into HTML table
"""
def convert2page(input_data: dict, log_file: str):
    # TODO: some checks for file existence, presence of cache etc

    html = "<!DOCTYPE html><html><head><meta charset=\"UTF-8\"><title>Vaidarr Updates</title> \
           <style> h2 {color: blue; font-family: arial;} \
           h3 {color: teal; font-family: arial;} \
           table {border-collapse: separate; border-spacing: 0; table-layout: fixed;} \
           th {position: sticky; top: 0; padding: 4px; background-color: #008abc; color: #ffffff; border-bottom: 2px solid #ddd; text-align: left;} \
           td {padding: 10px; text-align: left; background-color: #f2f2f2; border-bottom: 1px solid #ddd; }</style> \
           </head><body><h2>Deployed workflows - this week changes:</h2>" + convert2table(input_data) + "<br/>" \
           + "<div><h3>Updated on" + today_date() + "</h3></div><a href=" + log_file +">See full Log</a></body></html>"

    soup = Bs(html, "html.parser")
    return soup.prettify()


"""
   Using data from input, re-wrap the data into a hash and return HTML
"""
def convert2table(inputs: dict) -> dict:
    rewrapped = []
    data = {}
    for shesmu in ("STAGE", "RESEARCH", "CLINICAL"):
        if shesmu in inputs.keys():
            data[shesmu] = inputs[shesmu]
        else:
            data[shesmu] = "No Updates"
    rewrapped.append(data)
    return json2html.json2html.convert(json=rewrapped, table_attributes="id=\"info-table\" "
                                                                        "class=\"styled-table\""
                                                                        "width=\"60%\"", escape=False)


""" 
   ====================== Main entrance point to the script =============================
   pass (or not) the following:
   -i input file with workflows and versions
   -p output HTML page
   -c cache file, we need this to list updates
   
   we have defaults for everything
   at the end, script prints out data as a table and dumps data in a json
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run parsing script to generate gsiWorkflow status table')
    parser.add_argument('-i', '--input', help='Input tags', required=False, default="data/vidarr_tags.tsv")
    parser.add_argument('-p', '--output', help='Output page, HTML', required=False, default="vidarr_updates.html")
    parser.add_argument('-c', '--cache', help='Previous tags snapshot', required=False, default="data/vidarr_cache.tsv")
    parser.add_argument('-s', '--settings', help="Settings file", required=True, default="data/tracker_settings.json")
    args = parser.parse_args()

    log_file = "vidarr_tracker.log"

    # load settings
    my_settings = load_settings(args.settings)

    # load data (use settings)
    my_data = load_data(args.input, my_settings)

    # load cache (use settings)
    my_cache = load_data(args.cache, my_settings)

    # Compare cache with current state, return updated items (if any)
    my_report = compare_with_cache(my_data, my_cache, my_settings)

    # format report table
    report_formatted = format_lists(my_report)

    # Update cache
    update_cache(my_data, args.cache, my_settings)

    # Update log
    update_log(my_report, log_file, my_settings)

    # Render page and write it to the disk
    html_page = convert2page(report_formatted, log_file)

'''Return a rendered HTML page'''

with open(args.output, 'w') as op:
    op.write(html_page)
