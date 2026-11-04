import argparse
import json
import os
import sys
from urllib.parse import urlparse
import requests
import re
import time

CHECK_STATUS_TIMEOUT_SEC = 15
MAX_TIME_CHECKING_SEC = 7200
LOCAL_DOWNLOADS_DIR = "downloads"
MAX_REQUEST_TRIES = 5
MAX_POLL_RETRIES = 3
POLL_RETRY_DELAY = 30
MAX_DOWNLOAD_RETRIES = 3
DOWNLOAD_RETRY_DELAY = 15
BODY_DATA_AS_FORM = "form"
BODY_DATA_AS_JSON = "json"
PORT_HTTP = 80
PORT_HTTPS = 443
BUILD_GENERATING = "generating"
BUILD_GENERATED = "generated"
AVAILABLE_PLATFORMS_CONF = ["windows", "windows-x86", "linux", "android", "macos"]
RE_PATTERN_BUILD_STATUS = r" (.*?)<\/span>"
RE_PATTERN_CHECK_FOR_FILE = r"window\.location\.replace\('\/check_for_file\?(.*)'\);"
RE_PATTERN_PAGE_TITLE = r" (.*)<\/title>"
reBuildStatus = re.compile(RE_PATTERN_BUILD_STATUS)
reCheckFile = re.compile(RE_PATTERN_CHECK_FOR_FILE)
rePageTitle = re.compile(RE_PATTERN_PAGE_TITLE)


def parseAddress(url):
    if "://" not in url:
        url = "http://" + url
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        print(f"Wrong protocol (scheme): {parsed.scheme}")
        return None, None, None, None, None
    login = parsed.username
    password = parsed.password
    domain = parsed.hostname
    port = parsed.port
    scheme = parsed.scheme
    if port is None:
        port = PORT_HTTPS if scheme == "https" else PORT_HTTP
    return login, password, domain, port, scheme


def tryRequest(method, url, body=None, auth=None, bodyDataType=BODY_DATA_AS_JSON):
    curTry = 0
    response = None
    if bodyDataType not in (BODY_DATA_AS_FORM, BODY_DATA_AS_JSON) and body is not None:
        print(f"Unknown body data type: {bodyDataType}")
        return None
    while curTry != MAX_REQUEST_TRIES:
        try:
            formData = body if body and bodyDataType == BODY_DATA_AS_FORM else None
            jsonData = body if body and bodyDataType == BODY_DATA_AS_JSON else None
            response = requests.request(
                method=method, url=url, json=jsonData, data=formData, auth=auth
            )
            break
        except Exception as e:
            curTry += 1
            print(f"[{curTry}/{MAX_REQUEST_TRIES}] Request unsuccessful: {e}")
            if curTry == MAX_REQUEST_TRIES:
                return None
    return response


def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", required=True)
    parser.add_argument("-s", "--server", required=True)
    parser.add_argument("--set-version")
    parser.add_argument("--set-platform")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-p", "--preserve-log", action="store_true")
    parser.add_argument("-d", "--disable-download", action="store_true")
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args()
    return (
        args.file,
        args.server,
        args.verbose,
        args.preserve_log,
        args.disable_download,
        args.set_version,
        args.set_platform,
        args.allow_partial,
    )


def parseBuildStageInfo(html):
    resultStatus = reBuildStatus.search(html)
    if not resultStatus:
        print("Problem parsing build status from HTML.")
        return None, None, None, None
    stageInfo = resultStatus.group(1)
    resultCheckFile = reCheckFile.search(html)
    if not resultCheckFile:
        print("Problem parsing check file query from HTML.")
        return None, None, None, None
    checkFileQuery = resultCheckFile.group(1)
    filename = uuid = platform = None
    for q in checkFileQuery.split("&"):
        key, val = q.split("=", 1)
        if key == "filename":
            filename = val
        elif key == "uuid":
            uuid = val
        elif key == "platform":
            platform = val
    return stageInfo, filename, uuid, platform


def getPageTitle(html):
    result = rePageTitle.search(html)
    if result is None:
        print("Failed to get page title")
        return None
    return result.group(1)


def getResultDownloadLinks(baseUrl, filename, platform, uuid):
    common = f"{baseUrl}/download?"
    if platform == "windows":
        return [
            f"{common}filename={filename}.exe&uuid={uuid}",
            f"{common}filename={filename}.msi&uuid={uuid}",
        ]
    if platform == "windows-x86":
        return [f"{common}filename={filename}.exe&uuid={uuid}"]
    print(f"Unexpected platform: {platform}")
    return None


def downloadFiles(links, path, verbose):
    reFileName = re.compile(r"download\?filename=(.*)&")
    successCount = 0
    for idx, link in enumerate(links, 1):
        preamble = f"[{idx}/{len(links)}]"
        try:
            filename = reFileName.search(link).group(1)
            if verbose:
                print(f"{preamble} Downloading: {filename} ...", flush=True)
            downloaded = False
            for attempt in range(1, MAX_DOWNLOAD_RETRIES + 1):
                try:
                    response = requests.get(link, stream=True)
                    response.raise_for_status()
                    with open(f"{path}/{filename}", "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"{preamble} File saved locally: {filename}")
                    downloaded = True
                    break
                except requests.exceptions.RequestException as e:
                    if attempt < MAX_DOWNLOAD_RETRIES:
                        print(f"{preamble} Download attempt {attempt} failed: {e}")
                        time.sleep(DOWNLOAD_RETRY_DELAY)
                    else:
                        print(f"Error downloading {link}: {e}")
            if downloaded:
                successCount += 1
        except Exception as e:
            print(f"Error processing download link {link}: {e}")
    return successCount


def fatal(msg):
    print(f"! {msg}; Terminating.")
    sys.exit(-1)


def main():
    (
        confFile,
        rdgenAddress,
        verbose,
        dontFlushStatusLog,
        dontDownloadResult,
        setVersion,
        setPlatform,
        allowPartial,
    ) = parseArguments()
    if not os.path.exists(confFile):
        fatal(f"Configuration file not found: {confFile}")
    with open(confFile, "r", encoding="utf-8") as f:
        confObj = json.loads(f.read())
    print("Configuration JSON parsed successfully!")
    if setVersion:
        confObj["version"] = setVersion
    if setPlatform:
        confObj["platform"] = setPlatform
    login, password, domain, port, scheme = parseAddress(rdgenAddress)
    if domain is None:
        fatal("Failed parsing the address of rdgen server")
    portStr = f":{port}" if port not in (PORT_HTTPS, PORT_HTTP) else ""
    rdgenBaseUrl = f"{scheme}://{domain}{portStr}"
    basicAuth = (login, password) if login and password else None
    print("Requesting generator start...")
    # Convert bools/complex values for form post
    form = {}
    for k, v in confObj.items():
        if isinstance(v, bool):
            form[k] = "true" if v else "false"
        elif isinstance(v, (dict, list)):
            continue
        elif v is None:
            form[k] = ""
        else:
            form[k] = v
    response = tryRequest(
        "POST",
        f"{rdgenBaseUrl}/generator",
        body=form,
        auth=basicAuth,
        bodyDataType=BODY_DATA_AS_FORM,
    )
    if response is None:
        fatal(f"Connection error: {rdgenBaseUrl}")
    if not (200 <= response.status_code <= 299):
        fatal(f"Failed to start generator: HTTP {response.status_code}: {response.text[:500]}")
    print("Generator started! Checking initial build stage...")
    stageInfo, filename, uuid, platform = parseBuildStageInfo(response.text)
    if stageInfo is None:
        # dump snippet for debug
        print(response.text[:2000])
        fatal("Problem getting initial build stage information")
    print(f"File={filename} UUID={uuid} Platform={platform} Stage={stageInfo}")
    downloadLinks = getResultDownloadLinks(rdgenBaseUrl, filename, platform, uuid)
    if downloadLinks is None:
        fatal("Problem getting download links")
    checkForFileUrl = (
        f"{rdgenBaseUrl}/check_for_file?filename={filename}&uuid={uuid}&platform={platform}"
    )
    print(f"Web-page link: {checkForFileUrl}")
    for link in downloadLinks:
        print(f"  - {link}")
    print(f"Build initiated. Checking status every {CHECK_STATUS_TIMEOUT_SEC}s...")
    elapsedSeconds = 0
    pollFailures = 0
    while True:
        response = tryRequest("GET", checkForFileUrl, auth=basicAuth)
        if response is None or not (200 <= response.status_code <= 299):
            pollFailures += 1
            if pollFailures >= MAX_POLL_RETRIES:
                fatal("Response was not successful from rdgen server")
            time.sleep(POLL_RETRY_DELAY)
            elapsedSeconds += POLL_RETRY_DELAY
            continue
        pollFailures = 0
        pageTitle = getPageTitle(response.text)
        if pageTitle is None:
            fatal("Page title is None")
        pageTitle = pageTitle.lower()
        if BUILD_GENERATING in pageTitle:
            stageInfo, _, _, _ = parseBuildStageInfo(response.text)
        elif BUILD_GENERATED in pageTitle:
            if " Error: No file generated " in response.text:
                fatal("No result file were generated")
            break
        else:
            fatal(f"Unexpected page title: {pageTitle}")
        if stageInfo is None:
            fatal("Problem getting stage information")
        h = elapsedSeconds // 3600
        m = (elapsedSeconds % 3600) // 60
        s = elapsedSeconds % 60
        print(f"[{h:02}:{m:02}:{s:02}] Stage: {stageInfo}", flush=True)
        time.sleep(CHECK_STATUS_TIMEOUT_SEC)
        elapsedSeconds += CHECK_STATUS_TIMEOUT_SEC
        if elapsedSeconds >= MAX_TIME_CHECKING_SEC:
            fatal("Waiting for too long")
    print("Build complete!")
    if dontDownloadResult:
        for link in downloadLinks:
            print(link)
        return
    savePath = f"{LOCAL_DOWNLOADS_DIR}/{filename}_{uuid}"
    os.makedirs(savePath, exist_ok=True)
    downloadedCount = downloadFiles(downloadLinks, savePath, verbose)
    print(f"Downloaded {downloadedCount}/{len(downloadLinks)} -> {savePath}")
    if downloadedCount == 0:
        fatal("No files were downloaded")


if __name__ == "__main__":
    main()
