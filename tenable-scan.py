import requests
import time
import json
import urllib3
from jinja2 import Environment, BaseLoader, FileSystemLoader, select_autoescape
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



# Nessus Essentials API credentials and host information
access_key = '9622ef9b9dbe3d824aa4bc911686bd1b33f631d98a8cd84f913139d1bddf8eee'
secret_key = '1e368b6955f10818201016bbe8cb6dce5425160f1c3a4e8cc47dfa645a02deae'
nessus_url = 'https://44.203.217.213:8834'
scan_name = 'tms-dev'

headers = {
    'X-ApiKeys': f'accessKey={access_key}; secretKey={secret_key}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def list_scans():
    list_url = f'{nessus_url}/scans'
    response = requests.get(list_url, headers=headers, verify=False)
    if response.status_code == 200:
        scans = response.json()
        return scans['scans']
    else:
        print(f"Error listing scans: {response.status_code}")
        return None

def get_scan_id_by_name(scan_name):
    scans = list_scans()
    if scans:
        for scan in scans:
            if scan['name'] == scan_name:
                return scan['id']
    return None

# def start_scan(scan_id):
#     start_url = f'{nessus_url}/scans/{scan_id}/launch'
#     response = requests.post(start_url, headers=headers, verify=False)
#     if response.status_code in [200, 201]:
#         scan_uuid = response.json()['scan_uuid']
#         print(f"Scan started successfully with UUID: {scan_uuid}")
#         return scan_uuid
#     else:
#         print(f"Error starting scan: {response.status_code}")
#         return None

# def check_scan_status(scan_id):
#     status_url = f'{nessus_url}/scans/{scan_id}'
#     while True:
#         response = requests.get(status_url, headers=headers, verify=False)
#         if response.status_code == 200:
#             status = response.json()['info']['status']
#             if status in ['completed', 'canceled', 'stopped']:
#                 print(f"Scan status: {status}")
#                 return status
#             else:
#                 print(f"Scan status: {status}, waiting...")
#                 time.sleep(60)  # Wait for 60 seconds before checking again
#         else:
#             print(f"Error checking scan status: {response.status_code}")
#             return None

def get_scan_report(scan_id):
    report_url = f'{nessus_url}/scans/{scan_id}'
    response = requests.get(report_url, headers=headers, verify=False)
    if response.status_code == 200:
        report = response.json()
        return report
    else:
        print(f"Error retrieving scan report: {response.status_code}")
        return None

if __name__ == "__main__":
    scan_id = get_scan_id_by_name(scan_name)
    
    if scan_id:
        print(f"Found scan ID for '{scan_name}': {scan_id}")
        # Start the scan
        # scan_uuid = start_scan(scan_id)
        # if scan_uuid:
            # # Check the scan status periodically until completion
            # status = check_scan_status(scan_id)
            # if status == 'completed':
                # Retrieve the scan report
        report = get_scan_report(scan_id)
        if report:
            # Print the report or save it to a file
            print(json.dumps(report, indent=4))
            tenable_report = json.dumps(report, indent=4)
            template_str = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>{{ info.name }} Scan Report</title>
                <style>
                    table, th, td {
                        border: 1px solid black;
                        border-collapse: collapse;
                    }
                    th, td {
                        padding: 8px;
                        text-align: left;
                    }
                </style>
            </head>
            <body>
                <h1>Scan Report: {{ info.name }}</h1>
                <h2>Scan Summary</h2>
                <p><strong>Scan Type:</strong> {{ info.scan_type }}</p>
                <p><strong>Targets:</strong> {{ info.targets }}</p>
                <p><strong>Status:</strong> {{ info.status }}</p>
                <p><strong>Start Time:</strong> {{ info.scan_start | datetimeformat }}</p>
                <p><strong>End Time:</strong> {{ info.scan_end | datetimeformat }}</p>

                <h2>Vulnerabilities</h2>
                <table>
                    <tr>
                        <th>Plugin Name</th>
                        <th>Severity</th>
                        <th>Plugin ID</th>
                    </tr>
                    {% for vulnerability in vulnerabilities %}
                    <tr>
                        <td>{{ vulnerability.plugin_name }}</td>
                        <td>{{ vulnerability.severity }}</td>
                        <td>{{ vulnerability.plugin_id }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </body>
            </html>

            """
            
            # Setup Jinja2 environment
             # Create a Jinja2 environment and compile the template
            env = Environment(loader=BaseLoader() )
            env.filters['datetimeformat'] = lambda value: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(value)))
            template = env.from_string(template_str)

        # Render template with data
            html_output = template.render(json.loads(tenable_report))
            output_file_path_html = 'reports/tenable-report.html'
        # Save the output to an HTML file
            with open(output_file_path_html, 'x') as f:
                f.write(html_output)

            print("HTML report generated successfully.")
                
            output_file_path = 'reports/tenable-report.json'

            with open(output_file_path, 'x') as file:
                # Write the Scans DataFrame
                file.write(tenable_report)
                file.close()
                    # To save to a file, uncomment the following lines:
                    # with open('scan_report.json', 'w') as f:
                    #     json.dump(report, f, indent=4)
    else:
        print(f"No scan found with the name '{scan_name}'.")
