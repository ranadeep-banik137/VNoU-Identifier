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
        appearance_count = id_row[3]
        last_seen_at = id_row[1]
        match_index = get_tuple_index_from_list_matching_column(tuple_list=reporting_cache, column_index=0, column_val=user_id)
        if match_index is not None:
            user_name = reporting_cache[match_index][1]
            email_id = reporting_cache[match_index][2]
            last_email_sent_at = reporting_cache[match_index][3]
            max_email_count = reporting_cache[match_index][4]
        users_data[user_id] = {
            'username': user_name,
            'email_id': email_id,
            'last_email_sent_at': last_email_sent_at,
            'max_email_count': max_email_count,
            'appearance_count': appearance_count,
            'last_seen_at': None if not last_seen_at else convert_epoch_to_timestamp(last_seen_at)
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

    report_lines = ["<html>",
                    "<head><title>User Identification Report</title></head>",
                    "<body>",
                    "<h1>User Identification Report</h1>",
                    f"<p>Total Users Identified: {total_users}</p>",
                    f"<p>Total Frames Captured: {get_total_app_frames()}</p>",
                    f"<p>Start Time: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}</p>",
                    f"<p>End Time: {datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')}</p>",
                    "<h2>User Details:</h2>",
                    "<table border='1'><tr><th>ID</th><th>Name</th><th>Email ID</th><th>Total Appearances</th><th>Last Seen</th><th>Total Emails Sent</th><th>Last Emailed</th></tr>"]

    for user, data in users_data.items():
        report_lines.append(f"<tr><td>{str(user)}</td><td>{data['username']}</td><td>{data['email_id']}</td><td>{data['appearance_count']}</td><td>{data['last_seen_at']}</td><td>{data['max_email_count']}</td><td>{data['last_email_sent_at']}</td></tr>")

    report_lines.append("</table>")
    report_lines.append("</body>")
    report_lines.append("</html>")

    report_content = "\n".join(report_lines)
    reporting_path = f"{config['reporting']['path']}/report.html"
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
