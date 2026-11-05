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
from PIL import Image, ImageChops
from ruamel.yaml import YAML


ROOT = Path(__file__).resolve().parent
CONFIG = YAML(typ="safe").load(ROOT / "stash.yaml")
AIRPORT_TEMPLATE = YAML(typ="safe").load(ROOT / "airport.stoverride")
RULES = list(csv.reader(CONFIG["rules"]))
PROVIDERS = CONFIG["rule-providers"]
ALI_DOH = "https://223.5.5.5/dns-query"
PREMATCH_REJECTS = {
    "reject-drop": "REJECT-DROP",
    "reject-domain": "REJECT",
    "reject-extra": "REJECT",
    "reject-phishing": "REJECT",
    "reject": "REJECT",
    "reject-no-drop": "REJECT",
    "awavenue": "REJECT",
}
PREMATCH_RULES = {
    name: next(csv.reader([
        f"AND,((RULE-SET,{name}),(NOT,((RULE-SET,corporate-domains)))),{policy},pre-matching"
    ])) for name, policy in PREMATCH_REJECTS.items()
}
STREAM_POLICIES = {
    "stream-us": "美国",
    "stream-eu": "欧洲",
    "stream-jp": "日本",
    "stream-kr": "韩国",
    "stream-hk": "香港",
    "stream-tw": "台湾",
    "stream-biliintl": "台湾",
}


class ConfigTests(unittest.TestCase):
    def test_icon_colors_and_shape(self):
        sources = json.loads((ROOT / "icons/sources.json").read_text(encoding="utf-8"))
        reference_alpha = None
        for source in sources:
            with self.subTest(icon=source["id"]):
                with Image.open(ROOT / "icons/rounded" / (source["id"] + ".png")) as icon:
                    self.assertEqual(icon.format, "PNG")
                    self.assertEqual(icon.size, (256, 256))
                    red, green, blue, alpha = icon.convert("RGBA").split()
                self.assertEqual(alpha.getbbox(), (12, 12, 244, 244))
                if reference_alpha is None:
                    reference_alpha = alpha
                self.assertIsNone(ImageChops.difference(alpha, reference_alpha).getbbox())
                if source["id"] != "apple":
                    color_range = ImageChops.lighter(
                        ImageChops.difference(red, green),
                        ImageChops.difference(green, blue),
                    )
                    self.assertGreater(sum(color_range.histogram()[16:]), 256)

    def test_icon_set(self):
        icon_set = json.loads((ROOT / "icons/stash.json").read_text(encoding="utf-8"))
        sources = json.loads((ROOT / "icons/sources.json").read_text(encoding="utf-8"))
        self.assertTrue(icon_set["name"])
        self.assertTrue(icon_set["description"])
        icons = {item["name"]: item["url"] for item in icon_set["icons"]}
        self.assertEqual(len(icons), len(icon_set["icons"]))
        self.assertEqual(icons, {group["name"]: group["icon"] for group in CONFIG["proxy-groups"]})
        self.assertEqual(set(icons), {source["name"] for source in sources})
        base_url = "https://raw.githubusercontent.com/SivonLi/proxy-config/configs/stash/icons/rounded/"
        expected_files = {source["id"] + ".png" for source in sources}
        self.assertEqual(expected_files, {path.name for path in (ROOT / "icons/rounded").glob("*.png")})
        for source in sources:
            filename = source["id"] + ".png"
            self.assertEqual(icons[source["name"]], base_url + filename + "?v=2")
            self.assertGreater((ROOT / "icons/rounded" / filename).stat().st_size, 0)
            self.assertEqual(urlsplit(source["url"]).scheme, "https")

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
        for name in ["direct", "domestic"]:
            for target in ["cdn-domain", "cdn", "global"]:
                self.assertLess(RULES.index(["RULE-SET", name, "DIRECT"]),
                                RULES.index(["RULE-SET", target, "默认代理"]))

    def test_fake_ip_resolution_path(self):
        self.assertEqual(CONFIG["dns"]["fake-ip-filter"],
                         ["rule-set:corporate-domains", "rule-set:lan", "rule-set:fake-ip-exclude"])
        self.assertEqual(CONFIG["dns"]["nameserver-policy"], {"rule-set:corporate-domains": "system"})
        ip_phase = False
        for rule in RULES:
            if rule[0] == "RULE-SET":
                provider = PROVIDERS[rule[1]]
                is_ip = (provider["behavior"] == "ipcidr"
                         or "/Clash/ip/" in urlsplit(provider.get("url", "")).path)
                if is_ip:
                    ip_phase = True
                else:
                    self.assertFalse(ip_phase, rule)
            elif rule[0] in {"IP-CIDR", "IP-CIDR6", "IP-ASN", "GEOIP"}:
                ip_phase = True
            elif rule[0].startswith("DOMAIN") or rule[0] == "AND":
                self.assertFalse(ip_phase, rule)
        self.assertTrue(ip_phase)

    def test_ruleset_sources(self):
        inline = {name for name, provider in PROVIDERS.items() if provider.get("type") == "inline"}
        self.assertEqual(inline, {"corporate-domains", "onepassword", "lark"})
        for name, provider in PROVIDERS.items():
            if name == "awavenue":
                self.assertEqual(provider["url"], "https://raw.githubusercontent.com/TG-Twilight/"
                                 "AWAvenue-Ads-Rule/main/Filters/AWAvenue-Ads-Rule-Clash-Classical.yaml")
                self.assertEqual(provider["behavior"], "classical")
                self.assertEqual(provider["format"], "yaml")
                self.assertEqual(provider["interval"], 86400)
            elif name not in inline:
                self.assertEqual(urlsplit(provider["url"]).hostname, "ruleset.skk.moe")
                self.assertEqual(provider["format"], "text")
        paths = [provider["path"] for name, provider in PROVIDERS.items() if name not in inline]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertFalse({"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-WILDCARD"} & {rule[0] for rule in RULES})

    def test_sukka_reject_rules(self):
        sources = {
            "reject-domain": ("domainset/reject.txt", "domain"),
            "reject-extra": ("domainset/reject_extra.txt", "domain"),
            "reject-phishing": ("domainset/reject_phishing.txt", "domain"),
            "reject": ("non_ip/reject.txt", "classical"),
            "reject-drop": ("non_ip/reject-drop.txt", "classical"),
            "reject-no-drop": ("non_ip/reject-no-drop.txt", "classical"),
            "sogouinput": ("non_ip/sogouinput.txt", "classical"),
            "reject-ip": ("ip/reject.txt", "classical"),
        }
        for name, (path, behavior) in sources.items():
            with self.subTest(provider=name):
                self.assertIn(name, PROVIDERS)
                self.assertEqual(PROVIDERS[name]["url"], "https://ruleset.skk.moe/Clash/" + path)
                self.assertEqual(PROVIDERS[name]["behavior"], behavior)
                self.assertEqual(PROVIDERS[name]["interval"], 86400)
        for name, rule in PREMATCH_RULES.items():
            self.assertIn(rule, RULES, name)
            self.assertLess(RULES.index(rule), RULES.index(["RULE-SET", "onepassword", "DIRECT"]))
        drop = RULES.index(PREMATCH_RULES["reject-drop"])
        self.assertTrue(all(drop < RULES.index(rule) for name, rule in PREMATCH_RULES.items()
                            if name != "reject-drop"))
        process_rule = ["RULE-SET", "sogouinput", "REJECT"]
        self.assertLess(RULES.index(["RULE-SET", "corporate-domains", "DIRECT"]), RULES.index(process_rule))
        self.assertLess(RULES.index(process_rule), RULES.index(["RULE-SET", "onepassword", "DIRECT"]))
        ip_rule = ["RULE-SET", "reject-ip", "REJECT-DROP", "no-resolve"]
        self.assertLess(RULES.index(["RULE-SET", "lan-ip", "DIRECT"]), RULES.index(ip_rule))
        self.assertLess(RULES.index(ip_rule), RULES.index(["RULE-SET", "ai-ip", "AI", "no-resolve"]))

    def test_group_choices(self):
        groups = {item["name"]: item for item in CONFIG["proxy-groups"]}
        self.assertEqual(len(groups), len(CONFIG["proxy-groups"]))
        regions = {"香港", "日本", "美国", "新加坡", "台湾", "韩国", "欧洲", "其他地区"}
        self.assertEqual(set(groups["默认代理"]["proxies"]), regions)
        self.assertEqual(groups["下载"]["proxies"], ["默认代理", "DIRECT"])
        self.assertEqual(set(groups["AI"]["proxies"]), regions - {"香港"})
        self.assertEqual(groups["AI"]["proxies"][0], "新加坡")
        self.assertEqual(groups["Lark"]["proxies"], ["日本", "默认代理"])
        for name in ["Apple", "Microsoft"]:
            self.assertEqual(groups[name]["proxies"], ["DIRECT", "默认代理"])
        self.assertEqual(groups["测速"]["proxies"][0], "DIRECT")
        self.assertEqual(set(groups["测速"]["proxies"]), regions | {"DIRECT"})
        self.assertNotIn("Telegram", groups)
        self.assertNotIn("Spotify", groups)
        self.assertFalse(any("流媒体" in name or "Bilibili" in name for name in groups))
        self.assertTrue(set(STREAM_POLICIES.values()) <= regions)
        other = groups["其他地区"]
        self.assertEqual(other["type"], "select")
        self.assertTrue(other["include-all"])
        self.assertNotIn("proxies", other)
        self.assertNotIn("tolerance", other)
        re.compile(other["filter"])
        graph = {}
        for name, group in groups.items():
            targets = set(group.get("proxies", []))
            self.assertTrue(targets <= set(groups) | {"DIRECT"})
            self.assertTrue(set(group.get("use", [])) <= set(CONFIG["proxy-providers"]))
            graph[name] = targets & set(groups)
            if name in regions - {"其他地区"}:
                self.assertEqual(group["type"], "url-test")
                self.assertEqual(group["interval"], 600)
                self.assertEqual(group["tolerance"], 50)
                self.assertTrue(group["lazy"])
                re.compile(group["filter"])
            else:
                self.assertEqual(group["type"], "select")
                self.assertEqual(group["interval"], -1)
        list(TopologicalSorter(graph).static_order())

    def test_builtin_dns_encryption(self):
        settings = CONFIG["dns"]
        self.assertFalse(CONFIG["ipv6"])
        self.assertFalse(settings["ipv6"])
        self.assertFalse(settings["follow-rule"])
        self.assertNotIn("fallback", settings)
        self.assertEqual(RULES[0], ["DST-PORT", "53", "REJECT", "pre-matching"])
        self.assertEqual([rule for rule in RULES if "pre-matching" in rule],
                         [RULES[0], *PREMATCH_RULES.values()])
        endpoints = []
        for field in ["nameserver", "default-nameserver", "proxy-server-nameserver"]:
            self.assertEqual(len(settings[field]), 1)
            endpoints.extend(settings[field])
        for endpoint in endpoints:
            address = urlsplit(endpoint)
            self.assertEqual(address.scheme, "https")
            self.assertIn(address.port, {None, 443})
            ipaddress.ip_address(address.hostname)

    def test_subscription_provider(self):
        self.assertEqual(CONFIG["proxy-providers"], {})
        self.assertFalse(CONFIG.get("proxies"))
        for group in CONFIG["proxy-groups"]:
            if group["type"] == "url-test" or group["name"] == "其他地区":
                self.assertTrue(group["include-all"])
                self.assertNotIn("use", group)
                self.assertNotIn("use-url", group)

    def test_airport_override_scope(self):
        self.assertEqual(set(AIRPORT_TEMPLATE), {"name", "desc", "category", "proxy-providers"})
        self.assertEqual(set(AIRPORT_TEMPLATE["proxy-providers"]), {AIRPORT_TEMPLATE["name"]})
        provider = AIRPORT_TEMPLATE["proxy-providers"][AIRPORT_TEMPLATE["name"]]
        self.assertEqual(provider["url"], "https://example.invalid/replace-with-your-clash-subscription")
        self.assertEqual(provider["interval"], 86400)
        self.assertEqual(provider["benchmark-url"], "https://www.gstatic.com/generate_204")
        self.assertEqual(provider["benchmark-timeout"], 5)
        self.assertNotIn("path", provider)
        template = YAML().load(ROOT / "airport.stoverride")
        name = next(iter(template["proxy-providers"]))
        self.assertEqual(name.anchor.value, "airport_name")
        self.assertIs(template["name"], name)
        comment = template.ca.items.get("proxy-providers", [None] * 4)[2]
        if comment:
            self.assertNotIn("#!replace", comment.value)

    def test_references_and_service_order(self):
        groups = {item["name"] for item in CONFIG["proxy-groups"]}
        used = {value.removeprefix("rule-set:") for value in CONFIG["dns"]["fake-ip-filter"]
                if value.startswith("rule-set:")}
        for rule in RULES:
            if rule[0] == "AND":
                self.assertIn(rule, PREMATCH_RULES.values())
                used.add(next(name for name, expected in PREMATCH_RULES.items() if rule == expected))
                used.add("corporate-domains")
                continue
            self.assertIn(rule[0], {"RULE-SET", "IP-CIDR", "DST-PORT", "DOMAIN-KEYWORD", "MATCH"})
            self.assertIn(rule[1] if rule[0] == "MATCH" else rule[2], groups | {"DIRECT", "REJECT", "REJECT-DROP"})
            if rule[0] == "RULE-SET":
                self.assertIn(rule[1], PROVIDERS)
                used.add(rule[1])
            if rule[0] == "IP-CIDR":
                ipaddress.ip_network(rule[1])
        self.assertEqual(used, set(PROVIDERS))
        self.assertEqual(RULES[1], ["RULE-SET", "corporate-domains", "DIRECT"])
        self.assertEqual(PROVIDERS["corporate-domains"]["behavior"], "domain")
        self.assertEqual(PROVIDERS["corporate-domains"]["payload"], ["+.guorenpcic.com"])
        self.assertLess(RULES.index(PREMATCH_RULES["awavenue"]), RULES.index(["RULE-SET", "onepassword", "DIRECT"]))
        for name in ["stream", "telegram"]:
            self.assertIn(["RULE-SET", name, "默认代理"], RULES)
        for name, target in [("lark", "Lark"),
                             ("apple-services", "Apple"), ("apple-cn", "DIRECT")]:
            self.assertLess(RULES.index(["RULE-SET", name, target]),
                            RULES.index(["RULE-SET", "stream", "默认代理"]))
        lark = RULES.index(["RULE-SET", "lark", "Lark"])
        for name, target in [("download-domain", "下载"), ("domestic", "DIRECT"), ("global", "默认代理")]:
            self.assertLess(lark, RULES.index(["RULE-SET", name, target]))
        onepassword = RULES.index(["RULE-SET", "onepassword", "DIRECT"])
        for name, target in [("download-domain", "下载"), ("download", "下载"), ("global", "默认代理")]:
            self.assertLess(onepassword, RULES.index(["RULE-SET", name, target]))

    def test_regional_streaming_precedence(self):
        general = RULES.index(["RULE-SET", "stream", "默认代理"])
        for provider, policy in STREAM_POLICIES.items():
            position = RULES.index(["RULE-SET", provider, policy])
            self.assertLess(position, general)
            for service, target in [("apple-services", "Apple"),
                                    ("apple-cn", "DIRECT"), ("microsoft", "Microsoft")]:
                self.assertLess(RULES.index(["RULE-SET", service, target]), position)
        self.assertLess(RULES.index(["RULE-SET", "stream-jp", "日本"]),
                        RULES.index(["RULE-SET", "stream-us", "美国"]))
        self.assertLess(RULES.index(["RULE-SET", "stream-biliintl", "台湾"]),
                        RULES.index(["RULE-SET", "stream-hk", "香港"]))
        self.assertLess(RULES.index(["RULE-SET", "speedtest", "测速"]),
                        RULES.index(["RULE-SET", "apple-services", "Apple"]))
        for provider in ["download-domain", "download"]:
            self.assertLess(RULES.index(["RULE-SET", "speedtest", "测速"]),
                            RULES.index(["RULE-SET", provider, "下载"]))
        self.assertIn(["RULE-SET", "download-ip", "下载", "no-resolve"], RULES)
        self.assertIn(["RULE-SET", "neteasemusic-ip", "DIRECT", "no-resolve"], RULES)
        self.assertIn(["RULE-SET", "telegram-asn", "默认代理", "no-resolve"], RULES)


def fetch_provider(item, proxies):
    name, provider = item
    if provider.get("type") == "inline":
        entries = provider["payload"]
    else:
        session = requests.Session()
        session.trust_env = False
        response = session.get(provider["url"], timeout=45, proxies=proxies)
        response.raise_for_status()
        if provider["format"] == "yaml":
            entries = YAML(typ="safe").load(response.text)["payload"]
        else:
            assert provider["format"] == "text", name
            assert "EOF" in response.text, name
            entries = [line.strip() for line in response.text.splitlines() if line.strip() and not line.startswith("#")]
    assert isinstance(entries, list) and entries, name
    assert all(isinstance(entry, str) and entry for entry in entries), name
    if provider["behavior"] == "ipcidr":
        for entry in entries:
            ipaddress.ip_network(entry)
    elif provider["behavior"] == "domain":
        assert all("," not in entry for entry in entries), name
    else:
        allowed = {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "DOMAIN-WILDCARD", "PROCESS-NAME", "IP-CIDR", "IP-CIDR6", "IP-ASN"}
        rows = list(csv.reader(entries))
        types = {row[0] for row in rows}
        assert types <= allowed, name
        if name in PREMATCH_REJECTS:
            assert types <= {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "DOMAIN-WILDCARD",
                             "IP-CIDR", "IP-CIDR6", "IP-ASN"}, name
        if name == "awavenue":
            assert types <= {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "DOMAIN-WILDCARD"}, name
        for row in rows:
            if row[0] in {"IP-CIDR", "IP-CIDR6"}:
                ipaddress.ip_network(row[1])
        if "/Clash/non_ip/" in urlsplit(provider["url"]).path:
            assert all(row[0] not in {"IP-CIDR", "IP-CIDR6", "IP-ASN"}
                       or "no-resolve" in row[2:] for row in rows), name
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
    required_domains = {"api-sams.walmartmobile.cn", "decoration-sams.walmartmobile.cn",
                        "cinema-api-prd-mx.wandafilm.com", "misc-api-prd-mx.wandafilm.com"}
    for domain, addresses in answers:
        if domain in required_domains:
            assert all(any(address in network for network in networks) for address in addresses), domain
    print(json.dumps({"providers": len(entries), "records": sum(map(len, entries.values())),
                      "awavenue_records": len(entries["awavenue"]),
                      "sukka_reject_records": {name: len(entries[name])
                                               for name in [*PREMATCH_REJECTS, "sogouinput", "reject-ip"]
                                               if name != "awavenue"},
                      "dns": [{"domain": domain, "addresses": [str(address) for address in addresses],
                               "china_addresses": sum(any(address in network for network in networks) for address in addresses)}
                              for domain, addresses in answers]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--online", action="store_true", help="下载真实规则并检查 DoH 服务")
    parser.add_argument("--proxy", help="下载公开规则时使用的 HTTP 代理；DoH 检查保持直连")
    args = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ConfigTests))
    if not result.wasSuccessful():
        raise SystemExit(1)
    if args.online:
        check_online(args.proxy)
