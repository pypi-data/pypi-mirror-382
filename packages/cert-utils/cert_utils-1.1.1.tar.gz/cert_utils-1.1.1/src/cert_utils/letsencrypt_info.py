"""
This file contains the following:

* LetsEncrypt Rate Limits in JSON form
* Information on the LetsEncrypt Trust Chain
* A routine to load the LetsEncrypt Certificates into Python

Because this loads Certificates into memory for some operations, it should
generally not be imported.
"""

# stdlib
import copy
import os
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

# pypi
import requests
from typing_extensions import Required
from typing_extensions import TypedDict

# localapp
from .utils import cleanup_pem_text
from .utils import md5_text


# ==============================================================================


# updated ratelimits are published at:
# https://letsencrypt.org/docs/rate-limits/
# last checked: 2024.06.26

LIMITS: Dict[str, Dict[str, Any]] = {
    "names/certificate": {"limit": 100},  # "Names per Certificate"
    "certificates/domain": {
        "limit": 50,
        "timeframe": "1 week",
        "includes_renewals": False,
    },  # "Certificates per Registered Domain"
    "certificates/fqdn": {
        "limit": 5,
        "timeframe": "1 week",
    },  # "Duplicate Certificate"
    "registrations/ip_address": {
        "limit": 10,
        "timeframe": "3 hours",
    },  # "Accounts per IP Address"
    "registrations/ip_range": {
        "limit": 500,
        "timeframe": "3 hours",
        "range": "IPv6 /48",
    },  # "Accounts per IP Range"
    "new_orders": {
        "limit": 300,
        "timeframe": "3 hours",
        "acme-v2-only": True,
    },  # "New Orders"
    "pending_authorizations/account": {
        "limit": 300,
        "timeframe": "1 week",
    },  # "Pending Authorizations"
    "failed_validation/account/hostname": {
        "limit": 5,
        "timeframe": "1 hour",
    },  # "Failed Validation"
    "endpoints": {
        "new-reg": {
            "overall_requests": 20,
            "timeframe": "1 second",
        },  # ACME-V1
        "new-authz": {
            "overall_requests": 20,
            "timeframe": "1 second",
        },  # ACME-V1
        "new-cert": {
            "overall_requests": 20,
            "timeframe": "1 second",
        },  # ACME-V1
        "new-nonce": {
            "overall_requests": 20,
            "timeframe": "1 second",
        },  # ACME-V2
        "new-account": {
            "overall_requests": 20,
            "timeframe": "1 second",
        },  # ACME-V2
        "new-order": {
            "overall_requests": 20,
            "timeframe": "1 second",
        },  # ACME-V2
        "revoke-cert": {
            "overall_requests": 20,
            "timeframe": "1 second",
        },  # ACME-V2
        "/directory": {
            "overall_requests": 40,
            "timeframe": "1 second",
        },
        "/acme": {
            "overall_requests": 40,
            "timeframe": "1 second",
        },
        "/acme/*": {
            "overall_requests": 40,
            "timeframe": "1 second",
        },
    },  # "Overall Requests"; enforced by gateway/cdn/balancer
}


# ==============================================================================


# certificates are published online
# https://letsencrypt.org/certificates/
# last checked: 2020.12.03

# this info is checked for compliance with
# * tests.test_unit.UnitTest_LetsEncrypt_Data


CERT_CAS_VERSION = 4  # update when the information below changes
"""
format details:

the KEY in the dictionary is a unique string

the payload can have one of these two values, which reference another key:
    "alternates": ["isrg_root_x2_cross"],
    "alternate_of": "isrg_root_x2",

Special Values
    ".enddate": the args to datetime.datetime()

Compatibility Info
    via https://letsencrypt.org/docs/certificate-compatibility/
    Last updated: Jan 21, 2021

["cert.fingerprints"]["sha1"] = `openssl x509 -fingerprint -sha1 -noout -in isrg-root-x2.pem`

"""

CERT_CA_PAYLOAD = TypedDict(
    "CERT_CA_PAYLOAD",
    {
        "display_name": Required[str],
        "url_pem": Required[str],
        "is_trusted_root": Optional[bool],
        "is_untrusted_root": Optional[bool],
        "is_self_signed": Optional[bool],
        "signed_by": Required[str],
        "is_active": Required[bool],
        "is_retired": Optional[bool],
        "key_technology": Required[str],
        "cert.fingerprints": Optional[Dict[str, str]],
        ".enddate": Optional[Tuple[int, ...]],
        "compatibility": Optional[
            Dict[str, Tuple[str, Optional[str], Optional[str]]]
        ],  # platform: (min, max, note)
        "alternates": Optional[List[str]],
        "alternate_of": Optional[str],
        "letsencrypt_serial": Optional[str],
        # loaded via deprecated processors
        "cert_pem": Optional[str],
        "cert_pem_md5": Optional[str],
    },
    total=False,
)


CERT_CAS_DEPRECATED: Dict[str, CERT_CA_PAYLOAD] = {
    "trustid_root_x3": {
        "display_name": "DST Root CA X3",
        "url_pem": "https://letsencrypt.org/certs/trustid-x3-root.pem",
        "is_trusted_root": True,
        "is_self_signed": True,
        "signed_by": "trustid_root_x3",
        "is_active": False,
        "key_technology": "RSA",
        "cert.fingerprints": {
            "sha1": "DAC9024F54D8F6DF94935FB1732638CA6AD77C13",
        },
        ".enddate": (2021, 9, 30, 14, 1, 15),
        "compatibility": {
            "Windows": (">= XP SP3", None, None),
            "macOS": ("(most versions)", None, None),
            "iOS": ("(most versions)", None, None),
            "Android": (">= v2.3.6", None, None),
            "Mozilla Firefox": (">= v2.0", None, None),
            "Ubuntu": (">= precise / 12.04", None, None),
            "Debian": (">= squeee / 6", None, None),
            "Java 8": (">= 8u101", None, None),
            "Java 7": (">= 7u111", None, None),
            "NSS": (">= v3.11.9", None, None),
            "Amazon FireOS (Silk Browser)": ("?", None, None),
            "Cyanogen": ("> v10", None, None),
            "Jolla Sailfish OS": ("> v1.1.2.16", None, None),
            "Kindle": ("> v3.4.1", None, None),
            "Blackberry": (">= 10.3.3", None, None),
            "PS4 game console": ("with firmware >= 5.00", None, None),
        },
    },
    "isrg_root_x1_cross": {
        # x1 this is cross signed by x1 to act as an intermediate!
        "display_name": "ISRG Root X1 (IdenTrust cross-signed)",
        "url_pem": "https://letsencrypt.org/certs/isrg-root-x1-cross-signed.pem",
        "is_trusted_root": False,
        "is_active": False,
        "is_retired": True,
        "key_technology": "RSA",
        "signed_by": "trustid_root_x3",
        "alternate_of": "isrg_root_x1",
    },
    "letsencrypt_ocsp_root_x1": {
        "display_name": "Let's Encrypt OSCP Root X1",
        "url_pem": "https://letsencrypt.org/certs/isrg-root-ocsp-x1.pem",
        "is_active": True,
        "is_retired": True,
        "key_technology": "RSA",
        "signed_by": "isrg_root_x1",
    },
    "letsencrypt_intermediate_x1": {
        "display_name": "Let's Encrypt Authority X1",
        "url_pem": "https://letsencrypt.org/certs/letsencryptauthorityx1.pem",
        "is_active": False,
        "is_retired": True,
        "key_technology": "RSA",
        "signed_by": "isrg_root_x1",
        "alternates": ["letsencrypt_intermediate_x1_cross"],
        "letsencrypt_serial": "x1",
    },
    "letsencrypt_intermediate_x1_cross": {
        "display_name": "Let's Encrypt Authority X1 (IdenTrust cross-signed)",
        "url_pem": "https://letsencrypt.org/certs/lets-encrypt-x1-cross-signed.pem",
        "is_active": False,
        "is_retired": True,
        "key_technology": "RSA",
        "signed_by": "trustid_root_x3",
        "alternate_of": "letsencrypt_intermediate_x1",
        "letsencrypt_serial": "x1",
    },
    "letsencrypt_intermediate_x2": {
        "display_name": "Let's Encrypt Authority X2",
        "url_pem": "https://letsencrypt.org/certs/letsencryptauthorityx2.pem",
        "is_active": False,
        "is_retired": True,
        "key_technology": "RSA",
        "signed_by": "isrg_root_x1",
        "alternates": ["letsencrypt_intermediate_x2_cross"],
        "letsencrypt_serial": "x2",
    },
    "letsencrypt_intermediate_x2_cross": {
        "display_name": "Let's Encrypt Authority X2 (IdenTrust cross-signed)",
        "url_pem": "https://letsencrypt.org/certs/lets-encrypt-x2-cross-signed.pem",
        "is_active": False,
        "is_retired": True,
        "key_technology": "RSA",
        "signed_by": "trustid_root_x3",
        "alternate_of": "letsencrypt_intermediate_x2",
        "letsencrypt_serial": "x2",
    },
    "letsencrypt_intermediate_x3": {
        "display_name": "Let's Encrypt Authority X3",
        "url_pem": "https://letsencrypt.org/certs/letsencryptauthorityx3.pem",
        "is_active": False,
        "is_retired": True,
        "key_technology": "RSA",
        "signed_by": "isrg_root_x1",
        "alternates": ["letsencrypt_intermediate_x3_cross"],
        "letsencrypt_serial": "x3",
    },
    "letsencrypt_intermediate_x3_cross": {
        "display_name": "Let's Encrypt Authority X3 (IdenTrust cross-signed)",
        "url_pem": "https://letsencrypt.org/certs/lets-encrypt-x3-cross-signed.pem",
        "is_active": False,
        "is_retired": True,
        "key_technology": "RSA",
        "signed_by": "trustid_root_x3",
        "alternate_of": "letsencrypt_intermediate_x3",
        "letsencrypt_serial": "x3",
    },
    "letsencrypt_intermediate_x4": {
        "display_name": "Let's Encrypt Authority X4",
        "url_pem": "https://letsencrypt.org/certs/letsencryptauthorityx4.pem",
        "is_active": False,
        "is_retired": True,
        "key_technology": "RSA",
        "signed_by": "isrg_root_x1",
        "alternates": ["letsencrypt_intermediate_x4_cross"],
        "letsencrypt_serial": "x4",
    },
    "letsencrypt_intermediate_x4_cross": {
        "display_name": "Let's Encrypt Authority X4 (IdenTrust cross-signed)",
        "url_pem": "https://letsencrypt.org/certs/lets-encrypt-x4-cross-signed.pem",
        "is_active": False,
        "is_retired": True,
        "key_technology": "RSA",
        "signed_by": "trustid_root_x3",
        "alternate_of": "letsencrypt_intermediate_x4",
        "letsencrypt_serial": "x4",
    },
    "letsencrypt_intermediate_r3": {
        "display_name": "Let's Encrypt R3",
        "url_pem": "https://letsencrypt.org/certs/lets-encrypt-r3.pem",
        "is_active": True,
        "is_retired": True,
        "key_technology": "RSA",
        "signed_by": "isrg_root_x1",
        "alternates": ["letsencrypt_intermediate_r3_cross"],
        "letsencrypt_serial": "r3",
    },
    "letsencrypt_intermediate_r3_cross": {
        "display_name": "Let's Encrypt R3 (IdenTrust cross-signed)",
        "url_pem": "https://letsencrypt.org/certs/lets-encrypt-r3-cross-signed.pem",
        "is_active": True,
        "is_retired": True,
        "key_technology": "RSA",
        "signed_by": "trustid_root_x3",
        "alternate_of": "letsencrypt_intermediate_r3",
        "letsencrypt_serial": "r3",
    },
    "letsencrypt_intermediate_r4": {
        "display_name": "Let's Encrypt R4",
        "url_pem": "https://letsencrypt.org/certs/lets-encrypt-r4.pem",
        "is_active": True,
        "is_retired": True,
        "key_technology": "RSA",
        "signed_by": "isrg_root_x1",
        "alternates": ["letsencrypt_intermediate_r4_cross"],
        "letsencrypt_serial": "r4",
    },
    "letsencrypt_intermediate_r4_cross": {
        "display_name": "Let's Encrypt R4 (IdenTrust cross-signed)",
        "url_pem": "https://letsencrypt.org/certs/lets-encrypt-r4-cross-signed.pem",
        "is_active": True,
        "is_retired": True,
        "key_technology": "RSA",
        "signed_by": "trustid_root_x3",
        "alternate_of": "letsencrypt_intermediate_r4",
        "letsencrypt_serial": "r4",
    },
    "letsencrypt_intermediate_e1": {
        "display_name": "Let's Encrypt E1",
        "url_pem": "https://letsencrypt.org/certs/lets-encrypt-e1.pem",
        "is_active": True,
        "is_retired": True,
        "key_technology": "EC",  # ECDSA
        "signed_by": "isrg_root_x2",
        "letsencrypt_serial": "e1",
    },
    "letsencrypt_intermediate_e2": {
        "display_name": "Let's Encrypt E2",
        "url_pem": "https://letsencrypt.org/certs/lets-encrypt-e2.pem",
        "is_active": True,
        "is_retired": True,
        "key_technology": "EC",  # ECDSA
        "signed_by": "isrg_root_x2",
        "letsencrypt_serial": "e2",
    },
    "staging_letsencrypt_root_x1": {
        "display_name": "Fake LE Root X1",
        "url_pem": "https://letsencrypt.org/certs/fakelerootx1.pem",
        "is_trusted_root": True,  # not really, but we pretend!
        "is_untrusted_root": True,
        "is_self_signed": True,
        "is_active": True,
        "key_technology": "RSA",
        "signed_by": "staging_letsencrypt_root_x1",
    },
    "staging_letsencrypt_intermediate_x1": {
        "display_name": "Fake LE Intermediate X1",
        "url_pem": "https://letsencrypt.org/certs/fakeleintermediatex1.pem",
        "is_active": True,
        "key_technology": "RSA",
        "signed_by": "staging_letsencrypt_root_x1",
    },
    "e5": {
        "display_name": "Let's Encrypt E5",
        "url_pem": "https://letsencrypt.org/certs/e5.pem",
        "is_active": True,
        "key_technology": "EC",  # ECDSA
        "signed_by": "isrg_root_x2",
        "alternates": ["e5_cross"],
        "letsencrypt_serial": "e5",
    },
    "e5_cross": {
        "display_name": "Let's Encrypt E5 (X1 cross-signed)",
        "url_pem": "https://letsencrypt.org/certs/e5-cross.pem",
        "is_active": True,
        "key_technology": "EC",  # ECDSA
        "signed_by": "isrg_root_x1",
        "alternate_of": "e5",
        "letsencrypt_serial": "e5",
    },
    "e6": {
        "display_name": "Let's Encrypt E6",
        "url_pem": "https://letsencrypt.org/certs/e6.pem",
        "is_active": True,
        "key_technology": "EC",  # ECDSA
        "signed_by": "isrg_root_x2",
        "alternates": ["e6_cross"],
        "letsencrypt_serial": "e6",
    },
    "e6_cross": {
        "display_name": "Let's Encrypt E6 (X1 cross-signed)",
        "url_pem": "https://letsencrypt.org/certs/e6-cross.pem",
        "is_active": True,
        "key_technology": "EC",  # ECDSA
        "signed_by": "isrg_root_x1",
        "alternate_of": "e6",
        "letsencrypt_serial": "e6",
    },
    "r10": {
        "display_name": "Let's Encrypt R10",
        "url_pem": "https://letsencrypt.org/certs/r10.pem",
        "is_active": True,
        "key_technology": "RSA",
        "signed_by": "isrg_root_x1",
        "letsencrypt_serial": "r10",
    },
    "r11": {
        "display_name": "Let's Encrypt R11",
        "url_pem": "https://letsencrypt.org/certs/r11.pem",
        "is_active": True,
        "key_technology": "RSA",
        "signed_by": "isrg_root_x1",
        "letsencrypt_serial": "r11",
    },
}


CERT_CAS_DATA: Dict[str, CERT_CA_PAYLOAD] = {
    "isrg_root_x1": {
        "display_name": "ISRG Root X1",
        "url_pem": "https://letsencrypt.org/certs/isrgrootx1.pem",
        "is_trusted_root": True,
        "is_self_signed": True,
        "signed_by": "isrg_root_x1",
        "is_active": True,
        "key_technology": "RSA",
        "alternates": ["isrg_root_x1_cross"],
        "cert.fingerprints": {
            "sha1": "CABD2A79A1076A31F21D253635CB039D4329A5E8",
        },
        ".enddate": (2035, 6, 4, 11, 4, 38),
        "compatibility": {
            "Windows": (
                ">= XP SP3",
                None,
                "unless Automatic Root Certificate Updates have been disabled",
            ),
            "Windows Server": (
                ">= 2008",
                None,
                "unless Automatic Root Certificate Updates have been disabled",
            ),
            "macOS": (">= 10.12.1 Sierra", None, None),
            "iOS": (">= 10", None, None),
            "Android": (">= 7.1.1", None, None),
            "Firefox": (">= 50.0", None, None),
            "Ubuntu": (">= 12.04 Precise Pangolin ", None, "with updates applied"),
            "Debian": (">= 8 / Jessie", None, "with updates applied"),
            "RHEL 6": (">= 6.10", None, "with updates applied"),
            "RHEL 7": (">= 7.4", None, "with updates applied"),
            "RHEL 8": (">= 8", None, None),
            "Java 7": (">= 7u151", None, None),
            "Java 8": (">= 8u141", None, None),
            "Java 9": (">= 9", None, None),
            "NSS": (">= 3.26", None, None),
            "Chrome": (
                ">= 105",
                None,
                "earlier versions use the operating system trust store",
            ),
            "PlayStation PS4": (">= PS4 v8.0.0", None, None),
        },
    },
    "isrg_root_x2": {
        # x2 is self-signed by default, but is available as cross-signed by isrgrootx1
        "display_name": "ISRG Root X2",
        "url_pem": "https://letsencrypt.org/certs/isrg-root-x2.pem",
        "is_trusted_root": True,
        "is_self_signed": True,
        "signed_by": "isrg_root_x2",
        "is_active": True,
        "key_technology": "EC",  # ECDSA
        "alternates": ["isrg_root_x2_cross"],
        "cert.fingerprints": {
            "sha1": "BDB1B93CD5978D45C6261455F8DB95C75AD153AF",
        },
        ".enddate": (2040, 9, 17, 16, 0),
        "compatibility": {
            "Windows": (
                ">= XP SP3",
                None,
                "unless Automatic Root Certificate Updates have been disabled",
            ),
            "Windows Server": (
                ">= 2008",
                None,
                "unless Automatic Root Certificate Updates have been disabled",
            ),
            "macOS": (">= 13", None, None),
            "iOS": (">= 16", None, None),
            "Android": (">= 14", None, None),
            "Firefox": (">= 97", None, None),
            "Ubuntu": (">= 18.04 Bionic Beaver ", None, None),
            "Debian": (">= 12/ Bookworm", None, None),
            "RHEL 7": (">= 7.9", None, "with updates applied"),
            "RHEL 8": (">= 8.6", None, "with updates applied"),
            "RHEL 9": (">= 9.1", None, "with updates applied"),
            "Java 8": (">= 8u141", None, None),
            "Java 11": (">= 11.0.22", None, None),
            "Java 17": (">= 17.0.10", None, None),
            "Java 21": (">= 21.0.2", None, None),
            "Java 22": (">= 22", None, None),
            "NSS": (">= 3.74", None, None),
            "Chrome": (
                ">= 105",
                None,
                "earlier versions use the operating system trust store",
            ),
        },
    },
    "isrg_root_x2_cross": {
        # x2 this is cross signed by x1 to act as an intermediate!
        "display_name": "ISRG Root X2 (Cross-signed by ISRG Root X1)",
        "url_pem": "https://letsencrypt.org/certs/isrg-root-x2-cross-signed.pem",
        "is_trusted_root": False,
        "is_active": False,
        "key_technology": "RSA",
        "signed_by": "isrg_root_x1",
        "alternate_of": "isrg_root_x2",
    },
    "letsencrypt_staging_root_x1": {
        "display_name": "(STAGING) Pretend Pear X1",
        "url_pem": "https://letsencrypt.org/certs/staging/letsencrypt-stg-root-x1.pem",
        "is_trusted_root": True,
        "is_untrusted_root": True,
        "is_self_signed": True,
        "signed_by": "letsencrypt_staging_root_x1",
        "is_active": True,
        "key_technology": "EC",  # ECDSA
        "cert.fingerprints": {
            "sha1": "66493BA4F36D1731729B1118C7F5E2D540E3F37B",
        },
        ".enddate": (2035, 6, 4, 11, 0),
        "compatibility": {
            "All": ("<0", ">0", "Untrusted Fake Root"),
        },
    },
    "letsencrypt_staging_root_x2": {
        "display_name": "(STAGING) Bogus Broccoli X2",
        "url_pem": "https://letsencrypt.org/certs/staging/letsencrypt-stg-root-x2.pem",
        "is_trusted_root": True,
        "is_untrusted_root": True,
        "is_self_signed": True,
        "signed_by": "letsencrypt_staging_root_x2",
        "is_active": True,
        "key_technology": "EC",  # ECDSA
        "cert.fingerprints": {
            "sha1": "A465AF9AF04F1A86A2701B987B3ED3A75D50ECEA",
        },
        ".enddate": (2035, 6, 4, 11, 0),
        "compatibility": {
            "All": ("<0", ">0", "Untrusted Fake Root"),
        },
        "alternates": ["letsencrypt_staging_root_x2_signed_by_x2"],
    },
    "letsencrypt_staging_root_x2_signed_by_x2": {
        "display_name": "(STAGING) Bogus Broccoli X2 (X1 cross-signed)",
        "url_pem": "https://letsencrypt.org/certs/staging/letsencrypt-stg-root-x2-signed-by-x1.pem",
        "is_trusted_root": True,
        "is_untrusted_root": True,
        "is_self_signed": False,
        "signed_by": "letsencrypt_staging_root_x1",
        "alternate_of": "letsencrypt_staging_root_x2",
        "is_active": True,
        "key_technology": "EC",  # ECDSA
        "cert.fingerprints": {
            "sha1": "70CB7923F66CB2678B050CEF38D5B4CB28489E88",
        },
        ".enddate": (2025, 9, 15, 16, 0),
        "compatibility": {
            "All": ("<0", ">0", "Untrusted Fake Root"),
        },
    },
    "e7": {
        "display_name": "Let's Encrypt E7",
        "url_pem": "https://letsencrypt.org/certs/e7.pem",
        "is_active": True,
        "key_technology": "EC",  # ECDSA
        "signed_by": "isrg_root_x2",
        "alternates": ["e7_cross"],
        "letsencrypt_serial": "e7",
    },
    "e7_cross": {
        "display_name": "Let's Encrypt E7 (X1 cross-signed)",
        "url_pem": "https://letsencrypt.org/certs/e7-cross.pem",
        "is_active": True,
        "key_technology": "EC",  # ECDSA
        "signed_by": "isrg_root_x1",
        "alternate_of": "e7",
        "letsencrypt_serial": "e7",
    },
    "e8": {
        "display_name": "Let's Encrypt E8",
        "url_pem": "https://letsencrypt.org/certs/e8.pem",
        "is_active": True,
        "key_technology": "EC",  # ECDSA
        "signed_by": "isrg_root_x2",
        "alternates": ["e8_cross"],
        "letsencrypt_serial": "e8",
    },
    "e8_cross": {
        "display_name": "Let's Encrypt E8 (X1 cross-signed)",
        "url_pem": "https://letsencrypt.org/certs/e8-cross.pem",
        "is_active": True,
        "key_technology": "EC",  # ECDSA
        "signed_by": "isrg_root_x1",
        "alternate_of": "e8",
        "letsencrypt_serial": "e8",
    },
    "e9": {
        "display_name": "Let's Encrypt E9",
        "url_pem": "https://letsencrypt.org/certs/e9.pem",
        "is_active": True,
        "key_technology": "EC",  # ECDSA
        "signed_by": "isrg_root_x2",
        "alternates": ["e9_cross"],
        "letsencrypt_serial": "e9",
    },
    "e9_cross": {
        "display_name": "Let's Encrypt E9 (X1 cross-signed)",
        "url_pem": "https://letsencrypt.org/certs/e9-cross.pem",
        "is_active": True,
        "key_technology": "EC",  # ECDSA
        "signed_by": "isrg_root_x1",
        "alternate_of": "e9",
        "letsencrypt_serial": "e9",
    },
    "r12": {
        "display_name": "Let's Encrypt R12",
        "url_pem": "https://letsencrypt.org/certs/r12.pem",
        "is_active": True,
        "key_technology": "RSA",
        "signed_by": "isrg_root_x1",
        "letsencrypt_serial": "r12",
    },
    "r13": {
        "display_name": "Let's Encrypt R13",
        "url_pem": "https://letsencrypt.org/certs/r13.pem",
        "is_active": True,
        "key_technology": "RSA",
        "signed_by": "isrg_root_x1",
        "letsencrypt_serial": "r13",
    },
    "r14": {
        "display_name": "Let's Encrypt R14",
        "url_pem": "https://letsencrypt.org/certs/r14.pem",
        "is_active": True,
        "key_technology": "RSA",
        "signed_by": "isrg_root_x1",
        "letsencrypt_serial": "r14",
    },
}
_CERT_CAS_DEPRECATED_ORDER = [
    "trustid_root_x3",
    "isrg_root_x1_cross",
    "letsencrypt_ocsp_root_x1",
    "letsencrypt_intermediate_x1",
    "letsencrypt_intermediate_x1_cross",
    "letsencrypt_intermediate_x2",
    "letsencrypt_intermediate_x2_cross",
    "letsencrypt_intermediate_x3",
    "letsencrypt_intermediate_x3_cross",
    "letsencrypt_intermediate_x4",
    "letsencrypt_intermediate_x4_cross",
    "letsencrypt_intermediate_r3",
    "letsencrypt_intermediate_r3_cross",
    "letsencrypt_intermediate_r4",
    "letsencrypt_intermediate_r4_cross",
    "letsencrypt_intermediate_e1",
    "letsencrypt_intermediate_e2",
    "e5",
    "e5_cross",
    "e6",
    "e6_cross",
    "r10",
    "r11",
    "staging_letsencrypt_root_x1",
    "staging_letsencrypt_intermediate_x1",
]
_CERT_CAS_ORDER = [
    "isrg_root_x1",
    "isrg_root_x2",
    "isrg_root_x2_cross",
    "e7",
    "e7_cross",
    "e8",
    "e8_cross",
    "e9",
    "e9_cross",
    "r12",
    "r13",
    "r14",
    "letsencrypt_staging_root_x1",
    "letsencrypt_staging_root_x2",
    "letsencrypt_staging_root_x2_signed_by_x2",
]


# what are our default root preferences?
DEFAULT_CA_PREFERENCES = [
    "isrg_root_x2",
    "isrg_root_x1",
]


# these should be a listing of serials
# e.g.: ("x1", "x2", "x3", "x4", "r3", "r4", "e1", "e2")
CA_LE_INTERMEDIATES = []
CA_LE_INTERMEDIATES_CROSSED = []
for _cert_id, _payload in CERT_CAS_DATA.items():
    _serial = _payload.get("letsencrypt_serial")
    if not _serial:
        continue
    if not _payload.get("alternate_of"):
        if not _payload.get("is_trusted_root"):
            CA_LE_INTERMEDIATES.append(_serial)
    else:
        CA_LE_INTERMEDIATES_CROSSED.append(_serial)


# LOAD THE CERTS INTO THE SYSTEM
_dir_here = os.path.abspath(os.path.dirname(__file__))
_dir_certs = os.path.join(_dir_here, "letsencrypt-certs")
for cert_id, cert_data in CERT_CAS_DATA.items():
    _filename = cert_data["url_pem"].split("/")[-1]  # type: ignore[attr-defined]
    _filepath = os.path.join(_dir_certs, _filename)
    with open(_filepath, "r") as _fp:
        cert_pem_text = _fp.read()
        cert_pem_text = cleanup_pem_text(cert_pem_text)
        cert_data["cert_pem"] = cert_pem_text


def download_letsencrypt_certificates() -> Dict[str, Any]:
    """
    DEPRECATED

    nothing calls this. may be useful for testing to ensure the certs have not
    changed on disk, such as the whitespace issue in 2021/02

    download the known LetsEncrypt certificates

    * correct usage of `requests`
    - currently using `.content`, which is raw bytes
    - usually one uses `.text`, which is `.content` that is decoded
    - there was some concern that triggered this utf8 decode at some point...
    """
    # ???: raise Exception if the cert_pem changes?
    certs = copy.deepcopy(CERT_CAS_DATA)
    for c in list(certs.keys()):
        resp = requests.get(certs[c]["url_pem"])
        if resp.status_code != 200:
            raise ValueError("Could not load certificate")
        cert_pem_text = resp.text
        cert_pem_text = cleanup_pem_text(cert_pem_text)
        certs[c]["cert_pem"] = cert_pem_text
        certs[c]["cert_pem_md5"] = md5_text(cert_pem_text)
    return certs
