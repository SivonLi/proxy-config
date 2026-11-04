import argparse
import csv
import ipaddress
import json
import re
import unittest
from concurrent.futures import ThreadPoolExecutor
from graphlib import TopologicalSorter
from pathlib import Path
from urllib.parse import urlsplit

import dns.message
import dns.rcode
import dns.rdatatype
import requests
from ruamel.yaml import YAML


ROOT = Path(__file__).resolve().parent
CONFIG = YAML(typ="safe").load(ROOT / "stash.yaml")
RULES = list(csv.reader(CONFIG["rules"]))
PROVIDERS = CONFIG["rule-providers"]
ALI_DOH = "https://223.5.5.5/dns-query"
CF_DOH = "https://1.1.1.1/dns-query"


class ConfigTests(unittest.TestCase):
    def test_domestic_address_lookup(self):
        self.assertEqual(CONFIG["dns"]["nameserver"], [ALI_DOH])
        lookup = RULES.index(["RULE-SET", "lan-ip", "DIRECT"])
        self.assertLess(RULES.index(["RULE-SET", "global", "默认代理"]), lookup)
        self.assertLess(lookup, RULES.index(["RULE-SET", "apple-services-ip", "Apple", "no-resolve"]))
        for name in ["china-ip", "china-ipv6"]:
            rule = ["RULE-SET", name, "DIRECT"]
            self.assertIn(rule, RULES)
            self.assertLess(RULES.index(rule), RULES.index(["MATCH", "默认代理"]))

    def test_domestic_precedence(self):
        domestic = RULES.index(["RULE-SET", "domestic", "DIRECT"])
        for name in ["cdn", "cdn-domain", "global"]:
            if name in PROVIDERS:
                self.assertLess(domestic, RULES.index(["RULE-SET", name, "默认代理"]))
        policy = list(CONFIG["dns"]["nameserver-policy"])
        self.assertLess(policy.index("rule-set:direct,domestic"), policy.index("rule-set:global"))
        self.assertEqual(CONFIG["dns"]["nameserver-policy"]["rule-set:global"], CF_DOH)

    def test_ruleset_sources(self):
        inline = {name for name, provider in PROVIDERS.items() if provider.get("type") == "inline"}
        self.assertEqual(inline, {"spotify", "spotify-ip"})
        for name, provider in PROVIDERS.items():
            if name not in inline:
                self.assertEqual(urlsplit(provider["url"]).hostname, "ruleset.skk.moe")
                self.assertEqual(provider["format"], "text")
        self.assertFalse({"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-WILDCARD"} & {rule[0] for rule in RULES})

    def test_group_choices(self):
        groups = {item["name"]: item for item in CONFIG["proxy-groups"]}
        self.assertEqual(len(groups), len(CONFIG["proxy-groups"]))
        regions = {"香港", "日本", "美国", "新加坡", "台湾"}
        self.assertEqual(set(groups["默认代理"]["proxies"]), regions)
        self.assertEqual(set(groups["下载"]["proxies"]), regions)
        self.assertEqual(set(groups["AI"]["proxies"]), regions - {"香港"})
        self.assertEqual(groups["Spotify"]["proxies"][0], "默认代理")
        self.assertEqual(set(groups["Spotify"]["proxies"]), regions | {"默认代理"})
        for name in ["Apple", "Microsoft"]:
            self.assertEqual(groups[name]["proxies"][0], "DIRECT")
            self.assertEqual(set(groups[name]["proxies"]), regions | {"DIRECT"})
        self.assertFalse({"Telegram", "流媒体"} & set(groups))
        graph = {}
        for name, group in groups.items():
            targets = set(group.get("proxies", []))
            self.assertTrue(targets <= set(groups) | {"DIRECT"})
            self.assertTrue(set(group.get("use", [])) <= set(CONFIG["proxy-providers"]))
            graph[name] = targets & set(groups)
            if name in regions:
                self.assertEqual(group["type"], "url-test")
                self.assertEqual(group["interval"], 600)
                self.assertEqual(group["tolerance"], 50)
                self.assertTrue(group["lazy"])
                re.compile(group["filter"])
            else:
                self.assertEqual(group["type"], "select")
                self.assertEqual(group["interval"], -1)
        list(TopologicalSorter(graph).static_order())

    def test_dns_encryption(self):
        settings = CONFIG["dns"]
        self.assertFalse(CONFIG["ipv6"])
        self.assertFalse(settings["ipv6"])
        self.assertTrue(settings["follow-rule"])
        self.assertNotIn("fallback", settings)
        self.assertEqual(RULES[0], ["DST-PORT", "53", "REJECT"])
        endpoints = list(settings["nameserver-policy"].values())
        for field in ["nameserver", "default-nameserver", "proxy-server-nameserver"]:
            self.assertEqual(len(settings[field]), 1)
            endpoints.extend(settings[field])
        for endpoint in endpoints:
            address = urlsplit(endpoint)
            self.assertEqual(address.scheme, "https")
            self.assertIn(address.port, {None, 443})
            ipaddress.ip_address(address.hostname)
        self.assertIn(["IP-CIDR", "1.1.1.1/32", "默认代理", "no-resolve"], RULES)
        self.assertIn(["IP-CIDR", "223.5.5.5/32", "DIRECT", "no-resolve"], RULES)

    def test_references_and_service_order(self):
        groups = {item["name"] for item in CONFIG["proxy-groups"]}
        used = set()
        for rule in RULES:
            self.assertIn(rule[0], {"RULE-SET", "IP-CIDR", "DST-PORT", "DOMAIN-KEYWORD", "MATCH"})
            self.assertIn(rule[1] if rule[0] == "MATCH" else rule[2], groups | {"DIRECT", "REJECT"})
            if rule[0] == "RULE-SET":
                self.assertIn(rule[1], PROVIDERS)
                used.add(rule[1])
            if rule[0] == "IP-CIDR":
                ipaddress.ip_network(rule[1])
        self.assertEqual(used, set(PROVIDERS))
        for selector in CONFIG["dns"]["nameserver-policy"]:
            self.assertTrue(selector.startswith("rule-set:"))
            self.assertTrue(set(next(csv.reader([selector.removeprefix("rule-set:")]))) <= used)
        for name in ["stream", "telegram"]:
            self.assertIn(["RULE-SET", name, "默认代理"], RULES)
        for name, target in [("spotify", "Spotify"), ("apple-services", "Apple"), ("apple-cn", "DIRECT")]:
            self.assertLess(RULES.index(["RULE-SET", name, target]),
                            RULES.index(["RULE-SET", "stream", "默认代理"]))


def fetch_provider(item, proxies):
    name, provider = item
    if provider.get("type") == "inline":
        entries = provider["payload"]
    else:
        session = requests.Session()
        session.trust_env = False
        response = session.get(provider["url"], timeout=45, proxies=proxies)
        response.raise_for_status()
        assert "EOF" in response.text, name
        entries = [line.strip() for line in response.text.splitlines() if line.strip() and not line.startswith("#")]
    assert entries, name
    if provider["behavior"] == "ipcidr":
        for entry in entries:
            ipaddress.ip_network(entry)
    elif provider["behavior"] == "domain":
        assert all("," not in entry for entry in entries), name
    else:
        allowed = {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "DOMAIN-WILDCARD", "PROCESS-NAME", "IP-CIDR", "IP-CIDR6", "IP-ASN"}
        assert {row[0] for row in csv.reader(entries)} <= allowed, name
    return name, entries


def query_doh(endpoint, domain, proxies):
    session = requests.Session()
    session.trust_env = False
    query = dns.message.make_query(domain, "A")
    response = session.post(endpoint, data=query.to_wire(), timeout=30, proxies=proxies,
                            headers={"Content-Type": "application/dns-message", "Accept": "application/dns-message"})
    response.raise_for_status()
    answer = dns.message.from_wire(response.content)
    assert query.is_response(answer), domain
    assert answer.rcode() == dns.rcode.NOERROR, domain
    addresses = [ipaddress.ip_address(record.address) for records in answer.answer
                 if records.rdtype == dns.rdatatype.A for record in records]
    assert addresses, domain
    return domain, addresses


def check_online(proxy):
    proxies = {"http": proxy, "https": proxy} if proxy else {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        entries = dict(executor.map(lambda item: fetch_provider(item, proxies), PROVIDERS.items()))
    networks = [ipaddress.ip_network(entry) for entry in entries["china-ip"]]
    domains = ["cms.samsclub.cn", "api-sams.walmartmobile.cn", "decoration-sams.walmartmobile.cn",
               "cinema-api-prd-mx.wandafilm.com", "misc-api-prd-mx.wandafilm.com",
               "m.wandacinemas.com", "www.ruyifilm.com", "statici.icloud.com"]
    with ThreadPoolExecutor(max_workers=4) as executor:
        answers = list(executor.map(lambda domain: query_doh(ALI_DOH, domain, {}), domains))
    answers.append(query_doh(CF_DOH, "www.wikipedia.org", proxies))
    required_domains = {"api-sams.walmartmobile.cn", "decoration-sams.walmartmobile.cn",
                        "cinema-api-prd-mx.wandafilm.com", "misc-api-prd-mx.wandafilm.com"}
    for domain, addresses in answers:
        if domain in required_domains:
            assert all(any(address in network for network in networks) for address in addresses), domain
    print(json.dumps({"providers": len(entries), "records": sum(map(len, entries.values())),
                      "dns": [{"domain": domain, "addresses": [str(address) for address in addresses],
                               "china_addresses": sum(any(address in network for network in networks) for address in addresses)}
                              for domain, addresses in answers]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--online", action="store_true", help="下载真实规则并检查 DoH 服务")
    parser.add_argument("--proxy", help="下载规则和检查境外 DoH 时使用的 HTTP 代理")
    args = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ConfigTests))
    if not result.wasSuccessful():
        raise SystemExit(1)
    if args.online:
        check_online(args.proxy)
