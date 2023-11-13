# archive wayback downloader

![Version](https://img.shields.io/badge/Version-0.2.5-blue)
![Release](https://img.shields.io/badge/Release-alpha-red)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Downloading archived web pages from the [Wayback Machine](https://archive.org/web/).

Internet-archive is a nice source for several OSINT-information. This script is a work in progress to query and fetch archived web pages.

This project is not intended to get fast results. Moreover it is a tool to get a lot of data over a long period of time.

## Limitations

The wayback-machine does refuse connections over public access if the query rate is too high. So for now there seems no possibility to implement a multi-threaded download. As soon as a connection is refused, the script will wait and retry the query. Existing projects seem to ignore this limitation and just rush through the queries. This resulted in a lot of missing files and probably missing knowledge about the target.

Timeout seems to be about 2.5 minutes per 20 downloads.

## Installation

### Pip

1. Install the package <br>
   ```pip install pywaybackup```
2. Run the script <br>
   ```waybackup -h```

### Manual

1. Clone the repository <br>
   ```git clone https://github.com/bitdruid/waybackup.git```
2. Install requirements <br>
   ```pip install -r requirements.txt```
3. Run the script <br>
   ```python waybackup.py -h```

## Usage

- comming soon...

## Contributing

I'm always happy for some feature requests to improve the usability of this script.
Feel free to give suggestions and report issues. Project is still far from being perfect.