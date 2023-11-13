import threading
import requests
import datetime
import os
#import magic
from pprint import pprint
import time
import pathlib

def retry(ExceptionToCheck, tries=4, delay=3, backoff=2):
    def deco_retry(f):
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    #print(f"{e}, Retrying in {mdelay} seconds...")
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)
        return f_retry  # true decorator
    return deco_retry

def print_result(result_list):
    print("")
    if not result_list:
        print("No snapshots found")
    else:
        pprint(result_list)
        print(f"\n-----> {len(result_list)} snapshots listed")

# create filelist
def query_list(url: str, range: int, mode: str):
    print("\nQuerying snapshots...")
    if range:
        range = datetime.datetime.now().year - range
        range = "&from=" + str(range)
    else:
        range = ""
    cdxQuery = f"https://web.archive.org/cdx/search/xd?output=json&url=*.{url}/*{range}&fl=timestamp,original&filter=!statuscode:200"
    cdxResult_json = requests.get(cdxQuery).json()[1:] # first line is fieldlist, so remove it [timestamp, original]
    cdxResult_list = [{"timestamp": snapshot[0], "url": snapshot[1]} for snapshot in cdxResult_json]
    if mode == "current":
        cdxResult_list = sorted(cdxResult_list, key=lambda k: k['timestamp'], reverse=True)
        cdxResult_list_filtered = []
        for snapshot in cdxResult_list:
            if snapshot["url"] not in [snapshot["url"] for snapshot in cdxResult_list_filtered]:
                cdxResult_list_filtered.append(snapshot)
        cdxResult_list = cdxResult_list_filtered
    print(f"\n-----> {len(cdxResult_list)} snapshots found")
    return cdxResult_list





# create folders for output
def create_dirs(output):
    pathlib.Path(output).mkdir(parents=True, exist_ok=True)





def split_url(url):
    """
    Split url into domain, subdir and file.
    If no file is present, the filename will be index.html
    """
    domain = url.split("//")[-1].split("/")[0]
    subdir = "/".join(url.split("//")[-1].split("/")[1:-1])
    filename = url.split("/")[-1] or "index.html"
    return domain, subdir, filename

def determine_url_filetype(url):
    """
    Determine filetype of the archive-url by looking at the file extension.
    """
    image = ["jpg", "jpeg", "png", "gif", "svg", "ico"]
    css = ["css"]
    js = ["js"]
    file_extension = url.split(".")[-1]
    if file_extension in image:
        filetype = "image"
        urltype = "im_"
    elif file_extension in css:
        filetype = "css"
        urltype = "cs_"
    elif file_extension in js:
        filetype = "js"
        urltype = "js_"
    else:
        filetype = "unknown"
        urltype = "id_"
    return urltype





def remove_empty_folders(path, remove_root=True):
    print("")
    print("Removing empty output folders...")
    count = 0
    if not os.path.isdir(path):
        return
    # remove empty subfolders
    for root, dirs, files in os.walk(path, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):
                try:
                    os.rmdir(dir_path)
                    print(f"-----> {dir_path}")
                    count += 1
                except OSError as e:
                    print(f"Error removing {dir_path}: {e}")
    # remove empty root folder
    if remove_root and not os.listdir(path):
        try:
            os.rmdir(path)
            print(f"-----> {path}")
            count += 1
        except OSError as e:
            print(f"Error removing {path}: {e}")
    if count == 0:
        print("No empty folders found")





# example download: http://web.archive.org/web/20190815104545id_/https://www.google.com/
# example url: https://www.google.com/
# example timestamp: 20190815104545
def download_url_list(download_list, output, mode):
    """
    Download the latest version of each file snapshot.
    If a file has multiple snapshots, only the latest one will be downloaded.
    """
    #def download_batch(download_list):
    print("\nDownloading latest snapshots of each file...")
    failed_urls = []
    for snapshot in download_list:
        print(f"\n-----> Snapshot [{download_list.index(snapshot) + 1}/{len(download_list)}]")
        timestamp, url = snapshot["timestamp"], snapshot["url"]
        type = determine_url_filetype(url)
        download_url = f"http://web.archive.org/web/{timestamp}{type}/{url}"
        domain, subdir, filename = split_url(url)
        if mode == "current": download_dir = os.path.join(output, domain, subdir)
        if mode == "full": download_dir = os.path.join(output, domain, timestamp, subdir)
        download_filepath = os.path.join(download_dir, filename)
        create_dirs(download_dir)
        failed_urls.append(download_url_entry(download_url, download_filepath))
    failed_urls = [url for url in failed_urls if url]
    if failed_urls:
        skip_urls = []
        print(f"\n-----> {len(failed_urls)} downloads failed")
        print(f"\n-----> Retrying...")
        for snapshot in failed_urls:
            print(f"\n-----> RETRY Snapshot [{failed_urls.index(snapshot) + 1}/{len(failed_urls)}]")
            skip_urls.append(download_url_entry(download_url, download_filepath))
        skip_urls = [url for url in skip_urls if url]
        print(f"\n-----> Fail downloads: {len(skip_urls)}")

    print("\n-----> Success downloads: " + str(len(download_list) - len(failed_urls)))
    
    # batch_size = len(download_list) // 10
    # batch_list = [download_list[i:i + batch_size] for i in range(0, len(download_list), batch_size)]
    # for batch in batch_list:
    #     threads = []
    #     thread = threading.Thread(target=download_batch, args=(batch,))
    #     thread.start()
    #     threads.append(thread)
    # for thread in threads:
    #     thread.join()

def download_url_entry(url, output):
    max_retries = 2
    sleep_time = 45
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
    for i in range(max_retries):
        try:
            data = requests.get(url, headers=headers)
            with open(output, 'wb') as file:
                file.write(data.content)
            print(f"{url} -> {output}")
            break
        except requests.exceptions.ConnectionError as e:
            print(f"-----> REFUSED connection ({i+1}/{max_retries}), retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)
    else:
        print(f"FAILED download, append to failed_urls: {url}")
        return url





# scan output folder and guess mimetype for each file
# if add file extension if not present
# def guess_mimetype(filepath):
#     print("")
#     print("Guessing mimetypes for unknown files...")
    