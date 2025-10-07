# -*- coding: utf-8 -*-

import datetime
import json
import os
import unittest
from glob import glob

from dateutil.tz import tzoffset

from whois.exceptions import WhoisUnknownDateFormatError
from whois.parser import (
    WhoisCa,
    WhoisEntry,
    cast_date,
    datetime_parse,
)

utc = tzoffset('UTC', 0)


class TestParser(unittest.TestCase):
    def test_com_expiration(self):
        data = """
        Status: ok
        Updated Date: 2017-03-31T07:36:34Z
        Creation Date: 2013-02-21T19:24:57Z
        Registry Expiry Date: 2018-02-21T19:24:57Z

        >>> Last update of whois database: Sun, 31 Aug 2008 00:18:23 UTC <<<
        """
        w = WhoisEntry.load("urlowl.com", data)
        expires = w.expiration_date.strftime("%Y-%m-%d")
        self.assertEqual(expires, "2018-02-21")

    def test_cast_date(self):
        dates = [
            "14-apr-2008",
            "2008-04-14",
            "2008-04-14 18:55:20Z.0Z",
        ]
        for d in dates:
            r = cast_date(d).strftime("%Y-%m-%d")
            self.assertEqual(r, "2008-04-14")

    def test_unknown_date_format(self):
        with self.assertRaises(WhoisUnknownDateFormatError):
            datetime_parse("UNKNOWN")

    def test_com_allsamples(self):
        """
        Iterate over all of the sample/whois/*.com files, read the data,
        parse it, and compare to the expected values in sample/expected/.
        Only keys defined in keys_to_test will be tested.

        To generate fresh expected value dumps, see NOTE below.
        """
        keys_to_test = [
            "domain_name",
            "expiration_date",
            "updated_date",
            "registrar",
            "registrar_url",
            "creation_date",
            "status",
        ]
        total = 0
        whois_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "samples", "whois", "*"
        )
        expect_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "samples", "expected"
        )
        for path in glob(whois_path):
            # Parse whois data
            domain = os.path.basename(path)
            with open(path, encoding="utf-8") as whois_fp:
                data = whois_fp.read()

            w = WhoisEntry.load(domain, data)
            results = {key: w.get(key) for key in keys_to_test}

            # NOTE: Toggle condition below to write expected results from the
            # parse results This will overwrite the existing expected results.
            # Only do this if you've manually confirmed that the parser is
            # generating correct values at its current state.
            if False:

                def date2str4json(obj):
                    if isinstance(obj, datetime.datetime):
                        return str(obj)
                    raise TypeError("{} is not JSON serializable".format(repr(obj)))

                outfile_name = os.path.join(expect_path, domain)
                with open(outfile_name, "w") as outfil:
                    expected_results = json.dump(results, outfil, default=date2str4json)
                continue

            # Load expected result
            with open(os.path.join(expect_path, domain)) as infil:
                expected_results = json.load(infil)

            # Compare each key
            compare_keys = set.union(set(results), set(expected_results))
            if keys_to_test is not None:
                compare_keys = compare_keys.intersection(set(keys_to_test))
            for key in compare_keys:
                total += 1
                self.assertIn(key, results)

                result = results.get(key)
                if isinstance(result, list):
                    result = [str(element) for element in result]
                if isinstance(result, datetime.datetime):
                    result = str(result)
                expected = expected_results.get(key)
                self.assertEqual(expected, result, '{}: {} != {} for {}'.format(key, expected, result, domain))

    def test_ca_parse(self):
        data = """
        Domain name:           testdomain.ca
        Domain status:         registered
        Creation date:         2000/11/20
        Expiry date:           2020/03/08
        Updated date:          2016/04/29
        DNSSEC:                Unsigned

        Registrar:             Webnames.ca Inc.
        Registry Registrant ID: 70

        Registrant Name:       Test Industries
        Registrant Organization:

        Admin Name:            Test Person1
        Admin Street:          Test Address
        Admin City:            Test City, TestVille
        Admin Phone:           +1.1235434123x123
        Admin Fax:             +1.123434123
        Admin Email:           testperson1@testcompany.ca

        Tech Name:             Test Persion2
        Tech Street:           Other TestAddress
                               TestTown OCAS Canada
        Tech Phone:            +1.09876545123
        Tech Fax:              +1.12312993873
        Tech Email:            testpersion2@testcompany.ca

        Name server:           a1-1.akam.net
        Name server:           a2-2.akam.net
        Name server:           a3-3.akam.net
        """
        expected_results = {
            "admin_name": "Test Person1",
            "creation_date": datetime.datetime(2000, 11, 20, 0, 0, tzinfo=utc),
            "dnssec": "Unsigned",
            "domain_name": "testdomain.ca",
            "emails": ["testperson1@testcompany.ca", "testpersion2@testcompany.ca"],
            "expiration_date": datetime.datetime(2020, 3, 8, 0, 0, tzinfo=utc),
            "fax": ["+1.123434123", "+1.12312993873"],
            "name_servers": ["a1-1.akam.net", "a2-2.akam.net", "a3-3.akam.net"],
            "phone": ["+1.1235434123x123", "+1.09876545123"],
            "registrant_name": "Test Industries",
            "registrant_number": "70",
            "registrar": "Webnames.ca Inc.",
            "registrar_url": None,
            "status": "registered",
            "updated_date": datetime.datetime(2016, 4, 29, 0, 0, tzinfo=utc),
            "whois_server": None,
        }
        self._parse_and_compare(
            "testcompany.ca", data, expected_results, whois_entry=WhoisCa
        )

    def test_ai_parse(self):
        data = """
Domain Name: google.ai
Registry Domain ID: 6eddd132ab114b12bd2bd4cf9c492a04-DONUTS
Registrar WHOIS Server: whois.markmonitor.com
Registrar URL: http://www.markmonitor.com
Updated Date: 2025-01-23T22:17:03Z
Creation Date: 2017-12-16T05:37:20Z
Registry Expiry Date: 2025-09-25T05:37:20Z
Registrar: MarkMonitor Inc.
Registrar IANA ID: 292
Registrar Abuse Contact Email: abusecomplaints@markmonitor.com
Registrar Abuse Contact Phone: +1.2083895740
Domain Status: clientDeleteProhibited https://icann.org/epp#clientDeleteProhibited
Domain Status: clientTransferProhibited https://icann.org/epp#clientTransferProhibited
Domain Status: clientUpdateProhibited https://icann.org/epp#clientUpdateProhibited
Registry Registrant ID: 93b24aca40c6451785c486627aa03267-DONUTS
Registrant Name: Domain Administrator
Registrant Organization: Google LLC
Registrant Street: 1600 Amphitheatre Parkway
Registrant City: Mountain View
Registrant State/Province: CA
Registrant Postal Code: 94043
Registrant Country: US
Registrant Phone: +1.6502530000
Registrant Phone Ext: 
Registrant Fax: +1.6502530001
Registrant Fax Ext: 
Registrant Email: dns-admin@google.com
Registry Admin ID: 93b24aca40c6451785c486627aa03267-DONUTS
Admin Name: Domain Administrator
Admin Organization: Google LLC
Admin Street: 1600 Amphitheatre Parkway
Admin City: Mountain View
Admin State/Province: CA
Admin Postal Code: 94043
Admin Country: US
Admin Phone: +1.6502530000
Admin Phone Ext: 
Admin Fax: +1.6502530001
Admin Fax Ext: 
Admin Email: dns-admin@google.com
Registry Tech ID: 93b24aca40c6451785c486627aa03267-DONUTS
Tech Name: Domain Administrator
Tech Organization: Google LLC
Tech Street: 1600 Amphitheatre Parkway
Tech City: Mountain View
Tech State/Province: CA
Tech Postal Code: 94043
Tech Country: US
Tech Phone: +1.6502530000
Tech Phone Ext: 
Tech Fax: +1.6502530001
Tech Fax Ext: 
Tech Email: dns-admin@google.com
Name Server: ns2.zdns.google
Name Server: ns3.zdns.google
Name Server: ns4.zdns.google
Name Server: ns1.zdns.google
DNSSEC: unsigned
        """

        expected_results = {
            "admin_address": "1600 Amphitheatre Parkway",
            "admin_city": "Mountain View",
            "admin_country": "US",
            "admin_email": "dns-admin@google.com",
            "admin_name": "Domain Administrator",
            "admin_org": "Google LLC",
            "admin_phone": "+1.6502530000",
            "admin_postal_code": "94043",
            "admin_state": "CA",
            "billing_address": None,
            "billing_city": None,
            "billing_country": None,
            "billing_email": None,
            "billing_name": None,
            "billing_org": None,
            "billing_phone": None,
            "billing_postal_code": None,
            "billing_state": None,
            "creation_date": datetime.datetime(2017, 12, 16, 5, 37, 20, tzinfo=utc),
            "domain_id": "6eddd132ab114b12bd2bd4cf9c492a04-DONUTS",
            "domain_name": "google.ai",
            'expiration_date': datetime.datetime(2025, 9, 25, 5, 37, 20, tzinfo=utc),
            "name_servers": [
                "ns2.zdns.google",
                "ns3.zdns.google",
                "ns4.zdns.google",
                "ns1.zdns.google",
            ],
            "registrant_address": "1600 Amphitheatre Parkway",
            "registrant_city": "Mountain View",
            "registrant_country": "US",
            "registrant_email": "dns-admin@google.com",
            "registrant_name": "Domain Administrator",
            "registrant_org": "Google LLC",
            "registrant_phone": "+1.6502530000",
            "registrant_postal_code": "94043",
            "registrant_state": "CA",
            "registrar": "MarkMonitor Inc.",
            "registrar_email": "abusecomplaints@markmonitor.com",
            "registrar_phone": "+1.2083895740",
            "tech_address": "1600 Amphitheatre Parkway",
            "tech_city": "Mountain View",
            "tech_country": "US",
            "tech_email": "dns-admin@google.com",
            "tech_name": "Domain Administrator",
            "tech_org": "Google LLC",
            "tech_phone": "+1.6502530000",
            "tech_postal_code": "94043",
            "tech_state": "CA",
            "status": [
                'clientDeleteProhibited https://icann.org/epp#clientDeleteProhibited',
                'clientTransferProhibited https://icann.org/epp#clientTransferProhibited',
                'clientUpdateProhibited https://icann.org/epp#clientUpdateProhibited'
            ],
            "updated_date": datetime.datetime(2025, 1, 23, 22, 17, 3, tzinfo=utc)
        }
        self._parse_and_compare("google.ai", data, expected_results)

    def test_cn_parse(self):
        data = """
            Domain Name: cnnic.com.cn
            ROID: 20021209s10011s00047242-cn
            Domain Status: serverDeleteProhibited
            Domain Status: serverUpdateProhibited
            Domain Status: serverTransferProhibited
            Registrant ID: s1255673574881
            Registrant: 中国互联网络信息中心
            Registrant Contact Email: servicei@cnnic.cn
            Sponsoring Registrar: 北京新网数码信息技术有限公司
            Name Server: a.cnnic.cn
            Name Server: b.cnnic.cn
            Name Server: c.cnnic.cn
            Name Server: d.cnnic.cn
            Name Server: e.cnnic.cn
            Registration Time: 2000-09-14 00:00:00
            Expiration Time: 2023-08-16 16:26:39
            DNSSEC: unsigned
        """
        expected_results = {
            "creation_date": datetime.datetime(2000, 9, 14, 0, 0, tzinfo=utc),
            "dnssec": "unsigned",
            "domain_name": "cnnic.com.cn",
            "emails": "servicei@cnnic.cn",
            "expiration_date": datetime.datetime(2023, 8, 16, 16, 26, 39, tzinfo=utc),
            "name": "中国互联网络信息中心",
            "name_servers": [
                "a.cnnic.cn",
                "b.cnnic.cn",
                "c.cnnic.cn",
                "d.cnnic.cn",
                "e.cnnic.cn",
            ],
            "registrar": "北京新网数码信息技术有限公司",
            "status": [
                "serverDeleteProhibited",
                "serverUpdateProhibited",
                "serverTransferProhibited",
            ],
        }
        self._parse_and_compare("cnnic.com.cn", data, expected_results)

    def test_il_parse(self):
        data = """
            query:        python.org.il

            reg-name:     python
            domain:       python.org.il

            descr:        Arik Baratz
            descr:        PO Box 7775 PMB 8452
            descr:        San Francisco, CA
            descr:        94120
            descr:        USA
            phone:        +1 650 6441973
            e-mail:       hostmaster AT arik.baratz.org
            admin-c:      LD-AB16063-IL
            tech-c:       LD-AB16063-IL
            zone-c:       LD-AB16063-IL
            nserver:      dns1.zoneedit.com
            nserver:      dns2.zoneedit.com
            nserver:      dns3.zoneedit.com
            validity:     10-05-2018
            DNSSEC:       unsigned
            status:       Transfer Locked
            changed:      domain-registrar AT isoc.org.il 20050524 (Assigned)
            changed:      domain-registrar AT isoc.org.il 20070520 (Transferred)
            changed:      domain-registrar AT isoc.org.il 20070520 (Changed)
            changed:      domain-registrar AT isoc.org.il 20070520 (Changed)
            changed:      domain-registrar AT isoc.org.il 20070807 (Changed)
            changed:      domain-registrar AT isoc.org.il 20071025 (Changed)
            changed:      domain-registrar AT isoc.org.il 20071025 (Changed)
            changed:      domain-registrar AT isoc.org.il 20081221 (Changed)
            changed:      domain-registrar AT isoc.org.il 20081221 (Changed)
            changed:      domain-registrar AT isoc.org.il 20160301 (Changed)
            changed:      domain-registrar AT isoc.org.il 20160301 (Changed)

            person:       Arik Baratz
            address:      PO Box 7775 PMB 8452
            address:      San Francisco, CA
            address:      94120
            address:      USA
            phone:        +1 650 9635533
            e-mail:       hostmaster AT arik.baratz.org
            nic-hdl:      LD-AB16063-IL
            changed:      Managing Registrar 20070514
            changed:      Managing Registrar 20081002
            changed:      Managing Registrar 20081221
            changed:      Managing Registrar 20081221
            changed:      Managing Registrar 20090502

            registrar name: LiveDns Ltd
            registrar info: http://domains.livedns.co.il
        """
        expected_results = {
            "dnssec": "unsigned",
            "domain_name": "python.org.il",
            "emails": "hostmaster@arik.baratz.org",
            "expiration_date": datetime.datetime(2018, 5, 10, 0, 0, tzinfo=utc),
            "name_servers": [
                "dns1.zoneedit.com",
                "dns2.zoneedit.com",
                "dns3.zoneedit.com",
            ],
            "phone": ["+1 650 6441973", "+1 650 9635533"],
            "referral_url": "http://domains.livedns.co.il",
            "registrant_address": [
                ":      PO Box 7775 PMB 8452",
                ":      San Francisco, CA",
                ":      94120",
                ":      USA",
            ],
            "registrant_name": "Arik Baratz",
            "registrar": "LiveDns Ltd",
            "status": "Transfer Locked",
        }
        self._parse_and_compare("python.org.il", data, expected_results)

    def test_ie_parse(self):
        data = """
        refer:        whois.weare.ie

domain:       IE

organisation: University College Dublin
organisation: Computing Services
organisation: Computer Centre
address:      Belfield
address:      Dublin City,  Dublin 4
address:      Ireland

contact:      administrative
name:         Chief Executive
organisation: IE Domain Registry Limited
address:      2 Harbour Square
address:      Dún Laoghaire
address:      Co. Dublin
address:      Ireland
phone:        +353 1 236 5412
fax-no:       +353 1 230 1273
e-mail:       tld-admin@weare.ie

contact:      technical
name:         Technical Services Manager
organisation: IE Domain Registry Limited
address:      2 Harbour Square
address:      Dún Laoghaire
address:      Co. Dublin
address:      Ireland
phone:        +353 1 236 5421
fax-no:       +353 1 230 1273
e-mail:       tld-tech@weare.ie

nserver:      B.NS.IE 2a01:4b0:0:0:0:0:0:2 77.72.72.34
nserver:      C.NS.IE 194.146.106.98 2001:67c:1010:25:0:0:0:53
nserver:      D.NS.IE 2a01:3f0:0:309:0:0:0:53 77.72.229.245
nserver:      G.NS.IE 192.111.39.100 2001:7c8:2:a:0:0:0:64
nserver:      H.NS.IE 192.93.0.4 2001:660:3005:1:0:0:1:2
nserver:      I.NS.IE 194.0.25.35 2001:678:20:0:0:0:0:35
ds-rdata:     64134 13 2 77B9519D16B62D0A70A7301945CBB3092A7978BFDE75A3BCFB3D4719396E436A

whois:        whois.weare.ie

status:       ACTIVE
remarks:      Registration information: http://www.weare.ie

created:      1988-01-27
changed:      2021-03-11
source:       IANA

# whois.weare.ie

Domain Name: rte.ie
Registry Domain ID: 672279-IEDR
Registrar WHOIS Server: whois.weare.ie
Registrar URL: https://www.blacknight.com
Updated Date: 2020-11-15T17:55:24Z
Creation Date: 2000-02-11T00:00:00Z
Registry Expiry Date: 2025-03-31T13:20:07Z
Registrar: Blacknight Solutions
Registrar IANA ID: not applicable
Registrar Abuse Contact Email: abuse@blacknight.com
Registrar Abuse Contact Phone: +353.599183072
Domain Status: ok https://icann.org/epp#ok
Registry Registrant ID: 354955-IEDR
Registrant Name: RTE Commercial Enterprises Limited
Registry Admin ID: 202753-IEDR
Registry Tech ID: 3159-IEDR
Registry Billing ID: REDACTED FOR PRIVACY
Name Server: ns1.rte.ie
Name Server: ns2.rte.ie
Name Server: ns3.rte.ie
Name Server: ns4.rte.ie
DNSSEC: signedDelegation
        """
        expected_results = {
            "admin_id": "202753-IEDR",
            "creation_date": datetime.datetime(2000, 2, 11, 0, 0, tzinfo=utc),
            "domain_name": "rte.ie",
            "expiration_date": datetime.datetime(2025, 3, 31, 13, 20, 7, tzinfo=utc),
            "name_servers": ["ns1.rte.ie", "ns2.rte.ie", "ns3.rte.ie", "ns4.rte.ie"],
            "registrar": "Blacknight Solutions",
            "registrar_contact": "abuse@blacknight.com",
            "status": "ok https://icann.org/epp#ok",
            "tech_id": "3159-IEDR",
        }
        self._parse_and_compare("rte.ie", data, expected_results)

    def test_nl_parse(self):
        data = """
        Domain name: utwente.nl
        Status:      active

        Registrar:
           Universiteit Twente
           Drienerlolaan 5
           7522NB ENSCHEDE
           Netherlands

        Abuse Contact:

        DNSSEC:      yes

        Domain nameservers:
           ns3.utwente.nl          131.155.0.37
           ns1.utwente.nl          130.89.1.2
           ns1.utwente.nl          2001:67c:2564:a102::3:1
           ns2.utwente.nl          130.89.1.3
           ns2.utwente.nl          2001:67c:2564:a102::3:2

        Record maintained by: NL Domain Registry
        """
        expected_results = {
            "creation_date": None,
            "dnssec": "yes",
            "domain_name": "utwente.nl",
            "expiration_date": None,
            "name_servers": ["ns1.utwente.nl", "ns2.utwente.nl", "ns3.utwente.nl"],
            "registrar": "Universiteit Twente",
            "registrar_address": "Drienerlolaan 5",
            "registrar_city": "ENSCHEDE",
            "registrar_country": "Netherlands",
            "registrar_postal_code": "7522NB",
            "status": "active",
            "updated_date": None,
        }
        self._parse_and_compare("utwente.nl", data, expected_results)

    def test_nl_expiration(self):
        data = """
        domain_name: randomtest.nl
        Status:      in quarantine
        Creation Date: 2008-09-24
        Updated Date: 2020-10-27
        Date out of quarantine: 2020-12-06T20:31:25
        """

        w = WhoisEntry.load("randomtest.nl", data)
        expires = w.expiration_date.strftime("%Y-%m-%d")
        self.assertEqual(expires, "2020-12-06")

    def test_dk_parse(self):
        data = """
#
# Copyright (c) 2002 - 2019 by DK Hostmaster A/S
#
# Version:
#
# The data in the DK Whois database is provided by DK Hostmaster A/S
# for information purposes only, and to assist persons in obtaining
# information about or related to a domain name registration record.
# We do not guarantee its accuracy. We will reserve the right to remove
# access for entities abusing the data, without notice.
#
# Any use of this material to target advertising or similar activities
# are explicitly forbidden and will be prosecuted. DK Hostmaster A/S
# requests to be notified of any such activities or suspicions thereof.

Domain:               dk-hostmaster.dk
DNS:                  dk-hostmaster.dk
Registered:           1998-01-19
Expires:              2022-03-31
Registration period:  5 years
VID:                  yes
Dnssec:               Signed delegation
Status:               Active

Registrant
Handle:               DKHM1-DK
Name:                 DK HOSTMASTER A/S
Address:              Ørestads Boulevard 108, 11.
Postalcode:           2300
City:                 København S
Country:              DK

Nameservers
Hostname:             auth01.ns.dk-hostmaster.dk
Hostname:             auth02.ns.dk-hostmaster.dk
Hostname:             p.nic.dk
"""

        expected_results = {
            "creation_date": datetime.datetime(1998, 1, 19, 0, 0, tzinfo=utc),
            "dnssec": "Signed delegation",
            "domain_name": "dk-hostmaster.dk",
            "expiration_date": datetime.datetime(2022, 3, 31, 0, 0, tzinfo=utc),
            "name_servers": [
                "auth01.ns.dk-hostmaster.dk",
                "auth02.ns.dk-hostmaster.dk",
                "p.nic.dk",
            ],
            "registrant_address": "Ørestads Boulevard 108, 11.",
            "registrant_city": "København S",
            "registrant_country": "DK",
            "registrant_handle": "DKHM1-DK",
            "registrant_name": "DK HOSTMASTER A/S",
            "registrant_postal_code": "2300",
            "registrar": None,
            "status": "Active",
        }
        self._parse_and_compare("dk-hostmaster.dk", data, expected_results)

    def _parse_and_compare(
        self, domain_name, data, expected_results, whois_entry=WhoisEntry
    ):
        actual_results = whois_entry.load(domain_name, data)
        # import pprint; pprint.pprint(actual_results)
        self.assertEqual(expected_results, actual_results)

    def test_sk_parse(self):
        data = """
        # whois.sk-nic.sk

        Domain:                       pipoline.sk
        Registrant:                   H410977
        Admin Contact:                H410977
        Tech Contact:                 H410977
        Registrar:                    PIPO-0002
        Created:                      2012-07-23
        Updated:                      2020-07-02
        Valid Until:                  2021-07-13
        Nameserver:                   ns1.cloudlikeaboss.com
        Nameserver:                   ns2.cloudlikeaboss.com
        EPP Status:                   ok

        Registrar:                    PIPO-0002
        Name:                         Pipoline s.r.o.
        Organization:                 Pipoline s.r.o.
        Organization ID:              48273317
        Phone:                        +421.949347169
        Email:                        peter.gonda@pipoline.com
        Street:                       Ladožská 8
        City:                         Košice
        Postal Code:                  040 12
        Country Code:                 SK
        Created:                      2017-09-01
        Updated:                      2020-07-02

        Contact:                      H410977
        Name:                         Ing. Peter Gonda
        Organization:                 Pipoline s.r.o
        Organization ID:              48273317
        Email:                        info@pipoline.com
        Street:                       Ladozska 8
        City:                         Kosice
        Postal Code:                  04012
        Country Code:                 SK
        Registrar:                    PIPO-0002
        Created:                      2017-11-22
        Updated:                      2017-11-22"""

        expected_results = {
            "admin": "H410977",
            "admin_city": "Kosice",
            "admin_country_code": "SK",
            "admin_email": "info@pipoline.com",
            "admin_organization": "Pipoline s.r.o",
            "admin_postal_code": "04012",
            "admin_street": "Ladozska 8",
            "creation_date": datetime.datetime(2012, 7, 23, 0, 0, tzinfo=utc),
            "domain_name": "pipoline.sk",
            "expiration_date": datetime.datetime(2021, 7, 13, 0, 0, tzinfo=utc),
            "name_servers": ["ns1.cloudlikeaboss.com", "ns2.cloudlikeaboss.com"],
            "registrar": "Pipoline s.r.o.",
            "registrar_city": "Košice",
            "registrar_country_code": "SK",
            "registrar_created": "2012-07-23",
            "registrar_email": "peter.gonda@pipoline.com",
            "registrar_name": "Pipoline s.r.o.",
            "registrar_organization_id": "48273317",
            "registrar_phone": "+421.949347169",
            "registrar_postal_code": "040 12",
            "registrar_street": "Ladožská 8",
            "registrar_updated": "2020-07-02",
            "updated_date": datetime.datetime(2020, 7, 2, 0, 0, tzinfo=utc),
        }
        self._parse_and_compare("pipoline.sk", data, expected_results)

    def test_bw_parse(self):
        data = """
% IANA WHOIS server
% for more information on IANA, visit http://www.iana.org
% This query returned 1 object

refer:        whois.nic.net.bw

domain:       BW

organisation: Botswana Communications Regulatory Authority (BOCRA)
address:      Plot 206/207 Independence Avenue
address:      Private Bag 00495
address:      Gaborone
address:      Botswana

contact:      administrative
name:         Engineer - ccTLD
organisation: BOCRA - Botswana Communications Regulatory Authority
address:      Plot 206/207 Independence Avenue
address:      Private Bag 00495
address:      Gaborone
address:      Botswana
phone:        +2673685419
fax-no:       +267 395 7976
e-mail:       ramotsababa@bocra.org.bw

contact:      technical
name:         Engineer - ccTLD
organisation: Botswana Communications Regulatory Authority (BOCRA)
address:      Plot 206/207 Independence Avenue
address:      Private Bag 00495
address:      Gaborone
address:      Botswana
phone:        +267 368 5410
fax-no:       +267 395 7976
e-mail:       matlapeng@bocra.org.bw

nserver:      DNS1.NIC.NET.BW 168.167.98.226 2c0f:ff00:1:3:0:0:0:226
nserver:      MASTER.BTC.NET.BW 168.167.168.37 2c0f:ff00:0:6:0:0:0:3 2c0f:ff00:0:6:0:0:0:5
nserver:      NS-BW.AFRINIC.NET 196.216.168.72 2001:43f8:120:0:0:0:0:72
nserver:      PCH.NIC.NET.BW 2001:500:14:6070:ad:0:0:1 204.61.216.70

whois:        whois.nic.net.bw

status:       ACTIVE
remarks:      Registration information: http://nic.net.bw

created:      1993-03-19
changed:      2022-07-27
source:       IANA

# whois.nic.net.bw

Domain Name: google.co.bw
Registry Domain ID: 3486-bwnic
Registry WHOIS Server: whois.nic.net.bw
Updated Date: 2022-11-29T09:33:04.665Z
Creation Date: 2012-11-12T22:00:00.0Z
Registry Expiry Date: 2023-12-31T05:00:00.0Z
Registrar Registration Expiration Date: 2023-12-31T05:00:00.0Z
Registrar: MarkMonitor Inc
Domain Status: clientTransferProhibited https://icann.org/epp#clientTransferProhibited
Domain Status: clientDeleteProhibited https://icann.org/epp#clientDeleteProhibited
Domain Status: clientUpdateProhibited https://icann.org/epp#clientUpdateProhibited
Registry RegistrantID: GcIIG-Z2bWn
RegistrantName: Google LLC
RegistrantOrganization: Google LLC
RegistrantStreet: 1600 Amphitheatre Parkway
RegistrantCity: Mountain View
RegistrantState/Province: CA
RegistrantPostal Code: 94043
RegistrantCountry: US
RegistrantPhone: +1.6502530000
RegistrantFax: +1.6502530001
RegistrantEmail: dns-adminATgoogle.com
Registry AdminID: fDojv-TYe2q
AdminName: Google LLC
AdminOrganization: Google LLC
AdminStreet: 1600 Amphitheatre Parkway
AdminCity: Mountain View
AdminState/Province: CA
AdminPostal Code: 94043
AdminCountry: US
AdminPhone: +1.6502530000
AdminFax: +1.6502530001
AdminEmail: dns-adminATgoogle.com
Registry TechID: 2sYG1-BSVgz
TechName: Google LLC
TechOrganization: Google LLC
TechStreet: 1600 Amphitheatre Parkway
TechCity: Mountain View
TechState/Province: CA
TechPostal Code: 94043
TechCountry: US
TechPhone: +1.6502530000
TechFax: +1.6502530001
TechEmail: dns-adminATgoogle.com
Registry BillingID: C2KQL-UUtMh
BillingName: MarkMonitor Inc.
BillingOrganization: CCOPS Billing
BillingStreet: 3540 East Longwing Lane Suite 300
BillingCity: Meridian
BillingState/Province: ID
BillingPostal Code: 83646
BillingCountry: US
BillingPhone: +1.2083895740
BillingFax: +1.2083895771
BillingEmail: ccopsbillingATmarkmonitor.com
Name Server: ns1.google.com
Name Server: ns2.google.com
Name Server: ns3.google.com
Name Server: ns4.google.com
DNSSEC: unsigned
"""

        expected_results = {
            "admin_address": "1600 Amphitheatre Parkway",
            "admin_city": "Mountain View",
            "admin_country": "US",
            "admin_email": "dns-adminATgoogle.com",
            "admin_name": "Google LLC",
            "admin_org": "Google LLC",
            "admin_phone": "+1.6502530000",
            "billing_address": "3540 East Longwing Lane Suite 300",
            "billing_city": "Meridian",
            "billing_country": "US",
            "billing_email": "ccopsbillingATmarkmonitor.com",
            "billing_name": "MarkMonitor Inc.",
            "billing_org": "CCOPS Billing",
            "billing_phone": "+1.2083895740",
            "creation_date": datetime.datetime(2012, 11, 12, 22, 0, tzinfo=utc),
            "dnssec": "unsigned",
            "domain_id": "3486-bwnic",
            "domain_name": "google.co.bw",
            "name_servers": [
                "ns1.google.com",
                "ns2.google.com",
                "ns3.google.com",
                "ns4.google.com",
            ],
            "registrant_address": "1600 Amphitheatre Parkway",
            "registrant_city": "Mountain View",
            "registrant_country": "US",
            "registrant_email": "dns-adminATgoogle.com",
            "registrant_name": "Google LLC",
            "registrant_org": "Google LLC",
            "registrant_phone": "+1.6502530000",
            "registrar": "MarkMonitor Inc",
            "tech_address": "1600 Amphitheatre Parkway",
            "tech_city": "Mountain View",
            "tech_country": "US",
            "tech_email": "dns-adminATgoogle.com",
            "tech_name": "Google LLC",
            "tech_org": "Google LLC",
            "tech_phone": "+1.6502530000",
        }
        self._parse_and_compare("google.co.bw", data, expected_results)

    def test_cm_parse(self):
        data = """
Domain Name: icp.cm
Registry Domain ID: 1104110-RegCM
Updated Date: 2025-05-27T04:46:44.214Z
Creation Date: 2024-08-24T13:17:43.633Z
Registry Expiry Date: 2026-08-24T13:17:44.316Z
Domain Status: ok https://icann.org/epp#ok
Registrar: Netcom.cm Sarl
Reseller: NetSto Inc. - https://www.netsto.com
Name Server: ns1.huaweicloud-dns.com
Name Server: ns1.huaweicloud-dns.net
Name Server: ns1.huaweicloud-dns.cn
Name Server: ns1.huaweicloud-dns.org
>>> Last update of WHOIS database: 2025-05-28T04:47:00.968Z <<<

For more information on EPP status codes, please visit https://icann.org/epp

TERMS OF USE: You are not authorized to access or query our Whois
database through the use of electronic processes that are high-volume and
automated.  Whois database is provided by ANTIC as a service to the internet
community on behalf of ANTIC accredited registrars and resellers.

The data is for information purposes only. ANTIC does not
guarantee its accuracy. By submitting a Whois query, you agree to abide
by the following terms of use: You agree that you may use this Data only
for lawful purposes and that under no circumstances will you use this Data
to: (1) allow, enable, or otherwise support the transmission of mass
unsolicited, commercial advertising or solicitations via e-mail, telephone,
or facsimile; or (2) enable high volume, automated, electronic processes
that apply to ANTIC members (or their computer systems). The
compilation, repackaging, dissemination or other use of this Data is prohibited.
"""

        expected_results = {
            "domain_name": "icp.cm",
            "registry_domain_id": "1104110-RegCM",
            "updated_date": datetime.datetime(2025, 5, 27, 4, 46, 44, 214000, tzinfo=utc),
            "creation_date": datetime.datetime(2024, 8, 24, 13, 17, 43, 633000, tzinfo=utc),
            "expiration_date": datetime.datetime(2026, 8, 24, 13, 17, 44, 316000, tzinfo=utc),
            "status": "ok https://icann.org/epp#ok",
            "registrar": "Netcom.cm Sarl",
            "reseller": "NetSto Inc. - https://www.netsto.com",
            "name_servers": ['ns1.huaweicloud-dns.com', 'ns1.huaweicloud-dns.net', 'ns1.huaweicloud-dns.cn',
                             'ns1.huaweicloud-dns.org']
        }
        self._parse_and_compare("icp.cm", data, expected_results)


if __name__ == "__main__":
    unittest.main()
