# Lazy Timesheets

I hate building timesheets. It's work about work you've already done. Clearly,
a terrible script must be hacked together on short notice.

![Automate all the things!](http://i.imgur.com/x0MhMX7.jpg)

This script correlates Toggl entries with Pivotal Tracker stories.
It generates a CSV showing how long you spent on each story you've worked on in the designated
pariod. The estimated point value of completed stories will also be shown.
The last row of the CSV displays total time and total completed points.

Log your work with Toggl. Each "what are you working on?" description must be a story id from
Pivotal Tracker. Just the number; no spaces or hash-marks or anything else.

You'll probably need to install dependencies. `pip install -r requirements.txt`

You will also need to make a file, `secrets.py`. It should define the following variables:
- `toggl_token`
- `toggl_workspace_id`
- `pivotal_token`
- `pivotal_project_id`
- `pivotal_filter`

Yeah, there are better ways to keep track of secret things, but this is a quick hack.

You should probably define pivotal_filter. This is the same thing as the filters used
[in the search box on the website](https://www.pivotaltracker.com/help/faq#howcanasearchberefined).
Mine looks like `owner:JD includedone:true`. Future versions of this script should probably
make it easier to use the `modified_since` filter.
