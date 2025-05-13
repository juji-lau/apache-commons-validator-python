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
from src.apache_commons_validator_python.routines.url_validator import UrlValidator
from src.apache_commons_validator_python.routines.regex_validator import RegexValidator
from src.apache_commons_validator_python.routines.domain_validator import DomainValidator

class TestUrlValidator:

    def test_fragments(self):
        schemes = ["http", "https"]
        validator = UrlValidator(schemes=schemes, options=UrlValidator.NO_FRAGMENTS)
        assert validator.is_valid("http://apache.org/a/b/c#frag") is False
        validator = UrlValidator(schemes=schemes)
        assert validator.is_valid("http://apache.org/a/b/c#frag") is True

    def test_is_valid(self):
        options = UrlValidator.ALLOW_ALL_SCHEMES
        url_val = UrlValidator(options=options)
        assert url_val.is_valid("http://www.google.com") is True
        assert url_val.is_valid("http://www.google.com/") is True

        options = UrlValidator.ALLOW_2_SLASHES + UrlValidator.ALLOW_ALL_SCHEMES + UrlValidator.NO_FRAGMENTS
        url_val = UrlValidator(options=options)
        assert url_val.is_valid("http://www.google.com") is True
        assert url_val.is_valid("http://www.google.com/") is True
    
    def test_is_valid_scheme(self):
        schemes = ["http", "gopher", "g0-To+.", "not_valid"]
        test_scheme = [("http", True), ("ftp", False), ("httpd", False), ("gopher", True), 
                       ("g0-to+.", True), ("not_valid", False), ("HtTp", True), ("telnet", False)]
        url_val = UrlValidator(schemes=schemes)

        for pair in test_scheme:
            result = url_val._is_valid_scheme(pair[0])
            assert result == pair[1]
    
    def test_validator202(self):
        schemes = ["http", "https"]
        validator = UrlValidator(schemes=schemes, options=UrlValidator.NO_FRAGMENTS)
        assert validator.is_valid("http://l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.l.org") is True

    def test_validator204(self):
        schemes = ["http", "https"]
        validator = UrlValidator(schemes=schemes)
        assert validator.is_valid("http://tech.yahoo.com/rc/desktops/102;_ylt=Ao8yevQHlZ4On0O3ZJGXLEQFLZA5") is True
    
    def test_validator218(self):
        validator = UrlValidator(options=UrlValidator.ALLOW_2_SLASHES)
        assert validator.is_valid("http://somewhere.com/pathxyz/file(1).html") is True

    def test_validator235(self):
        validator = UrlValidator()
        assert validator.is_valid("http://xn--d1abbgf6aiiy.xn--p1ai") is True
        assert validator.is_valid("http://президент.рф") is True
        assert validator.is_valid("http://www.b\u00fccher.ch") is True
        assert validator.is_valid("http://www.\uFFFD.ch") is False
        assert validator.is_valid("ftp://www.b\u00fccher.ch") is True
        assert validator.is_valid("ftp://www.\uFFFD.ch") is False
    
    def test_validator248(self):
        regex = RegexValidator(regexs=["localhost", ".*\\.my-testing"])
        validator = UrlValidator(authority_validator=regex)
        assert validator.is_valid("http://localhost/test/index.html") is True
        assert validator.is_valid("http://first.my-testing/test/index.html") is True
        assert validator.is_valid("http://sup3r.my-testing/test/index.html") is True
        assert validator.is_valid("http://broke.my-test/test/index.html") is False
        assert validator.is_valid("http://www.apache.org/test/index.html") is True

        # Now check using options
        validator = UrlValidator(options=UrlValidator.ALLOW_LOCAL_URLS)
        assert validator.is_valid("http://localhost/test/index.html") is True
        assert validator.is_valid("http://machinename/test/index.html") is True
        assert validator.is_valid("http://www.apache.org/test/index.html") is True
    
    def test_validator276(self):
        # file:// isn't allowed by default
        validator = UrlValidator()
        assert validator.is_valid("http://www.apache.org/test/index.html") is True
        assert validator.is_valid("file:///C:/some.file") is False
        assert validator.is_valid("file:///C:\\some.file") is False
        assert validator.is_valid("file:///etc/hosts") is False
        assert validator.is_valid("file://localhost/etc/hosts") is False
        assert validator.is_valid("file://localhost/c:/some.file") is False

        # Turn it on, and check
        # Note - we need to enable local urls when working with file:
        validator = UrlValidator(schemes=["http", "file"], options=UrlValidator.ALLOW_LOCAL_URLS)
        assert validator.is_valid("http://www.apache.org/test/index.html") is True
        assert validator.is_valid("file:///C:/some.file") is True

        # Only allow forward slashes
        assert validator.is_valid("file:///C:\\some.file") is False
        assert validator.is_valid("file:///etc/hosts") is True
        assert validator.is_valid("file://localhost/etc/hosts") is True
        assert validator.is_valid("file://localhost/c:/some.file") is True

        # These are never valid
        assert validator.is_valid("file://C:/some.file") is False
        assert validator.is_valid("file://C:\\some.file") is False
    
    def test_validator283(self):
        validator = UrlValidator()
        assert validator.is_valid("http://finance.yahoo.com/news/Owners-54B-NY-housing-apf-2493139299.html?x=0&ap=%fr") is False
        assert validator.is_valid("http://finance.yahoo.com/news/Owners-54B-NY-housing-apf-2493139299.html?x=0&ap=%22") is True

    def test_validator288(self):
        validator = UrlValidator(options=UrlValidator.ALLOW_LOCAL_URLS)
        assert validator.is_valid("http://hostname") is True
        assert validator.is_valid("http://hostname/test/index.html") is True
        assert validator.is_valid("http://localhost/test/index.html") is True
        assert validator.is_valid("http://first.my-testing/test/index.html") is False
        assert validator.is_valid("http://broke.hostname/test/index.html") is False
        assert validator.is_valid("http://www.apache.org/test/index.html") is True

        # Turn it off, and check
        validator = UrlValidator(options=0)
        assert validator.is_valid("http://hostname") is False
        assert validator.is_valid("http://localhost/test/index.html") is False
        assert validator.is_valid("http://www.apache.org/test/index.html") is True
    
    def test_validator290(self):
        validator = UrlValidator()
        assert validator.is_valid("http://xn--h1acbxfam.idn.icann.org/") is True
        # Internationalized country code top-level domains
        assert validator.is_valid("http://test.xn--lgbbat1ad8j") is True  # Algeria
        assert validator.is_valid("http://test.xn--fiqs8s") is True        # China
        assert validator.is_valid("http://test.xn--fiqz9s") is True        # China
        assert validator.is_valid("http://test.xn--wgbh1c") is True        # Egypt
        assert validator.is_valid("http://test.xn--j6w193g") is True       # Hong Kong
        assert validator.is_valid("http://test.xn--h2brj9c") is True       # India
        assert validator.is_valid("http://test.xn--mgbbh1a71e") is True    # India
        assert validator.is_valid("http://test.xn--fpcrj9c3d") is True     # India
        assert validator.is_valid("http://test.xn--gecrj9c") is True       # India
        assert validator.is_valid("http://test.xn--s9brj9c") is True       # India
        assert validator.is_valid("http://test.xn--xkc2dl3a5ee0h") is True # India
        assert validator.is_valid("http://test.xn--45brj9c") is True       # India
        assert validator.is_valid("http://test.xn--mgba3a4f16a") is True   # Iran
        assert validator.is_valid("http://test.xn--mgbayh7gpa") is True    # Jordan
        assert validator.is_valid("http://test.xn--mgbc0a9azcg") is True   # Morocco
        assert validator.is_valid("http://test.xn--ygbi2ammx") is True     # Palestinian Territory
        assert validator.is_valid("http://test.xn--wgbl6a") is True        # Qatar
        assert validator.is_valid("http://test.xn--p1ai") is True          # Russia
        assert validator.is_valid("http://test.xn--mgberp4a5d4ar") is True # Saudi Arabia
        assert validator.is_valid("http://test.xn--90a3ac") is True        # Serbia
        assert validator.is_valid("http://test.xn--yfro4i67o") is True     # Singapore
        assert validator.is_valid("http://test.xn--clchc0ea0b2g2a9gcd") is True  # Singapore
        assert validator.is_valid("http://test.xn--3e0b707e") is True      # South Korea
        assert validator.is_valid("http://test.xn--fzc2c9e2c") is True     # Sri Lanka
        assert validator.is_valid("http://test.xn--xkc2al3hye2a") is True  # Sri Lanka
        assert validator.is_valid("http://test.xn--ogbpf8fl") is True      # Syria
        assert validator.is_valid("http://test.xn--kprw13d") is True       # Taiwan
        assert validator.is_valid("http://test.xn--kpry57d") is True       # Taiwan
        assert validator.is_valid("http://test.xn--o3cw4h") is True        # Thailand
        assert validator.is_valid("http://test.xn--pgbs0dh") is True       # Tunisia
        assert validator.is_valid("http://test.xn--mgbaam7a8h") is True    # United Arab Emirates

    def test_validator309(self):
        validator = UrlValidator()
        assert validator.is_valid("http://sample.ondemand.com/") is True
        assert validator.is_valid("hTtP://sample.ondemand.CoM/") is True
        assert validator.is_valid("httpS://SAMPLE.ONEMAND.COM/") is True
        validator = UrlValidator(schemes=["HTTP", "HTTPS"])
        assert validator.is_valid("http://sample.ondemand.com/") is True
        assert validator.is_valid("hTtP://sample.ondemand.CoM/") is True
        assert validator.is_valid("httpS://SAMPLE.ONEMAND.COM/") is True
    
    def test_validator339(self):
        validator = UrlValidator()
        assert validator.is_valid("http://www.cnn.com/WORLD/?hpt=sitenav") is True
        assert validator.is_valid("http://www.cnn.com./WORLD/?hpt=sitenav") is True
        assert validator.is_valid("http://www.cnn.com../") is False
        assert validator.is_valid("http://www.cnn.invalid/") is False
        assert validator.is_valid("http://www.cnn.invalid./") is False
    
    def test_validator339_idn(self):
        validator = UrlValidator()
        assert validator.is_valid("http://президент.рф/WORLD/?hpt=sitenav") is True
        assert validator.is_valid("http://президент.рф./WORLD/?hpt=sitenav") is True
        assert validator.is_valid("http://президент.рф..../") is False
        assert validator.is_valid("http://президент.рф.../") is False
        assert validator.is_valid("http://президент.рф../") is False
    
    def test_validator342(self):
        validator = UrlValidator()
        assert validator.is_valid("http://example.rocks/") is True
        assert validator.is_valid("http://example.rocks") is True
    
    def test_validator353(self):
        validator = UrlValidator()
        assert validator.is_valid("http://www.apache.org:80/path") is True
        assert validator.is_valid("http://user:pass@www.apache.org:80/path") is True
        assert validator.is_valid("http://user:@www.apache.org:80/path") is True
        assert validator.is_valid("http://user@www.apache.org:80/path") is True
        assert validator.is_valid("http://us%00er:-._~!$&'()*+,;=@www.apache.org:80/path") is True
        assert validator.is_valid("http://:pass@www.apache.org:80/path") is False
        assert validator.is_valid("http://:@www.apache.org:80/path") is False
        assert validator.is_valid("http://user:pa:ss@www.apache.org/path") is False
        assert validator.is_valid("http://user:pa@ss@www.apache.org/path") is False
    
    def test_validator361(self):
        validator = UrlValidator()
        assert validator.is_valid("http://hello.tokyo/") is True
    
    def test_validator363(self):
        validator = UrlValidator()
        assert validator.is_valid("http://www.example.org/a/b/hello..world") is True
        assert validator.is_valid("http://www.example.org/a/hello..world") is True
        assert validator.is_valid("http://www.example.org/hello.world/") is True
        assert validator.is_valid("http://www.example.org/hello..world/") is True
        assert validator.is_valid("http://www.example.org/hello.world") is True
        assert validator.is_valid("http://www.example.org/hello..world") is True
        assert validator.is_valid("http://www.example.org/..world") is True
        assert validator.is_valid("http://www.example.org/.../world") is True
        assert validator.is_valid("http://www.example.org/../world") is False
        assert validator.is_valid("http://www.example.org/..") is False
        assert validator.is_valid("http://www.example.org/../") is False
        assert validator.is_valid("http://www.example.org/./..") is False
        assert validator.is_valid("http://www.example.org/././..") is False
        assert validator.is_valid("http://www.example.org/...") is True
        assert validator.is_valid("http://www.example.org/.../") is True
        assert validator.is_valid("http://www.example.org/.../..") is True
    
    def test_validator375(self):
        validator = UrlValidator()
        url = "http://[FEDC:BA98:7654:3210:FEDC:BA98:7654:3210]:80/index.html"
        assert validator.is_valid(url) is True
        url = "http://[::1]:80/index.html"
        assert validator.is_valid(url) is True
        url = "http://FEDC:BA98:7654:3210:FEDC:BA98:7654:3210:80/index.html"
        assert validator.is_valid(url) is False
    
    def test_validator380(self):
        validator = UrlValidator()
        assert validator.is_valid("http://www.apache.org:80/path") is True
        assert validator.is_valid("http://www.apache.org:8/path") is True
        assert validator.is_valid("http://www.apache.org:/path") is True
    
    def test_validator382(self):
        validator = UrlValidator()
        assert validator.is_valid("ftp://username:password@example.com:8042/over/there/index.dtb?type=animal&name=narwhal#nose") is True
    
    def test_validator391_fails(self):
        schemes = ["file"]
        validator = UrlValidator(schemes=schemes)
        assert validator.is_valid("file:/C:/path/to/dir/") is True
    
    def test_validator391_ok(self):
        schemes = ["file"]
        validator = UrlValidator(schemes=schemes)
        assert validator.is_valid("file:///C:/path/to/dir/") is True
    
    def test_validator411(self):
        validator = UrlValidator()
        assert validator.is_valid("http://example.rocks:/") is True
        assert validator.is_valid("http://example.rocks:0/") is True
        assert validator.is_valid("http://example.rocks:65535/") is True
        assert validator.is_valid("http://example.rocks:65536/") is False
        assert validator.is_valid("http://example.rocks:100000/") is False

    def test_validator420(self):
        validator = UrlValidator()
        assert validator.is_valid("http://example.com/serach?address=Main Avenue") is True
        assert validator.is_valid("http://example.com/serach?address=Main%20Avenue") is True
        assert validator.is_valid("http://example.com/serach?address=Main+Avenue") is True
    
    def test_validator452(self):
        validator = UrlValidator()
        assert validator.is_valid("http://[::FFFF:129.144.52.38]:80/index.html") is True
    
    def test_validator464(self):
        schemes = ["file"]
        validator = UrlValidator(schemes=schemes)
        fileNAK = "file://bad ^ domain.com/label/test"
        assert validator.is_valid(fileNAK) is False
    
    def test_validator467(self):
        validator = UrlValidator(options=UrlValidator.ALLOW_2_SLASHES)
        assert validator.is_valid("https://example.com/some_path/path/") is True
        assert validator.is_valid("https://example.com//somepath/path/") is True
        assert validator.is_valid("https://example.com//some_path/path/") is True
        assert validator.is_valid("http://example.com//_test") is True

    def test_validator473_part2(self):
        with pytest.raises(Exception):
            UrlValidator([], None, 0, domain_validator=DomainValidator.get_instance(True, []))
    
    def test_validator473_part3(self):
        with pytest.raises(Exception):
            UrlValidator([], None, UrlValidator.ALLOW_LOCAL_URLS, domain_validator=DomainValidator.get_instance(False, []))
