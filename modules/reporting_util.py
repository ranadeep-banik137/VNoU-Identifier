import csv
import logging
import time
from datetime import datetime
from modules.data_cache import get_reporting_cache, get_identification_cache, get_total_app_frames
from modules.data_reader import get_tuple_index_from_list_matching_column, make_dir_if_not_exist
from modules.date_time_converter import convert_epoch_to_timestamp
from modules.config_reader import read_config

# Example structure for user data
# users_data = {}
config = read_config()


def merge_users_data():
    users_data = {}
    # Reporting cache has (_id, name, email_id, email_sent_at, email_count)
    reporting_cache = get_reporting_cache()
    # Identification cache has (_id, time_identified, valid_till, count, is_eligible)
    identification_cache = get_identification_cache()
    for id_row in identification_cache:
        user_id = id_row[0]
        user_name = None
        email_id = None
        last_email_sent_at = None
        max_email_count = None
        last_image = None
        appearance_count = id_row[3]
        last_seen_at = id_row[1]
        match_index = get_tuple_index_from_list_matching_column(tuple_list=reporting_cache, column_index=0, column_val=user_id)
        if match_index is not None:
            user_name = reporting_cache[match_index][1]
            email_id = reporting_cache[match_index][2]
            last_email_sent_at = reporting_cache[match_index][3]
            max_email_count = reporting_cache[match_index][4]
            last_image = reporting_cache[match_index][5]
        users_data[user_id] = {
            'username': user_name,
            'email_id': email_id,
            'last_email_sent_at': last_email_sent_at,
            'max_email_count': max_email_count,
            'appearance_count': appearance_count,
            'last_seen_at': None if not last_seen_at else convert_epoch_to_timestamp(last_seen_at),
            'last_image_path': last_image
        }
    return users_data


def generate_csv_report(start_time):
    end_time = time.time()
    users_data = merge_users_data()
    total_users = len(users_data)
    reporting_path = f"{config['reporting']['path']}/report.csv"
    make_dir_if_not_exist(reporting_path)
    with open(reporting_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['User Identification Report'])
        writer.writerow(['Total Users Identified', total_users])
        writer.writerow(['Total Frames Captured', get_total_app_frames()])
        writer.writerow(['Start Time', datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow(['End Time', datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])  # Blank line
        writer.writerow(['ID', 'Name', 'Email ID', 'Total Appearances', 'Last Seen', 'Total Emails Sent', 'Last Emailed'])

        for user, data in users_data.items():
            writer.writerow([str(user), data['username'], data['email_id'], data['appearance_count'], data['last_seen_at'], data['max_email_count'], data['last_email_sent_at']])

    logging.info("Report generated: report.csv")


def generate_text_report(start_time):
    end_time = time.time()
    users_data = merge_users_data()
    total_users = len(users_data)

    report_lines = ["User Identification Report",
                    "=" * 25,
                    f"Total Users Identified: {total_users}",
                    f"Total Frames Captured: {get_total_app_frames()}",
                    f"Start Time: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}",
                    f"End Time: {datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')}",
                    "\nUser Details:",
                    "=" * 12]

    for user, data in users_data.items():
        report_lines.append(f"\nID: {str(user)}")
        report_lines.append(f"Name: {data['username']}")
        report_lines.append(f"Email ID: {data['email_id']}")
        report_lines.append(f"Total Appearances: {data['appearance_count']}")
        report_lines.append(f"Last Seen: {data['last_seen_at']}")
        report_lines.append(f"Total Emails Sent: {data['max_email_count']}")
        report_lines.append(f"Last Emailed: {data['last_email_sent_at']}")

    report_content = "\n".join(report_lines)
    reporting_path = f"{config['reporting']['path']}/report.txt"
    make_dir_if_not_exist(reporting_path)
    # Save report to a file
    with open(reporting_path, 'w') as f:
        f.write(report_content)

    # Print report
    logging.info('Report generated: report.txt')
    logging.info(report_content)


def generate_html_report(start_time):
    end_time = time.time()
    users_data = merge_users_data()
    total_users = len(users_data)
    background_image_url = 'https://images.pexels.com/photos/23886066/pexels-photo-23886066/free-photo-of-desert.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'
    report_lines = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head>",
        "    <meta charset='UTF-8'>",
        "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
        "    <title>User Identification Report</title>",
        "    <style>",
        f"        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: url('{background_image_url}') no-repeat center center fixed; background-size: cover; color: #333; }}",
        "        h1, h2 { color: #0056b3; }",
        "        table { width: 100%; border-collapse: collapse; margin-top: 20px; }",
        "        table, th, td { border: 1px solid #ddd; }",
        "        th, td { padding: 12px; text-align: left; }",
        "        th { background-color: #0056b3; color: white; }",
        "        tr:nth-child(even) { background-color: rgba(255, 255, 255, 0.8); }",
        "        tr:hover { background-color: rgba(255, 255, 255, 0.9); }",
        "        .container { width: auto; max-width: 800px; margin: auto; background: rgba(255, 255, 255, 0.9); padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); border-radius: 8px; box-sizing: border-box; overflow-x: auto;}",
        "        .summary { margin-top: 20px; }",
        "        .summary p { margin: 8px 0; }",
        "        img { max-width: 100px; cursor: pointer; }",  # Added styles for images
        "    </style>",
        "</head>",
        "<body>",
        "    <div class='container'>",
        "        <h1>User Identification Report</h1>",
        "        <div class='summary'>",
        f"            <p><strong>Total Users Identified:</strong> {total_users}</p>",
        f"            <p><strong>Total Frames Captured:</strong> {get_total_app_frames()}</p>",
        f"            <p><strong>Start Time:</strong> {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}</p>",
        f"            <p><strong>End Time:</strong> {datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')}</p>",
        "        </div>",
        "        <h2>User Details:</h2>",
        "        <table>",
        "            <tr>",
        "                <th>ID</th>",
        "                <th>Name</th>",
        "                <th>Email ID</th>",
        "                <th>Total Appearances</th>",
        "                <th>Last Seen</th>",
        "                <th>Total Emails Sent</th>",
        "                <th>Last Emailed</th>",
        "                <th>Last Captured Image</th>",
        "            </tr>"
    ]

    for user, data in users_data.items():
        report_lines.append(f"<tr><td>{str(user)}</td><td>{data['username']}</td><td>{data['email_id']}</td><td>{data['appearance_count']}</td><td>{data['last_seen_at']}</td><td>{data['max_email_count']}</td><td>{data['last_email_sent_at']}</td><td><a href='data:image/jpeg;base64,{data['last_image_path']}' download='{data['username']}{int(time.time())}.jpg' target='_blank'><img src='data:image/jpeg;base64,{data['last_image_path']}' alt='Image of {data['username']}'></a></td></tr>")

    report_lines.extend([
        "        </table>",
        "    </div>",
        "</body>",
        "</html>"
    ])

    report_content = "\n".join(report_lines)
    reporting_path = f"{config['reporting']['path']}/report.html"  # Update this to your desired path
    make_dir_if_not_exist(reporting_path)

    # Save report to a file
    with open(reporting_path, 'w') as f:
        f.write(report_content)

    logging.info("Report generated: report.html")


create_report = {
    'csv': generate_csv_report,
    'html': generate_html_report,
    'text': generate_text_report
}


def generate_reports(report_type=config['reporting']['type'], start_time=time.time()):
    if report_type not in ['csv', 'html', 'text']:
        generate_csv_report(start_time)
        generate_html_report(start_time)
        generate_text_report(start_time)
    else:
        create_report[report_type](start_time)
