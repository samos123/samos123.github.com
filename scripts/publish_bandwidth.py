import argparse
import base64
import datetime
import json
import urllib.request
import sys

def publish(speed_results, date):


    blog_post = """Title: RobotRouter: Bandwidth of Xfinity Internet on {date}
Date: {date}
Author: Robot Router
Category: Bandwidth
Tags: bandwidth, openwrt
Slug: robotrouter-bandwidth-test-result-{date}

RobotRouter ran speedtest-cli.sh every hour on {date} and reported
the following aggregate statistics:

Metric | Value 
--- | ---
Average Download Speed | {averageDownloadSpeed}
Average Upload Speed | {averageUploadSpeed}
Min Download Speed | {minDownloadSpeed}
Min Upload Speed | {minUploadSpeed}
Max Download Speed | {maxDownloadSpeed}
Max Upload Speed | {maxUploadSpeed}

The raw results can be viewed in the following table below:

```
{rawResults}
```

""".format(date=date, **speed_results)

    publish_bandwidth_data = {
      "message": "Publish bandwidth %s" % (date,),
      "committer": {
        "name": "Sam Stoelinga",
        "email": "sammiestoel@gmail.com"
      },
      "content": base64.b64encode(blog_post.encode("ascii")).decode()
    }

    git_api_json_data = json.dumps(publish_bandwidth_data)

    url = "https://api.github.com/repos/{owner}/{repo}/contents/{path}?access_token={token}"
    token = ""
    with open("/root/token.txt", "r") as token_file:
        token = token_file.read().replace("\n", "")

    path = "content/bandwidth/bandwidth-speedtest-%s.md" % date.isoformat()

    url_params = {
        "owner": "samos123",
        "repo": "samos123.github.com",
        "path": path,
        "token": token,
    }


    req = urllib.request.Request(url=url.format(**url_params),
                                 data=git_api_json_data.encode("utf-8"), method='PUT',
                                 headers={'content-type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as f:
            pass
        print(f.status)
        print(f.reason)
    except urllib.error.HTTPError as e:
        print(e)
        print(e.fp.read())
