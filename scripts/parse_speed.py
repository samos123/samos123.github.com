import sys
import re
import json



def parse_float(line):
    res = re.findall(r"[-+]?\d*\.\d+|\d+", line.strip())
    if res:
        return float(res[0])
    else:
        return 0


def parse(filename):
    results = {
            "averageDownloadSpeed": 0,
            "averageUploadSpeed": 0,
            "minDownloadSpeed": 99999999,
            "minUploadSpeed": 999999999,
            "maxDownloadSpeed": 0,
            "maxUploadSpeed": 0,
            "count": 0,
            "rawResults": "",
    }

    with open(filename, "r") as speed_results_file:
        results["rawResults"] = speed_results_file.read()
        for line in results["rawResults"].splitlines():
            if "Download" in line:
                dl_speed = parse_float(line)
                results["count"] += 1
                results["averageDownloadSpeed"] += dl_speed
                results["maxDownloadSpeed"] = max(dl_speed, results["maxDownloadSpeed"])
                results["minDownloadSpeed"] = min(dl_speed, results["minDownloadSpeed"])
            if "Upload" in line:
                speed = parse_float(line)
                results["averageUploadSpeed"] += speed
                results["maxUploadSpeed"] = max(speed, results["maxUploadSpeed"])
                results["minUploadSpeed"] = min(speed, results["minUploadSpeed"])

    results["averageDownloadSpeed"] = results["averageDownloadSpeed"] / results["count"]
    results["averageUploadSpeed"] = results["averageUploadSpeed"] / results["count"]
    return results


if __name__ == "__main__":
    filename = sys.argv[1] 
    results = parse(filename)
    json.dump(results, sys.stdout)
