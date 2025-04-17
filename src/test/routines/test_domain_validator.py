"""
    Licensed to the Apache Software Foundation (ASF) under one or more
    contributor license agreements.  See the NOTICE file distributed with
    this work for additional information regarding copyright ownership.
    The ASF licenses this file to You under the Apache License, Version 2.0
    (the "License"); you may not use this file except in compliance with
    the License.  You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
import pytest
from src.main.routines.domain_validator import DomainValidator

class TestDomainValidator:

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        DomainValidator._DomainValidator__reset_singletons()
        # DomainValidator._reset_singletons()

    def test_allow_local(self):
        validator = DomainValidator.get_instance()
        no_local = DomainValidator.get_instance(allow_local=False)
        allow_local = DomainValidator.get_instance(allow_local=True)

        # default is false and should use singletons
        assert no_local == validator, f"Default validator should not allow local"

        # default won't allow local
        assert no_local.is_valid("localhost.localdomain") is False, f"no_local should return False when validating 'localhost.localdomain'"
        assert no_local.is_valid("localhost") is False, f"no_local should return False when validating 'localhost'"

        # but allow local should
        assert allow_local.is_valid("localhost.localdomain") is True, f"allow_local should return True when validating 'localhost.localdomain'"
        assert allow_local.is_valid("localhost") is True, f"allow_local should return True when validating 'localhost.localdomain'"
        assert allow_local.is_valid("hostname") is True, f"allow_local should return True when validating 'hostname'"
        assert allow_local.is_valid("machinename") is True, f"allow_local should return True when validating 'machinename'"

        # local host should allow correct non-local
        assert allow_local.is_valid("apache.org") is True, f"allow_local should return True when validating 'apache.org'"
        assert allow_local.is_valid(" apache.org ") is False, f"allow_local should return False when validating  ' apache.org '"
    
    def test_domain_no_dots(self): # rfc1123
        validator = DomainValidator.get_instance()
        assert validator._is_valid_domain_syntax("a") is True, f"a (alpha) should validate"
        assert validator._is_valid_domain_syntax("9") is True, f"9 (alphanum) should validate"
        assert validator._is_valid_domain_syntax("c-z") is True, f"c-z (alpha - alpha) should validate"

        assert validator._is_valid_domain_syntax("c-") is False, f"c- (alpha -) should fail"
        assert validator._is_valid_domain_syntax("-c") is False, f"-c (- alpha) should fail"
        assert validator._is_valid_domain_syntax("-") is False, f"- (-) should fail"
    
    def test_get_array(self):
        assert DomainValidator.get_tld_entries(DomainValidator.ArrayType.COUNTRY_CODE_MINUS) != None
        assert DomainValidator.get_tld_entries(DomainValidator.ArrayType.COUNTRY_CODE_PLUS) != None
        assert DomainValidator.get_tld_entries(DomainValidator.ArrayType.GENERIC_MINUS) != None
        assert DomainValidator.get_tld_entries(DomainValidator.ArrayType.GENERIC_PLUS) != None
        assert DomainValidator.get_tld_entries(DomainValidator.ArrayType.LOCAL_MINUS) != None
        assert DomainValidator.get_tld_entries(DomainValidator.ArrayType.LOCAL_PLUS) != None
        assert DomainValidator.get_tld_entries(DomainValidator.ArrayType.COUNTRY_CODE_RO) != None
        assert DomainValidator.get_tld_entries(DomainValidator.ArrayType.GENERIC_RO) != None
        assert DomainValidator.get_tld_entries(DomainValidator.ArrayType.INFRASTRUCTURE_RO) != None
        assert DomainValidator.get_tld_entries(DomainValidator.ArrayType.LOCAL_RO) != None
    
    def test_idn(self):
        validator = DomainValidator.get_instance()
        assert validator.is_valid("www.xn--bcher-kva.ch") is True, f"b\u00fccher.ch in IDN should validate"

    def test_idn_java_60_or_later(self):
        # xn--d1abbgf6aiiy.xn--p1ai http://президент.рф
        validator = DomainValidator.get_instance()
        assert validator.is_valid("www.b\u00fccher.ch") is True, f"b\u00fccher.ch should validate"
        assert validator.is_valid("xn--d1abbgf6aiiy.xn--p1ai") is True, f"xn--d1abbgf6aiiy.xn--p1ai should validate"
        assert validator.is_valid("президент.рф") is True, f"президент.рф should validate"
        assert validator.is_valid("www.\uFFFD.ch") is False, f"www.\uFFFD.ch FFFD should fail"

    def test_invalid_domains(self):
        validator = DomainValidator.get_instance()
        assert validator.is_valid(".org") is False, f"Bare TLD .org shouldn't validate"
        assert validator.is_valid(" apache.org ") is False, f"Domain name with spaces shouldn't validate"
        assert validator.is_valid("apa che.org") is False, f"Domain name containing spaces shouldn't validate"
        assert validator.is_valid("-testdomain.name") is False, f"Domain name starting with dash shouldn't validate"
        assert validator.is_valid("testdomain-.name") is False, f"Domain name ending with dash shouldn't validate"
        assert validator.is_valid("---c.com") is False, f"Domain name starting with multiple dashes shouldn't validate"
        assert validator.is_valid("c--.com") is False, f"Domain name ending with multiple dashes shouldn't validate"
        assert validator.is_valid("apache.rog") is False, f"Domain name with invalid TLD shouldn't validate"
        assert validator.is_valid("http://www.apache.org") is False, f"URL shouldn't validate"
        assert validator.is_valid(" ") is False, f"Empty string shouldn't validate as domain name"
        assert validator.is_valid(None) is False, f"None shouldn't validate"

    def test_rfc2396_domain_label(self):
        validator = DomainValidator.get_instance()
        assert validator.is_valid("a.ch") is True, f"a.ch should validate"
        assert validator.is_valid("9.ch") is True, f"9.ch should validate"
        assert validator.is_valid("az.ch") is True, f"az.ch should validate"
        assert validator.is_valid("09.ch") is True, f"09.ch should validate"
        assert validator.is_valid("9-1.ch") is True, f"9-1.ch should validate"

        assert validator.is_valid("91-.ch") is False, f"91-.ch shouldn't validate"
        assert validator.is_valid("-.ch") is False, f"-.ch shouldn't validate"

    def test_rfc2396_top_label(self):
        validator = DomainValidator.get_instance()
        assert validator._is_valid_domain_syntax("a.c") is True, f"a.c (alpha) should validate"
        assert validator._is_valid_domain_syntax("a.cc") is True, f"a.cc (alpha alpha) should validate"
        assert validator._is_valid_domain_syntax("a.c9") is True, f"a.c9 (alpha alphanum) should validate"
        assert validator._is_valid_domain_syntax("a.c-9") is True, f"a.c-9 (alpha - alphanum) should validate"
        assert validator._is_valid_domain_syntax("a.c-z") is True, f"a.c-z (alpha - alpha) should validate"

        assert validator._is_valid_domain_syntax("a.9c") is False, f"a.9c (aphanum alpha) shouldn't validate"
        assert validator._is_valid_domain_syntax("a.c-") is False, f"a.c- (alpha -) shouldn't validate"
        assert validator._is_valid_domain_syntax("a.-") is False, f"a.- (-) shouldn't validate"
        assert validator._is_valid_domain_syntax("a.-9") is False, f"a.-9 (- alpha) shouldn't validate"
    
    def test_top_level_domains(self):
        validator = DomainValidator.get_instance()
        # infrastructure TLDs
        assert validator.is_valid_infrastructure_tld(".arpa") is True, f".arpa should validate as iTLD"
        assert validator.is_valid_infrastructure_tld(".com") is False, f".com shouldn't validate as iTLD"

        # generic TLDs
        assert validator.is_valid_generic_tld(".name") is True, f".name should validate as gTLD"
        assert validator.is_valid_generic_tld(".us") is False, f".us shouldn't validate as gTLD"

        # country code TLDs
        assert validator.is_valid_country_code_tld(".uk") is True, f"uk should validate as ccTLD"
        assert validator.is_valid_country_code_tld(".org") is False, f".org shouldn't validate as ccTLD"

        # case-insensitive
        assert validator.is_valid_tld(".COM") is True, f".COM should validate as TLD"
        assert validator.is_valid_tld(".BiZ") is True, f".BiZ should validate as TLD"

        # corner cases
        assert validator.is_valid(".nope") is False, f"Invalid TLD shouldn't validate" # this is not guarenteed to be invalid forever
        assert validator.is_valid("") is False, f"Empty string shouldn't validate as TLD"
        assert validator.is_valid(None) is False, f"None shouldn't validate as TLD"

    def test_unicode_to_ascii(self):
        ascii_dots = ["", ",", ".", "a.", "a.b", "a..b", "a...b", ".a", "..a"]
        for s in ascii_dots:
            assert s == DomainValidator.unicode_to_ascii(s)

        other_dots = [["a\u3002", "a."], ["b\uFF0E", "b."], ["c\uFF61", "c."], ["\u3002", "."], ["\uFF0E", "."], ["\uFF61", "."]]
        for s in other_dots:
            assert s[1] == DomainValidator.unicode_to_ascii(s[0])
    
    def test_validator297(self):
        validator = DomainValidator.get_instance()
        assert validator.is_valid("xn--d1abbgf6aiiy.xn--p1ai") is True, f"xn--d1abbgf6aiiy.xn--p1ai should validate"

    def test_validator306(self):
        validator = DomainValidator.get_instance()
        long_string = "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz0123456789A"
        assert len(long_string) == 63

        assert validator._is_valid_domain_syntax(long_string + ".com") is True, f"63 chars label should validate"
        assert validator._is_valid_domain_syntax(long_string + "x.com") is False, f"64 chars label should fail"

        assert validator._is_valid_domain_syntax("test." + long_string) is True, f"63 chars TLD should validate"
        assert validator._is_valid_domain_syntax("test.x" + long_string) is False, f"64 chars TLD should fail"

        long_domain = long_string + '.' + long_string + '.' + long_string + '.' + long_string[0:61]
        assert len(long_domain) == 253

        assert validator._is_valid_domain_syntax(long_domain) is True, f"253 chars domain should validate"
        assert validator._is_valid_domain_syntax(long_domain + 'x') is False, f"254 chars domain should fail"

    def test_valid_domains(self):
        validator = DomainValidator.get_instance()
        assert validator.is_valid("apache.org") is True, f"apache.org should validate"
        assert validator.is_valid("www.google.com") is True, f"www.google.com should validate"
        assert validator.is_valid("test-domain.com") is True, f"Test-domain.com should validate"
        assert validator.is_valid("test---domain.com") is True, f"test---domain.com should validate"
        assert validator.is_valid("test-d-o-m-ain.com") is True, f"test-d-o-m-ain.com should validate"
        assert validator.is_valid("as.uk") is True, f"Two-letter domain label should validate"
        assert validator.is_valid("ApAchE.Org") is True, f"Case-insensitive ApAchE.Org should validate"
        assert validator.is_valid("z.com") is True, f"Single-character domain label should validate"
        assert validator.is_valid("i.have.an-example.domain.name") is True, f"i.have.an-example.domain.name should validate"
