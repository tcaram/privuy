import json

from storage import *
from utils import *

STATE_OWNED_PROVIDERS = [
    "CLIENTE ANTEL URUGUAY",
    "Administracion Nacional de Telecomunicaciones",
    "Presidencia",
    "UTE",
    "Servicio Central de Informatica"
]

def analyze_badger_data(site, report_by_site):
    block_count = 0
    trackers = []

    # one report for each crawled site
    for report in report_by_site:
        origins = report['origins']
        for dom, action in origins.items():
            if action in ['block', 'cookieblock']:
                trackers.append(dom)
                block_count += 1

    return (trackers, block_count)


def analyze_hosting(site, hosting):
    # must be hosted in Uruguay and within an IP Range owned by the government
    is_hosted_in_state_owned_servers = hosting['country'] == "UY" and hosting['provider'] in STATE_OWNED_PROVIDERS

    return (hosting['country'] == "UY", is_hosted_in_state_owned_servers, hosting['provider'])


def main():
    reports_store = Store("reports.csv")
    reports = reports_store.get_all()

    analytics_store = Store("analytics.csv")

    digested_reports = {}
    priv={}

    for entry in reports:
        try:
            site, privacy_report = entry[0], json.loads(entry[1])
        except Exception:
            print("Couldn't parse data from %s, skipping" % (entry[0]))
            continue

        _, tracker_count = analyze_badger_data(site, privacy_report['badger'])
        is_hosted_in_uy, is_hosted_in_state_owned_servers, hosting_provider = analyze_hosting(site, privacy_report['ip'])

        digested_reports[site] = {
            "tracker_count": tracker_count,
            "is_hosted_in_uy": is_hosted_in_uy,
            "is_hosted_in_state_owned_servers": is_hosted_in_state_owned_servers,
            "hosting_provider": hosting_provider,
            "score": score
        }

        analytics_store.save(site, tracker_count, int(is_hosted_in_uy), int(is_hosted_in_state_owned_servers), hosting_provider)

if __name__ == '__main__':
    main()
