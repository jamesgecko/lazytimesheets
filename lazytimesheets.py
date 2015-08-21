#!/usr/bin/python
import secrets
import requests
from requests.auth import HTTPBasicAuth
from sys import argv, exit
import csv

class Story(object):
    def __init__(self, _id, time):
        self._id = _id
        self.time = time
        self.name = None
        self.points = None

def main():
    if len(argv) != 3:
        show_help()
        exit()
    since, until = argv[1:3]

    toggl_json = fetch_toggl(secrets.toggl_token, secrets.toggl_workspace_id, since, until)
    pivotal_json = fetch_pivotal(secrets.pivotal_token, secrets.pivotal_project_id, secrets.pivotal_filter)

    stories, total_time = parse_toggl(toggl_json)
    stories, total_points = parse_pivotal(pivotal_json, stories)
    generate_csv(since, until, stories, total_time, total_points)

def show_help():
    print("Usage: lazytimesheets [since] [until]")
    print("Time arguments are of the format YYYY-MM-DD")
    print("It will generate a csv: `Timesheet YYYY-MM-DD to YYYY-MM-DD.csv`")

def fetch_pivotal(token, project_id, filter_string):
    url = "https://www.pivotaltracker.com/services/v5/projects/%(project_id)s/stories" % {'project_id': project_id}
    params = {'date_format': 'millis',
              'filter': filter_string}
    headers = {'X-TrackerToken': token}
    r = requests.get(url, params=params, headers=headers)
    if r.status_code == 200:
        return r.json()
    else:
        print(r.status_code)
        print(r.json())
        raise "Pivotal fetch error"

def fetch_toggl(token, workspace_id, since, until):
    url = "https://toggl.com/reports/api/v2/summary"
    params = {'user_agent': 'jamesgecko@gmail.com',
              'workspace_id': workspace_id,
              'since': since,
              'until': until}
    r = requests.get(url, params=params, auth=HTTPBasicAuth(token, 'api_token'))
    if r.status_code == 200:
        return r.json()
    else:
        raise "Toggl fetch error"

def parse_pivotal(pivotal_json, stories):
    total_points = 0
    for story in pivotal_json:
        if str(story['id']) in stories.keys():
            stories[str(story['id'])].name = story['name']
            if 'accepted_at' in story.keys() and 'estimate' in story:
                stories[str(story['id'])].points = story['estimate']
                total_points += story['estimate']
    return stories, total_points

def parse_toggl(json):
    stories = {}
    for item in json['data'][0]['items']:
        # Does anyone at all care about timecard percision smaller than a second? I don't even.
        time = item['time'] / 1000
        stories[item['title']['time_entry']] = Story(item['title']['time_entry'], time)
    total_time = json['total_grand'] / 1000
    return stories, total_time

def generate_csv(since, until, stories, total_time, total_points):
    file_name = "Timesheet %(since)s to %(until)s.csv" % {'since': since, 'until': until}
    with open(file_name, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["Description", "Story Points", "Quantity"])
        for s in stories.values():
            description = "[#%(_id)s] %(name)s" % {"_id": s._id, "name": s.name}
            points = s.points or ''
            m, s = divmod(s.time, 60)
            h, m = divmod(m, 60)
            h, m = round_to_nearest_quarter(h, m)
            duration = "%d:%d" % (h,m)
            writer.writerow([description, points, duration])

        m, s = divmod(total_time, 60)
        h, m = divmod(m, 60)
        h, m = round_to_nearest_quarter(h, m)
        total_duration = "%d:%d" % (h,m)
        writer.writerow(["Total", total_points, total_duration])

def round_to_nearest_quarter(h, m):
    m = 15 * round(float(m)/15)
    if m == 60:
        m = 0
        h += 1
    return h, m

if __name__ == '__main__':
    main()
