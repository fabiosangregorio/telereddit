import re
from urllib.parse import quote

with open("./documentation-reports/docstr-coverage.txt", "r") as f:
    last_line = f.read().splitlines()[-1]

percentage = int(float(re.search("\\d+(?:\\.\\d+)?", last_line).group()))

if percentage >= 90:
    color = "brightgreen"
elif percentage >= 80:
    color = "green"
elif percentage >= 60:
    color = "yellowgreen"
elif percentage >= 40:
    color = "yellow"
else:
    color = "red"

query = quote(f"docs-{percentage}%-{color}")
url = f"https://img.shields.io/badge/{query}"
print(url)

with open("./README.md", "r+") as r:
    data = r.read()
    data = re.sub(
        r"docs-coverage\"(\W)*src=\"\S*\"", f'docs-coverage" src="{url}"', data
    )
    r.seek(0)
    r.write(data)
    r.truncate()
