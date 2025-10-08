# stdlib
import json
import os
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import TYPE_CHECKING
import unittest

# pypi
import cryptography
import josepy
from typing_extensions import Literal

# local
import cert_utils
from cert_utils import model
from cert_utils import utils
from cert_utils.errors import OpenSslError
from ._utils import _Mixin_filedata
from ._utils import CERT_CA_SETS
from ._utils import CSR_SETS
from ._utils import KEY_SETS
from ._utils import TEST_FILES

# ==============================================================================

EXTENDED_TESTS = bool(int(os.getenv("CERT_UTILS_EXTENDED_TESTS", "0")))

# ------------------------------------------------------------------------------

TYPE_KEY_TESTING_COMBINATIONS = Tuple[
    Tuple[
        Literal[model.KeyTechnologyEnum.RSA, model.KeyTechnologyEnum.EC],
        Optional[int],
        Optional[str],
    ],
    ...,
]

# these mixins are used to simulate behavior as if we are missing libraries


class _Mixin_fallback_possible(object):
    _fallback = False
    _fallback_global = False
    _fallback_cryptography = False
    _fallback_josepy = False


class _MixinNoCrypto_Global(_Mixin_fallback_possible):
    _fallback = True
    _fallback_global = True
    _fallback_cryptography = True
    _fallback_josepy = True

    def setUp(self):
        # print("_MixinNoCrypto_Global.setUp")
        # global cert_utils
        cert_utils.conditionals.cryptography = None
        cert_utils.conditionals.josepy = None

    def tearDown(self):
        # print("_MixinNoCrypto_Global.tearDown")
        # global cert_utils
        cert_utils.conditionals.cryptography = cryptography
        cert_utils.conditionals.josepy = josepy


class _Mixin_Missing_cryptography(_Mixin_fallback_possible):
    _fallback = True
    _fallback_cryptography = True

    def setUp(self):
        # global cert_utils
        cert_utils.conditionals.cryptography = None

    def tearDown(self):
        # global cert_utils
        cert_utils.conditionals.cryptography = cryptography


class _Mixin_Missing_josepy(_Mixin_fallback_possible):
    _fallback = True
    _fallback_josepy = True

    def setUp(self):
        # global cert_utils
        cert_utils.conditionals.josepy = None

    def tearDown(self):
        # global cert_utils
        cert_utils.conditionals.josepy = josepy


# ------------------------------------------------------------------------------


class UnitTest_VersionCompat(unittest.TestCase):
    """python -m unittest tests.test_unit.UnitTest_VersionCompat"""

    def test__josepy(self):
        self.assertTrue(cert_utils.conditionals.is_josepy_compatible())


class UnitTest_CertUtils(unittest.TestCase, _Mixin_fallback_possible, _Mixin_filedata):
    """python -m unittest tests.test_unit.UnitTest_CertUtils"""

    _account_sets: Dict = {
        "001": {
            "keytype": "RSA",
            "letsencrypt": True,
            "pem": True,
            "signature.input": "example.sample",
            "signature.output": "hN3bre1YpxSGbvKmx8zK9_o0yaxtDblDfS3Q3CsjAas9wUVIHk7NqxXH0HeEeZG_7T0AHH6HTfxMbucXK_dLog_g9AxQYFsRBc8587C8Z5rWF2YDCoo0W7JB7VOoLEHGfe7JRXeqgA9QSnci0wMFlKXC_6MbKxql8QtswOdvtFM85qcJsMCOSu2Xf6HLIAYFhdBJH-DvQGzE4ctOKAYCmDyXs42DBUU4CU0cNXj8TsN0cFRXvInvSqDsiPNSjyV32WC4clPHX69KEbs5Wr0WV2diHR-Q6w0QUljWZEDpcl8mb86LZwBqoUTHX2xstQI77sLcg7YhDfaIPrCjYJcNZw",
        },
        "002": {
            "keytype": "RSA",
            "letsencrypt": False,
            "pem": True,
            "signature.input": "example.sample",
            "signature.output": "eEwkfxlNp9qvpX1Mm_erpBwCj9BjqWqZj1PX7Qucw1CkUqfNVJokgas0MpsmBASjN2yX93TnFtgOXG81_vaitAGifcZlPEbFstQ1LLyUtKC2arbNiVBkHAzseCsU5MnUC6WWFonsPUJ_Lr5xHYkfd2vGfOs8_e-CPAOVHmv7LJQjNGovV0MbInlCbHY9P3d9OHA-hN-tOABke5kyO1lSiX3fifAcRGnLlJqz5Dumb9K80_oySzEPio4Ad1ktufwJP9l-MA4FaUI7lOkNbTq_he1SuIG8Mjw9hfx9I4YoGk9eqPdcWwBZc5hwErqtqfPOCI8Qcu84ipFU-9Z9Q7waOIMtWl8Sj4pJfGGkiCITEcrWpupWdHlv33s2rwTWFo6ZXyYuMiTddcSJIPhFmAsD74MKxFUBgSViCHNjisjqyCSzA2geAcWsXOAwtokTp62wEv5tlW9ZhhifD-VqucipFwCTuTkaJLKonMPX0DNikRYYKgonKaf7h8-eMZxebI-z0RxO57e4vHpR__3-bXcXl_Pfvf_iYipuluwrt1MoDod4_ahLnvVNIBvnXdhvBhKHsxHPOOya399BHKSeCllsUyNlBHay2i4ibP8efWEhW1emz21nu4isLxvFqeFjJaqeuFZmlFskMjHUbkvDSOq1BTafk3yI3mTFRFqDL7GbxrA",
        },
        "003": {
            "keytype": "EC",
            "letsencrypt": False,
            "pem": True,
            "signature.input": "example.sample",
            "signature.output": "MGUCMQCo82gcmd7B9SsMyW9VE7YRSpmw23s3_cGY5GNkHbtSsfEJ7LbnT715iDZNCG4sjOUCMAd4OqpbuAA2G5rkZRWvimGG-Ub9syYZ42dX1rV-r00I6BaL2AhZLPp9amZvFu32mg",
        },
    }
    _cert_sets: Dict = {
        "001": {
            "csr": True,
            "csr.subject": "",
            "csr.domains.all": [
                "a.example.com",
                "b.example.com",
                "c.example.com",
                "d.example.com",
            ],
            "csr.domains.subject": None,
            "csr.domains.san": [
                "a.example.com",
                "b.example.com",
                "c.example.com",
                "d.example.com",
            ],
            "cert": True,
            "cert.domains.all": [
                "a.example.com",
                "b.example.com",
                "c.example.com",
                "d.example.com",
            ],
            "cert.domains.subject": "a.example.com",
            "cert.domains.san": [
                "a.example.com",
                "b.example.com",
                "c.example.com",
                "d.example.com",
            ],
            "cert.notAfter": "2025-06-16 20:19:30+00:00",  # "Jun 16 20:19:30 2025 GMT",
            "cert.notBefore": "2020-06-16 20:19:30+00:00",
            "cert.fingerprints": {
                "sha1": "F63C5C66B52551EEDADF7CE44301D646680B8F5D",
                "sha256": "027E69B35F0D8F2D2A3D06D47208F0C4FD31B69A429DFC36BE8DD0D5B73D8DC4",
                "md5": "21C60FE639DF16CA5BF15D8207F07A42",
            },
            "cert.authority_key_identifier": "D159010094B0A62ADBABE54B2321CA1B6EBA93E7",
            "cert.issuer_uri": None,
            "key_technology_basic": "RSA",
            "key_technology": ("RSA", (4096,)),
            "pubkey_modulus_md5": "052dec9ebfb5036c7aa6dd61888765b6",
            "spki_sha256": "34E67CC615761CBADAF430B2E02E0EC39C99EEFC73CCE469B18AE54A37EF6942",
            "spki_sha256.b64": "NOZ8xhV2HLra9DCy4C4Ow5yZ7vxzzORpsYrlSjfvaUI=",
        },
        "002": {
            "csr": True,
            "csr.subject": "CN=example.com",
            "csr.domains.all": [
                "example.com",
            ],
            "csr.domains.subject": "example.com",
            "csr.domains.san": [],
            "cert": False,
            "key_technology_basic": "RSA",
            "key_technology": ("RSA", (1024,)),
            "pubkey_modulus_md5": "c25a298dc7de8f855453a6ed8be8bb5f",
            "spki_sha256": "C1FF7146EE861479AE997617CB994424905F9441C6D9E669A9A6CC520445C663",
            "spki_sha256.b64": "wf9xRu6GFHmumXYXy5lEJJBflEHG2eZpqabMUgRFxmM=",
        },
        "003": {
            "csr": True,
            "csr.subject": "",
            "csr.domains.all": [
                "example.com",
            ],
            "csr.domains.subject": None,
            "csr.domains.san": ["example.com"],
            "cert": True,
            "cert.domains.all": [
                "example.com",
            ],
            "cert.domains.subject": "example.com",
            "cert.domains.san": [
                "example.com",
            ],
            "cert.notAfter": "2025-06-16 22:06:46+00:00",  # "Jun 16 22:06:46 2025 GMT",
            "cert.notBefore": "2020-06-16 22:06:46+00:00",
            "cert.fingerprints": {
                "sha1": "E8503EAC0F4F9685841F961AD966774D66521C5E",
                "sha256": "CC8D066A7C59D67A4DAEE02AC67BAAC5DA0296303758CC824AF6243D5A8C78F6",
                "md5": "455A11B05729B3BDE11A86D5A94C40D7",
            },
            "cert.authority_key_identifier": "D159010094B0A62ADBABE54B2321CA1B6EBA93E7",
            "cert.issuer_uri": None,
            "key_technology_basic": "RSA",
            "key_technology": ("RSA", (1024,)),
            "pubkey_modulus_md5": "f625ac6f399f90867cbf6a4e5dd8fc9e",
            "spki_sha256": "043AF1B9CC1AF925C132E19574FB7B251F727D55E185D9882B7A72F11F82AD97",
            "spki_sha256.b64": "BDrxucwa+SXBMuGVdPt7JR9yfVXhhdmIK3py8R+CrZc=",
        },
        "004": {
            "csr": True,
            "csr.subject": "",
            "csr.domains.all": [
                "a.example.com",
                "b.example.com",
                "c.example.com",
                "d.example.com",
            ],
            "csr.domains.subject": "",
            "csr.domains.san": [
                "a.example.com",
                "b.example.com",
                "c.example.com",
                "d.example.com",
            ],
            "cert": True,
            "cert.domains.all": [
                "a.example.com",
                "b.example.com",
                "c.example.com",
                "d.example.com",
            ],
            "cert.domains.subject": "a.example.com",
            "cert.domains.san": [
                "a.example.com",
                "b.example.com",
                "c.example.com",
                "d.example.com",
            ],
            "cert.notAfter": "2025-06-16 22:07:02+00:00",  # "Jun 16 22:07:02 2025 GMT",
            "cert.notBefore": "2020-06-16 22:07:02+00:00",
            "cert.fingerprints": {
                "sha1": "A8880200452452ADF192847CDEC1330617204D14",
                "sha256": "3906F17472B9E180C6526135B0BBF4CA2C6187D2DC9067809FC023B5EA276257",
                "md5": "36D3A42948CF7C78D50660C9F46618B3",
            },
            "cert.authority_key_identifier": "D159010094B0A62ADBABE54B2321CA1B6EBA93E7",
            "cert.issuer_uri": None,
            "pubkey_modulus_md5": "797ba616e62dedcb014a7a37bcde3fdf",
            "key_technology_basic": "RSA",
            "key_technology": ("RSA", (1024,)),
            "spki_sha256": "04825ACA7FDE791C3FFDAC73B8F52575EA598753D0F9E995187E856E34633922",
            "spki_sha256.b64": "BIJayn/eeRw//axzuPUldepZh1PQ+emVGH6FbjRjOSI=",
        },
        "005": {
            "csr": True,
            "csr.subject": "CN=a.example.com",
            "csr.domains.all": [
                "a.example.com",
                "b.example.com",
                "c.example.com",
                "d.example.com",
            ],
            "csr.domains.subject": "a.example.com",
            "csr.domains.san": [
                "b.example.com",
                "c.example.com",
                "d.example.com",
            ],
            "cert": False,
            "key_technology_basic": "RSA",
            "key_technology": ("RSA", (1024,)),
            "pubkey_modulus_md5": "f4614ec52f34066ce074798cdc494d74",
            "spki_sha256": "BED992DAD570A4984EA47BE1C92F091839888BC3482D9206F891C4A8239AD2AB",
            "spki_sha256.b64": "vtmS2tVwpJhOpHvhyS8JGDmIi8NILZIG+JHEqCOa0qs=",
        },
    }
    _csr_sets_alt = {
        "001": {
            "directory": "key_technology-ec",
            "file.key": "ec384-1-key.pem",
            "file.csr": "ec384-1.csr",
            "csr": True,
            "csr.subject": "CN=ec384-1.example.com",
            "csr.domains.all": [
                "ec384-1.example.com",
            ],
            "csr.domains.subject": "ec384-1.example.com",
            "csr.domains.san": [],
            "cert": False,
            "pubkey_modulus_md5": "None",
            "key_technology_basic": "EC",
            "key_technology": ("EC", ("P-384",)),
            "spki_sha256": "E739FB0081868C97B8AC0D3773680974E9FCECBFA1FC8B80AFDDBE42F30D1D9D",
            "spki_sha256.b64": "5zn7AIGGjJe4rA03c2gJdOn87L+h/IuAr92+QvMNHZ0=",
        }
    }

    def test__parse_cert__domains(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test__parse_cert__domains
        """

        for cert_set in sorted(self._cert_sets.keys()):
            if not self._cert_sets[cert_set]["cert"]:
                continue
            cert_filename = "unit_tests/cert_%s/cert.pem" % cert_set
            cert_pem_filepath = self._filepath_testfile(cert_filename)
            cert_pem = self._filedata_testfile(cert_filename)
            with self.assertLogs("cert_utils", level="DEBUG") as logged:
                cert_domains = cert_utils.parse_cert__domains(
                    cert_pem=cert_pem, cert_pem_filepath=cert_pem_filepath
                )
                self.assertEqual(
                    cert_domains, self._cert_sets[cert_set]["cert.domains.all"]
                )
                if self._fallback_global or self._fallback_cryptography:
                    self.assertIn(
                        "DEBUG:cert_utils:.parse_cert__domains > openssl fallback",
                        logged.output,
                    )
                else:
                    self.assertNotIn(
                        "DEBUG:cert_utils:.parse_cert__domains > openssl fallback",
                        logged.output,
                    )

    def test__fingerprint_cert(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test__fingerprint_cert
        """

        for cert_set in sorted(self._cert_sets.keys()):
            if not self._cert_sets[cert_set]["cert"]:
                continue
            cert_filename = "unit_tests/cert_%s/cert.pem" % cert_set
            cert_pem_filepath = self._filepath_testfile(cert_filename)
            cert_pem = self._filedata_testfile(cert_filename)

            # defaults to sha1
            with self.assertLogs("cert_utils", level="DEBUG") as logged:
                _fingerprint = cert_utils.fingerprint_cert(
                    cert_pem=cert_pem, cert_pem_filepath=cert_pem_filepath
                )
                self.assertEqual(
                    _fingerprint, self._cert_sets[cert_set]["cert.fingerprints"]["sha1"]
                )
                if self._fallback_global or self._fallback_cryptography:
                    self.assertIn(
                        "DEBUG:cert_utils:.fingerprint_cert > openssl fallback",
                        logged.output,
                    )
                else:
                    self.assertNotIn(
                        "DEBUG:cert_utils:.fingerprint_cert > openssl fallback",
                        logged.output,
                    )

            # test the supported
            for _alg in ("sha1", "sha256", "md5"):
                _fingerprint = cert_utils.fingerprint_cert(
                    cert_pem=cert_pem,
                    cert_pem_filepath=cert_pem_filepath,
                    algorithm=_alg,
                )
                self.assertEqual(
                    _fingerprint, self._cert_sets[cert_set]["cert.fingerprints"][_alg]
                )
                # no need to test the fallback behavior again

            # test unsupported
            with self.assertRaises(ValueError) as cm:
                _fingerprint = cert_utils.fingerprint_cert(
                    cert_pem=cert_pem,
                    cert_pem_filepath=cert_pem_filepath,
                    algorithm="fake",
                )
            self.assertTrue(
                cm.exception.args[0].startswith("algorithm `fake` not in `('")
            )

    def test__parse_csr_domains(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test__parse_csr_domains
        """

        for cert_set in sorted(self._cert_sets.keys()):
            csr_filename = "unit_tests/cert_%s/csr.pem" % cert_set
            csr_pem_filepath = self._filepath_testfile(csr_filename)
            csr_pem = self._filedata_testfile(csr_filename)
            with self.assertLogs("cert_utils", level="DEBUG") as logged:
                csr_domains = cert_utils.parse_csr_domains(
                    csr_pem=csr_pem,
                    csr_pem_filepath=csr_pem_filepath,
                    submitted_domain_names=self._cert_sets[cert_set]["csr.domains.all"],
                )
                self.assertEqual(
                    csr_domains, self._cert_sets[cert_set]["csr.domains.all"]
                )
                if self._fallback_global or self._fallback_cryptography:
                    self.assertIn(
                        "DEBUG:cert_utils:.parse_csr_domains > openssl fallback",
                        logged.output,
                    )
                else:
                    self.assertNotIn(
                        "DEBUG:cert_utils:.parse_csr_domains > openssl fallback",
                        logged.output,
                    )

    def test__validate_csr(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test__validate_csr
        """
        for cert_set in sorted(self._cert_sets.keys()):
            csr_filename = "unit_tests/cert_%s/csr.pem" % cert_set
            csr_pem_filepath = self._filepath_testfile(csr_filename)
            csr_pem = self._filedata_testfile(csr_filename)
            with self.assertLogs("cert_utils", level="DEBUG") as logged:
                cert_utils.validate_csr(
                    csr_pem=csr_pem, csr_pem_filepath=csr_pem_filepath
                )
                if self._fallback_global or self._fallback_cryptography:
                    self.assertIn(
                        "DEBUG:cert_utils:.validate_csr > openssl fallback",
                        logged.output,
                    )
                else:
                    self.assertNotIn(
                        "DEBUG:cert_utils:.validate_csr > openssl fallback",
                        logged.output,
                    )

    def test__validate_key(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test__validate_key
        """

        for cert_set in sorted(self._cert_sets.keys()):
            key_filename = "unit_tests/cert_%s/privkey.pem" % cert_set
            key_pem_filepath = self._filepath_testfile(key_filename)
            key_pem = self._filedata_testfile(key_filename)
            with self.assertLogs("cert_utils", level="DEBUG") as logged:
                key_technology = cert_utils.validate_key(
                    key_pem=key_pem, key_pem_filepath=key_pem_filepath
                )
                if self._fallback_global or self._fallback_cryptography:
                    self.assertIn(
                        "DEBUG:cert_utils:.validate_key > openssl fallback",
                        logged.output,
                    )
                else:
                    self.assertNotIn(
                        "DEBUG:cert_utils:.validate_key > openssl fallback",
                        logged.output,
                    )

        for key_filename in sorted(KEY_SETS.keys()):
            key_pem_filepath = self._filepath_testfile(key_filename)
            key_pem = self._filedata_testfile(key_filename)
            with self.assertLogs("cert_utils", level="DEBUG") as logged:
                key_technology = cert_utils.validate_key(
                    key_pem=key_pem, key_pem_filepath=key_pem_filepath
                )
                self.assertEqual(
                    key_technology, KEY_SETS[key_filename]["key_technology"]
                )
                if self._fallback_global or self._fallback_cryptography:
                    self.assertIn(
                        "DEBUG:cert_utils:.validate_key > openssl fallback",
                        logged.output,
                    )
                else:
                    self.assertNotIn(
                        "DEBUG:cert_utils:.validate_key > openssl fallback",
                        logged.output,
                    )

    def test__validate_cert(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test__validate_cert
        """

        for cert_set in sorted(self._cert_sets.keys()):
            if not self._cert_sets[cert_set]["cert"]:
                continue
            cert_filename = "unit_tests/cert_%s/cert.pem" % cert_set
            cert_pem_filepath = self._filepath_testfile(cert_filename)
            cert_pem = self._filedata_testfile(cert_filename)
            with self.assertLogs("cert_utils", level="DEBUG") as logged:
                cert_utils.validate_cert(
                    cert_pem=cert_pem, cert_pem_filepath=cert_pem_filepath
                )
                if self._fallback_global or self._fallback_cryptography:
                    self.assertIn(
                        "DEBUG:cert_utils:.validate_cert > openssl fallback",
                        logged.output,
                    )
                else:
                    self.assertNotIn(
                        "DEBUG:cert_utils:.validate_cert > openssl fallback",
                        logged.output,
                    )

    def test__make_csr(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test__make_csr
        """

        for cert_set in sorted(self._cert_sets.keys()):
            key_filename = "unit_tests/cert_%s/privkey.pem" % cert_set
            key_pem_filepath = self._filepath_testfile(key_filename)
            key_pem = self._filedata_testfile(key_filename)
            with self.assertLogs("cert_utils", level="DEBUG") as logged:
                csr_pem = cert_utils.make_csr(
                    domain_names=self._cert_sets[cert_set]["csr.domains.all"],
                    key_pem=key_pem,
                    key_pem_filepath=key_pem_filepath,
                )
                if self._fallback_global or self._fallback_cryptography:
                    self.assertIn(
                        "DEBUG:cert_utils:.make_csr > openssl fallback",
                        logged.output,
                    )
                else:
                    self.assertNotIn(
                        "DEBUG:cert_utils:.make_csr > openssl fallback",
                        logged.output,
                    )

    def test__modulus_md5_key(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test__modulus_md5_key
        """
        for cert_set in sorted(self._cert_sets.keys()):
            key_filename = "unit_tests/cert_%s/privkey.pem" % cert_set
            key_pem_filepath = self._filepath_testfile(key_filename)
            key_pem = self._filedata_testfile(key_filename)
            with self.assertLogs("cert_utils", level="DEBUG") as logged:
                modulus_md5 = cert_utils.modulus_md5_key(
                    key_pem=key_pem, key_pem_filepath=key_pem_filepath
                )
                self.assertEqual(
                    modulus_md5, self._cert_sets[cert_set]["pubkey_modulus_md5"]
                )
                if self._fallback_global or self._fallback_cryptography:
                    self.assertIn(
                        "DEBUG:cert_utils:.modulus_md5_key > openssl fallback",
                        logged.output,
                    )
                else:
                    self.assertNotIn(
                        "DEBUG:cert_utils:.modulus_md5_key > openssl fallback",
                        logged.output,
                    )

        for key_filename in sorted(KEY_SETS.keys()):
            key_pem_filepath = self._filepath_testfile(key_filename)
            key_pem = self._filedata_testfile(key_filename)
            modulus_md5 = cert_utils.modulus_md5_key(
                key_pem=key_pem, key_pem_filepath=key_pem_filepath
            )
            self.assertEqual(modulus_md5, KEY_SETS[key_filename]["modulus_md5"])
            # no need to test for fallback behavior again

    def test__modulus_md5_csr(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test__modulus_md5_csr
        """
        for cert_set in sorted(self._cert_sets.keys()):
            csr_filename = "unit_tests/cert_%s/csr.pem" % cert_set
            csr_pem_filepath = self._filepath_testfile(csr_filename)
            csr_pem = self._filedata_testfile(csr_filename)
            with self.assertLogs("cert_utils", level="DEBUG") as logged:
                modulus_md5 = cert_utils.modulus_md5_csr(
                    csr_pem=csr_pem, csr_pem_filepath=csr_pem_filepath
                )
                self.assertEqual(
                    modulus_md5, self._cert_sets[cert_set]["pubkey_modulus_md5"]
                )
                if self._fallback_global or self._fallback_cryptography:
                    self.assertIn(
                        "DEBUG:cert_utils:.modulus_md5_csr > openssl fallback",
                        logged.output,
                    )
                else:
                    self.assertNotIn(
                        "DEBUG:cert_utils:.modulus_md5_csr > openssl fallback",
                        logged.output,
                    )

        # csr sets
        for csr_filename in sorted(CSR_SETS.keys()):
            csr_pem_filepath = self._filepath_testfile(csr_filename)
            csr_pem = self._filedata_testfile(csr_filename)
            modulus_md5 = cert_utils.modulus_md5_csr(
                csr_pem=csr_pem, csr_pem_filepath=csr_pem_filepath
            )
            if modulus_md5 is None:
                # TODO: Support EC Key Modulus Variant - https://github.com/aptise/cert_utils/issues/15
                if csr_filename.startswith("key_technology-ec"):
                    continue
            self.assertEqual(modulus_md5, CSR_SETS[csr_filename]["modulus_md5"])
            # no need to test for fallback behavior again

    def test__modulus_md5_cert(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test__modulus_md5_cert
        """

        for cert_set in sorted(self._cert_sets.keys()):
            if not self._cert_sets[cert_set]["cert"]:
                continue
            cert_filename = "unit_tests/cert_%s/cert.pem" % cert_set
            cert_pem_filepath = self._filepath_testfile(cert_filename)
            cert_pem = self._filedata_testfile(cert_filename)
            with self.assertLogs("cert_utils", level="DEBUG") as logged:
                modulus_md5 = cert_utils.modulus_md5_cert(
                    cert_pem=cert_pem, cert_pem_filepath=cert_pem_filepath
                )
                self.assertEqual(
                    modulus_md5, self._cert_sets[cert_set]["pubkey_modulus_md5"]
                )
                if self._fallback_global or self._fallback_cryptography:
                    self.assertIn(
                        "DEBUG:cert_utils:.modulus_md5_cert > openssl fallback",
                        logged.output,
                    )
                else:
                    self.assertNotIn(
                        "DEBUG:cert_utils:.modulus_md5_cert > openssl fallback",
                        logged.output,
                    )

        # ca certs
        for cert_filename in sorted(CERT_CA_SETS.keys()):
            cert_pem_filepath = self._filepath_testfile(cert_filename)
            cert_pem = self._filedata_testfile(cert_filename)
            modulus_md5 = cert_utils.modulus_md5_cert(
                cert_pem=cert_pem, cert_pem_filepath=cert_pem_filepath
            )
            self.assertEqual(modulus_md5, CERT_CA_SETS[cert_filename]["modulus_md5"])
            # no need to test for fallback behavior again

    def test__parse_cert__enddate(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test__parse_cert__enddate
        """

        for cert_set in sorted(self._cert_sets.keys()):
            if not self._cert_sets[cert_set]["cert"]:
                continue
            cert_filename = "unit_tests/cert_%s/cert.pem" % cert_set
            cert_pem_filepath = self._filepath_testfile(cert_filename)
            cert_pem = self._filedata_testfile(cert_filename)
            with self.assertLogs("cert_utils", level="DEBUG") as logged:
                cert_enddate = cert_utils.parse_cert__enddate(
                    cert_pem=cert_pem, cert_pem_filepath=cert_pem_filepath
                )
                self.assertEqual(
                    str(cert_enddate), self._cert_sets[cert_set]["cert.notAfter"]
                )
                if self._fallback_global or self._fallback_cryptography:
                    self.assertIn(
                        "DEBUG:cert_utils:.parse_cert__enddate > openssl fallback",
                        logged.output,
                    )
                else:
                    self.assertNotIn(
                        "DEBUG:cert_utils:.parse_cert__enddate > openssl fallback",
                        logged.output,
                    )

    def test__parse_cert__startdate(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test__parse_cert__startdate
        """

        for cert_set in sorted(self._cert_sets.keys()):
            if not self._cert_sets[cert_set]["cert"]:
                continue
            cert_filename = "unit_tests/cert_%s/cert.pem" % cert_set
            cert_pem_filepath = self._filepath_testfile(cert_filename)
            cert_pem = self._filedata_testfile(cert_filename)
            with self.assertLogs("cert_utils", level="DEBUG") as logged:
                cert_startdate = cert_utils.parse_cert__startdate(
                    cert_pem=cert_pem, cert_pem_filepath=cert_pem_filepath
                )
                self.assertEqual(
                    str(cert_startdate), self._cert_sets[cert_set]["cert.notBefore"]
                )
                if self._fallback_global or self._fallback_cryptography:
                    self.assertIn(
                        "DEBUG:cert_utils:.parse_cert__startdate > openssl fallback",
                        logged.output,
                    )
                else:
                    self.assertNotIn(
                        "DEBUG:cert_utils:.parse_cert__startdate > openssl fallback",
                        logged.output,
                    )

    def test__parse_cert(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test__parse_cert
        python -m unittest tests.test_unit.UnitTest_CertUtils_fallback.test__parse_cert

        This UnitTest tests the following functions:

            * cert_utils.parse_cert
            * cert_utils.parse_cert__spki_sha256
            * cert_utils.parse_cert__key_technology

        These are run on Signed and CA Certificates
            self._cert_sets
            CERT_CA_SETS
        """

        # normal certs
        for cert_set in sorted(self._cert_sets.keys()):
            if not self._cert_sets[cert_set]["cert"]:
                continue
            cert_filename = "unit_tests/cert_%s/cert.pem" % cert_set
            cert_pem_filepath = self._filepath_testfile(cert_filename)
            cert_pem = self._filedata_testfile(cert_filename)

            # `cert_utils.parse_cert`
            with self.assertLogs("cert_utils", level="DEBUG") as logged:
                rval = cert_utils.parse_cert(
                    cert_pem=cert_pem, cert_pem_filepath=cert_pem_filepath
                )
                if self._fallback_global or self._fallback_cryptography:
                    self.assertIn(
                        "DEBUG:cert_utils:.parse_cert > openssl fallback",
                        logged.output,
                    )
                else:
                    self.assertNotIn(
                        "DEBUG:cert_utils:.parse_cert > openssl fallback",
                        logged.output,
                    )
            self.assertEqual(
                rval["fingerprint_sha1"],
                self._cert_sets[cert_set]["cert.fingerprints"]["sha1"],
            )
            self.assertEqual(
                rval["spki_sha256"], self._cert_sets[cert_set]["spki_sha256"]
            )
            self.assertEqual(
                rval["issuer_uri"], self._cert_sets[cert_set]["cert.issuer_uri"]
            )
            self.assertEqual(
                rval["authority_key_identifier"],
                self._cert_sets[cert_set]["cert.authority_key_identifier"],
            )

            # `cert_utils.parse_cert__spki_sha256`
            with self.assertLogs("cert_utils", level="DEBUG") as logged:
                spki_sha256 = cert_utils.parse_cert__spki_sha256(
                    cert_pem=cert_pem, cert_pem_filepath=cert_pem_filepath
                )
                if self._fallback_global or self._fallback_cryptography:
                    self.assertIn(
                        "DEBUG:cert_utils:.parse_cert__spki_sha256 > openssl fallback",
                        logged.output,
                    )
                else:
                    self.assertNotIn(
                        "DEBUG:cert_utils:.parse_cert__spki_sha256 > openssl fallback",
                        logged.output,
                    )

            self.assertEqual(spki_sha256, self._cert_sets[cert_set]["spki_sha256"])
            spki_sha256_b64 = cert_utils.parse_cert__spki_sha256(
                cert_pem=cert_pem, cert_pem_filepath=cert_pem_filepath, as_b64=True
            )
            self.assertEqual(
                spki_sha256_b64, self._cert_sets[cert_set]["spki_sha256.b64"]
            )

            # `cert_utils.parse_cert__key_technology`
            key_technology = cert_utils.parse_cert__key_technology(
                cert_pem=cert_pem, cert_pem_filepath=cert_pem_filepath
            )
            self.assertEqual(
                key_technology, self._cert_sets[cert_set]["key_technology"]
            )

        # ca certs
        for cert_filename in sorted(CERT_CA_SETS.keys()):
            cert_pem_filepath = self._filepath_testfile(cert_filename)
            cert_pem = self._filedata_testfile(cert_filename)

            # `cert_utils.parse_cert`
            rval = cert_utils.parse_cert(
                cert_pem=cert_pem, cert_pem_filepath=cert_pem_filepath
            )
            for field in (
                "issuer",
                "subject",
                "issuer_uri",
                "authority_key_identifier",
                "key_technology",
            ):
                self.assertEqual(rval[field], CERT_CA_SETS[cert_filename][field])
            self.assertEqual(
                rval["fingerprint_sha1"],
                CERT_CA_SETS[cert_filename]["cert.fingerprints"]["sha1"],
            )

            # `cert_utils.parse_cert__spki_sha256`
            spki_sha256 = cert_utils.parse_cert__spki_sha256(
                cert_pem=cert_pem, cert_pem_filepath=cert_pem_filepath
            )
            self.assertEqual(spki_sha256, CERT_CA_SETS[cert_filename]["spki_sha256"])
            spki_sha256_b64 = cert_utils.parse_cert__spki_sha256(
                cert_pem=cert_pem, cert_pem_filepath=cert_pem_filepath, as_b64=True
            )
            self.assertEqual(
                spki_sha256_b64, CERT_CA_SETS[cert_filename]["spki_sha256.b64"]
            )

            # `cert_utils.parse_cert__key_technology`
            key_technology = cert_utils.parse_cert__key_technology(
                cert_pem=cert_pem, cert_pem_filepath=cert_pem_filepath
            )
            self.assertEqual(
                key_technology, CERT_CA_SETS[cert_filename]["key_technology"]
            )

    def test__parse_csr(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test__parse_csr
        python -m unittest tests.test_unit.UnitTest_CertUtils_fallback.test__parse_csr

        This UnitTest tests the following functions:

            * cert_utils.parse_csr
            * cert_utils.parse_csr__spki_sha256
            * cert_utils.parse_csr__key_technology

        These are run on Signed and CA Certificates
            self._cert_sets
            CERT_CA_SETS
        """

        # normal certs
        for cert_set in sorted(self._cert_sets.keys()):
            if not self._cert_sets[cert_set]["csr"]:
                raise ValueError("missing csr!")
            csr_filename = "unit_tests/cert_%s/csr.pem" % cert_set
            csr_pem_filepath = self._filepath_testfile(csr_filename)
            csr_pem = self._filedata_testfile(csr_filename)

            # `cert_utils.parse_csr`
            with self.assertLogs("cert_utils", level="DEBUG") as logged:
                rval = cert_utils.parse_csr(
                    csr_pem=csr_pem, csr_pem_filepath=csr_pem_filepath
                )
                self.assertEqual(
                    rval["key_technology"],
                    self._cert_sets[cert_set]["key_technology"],
                )
                self.assertEqual(
                    rval["spki_sha256"], self._cert_sets[cert_set]["spki_sha256"]
                )
                self.assertEqual(
                    rval["subject"],
                    self._cert_sets[cert_set]["csr.subject"],
                )
                self.assertEqual(
                    rval["SubjectAlternativeName"],
                    self._cert_sets[cert_set]["csr.domains.san"],
                )
                if self._fallback_global or self._fallback_cryptography:
                    self.assertIn(
                        "DEBUG:cert_utils:.parse_csr > openssl fallback",
                        logged.output,
                    )
                else:
                    self.assertNotIn(
                        "DEBUG:cert_utils:.parse_csr > openssl fallback",
                        logged.output,
                    )

            # `cert_utils.parse_csr__spki_sha256`
            with self.assertLogs("cert_utils", level="DEBUG") as logged:
                spki_sha256 = cert_utils.parse_csr__spki_sha256(
                    csr_pem=csr_pem, csr_pem_filepath=csr_pem_filepath
                )
                self.assertEqual(spki_sha256, self._cert_sets[cert_set]["spki_sha256"])
                spki_sha256_b64 = cert_utils.parse_csr__spki_sha256(
                    csr_pem=csr_pem, csr_pem_filepath=csr_pem_filepath, as_b64=True
                )
                self.assertEqual(
                    spki_sha256_b64, self._cert_sets[cert_set]["spki_sha256.b64"]
                )
                if self._fallback_global or self._fallback_cryptography:
                    self.assertIn(
                        "DEBUG:cert_utils:.parse_csr__spki_sha256 > openssl fallback",
                        logged.output,
                    )
                else:
                    self.assertNotIn(
                        "DEBUG:cert_utils:.parse_csr__spki_sha256 > openssl fallback",
                        logged.output,
                    )

            # `cert_utils.parse_csr__key_technology
            with self.assertLogs("cert_utils", level="DEBUG") as logged:
                key_technology = cert_utils.parse_csr__key_technology(
                    csr_pem=csr_pem, csr_pem_filepath=csr_pem_filepath
                )
                self.assertEqual(
                    key_technology, self._cert_sets[cert_set]["key_technology"]
                )
                if self._fallback_global or self._fallback_cryptography:
                    self.assertIn(
                        "DEBUG:cert_utils:.parse_csr__key_technology > openssl fallback",
                        logged.output,
                    )
                else:
                    self.assertNotIn(
                        "DEBUG:cert_utils:.parse_csr__key_technology > openssl fallback",
                        logged.output,
                    )

        # extended csr
        for csr_set in sorted(self._csr_sets_alt.keys()):
            if not self._csr_sets_alt[csr_set]["csr"]:
                raise ValueError("missing csr!")
            csr_filename = "%s/%s" % (
                self._csr_sets_alt[csr_set]["directory"],
                self._csr_sets_alt[csr_set]["file.csr"],
            )
            csr_pem_filepath = self._filepath_testfile(csr_filename)
            csr_pem = self._filedata_testfile(csr_filename)

            # `cert_utils.parse_csr`
            rval = cert_utils.parse_csr(
                csr_pem=csr_pem, csr_pem_filepath=csr_pem_filepath
            )
            self.assertEqual(
                rval["key_technology"],
                self._csr_sets_alt[csr_set]["key_technology"],
            )
            self.assertEqual(
                rval["spki_sha256"], self._csr_sets_alt[csr_set]["spki_sha256"]
            )
            self.assertEqual(
                rval["subject"],
                self._csr_sets_alt[csr_set]["csr.subject"],
            )
            self.assertEqual(
                rval["SubjectAlternativeName"],
                self._csr_sets_alt[csr_set]["csr.domains.san"],
            )

            # `cert_utils.parse_csr__spki_sha256`
            spki_sha256 = cert_utils.parse_csr__spki_sha256(
                csr_pem=csr_pem, csr_pem_filepath=csr_pem_filepath
            )
            self.assertEqual(spki_sha256, self._csr_sets_alt[csr_set]["spki_sha256"])
            spki_sha256_b64 = cert_utils.parse_csr__spki_sha256(
                csr_pem=csr_pem, csr_pem_filepath=csr_pem_filepath, as_b64=True
            )
            self.assertEqual(
                spki_sha256_b64, self._csr_sets_alt[csr_set]["spki_sha256.b64"]
            )

            # `cert_utils.parse_csr__key_technology`
            key_technology = cert_utils.parse_csr__key_technology(
                csr_pem=csr_pem, csr_pem_filepath=csr_pem_filepath
            )
            self.assertEqual(
                key_technology, self._csr_sets_alt[csr_set]["key_technology"]
            )

    def test__parse_key(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test__parse_key
        python -m unittest tests.test_unit.UnitTest_CertUtils_fallback.test__parse_key

        This is a debugging display function. The output is not guaranteed across installations.

        This UnitTest tests the following functions:

            * cert_utils.parse_key
            * cert_utils.parse_key__spki_sha256
            * cert_utils.parse_key__technology_basic
        """

        for cert_set in sorted(self._cert_sets.keys()):
            key_filename = "unit_tests/cert_%s/privkey.pem" % cert_set
            key_pem_filepath = self._filepath_testfile(key_filename)
            key_pem = self._filedata_testfile(key_filename)

            # `cert_utils.parse_key`
            with self.assertLogs("cert_utils", level="DEBUG") as logged:
                rval = cert_utils.parse_key(
                    key_pem=key_pem, key_pem_filepath=key_pem_filepath
                )
                self.assertEqual(
                    rval["key_technology"], self._cert_sets[cert_set]["key_technology"]
                )
                self.assertEqual(
                    rval["key_technology_basic"],
                    self._cert_sets[cert_set]["key_technology_basic"],
                )
                self.assertEqual(
                    rval["modulus_md5"], self._cert_sets[cert_set]["pubkey_modulus_md5"]
                )
                self.assertEqual(
                    rval["spki_sha256"], self._cert_sets[cert_set]["spki_sha256"]
                )
                if self._fallback_global or self._fallback_cryptography:
                    self.assertIn(
                        "DEBUG:cert_utils:.parse_key > openssl fallback",
                        logged.output,
                    )
                else:
                    self.assertNotIn(
                        "DEBUG:cert_utils:.parse_key > openssl fallback",
                        logged.output,
                    )

            # `cert_utils.parse_key__spki_sha256`
            with self.assertLogs("cert_utils", level="DEBUG") as logged:
                spki_sha256 = cert_utils.parse_key__spki_sha256(
                    key_pem=key_pem, key_pem_filepath=key_pem_filepath
                )
                self.assertEqual(spki_sha256, self._cert_sets[cert_set]["spki_sha256"])
                spki_sha256_b64 = cert_utils.parse_key__spki_sha256(
                    key_pem=key_pem, key_pem_filepath=key_pem_filepath, as_b64=True
                )
                self.assertEqual(
                    spki_sha256_b64, self._cert_sets[cert_set]["spki_sha256.b64"]
                )
                if self._fallback_global or self._fallback_cryptography:
                    self.assertIn(
                        "DEBUG:cert_utils:.parse_key__spki_sha256 > openssl fallback",
                        logged.output,
                    )
                else:
                    self.assertNotIn(
                        "DEBUG:cert_utils:.parse_key__spki_sha256 > openssl fallback",
                        logged.output,
                    )

            # `cert_utils.parse_key__technology_basic`
            with self.assertLogs("cert_utils", level="DEBUG") as logged:
                key_technology_basic = cert_utils.parse_key__technology_basic(
                    key_pem=key_pem, key_pem_filepath=key_pem_filepath
                )
                self.assertEqual(
                    key_technology_basic,
                    self._cert_sets[cert_set]["key_technology_basic"],
                )
                if self._fallback_global or self._fallback_cryptography:
                    self.assertIn(
                        "DEBUG:cert_utils:.parse_key__technology_basic > openssl fallback",
                        logged.output,
                    )
                else:
                    self.assertNotIn(
                        "DEBUG:cert_utils:.parse_key__technology_basic > openssl fallback",
                        logged.output,
                    )

        # this will test against EC+RSA
        for key_filename in sorted(KEY_SETS.keys()):
            key_pem_filepath = self._filepath_testfile(key_filename)
            key_pem = self._filedata_testfile(key_filename)

            # `cert_utils.parse_key`
            rval = cert_utils.parse_key(
                key_pem=key_pem, key_pem_filepath=key_pem_filepath
            )
            self.assertEqual(
                rval["key_technology"], KEY_SETS[key_filename]["key_technology"]
            )
            self.assertEqual(rval["modulus_md5"], KEY_SETS[key_filename]["modulus_md5"])
            self.assertEqual(rval["spki_sha256"], KEY_SETS[key_filename]["spki_sha256"])

            # `cert_utils.parse_key__spki_sha256`
            spki_sha256 = cert_utils.parse_key__spki_sha256(
                key_pem=key_pem, key_pem_filepath=key_pem_filepath
            )
            self.assertEqual(spki_sha256, KEY_SETS[key_filename]["spki_sha256"])
            spki_sha256_b64 = cert_utils.parse_key__spki_sha256(
                key_pem=key_pem, key_pem_filepath=key_pem_filepath, as_b64=True
            )
            self.assertEqual(spki_sha256_b64, KEY_SETS[key_filename]["spki_sha256.b64"])

            # `cert_utils.parse_key__technology_basic`
            key_technology_basic = cert_utils.parse_key__technology_basic(
                key_pem=key_pem, key_pem_filepath=key_pem_filepath
            )
            self.assertEqual(
                key_technology_basic, KEY_SETS[key_filename]["key_technology_basic"]
            )

    def test__cert_and_chain_from_fullchain(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test__cert_and_chain_from_fullchain
        """
        for cert_set in sorted(self._cert_sets.keys()):
            if not self._cert_sets[cert_set]["cert"]:
                continue
            fullchain_filename = "unit_tests/cert_%s/fullchain.pem" % cert_set
            fullchain_pem_filepath = self._filepath_testfile(fullchain_filename)
            fullchain_pem = self._filedata_testfile(fullchain_filename)

            cert_filename = "unit_tests/cert_%s/cert.pem" % cert_set
            cert_pem_filepath = self._filepath_testfile(cert_filename)
            cert_pem = self._filedata_testfile(cert_filename)

            with self.assertLogs("cert_utils", level="DEBUG") as logged:
                (_cert, _chain) = cert_utils.cert_and_chain_from_fullchain(
                    fullchain_pem
                )
                self.assertEqual(_cert, cert_pem)
                if self._fallback_global or self._fallback_cryptography:
                    self.assertIn(
                        "DEBUG:cert_utils:.cert_and_chain_from_fullchain > openssl fallback",
                        logged.output,
                    )
                else:
                    self.assertNotIn(
                        "DEBUG:cert_utils:.cert_and_chain_from_fullchain > openssl fallback",
                        logged.output,
                    )

    def test__analyze_chains(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test__analyze_chains
        This tests:
        * cert_utils.cert_and_chain_from_fullchain
        * cert_utils.decompose_chain
        * cert_utils.ensure_chain
        * cert_utils.ensure_chain_order
        """
        # test long chains
        long_chain_tests = [
            "TestA",
        ]
        for _test_id in long_chain_tests:
            _test_dir = "long_chains/%s" % _test_id
            _test_data_filename = "%s/_data.json" % _test_dir
            _test_data_filepath = self._filepath_testfile(_test_data_filename)
            _test_data_string = self._filedata_testfile(_test_data_filepath)
            _test_data = json.loads(_test_data_string)
            count_roots = _test_data["roots"]
            count_intermediates = _test_data["intermediates"]

            cert_filename = "%s/cert.pem" % _test_dir
            cert_pem = self._filedata_testfile(cert_filename)

            test_pems = {}
            for i in range(0, count_roots):
                root_filename = "%s/root_%s.pem" % (_test_dir, i)
                root_pem_filepath = self._filepath_testfile(root_filename)
                root_pem = self._filedata_testfile(root_pem_filepath)

                chain_filename = "%s/chain_%s.pem" % (_test_dir, i)
                chain_pem_filepath = self._filepath_testfile(chain_filename)
                chain_pem = self._filedata_testfile(chain_pem_filepath)

                test_pems[i] = {"root": root_pem, "chain": chain_pem}

            for idx in test_pems:
                # create a fullchain
                # cert_pem ends in a "\n"
                fullchain_pem = cert_pem + test_pems[idx]["chain"]

                # decompose a fullchain
                (_cert, _chain) = cert_utils.cert_and_chain_from_fullchain(
                    fullchain_pem
                )
                self.assertEqual(_cert, cert_pem)
                self.assertEqual(_chain, test_pems[idx]["chain"])

                with self.assertLogs("cert_utils", level="DEBUG") as logged:
                    _upstream_certs = cert_utils.decompose_chain(_chain)
                    self.assertEqual(len(_upstream_certs), count_intermediates)

                    _all_certs = cert_utils.decompose_chain(fullchain_pem)
                    self.assertEqual(len(_all_certs), count_intermediates + 1)
                    if self._fallback_global or self._fallback_cryptography:
                        self.assertIn(
                            "DEBUG:cert_utils:.decompose_chain > openssl fallback",
                            logged.output,
                        )
                    else:
                        self.assertNotIn(
                            "DEBUG:cert_utils:.decompose_chain > openssl fallback",
                            logged.output,
                        )

                # `ensure_chain` can accept two types of data
                root_pem = test_pems[idx]["root"]
                with self.assertLogs("cert_utils", level="DEBUG") as logged:
                    self.assertTrue(
                        cert_utils.ensure_chain(
                            root_pem=root_pem, chain_pem=_chain, cert_pem=cert_pem
                        )
                    )
                    self.assertTrue(
                        cert_utils.ensure_chain(
                            root_pem=root_pem, fullchain_pem=fullchain_pem
                        )
                    )
                    if self._fallback_global or self._fallback_cryptography:
                        self.assertIn(
                            "DEBUG:cert_utils:.ensure_chain > openssl fallback",
                            logged.output,
                        )
                    else:
                        self.assertNotIn(
                            "DEBUG:cert_utils:.ensure_chain > openssl fallback",
                            logged.output,
                        )

                # `ensure_chain` will not accept user error
                # fullchain error
                _error_expected = "If `ensure_chain` is invoked with `fullchain_pem`, do not pass in `chain_pem` or `cert_pem`."
                # invoking `fullchain_pem` with: `chain_pem`
                with self.assertRaises(ValueError) as cm:
                    result = cert_utils.ensure_chain(
                        root_pem=root_pem, fullchain_pem=fullchain_pem, chain_pem=_chain
                    )
                self.assertEqual(cm.exception.args[0], _error_expected)
                # invoking `fullchain_pem` with: `cert_pem`
                with self.assertRaises(ValueError) as cm:
                    result = cert_utils.ensure_chain(
                        root_pem=root_pem,
                        fullchain_pem=fullchain_pem,
                        cert_pem=cert_pem,
                    )
                self.assertEqual(cm.exception.args[0], _error_expected)
                # invoking `fullchain_pem` with: `cert_pem` and `chain_pem`
                with self.assertRaises(ValueError) as cm:
                    result = cert_utils.ensure_chain(
                        root_pem=root_pem,
                        fullchain_pem=fullchain_pem,
                        chain_pem=_chain,
                        cert_pem=cert_pem,
                    )
                self.assertEqual(cm.exception.args[0], _error_expected)
                # NO fullchain error
                _error_expected = "If `ensure_chain` is not invoked with `fullchain_pem`, you must pass in `chain_pem` and `cert_pem`."
                # invoking NO `fullchain_pem` with: `chain_pem`
                with self.assertRaises(ValueError) as cm:
                    result = cert_utils.ensure_chain(
                        root_pem=root_pem, chain_pem=_chain
                    )
                self.assertEqual(cm.exception.args[0], _error_expected)
                # invoking NO `fullchain_pem` with: `cert_pem`
                with self.assertRaises(ValueError) as cm:
                    result = cert_utils.ensure_chain(
                        root_pem=root_pem, cert_pem=cert_pem
                    )

                # ENSURE THE CHAIN ORDER
                # forward: YAY!
                _all_certs = cert_utils.decompose_chain(fullchain_pem)
                with self.assertLogs("cert_utils", level="DEBUG") as logged:
                    cert_utils.ensure_chain_order(_all_certs)
                    if self._fallback_global or self._fallback_cryptography:
                        self.assertIn(
                            "DEBUG:cert_utils:.ensure_chain_order > openssl fallback",
                            logged.output,
                        )
                    else:
                        self.assertNotIn(
                            "DEBUG:cert_utils:.ensure_chain_order > openssl fallback",
                            logged.output,
                        )
                # reverse: nay :(
                _all_certs_reversed = _all_certs[::-1]
                with self.assertRaises(OpenSslError) as cm2:
                    cert_utils.ensure_chain_order(_all_certs_reversed)
                self.assertTrue(cm2.exception.args[0].startswith("could not verify:"))

    def test__convert_lejson_to_pem(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test__convert_lejson_to_pem
        """
        for account_set in sorted(self._account_sets.keys()):
            if not self._account_sets[account_set]["letsencrypt"]:
                continue
            if not self._account_sets[account_set]["pem"]:
                raise ValueError("need pem")

            # load the json
            key_jsons_filename = "unit_tests/account_%s/private_key.json" % account_set
            key_jsons_filepath = self._filepath_testfile(key_jsons_filename)
            key_jsons = self._filedata_testfile(key_jsons_filepath)

            # load the pem
            key_pem_filename = "unit_tests/account_%s/private_key.pem" % account_set
            key_pem_filepath = self._filepath_testfile(key_pem_filename)
            key_pem = self._filedata_testfile(key_pem_filepath)

            # convert
            with self.assertLogs("cert_utils", level="DEBUG") as logged:
                rval = cert_utils.convert_lejson_to_pem(key_jsons)
            print(logged.output)
            if (
                self._fallback_global
                or self._fallback_cryptography
                or self._fallback_josepy
            ):
                self.assertIn(
                    "DEBUG:cert_utils:.convert_lejson_to_pem > openssl fallback",
                    logged.output,
                )
            else:
                self.assertNotIn(
                    "DEBUG:cert_utils:.convert_lejson_to_pem > openssl fallback",
                    logged.output,
                )

            # compare
            self.assertEqual(rval, key_pem)

    def test__account_key__parse(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test__account_key__parse
        """
        for account_set in sorted(self._account_sets.keys()):
            if not self._account_sets[account_set]["pem"]:
                raise ValueError("need pem")

            # load the pem
            key_pem_filename = "unit_tests/account_%s/private_key.pem" % account_set
            key_pem_filepath = self._filepath_testfile(key_pem_filename)
            key_pem = self._filedata_testfile(key_pem_filepath)

            with self.assertLogs("cert_utils", level="DEBUG") as logged:
                rval = cert_utils.account_key__parse(
                    key_pem=key_pem, key_pem_filepath=key_pem_filepath
                )
                if self._fallback_global or self._fallback_josepy:
                    self.assertIn(
                        "DEBUG:cert_utils:.account_key__parse > openssl fallback",
                        logged.output,
                    )
                else:
                    self.assertNotIn(
                        "DEBUG:cert_utils:.account_key__parse > openssl fallback",
                        logged.output,
                    )

    def test__account_key__sign(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test__account_key__sign
        """
        for account_set in sorted(self._account_sets.keys()):
            if not self._account_sets[account_set]["pem"]:
                raise ValueError("need pem")

            # load the pem
            key_pem_filename = "unit_tests/account_%s/private_key.pem" % account_set
            key_pem_filepath = self._filepath_testfile(key_pem_filename)
            key_pem = self._filedata_testfile(key_pem_filepath)

            keytype = self._account_sets[account_set]["keytype"]
            input = self._account_sets[account_set]["signature.input"]
            expected = self._account_sets[account_set].get("signature.output")

            with self.assertLogs("cert_utils", level="DEBUG") as logged:
                _signature = cert_utils.account_key__sign(
                    input, key_pem=key_pem, key_pem_filepath=key_pem_filepath
                )
                signature = cert_utils.jose_b64(_signature)

                if keytype == "RSA":
                    self.assertEqual(signature, expected)
                elif keytype == "EC":
                    pass
                else:
                    raise ValueError("unknown keytype")

                if (
                    self._fallback_global
                    or self._fallback_cryptography
                    or self._fallback_josepy
                ):
                    self.assertIn(
                        "DEBUG:cert_utils:.account_key__sign > openssl fallback",
                        logged.output,
                    )
                else:
                    self.assertNotIn(
                        "DEBUG:cert_utils:.account_key__sign > openssl fallback",
                        logged.output,
                    )
                    # ALL must verify
                    # note we track the `_signature`
                    # We can't do this on openssl only yet, if ever
                    verified = cert_utils.account_key__verify(
                        _signature,
                        input,
                        key_pem=key_pem,
                        key_pem_filepath=key_pem_filepath,
                    )

    def test__new_account_key(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test__new_account_key
        """
        _combinations: TYPE_KEY_TESTING_COMBINATIONS = (
            (model.KeyTechnologyEnum.RSA, 2048, None),
            (model.KeyTechnologyEnum.RSA, 3072, None),
            (model.KeyTechnologyEnum.RSA, 4096, None),
            (model.KeyTechnologyEnum.EC, None, "P-256"),
            (model.KeyTechnologyEnum.EC, None, "P-384"),
        )
        for _combo in _combinations:
            key_pem = cert_utils.new_account_key(
                _combo[0],
                rsa_bits=_combo[1],  # type: ignore[arg-type]
                ec_curve=_combo[2],  # type: ignore[arg-type]
            )
            if _combo[0] == model.KeyTechnologyEnum.RSA:
                # crypto: -----BEGIN PRIVATE KEY-----
                # openssl fallback: -----BEGIN RSA PRIVATE KEY-----
                self.assertIn(
                    key_pem.split("\n")[0],
                    (
                        "-----BEGIN RSA PRIVATE KEY-----",
                        "-----BEGIN PRIVATE KEY-----",
                    ),
                )
            elif _combo[0] == model.KeyTechnologyEnum.EC:
                self.assertEqual(
                    "-----BEGIN EC PRIVATE KEY-----", key_pem.split("\n")[0]
                )

            key_parsed = cert_utils.account_key__parse(key_pem=key_pem)

    def test__private_key__new(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test__private_key__new
        """
        _combinations: TYPE_KEY_TESTING_COMBINATIONS = (
            (model.KeyTechnologyEnum.RSA, 2048, None),
            (model.KeyTechnologyEnum.RSA, 3072, None),
            (model.KeyTechnologyEnum.RSA, 4096, None),
            (model.KeyTechnologyEnum.EC, None, "P-256"),
            (model.KeyTechnologyEnum.EC, None, "P-384"),
        )
        for _combo in _combinations:
            key_pem = cert_utils.new_private_key(
                _combo[0],
                rsa_bits=_combo[1],  # type: ignore[arg-type]
                ec_curve=_combo[2],  # type: ignore[arg-type]
            )
            if _combo[0] == model.KeyTechnologyEnum.RSA:
                # crypto: -----BEGIN PRIVATE KEY-----
                # openssl fallback: -----BEGIN RSA PRIVATE KEY-----
                self.assertIn(
                    key_pem.split("\n")[0],
                    (
                        "-----BEGIN RSA PRIVATE KEY-----",
                        "-----BEGIN PRIVATE KEY-----",
                    ),
                )
            elif _combo[0] == model.KeyTechnologyEnum.EC:
                self.assertEqual(
                    "-----BEGIN EC PRIVATE KEY-----", key_pem.split("\n")[0]
                )

    def test_new_key_ec(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test_new_key_ec
        """
        # test no bits
        with self.assertLogs("cert_utils", level="DEBUG") as logged:
            key_pem = cert_utils.new_key_ec()
            self.assertIn("-----BEGIN EC PRIVATE KEY-----", key_pem)
            if self._fallback_global or self._fallback_cryptography:
                self.assertIn(
                    "DEBUG:cert_utils:.new_key_ec > openssl fallback",
                    logged.output,
                )
            else:
                self.assertNotIn(
                    "DEBUG:cert_utils:.new_key_ec > openssl fallback",
                    logged.output,
                )

        # test valid bits
        key_pem = cert_utils.new_key_ec(curve="P-256")
        self.assertIn("-----BEGIN EC PRIVATE KEY-----", key_pem)
        key_pem = cert_utils.new_key_ec(curve="P-384")
        self.assertIn("-----BEGIN EC PRIVATE KEY-----", key_pem)

        # test invalid bits
        with self.assertRaises(ValueError) as cm:
            key_pem = cert_utils.new_key_ec(curve="A")  # type: ignore[arg-type]
        self.assertIn(
            "LetsEncrypt only supports ECDSA keys with curves:", cm.exception.args[0]
        )

    def test_new_key_rsa(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test_new_key_rsa
        """
        # test no bits

        def _key_compliance(key_pem: str):
            # crypto: -----BEGIN PRIVATE KEY-----
            # openssl fallback: -----BEGIN RSA PRIVATE KEY-----
            self.assertIn(
                key_pem.split("\n")[0],
                (
                    "-----BEGIN RSA PRIVATE KEY-----",
                    "-----BEGIN PRIVATE KEY-----",
                ),
            )

        with self.assertLogs("cert_utils", level="DEBUG") as logged:
            key_pem = cert_utils.new_key_rsa()
            _key_compliance(key_pem)
            if self._fallback_global or self._fallback_cryptography:
                self.assertIn(
                    "DEBUG:cert_utils:.new_key_rsa > openssl fallback",
                    logged.output,
                )
            else:
                self.assertNotIn(
                    "DEBUG:cert_utils:.new_key_rsa > openssl fallback",
                    logged.output,
                )

        # test valid bits
        key_pem = cert_utils.new_key_rsa(bits=2048)
        _key_compliance(key_pem)

        key_pem = cert_utils.new_key_rsa(bits=3072)
        _key_compliance(key_pem)

        key_pem = cert_utils.new_key_rsa(bits=4096)
        _key_compliance(key_pem)

        # test invalid bits
        with self.assertRaises(ValueError) as cm:
            key_pem = cert_utils.new_key_rsa(bits=1)  # type: ignore[arg-type]
        self.assertIn(
            "LetsEncrypt only supports RSA keys with bits:", cm.exception.args[0]
        )

    def test_convert_pkcs7_to_pems(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test_convert_pkcs7_to_pems
        python -m unittest tests.test_unit.UnitTest_CertUtils_fallback.test_convert_pkcs7_to_pems
        """
        fname_pkcs7 = "letsencrypt-certs/deprecated/trustid-x3-root.p7c"
        fpath_pkcs7 = self._filepath_testfile(fname_pkcs7)
        fdata_pkcs7 = self._filedata_testfile_binary(fname_pkcs7)
        with self.assertLogs("cert_utils", level="DEBUG") as logged:
            pkcs7_pems = cert_utils.convert_pkcs7_to_pems(fdata_pkcs7)
            if self._fallback_global or self._fallback_cryptography:
                self.assertIn(
                    "DEBUG:cert_utils:.convert_pkcs7_to_pems > openssl fallback",
                    logged.output,
                )
            else:
                self.assertNotIn(
                    "DEBUG:cert_utils:.convert_pkcs7_to_pems > openssl fallback",
                    logged.output,
                )

        fname_pem = "letsencrypt-certs/deprecated/trustid-x3-root.pem"
        fpath_pem = self._filedata_testfile(fname_pem)
        fdata_pem = self._filedata_testfile(fname_pem)
        pem_pem = cert_utils.cleanup_pem_text(fdata_pem)
        self.assertEqual(len(pkcs7_pems), 1)
        self.assertEqual(pkcs7_pems[0], pem_pem)

    def test_convert_pkix_to_pem(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test_convert_pkix_to_pem
        python -m unittest tests.test_unit.UnitTest_CertUtils_fallback.test_convert_pkix_to_pem
        """
        fname_pkix = "letsencrypt-certs/isrgrootx1.pkix"
        fpath_pkix = self._filepath_testfile(fname_pkix)
        fdata_pkix = self._filedata_testfile_binary(fname_pkix)
        pkix_pem = cert_utils.convert_der_to_pem(fdata_pkix)

        fname_pem = "letsencrypt-certs/isrgrootx1.pem"
        fpath_pem = self._filedata_testfile(fname_pem)
        fdata_pem = self._filedata_testfile(fname_pem)
        pem_pem = cert_utils.cleanup_pem_text(fdata_pem)

        self.assertEqual(pkix_pem, pem_pem)

    def test_ari_construct_identifier(self):
        """
        python -m unittest tests.test_unit.UnitTest_CertUtils.test_ari_construct_identifier
        python -m unittest tests.test_unit.UnitTest_CertUtils_fallback.test_ari_construct_identifier
        """

        fname_pem = "draft-acme-ari/appendix_a-cert.pem"
        expected_identifier = "aYhba4dGQEHhs3uEe6CuLN4ByNQ.AIdlQyE"
        fpath_pem = self._filedata_testfile(fname_pem)
        fdata_pem = self._filedata_testfile(fname_pem)
        ari_identifier = cert_utils.ari_construct_identifier(fdata_pem)
        self.assertEqual(ari_identifier, expected_identifier)

        # custom edge cases

        fname_pem = "draft-acme-ari/cert--key_id.pem"
        expected_identifier = "aYhba4dGQEHhs3uEe6CuLN4ByNQ.AIdlQyE"
        fpath_pem = self._filedata_testfile(fname_pem)
        fdata_pem = self._filedata_testfile(fname_pem)
        ari_identifier = cert_utils.ari_construct_identifier(fdata_pem)
        self.assertEqual(ari_identifier, expected_identifier)

        fname_pem = "draft-acme-ari/cert--all.pem"
        expected_identifier = "aYhba4dGQEHhs3uEe6CuLN4ByNQ.AIdlQyE"
        fpath_pem = self._filedata_testfile(fname_pem)
        fdata_pem = self._filedata_testfile(fname_pem)
        ari_identifier = cert_utils.ari_construct_identifier(fdata_pem)
        self.assertEqual(ari_identifier, expected_identifier)

        fname_pem = "draft-acme-ari/cert--issuer+serial.pem"
        expected_identifier = "aYhba4dGQEHhs3uEe6CuLN4ByNQ.AIdlQyE"
        fpath_pem = self._filedata_testfile(fname_pem)
        fdata_pem = self._filedata_testfile(fname_pem)
        with self.assertRaises(ValueError) as cm:
            ari_identifier = cert_utils.ari_construct_identifier(fdata_pem)
        the_exception = cm.exception
        self.assertEqual(the_exception.args[0], "akid: not found")


class UnitTest_OpenSSL(unittest.TestCase, _Mixin_fallback_possible, _Mixin_filedata):
    """python -m unittest tests.test_unit.UnitTest_OpenSSL"""

    def test_modulus_PrivateKey(self):
        """
        modulus_md5_key is covered in the CertUtils tests. not sure why we have this
        """
        for pkey_set_id, set_data in sorted(TEST_FILES["PrivateKey"].items()):
            key_pem_filepath = self._filepath_testfile(set_data["file"])
            key_pem = self._filedata_testfile(key_pem_filepath)
            _computed_modulus_md5 = cert_utils.modulus_md5_key(
                key_pem=key_pem,
                key_pem_filepath=key_pem_filepath,
            )
            _expected_modulus_md5 = set_data["key_pem_modulus_md5"]
            assert _computed_modulus_md5 == _expected_modulus_md5
            _computed_md5 = cert_utils.utils.md5_text(
                self._filedata_testfile(key_pem_filepath)
            )
            _expected_md5 = set_data["key_pem_md5"]
            assert _computed_md5 == _expected_md5

        # this will test against EC+RSA
        for key_filename in sorted(KEY_SETS.keys()):
            key_pem_filepath = self._filepath_testfile(key_filename)
            key_pem = self._filedata_testfile(key_filename)
            _computed_modulus_md5 = cert_utils.modulus_md5_key(
                key_pem=key_pem, key_pem_filepath=key_pem_filepath
            )
            _expected_modulus_md5 = KEY_SETS[key_filename]["modulus_md5"]
            assert _computed_modulus_md5 == _expected_modulus_md5


class UnitTest_CertUtils_fallback(_MixinNoCrypto_Global, UnitTest_CertUtils):
    """python -m unittest tests.test_unit.UnitTest_CertUtils_fallback"""

    pass


@unittest.skipUnless(EXTENDED_TESTS, "Extended tests disabled")
class UnitTest_CertUtils_fallback_missing_cryptography(
    _Mixin_Missing_cryptography, UnitTest_CertUtils
):
    """python -m unittest tests.test_unit.UnitTest_CertUtils_fallback_missing_cryptography"""

    pass


@unittest.skipUnless(EXTENDED_TESTS, "Extended tests disabled")
class UnitTest_CertUtils_fallback_missing_josepy(
    _Mixin_Missing_josepy, UnitTest_CertUtils
):
    """python -m unittest tests.test_unit.UnitTest_CertUtils_fallback_missing_josepy"""

    pass


class UnitTest_OpenSSL_fallback(_MixinNoCrypto_Global, UnitTest_OpenSSL):
    """python -m unittest tests.test_unit.UnitTest_OpenSSL_fallback"""

    pass


class UnitTest_api(unittest.TestCase):
    """python -m unittest tests.test_unit.UnitTest_api"""

    def test_check_openssl_version(self):
        """
        python -m unittest tests.test_unit.UnitTest_api.test_check_openssl_version

        # this is not set until used, but we can't trust the execution order
        import cert_utils
        _original = cert_utils.core.openssl_version
        self.assertIsNone(_original)
        """
        # invoking `check` will return the new version
        active = cert_utils.check_openssl_version()
        # first invocation should set the value
        self.assertEqual(active, cert_utils.core.openssl_version)

        # let's try to replace it
        cert_utils.core.openssl_version = [0]
        self.assertEqual(
            [0],
            cert_utils.core.openssl_version,
        )
        new = cert_utils.check_openssl_version(replace=True)
        self.assertEqual(active, new)
        self.assertEqual(new, cert_utils.core.openssl_version)


class _UnitTest_utils__CORE(unittest.TestCase):
    """
    pytest tests/test_unit.py::UnitTest_utils_ips
    """

    """
        domains_from_string
        domains_from_list
        validate_domains
    """

    _DOMAINS__valid = (
        "EXAMPLE.com",
        "example.com",
        "a.example.com",
        "0.example.com",
        "example.us",
        "a.example.us",
        "0.example.us",
        "foo.example.com",
        "test-1.example.com",
        "*.example.com",
    )

    _HOSTNAMES__invalid = (
        "-EXAMPLE.com",
        "example.com-",
        "example.com.",
        ".example.com.",
        "test_1.example.com",
        "*.*.example.com",
        "*.example.*.com",
        "example.*.com",
    )
    _DOMAINS__invalid = _HOSTNAMES__invalid + (
        "127.0.0.1",
        "192.168.0.1",
        "255.255.255.255",
    )

    _ADDRS_IPV4 = (
        "192.168.0.1",
        "127.0.0.1",
        "255.255.255.255",
    )
    _ADDRS_IPV6 = (
        # search engine result
        "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
        "2001:db8:85a3::8a2e:370:7334",
        # boulder
        "2001:0db8:0bad:0dab:c0ff:fee0:0007:1337",
        "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
        "2001:0db8:85a3:0000:0000:8a2e:0370:7334:9000",
        "2606:4700:4700::1111",
        "2606:4700:4700::1111:53",
        "3fff::",
    )

    _ADDRS_IPV6_advanced = (
        {
            "valid": True,
            "address": "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            "compressed": "2001:db8:85a3::8a2e:370:7334",
            "exceptions": {
                "validate_ipv6_address|ipv6_require_compressed=True": """invalid domain: `2001:0db8:85a3:0000:0000:8a2e:0370:7334`; ipv6 must be compressed.""",
                "validate_domains|allow_ipv6=True|ipv6_require_compressed=True": """invalid domain: `2001:0db8:85a3:0000:0000:8a2e:0370:7334`; ipv6 must be compressed.""",
                "domains_from_list|allow_ipv6=True|ipv6_require_compressed=True": """invalid domain: `2001:0db8:85a3:0000:0000:8a2e:0370:7334`; ipv6 must be compressed.""",
                "domains_from_string|allow_ipv6=True|ipv6_require_compressed=True": """invalid domain: `2001:0db8:85a3:0000:0000:8a2e:0370:7334`; ipv6 must be compressed.""",
            },
        },
        {
            "valid": False,
            "address": "2001:0db8:85a3:0000:0000:8a2e:0370:xxx",
            "compressed": None,
            "exceptions": {
                "validate_ipv6_address": """invalid domain: `2001:0db8:85a3:0000:0000:8a2e:0370:xxx`; ipaddress.AddressValueError("Only hex digits permitted in \'xxx\' in \'2001:0db8:85a3:0000:0000:8a2e:0370:xxx\'").""",
                "validate_domains|allow_ipv6=True": """invalid domain: `2001:0db8:85a3:0000:0000:8a2e:0370:xxx`""",
                "domains_from_list|allow_ipv6=True": """invalid domain: `2001:0db8:85a3:0000:0000:8a2e:0370:xxx`""",
                "domains_from_string|allow_ipv6=True": """invalid domain: `2001:0db8:85a3:0000:0000:8a2e:0370:xxx`""",
            },
        },
    )

    def _mimic_standardize(self, domains: Iterable[str]) -> List[str]:
        return sorted(list(set([i.lower() for i in domains])))  # standardize and dedupe

    def _mimc_string(self, domains: Iterable[str]) -> str:
        # return ",".join(domains)
        # every other element will have whitespace
        return ",".join(d if idx % 2 else " %s" % d for idx, d in enumerate(domains))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


class UnitTest_utils(_UnitTest_utils__CORE, unittest.TestCase):

    def test__validate_domains__ipv4(self):
        for addr in self._ADDRS_IPV4:
            # validate domains expects a list
            utils.validate_domains([addr], allow_ipv4=True)

    def test__validate_domains__ipv6(self):
        for addr in self._ADDRS_IPV6:
            # validate domains expects a list
            utils.validate_domains([addr], allow_ipv6=True)

    def test__validate_domains__domains(self):
        for addr in self._DOMAINS__valid:
            # validate domains expects a list
            utils.validate_domains([addr])

    def test__validate_domains__all(self):
        addresses = self._DOMAINS__valid + self._ADDRS_IPV4 + self._ADDRS_IPV6
        for addr in addresses:
            # validate domains expects a list
            utils.validate_domains([addr], allow_ipv4=True, allow_ipv6=True)

    def test__validate_domains__fail__domain(self):
        for addr in self._DOMAINS__valid:
            # validate domains expects a list
            with self.assertRaises(ValueError) as cm:
                utils.validate_domains([addr], allow_hostname=False)

        for addr in self._DOMAINS__invalid:
            # validate domains expects a list
            with self.assertRaises(ValueError) as cm:
                utils.validate_domains([addr])

    def test__validate_domains__fail__ipv4(self):
        for addr in self._ADDRS_IPV4:
            # validate domains expects a list
            with self.assertRaises(ValueError) as cm:
                utils.validate_domains([addr])
            with self.assertRaises(ValueError) as cm:
                utils.validate_domains([addr], allow_ipv6=True)  # allow ipv6, not ipv4

    def test__validate_domains__fail__ipv6(self):
        for addr in self._ADDRS_IPV6:
            # validate domains expects a list
            with self.assertRaises(ValueError) as cm:
                utils.validate_domains([addr])
            with self.assertRaises(ValueError) as cm:
                utils.validate_domains([addr], allow_ipv4=True)  # allow ipv4, not ipv6

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def test__domains_from_list__ipv4(self):
        addresses = self._mimic_standardize(self._ADDRS_IPV4)
        self.assertEqual(
            addresses,
            utils.domains_from_list(self._ADDRS_IPV4, allow_ipv4=True),
        )

    def test__domains_from_list__ipv6(self):
        addresses = self._mimic_standardize(self._ADDRS_IPV6)
        self.assertEqual(
            addresses,
            utils.domains_from_list(self._ADDRS_IPV6, allow_ipv6=True),
        )

    def test__domains_from_list__domains(self):
        addresses = self._mimic_standardize(self._DOMAINS__valid)
        self.assertEqual(
            addresses,
            utils.domains_from_list(self._DOMAINS__valid),
        )

    def test__domains_from_list__all(self):
        addresses = list(self._DOMAINS__valid + self._ADDRS_IPV4 + self._ADDRS_IPV6)
        addresses = self._mimic_standardize(addresses)
        self.assertEqual(
            addresses,
            sorted(
                utils.domains_from_list(addresses, allow_ipv4=True, allow_ipv6=True)
            ),
        )

    def test__domains_from_list__fail__domain(self):
        with self.assertRaises(ValueError) as cm:
            utils.domains_from_list(self._DOMAINS__invalid)

        with self.assertRaises(ValueError) as cm:
            utils.domains_from_list(self._DOMAINS__valid, allow_hostname=False)

    def test__domains_from_list__fail__ipv4(self):
        with self.assertRaises(ValueError) as cm:
            utils.domains_from_list(self._ADDRS_IPV4)
        with self.assertRaises(ValueError) as cm:
            utils.domains_from_list(
                self._ADDRS_IPV4, allow_ipv6=True
            )  # allow ipv6, not ipv4

    def test__domains_from_list__fail__ipv6(self):
        with self.assertRaises(ValueError) as cm:
            utils.domains_from_list(self._ADDRS_IPV6)
        with self.assertRaises(ValueError) as cm:
            utils.domains_from_list(
                self._ADDRS_IPV6, allow_ipv4=True
            )  # allow ipv4, not ipv6

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def test__domains_from_string__ipv4(self):
        addresses = self._mimic_standardize(self._ADDRS_IPV4)
        addresses_string = self._mimc_string(addresses)
        self.assertEqual(
            addresses,
            utils.domains_from_string(addresses_string, allow_ipv4=True),
        )

    def test__domains_from_string__ipv6(self):
        addresses = self._mimic_standardize(self._ADDRS_IPV6)
        addresses_string = self._mimc_string(addresses)
        self.assertEqual(
            addresses,
            utils.domains_from_string(addresses_string, allow_ipv6=True),
        )

    def test__domains_from_string__domains(self):
        addresses = self._mimic_standardize(self._DOMAINS__valid)
        addresses_string = self._mimc_string(addresses)
        self.assertEqual(
            addresses,
            utils.domains_from_string(addresses_string),
        )

    def test__domains_from_string__all(self):
        addresses = list(self._DOMAINS__valid + self._ADDRS_IPV4 + self._ADDRS_IPV6)
        addresses = self._mimic_standardize(addresses)
        addresses_string = self._mimc_string(addresses)
        self.assertEqual(
            addresses,
            sorted(
                utils.domains_from_string(
                    addresses_string, allow_ipv4=True, allow_ipv6=True
                )
            ),
        )

    def test__domains_from_string__fail__domain(self):
        addresses_string = self._mimc_string(self._DOMAINS__invalid)
        with self.assertRaises(ValueError) as cm:
            utils.domains_from_string(addresses_string)

        addresses_string2 = self._mimc_string(self._DOMAINS__valid)
        with self.assertRaises(ValueError) as cm:
            utils.domains_from_string(addresses_string, allow_hostname=False)

    def test__domains_from_string__fail__ipv4(self):
        addresses_string = self._mimc_string(self._ADDRS_IPV4)
        with self.assertRaises(ValueError) as cm:
            utils.domains_from_string(addresses_string)
        with self.assertRaises(ValueError) as cm:
            utils.domains_from_string(
                addresses_string, allow_ipv6=True
            )  # allow ipv6, not ipv4

    def test__domains_from_string__fail__ipv6(self):
        addresses_string = self._mimc_string(self._ADDRS_IPV6)
        with self.assertRaises(ValueError) as cm:
            utils.domains_from_string(addresses_string)
        with self.assertRaises(ValueError) as cm:
            utils.domains_from_string(
                addresses_string, allow_ipv4=True
            )  # allow ipv4, not ipv6

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def test__identify_san_type__ipv4(self):
        for addr in self._ADDRS_IPV4:
            self.assertEqual("ipv4", utils.identify_san_type(addr))

    def test__identify_san_type__ipv6(self):
        for addr in self._ADDRS_IPV6:
            self.assertEqual("ipv6", utils.identify_san_type(addr))

    def test__identify_san_type__domains(self):
        for addr in self._DOMAINS__valid:
            self.assertEqual("hostname", utils.identify_san_type(addr))

    def test__identify_san_type__fail__domain(self):
        for addr in self._HOSTNAMES__invalid:
            with self.assertRaises(ValueError) as cm:
                utils.identify_san_type(addr)


class UnitTest_utils__ipv6_advanced(_UnitTest_utils__CORE, unittest.TestCase):

    def test__validate_ipv6_address(self):
        for test_data in self._ADDRS_IPV6_advanced:
            address = test_data["address"]
            compressed = test_data["compressed"]
            if TYPE_CHECKING:
                assert isinstance(address, str)
                assert isinstance(compressed, str)
            if test_data["valid"]:
                success = utils.validate_ipv6_address(address)
                if address != compressed:
                    # ensure compressed is valid
                    success2 = utils.validate_ipv6_address(compressed)
                    # ensure uncompressed fails
                    with self.assertRaises(ValueError) as cm:
                        failure = utils.validate_ipv6_address(
                            address,
                            ipv6_require_compressed=True,
                        )
            else:
                with self.assertRaises(ValueError) as cm:
                    failure = utils.validate_ipv6_address(address)
                if TYPE_CHECKING:
                    assert isinstance(cm.exception.args, list)
                self.assertEqual(
                    cm.exception.args[0],
                    test_data["exceptions"]["validate_ipv6_address"],
                )

    def test__validate_domains(self):
        for test_data in self._ADDRS_IPV6_advanced:
            address = test_data["address"]
            compressed = test_data["compressed"]
            if TYPE_CHECKING:
                assert isinstance(address, str)
                assert isinstance(compressed, str)
            if test_data["valid"]:
                success = utils.validate_domains([address], allow_ipv6=True)
                if address != compressed:
                    # ensure compressed is valid
                    success2 = utils.validate_domains(
                        [compressed],
                        allow_ipv6=True,
                        ipv6_require_compressed=True,
                    )
                    # ensure uncompressed fails
                    with self.assertRaises(ValueError) as cm:
                        failure = utils.validate_domains(
                            [address],
                            allow_ipv6=True,
                            ipv6_require_compressed=True,
                        )
                    if TYPE_CHECKING:
                        assert isinstance(cm.exception.args, list)
                    self.assertEqual(
                        cm.exception.args[0],
                        test_data["exceptions"][
                            "validate_domains|allow_ipv6=True|ipv6_require_compressed=True"
                        ],
                    )
            else:
                with self.assertRaises(ValueError) as cm:
                    failure = utils.validate_domains(
                        [address],
                        allow_ipv6=True,
                    )
                if TYPE_CHECKING:
                    assert isinstance(cm.exception.args, list)
                self.assertEqual(
                    cm.exception.args[0],
                    test_data["exceptions"]["validate_domains|allow_ipv6=True"],
                )

    def test__domains_from_list(self):
        for test_data in self._ADDRS_IPV6_advanced:
            address = test_data["address"]
            compressed = test_data["compressed"]
            if TYPE_CHECKING:
                assert isinstance(address, str)
                assert isinstance(compressed, str)
            if test_data["valid"]:
                success = utils.domains_from_list([address], allow_ipv6=True)
                self.assertEqual(1, len(success))
                self.assertIn(address, success)
                if address != compressed:
                    # ensure compressed is valid
                    success2 = utils.domains_from_list(
                        [compressed],
                        allow_ipv6=True,
                        ipv6_require_compressed=True,
                    )
                    # ensure uncompressed fails
                    with self.assertRaises(ValueError) as cm:
                        failure = utils.domains_from_list(
                            [address],
                            allow_ipv6=True,
                            ipv6_require_compressed=True,
                        )
                    if TYPE_CHECKING:
                        assert isinstance(cm.exception.args, list)
                    self.assertEqual(
                        cm.exception.args[0],
                        test_data["exceptions"][
                            "domains_from_list|allow_ipv6=True|ipv6_require_compressed=True"
                        ],
                    )
            else:
                with self.assertRaises(ValueError) as cm:
                    failure = utils.domains_from_list(
                        [address],
                        allow_ipv6=True,
                    )
                if TYPE_CHECKING:
                    assert isinstance(cm.exception.args, list)
                self.assertEqual(
                    cm.exception.args[0],
                    test_data["exceptions"]["domains_from_list|allow_ipv6=True"],
                )

    def test__domains_from_string(self):
        for test_data in self._ADDRS_IPV6_advanced:
            address = test_data["address"]
            compressed = test_data["compressed"]
            if TYPE_CHECKING:
                assert isinstance(address, str)
                assert isinstance(compressed, str)
            addresses_string = self._mimc_string([address])
            compressed_string = self._mimc_string([compressed])
            if test_data["valid"]:
                success = utils.domains_from_string(addresses_string, allow_ipv6=True)
                self.assertEqual(1, len(success))
                self.assertIn(address, success)
                if address != compressed:
                    # ensure compressed is valid
                    success2 = utils.domains_from_string(
                        compressed_string,
                        allow_ipv6=True,
                        ipv6_require_compressed=True,
                    )
                    # ensure uncompressed fails
                    with self.assertRaises(ValueError) as cm:
                        failure = utils.domains_from_string(
                            addresses_string,
                            allow_ipv6=True,
                            ipv6_require_compressed=True,
                        )
                    if TYPE_CHECKING:
                        assert isinstance(cm.exception.args, list)
                    self.assertEqual(
                        cm.exception.args[0],
                        test_data["exceptions"][
                            "domains_from_string|allow_ipv6=True|ipv6_require_compressed=True"
                        ],
                    )
            else:
                with self.assertRaises(ValueError) as cm:
                    failure = utils.domains_from_string(
                        addresses_string,
                        allow_ipv6=True,
                    )
                if TYPE_CHECKING:
                    assert isinstance(cm.exception.args, list)
                self.assertEqual(
                    cm.exception.args[0],
                    test_data["exceptions"]["domains_from_string|allow_ipv6=True"],
                )
