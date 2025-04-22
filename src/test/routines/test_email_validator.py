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
from src.main.routines.email_validator import EmailValidator
from src.main.routines.domain_validator import DomainValidator

class TestEmailValidator:

    validator = EmailValidator.get_instance()

    def test_email(self):
        assert self.validator.is_valid("jsmith@apache.org") is True

    def test_email_at_tld(self):
        val = EmailValidator.get_instance(allow_local=False, allow_tld=True)
        assert val.is_valid("test@com") is True
    
    @pytest.mark.parametrize("test_input,expected", [("jsmith@apache.org", True), ("jsmith@apache.com", True),
                                ("jsmith@apache.net", True), ("jsmith@apache.info", True), ("jsmith@apache.", False),
                                ("jsmith@apache.c", False), ("someone@yahoo.museum", True), ("someone@yahoo.mu-seum", False)])
    def test_email_extension(self, test_input, expected):
        assert self.validator.is_valid(test_input) is expected

    def test_email_localhost(self):
        # Check the default is not to allow
        no_local = EmailValidator.get_instance(allow_local=False)
        allow_local = EmailValidator.get_instance(allow_local=True)
        assert no_local == self.validator
        assert allow_local != self.validator

        # Depends on the validator
        assert allow_local.is_valid("joe@localhost.localdomain") is True
        assert allow_local.is_valid("joe@localhost") is True

        assert no_local.is_valid("joe@localhost.localdomain") is False
        assert no_local.is_valid("joe@localhost") is False

    @pytest.mark.parametrize("test_input,expected", [("joe1blow@apache.org", True), ("joe$blow@apache.org", True), ("joe-@apache.org", True),
                                ("joe_@apache.org", True), ("joe+@apache.org", True), ("joe!@apache.org", True), ("joe*@apache.org", True),
                                ("joe'@apache.org", True), ("joe%45@apache.org", True), ("joe?@apache.org", True), ("joe&@apache.org", True),
                                ("joe=@apache.org", True), ("+joe@apache.org", True), ("!joe@apache.org", True), ("*joe@apache.org", True),
                                ("'joe@apache.org", True), ("%joe45@apache.org", True), ("?joe@apache.org", True), ("&joe@apache.org", True), 
                                ("=joe@apache.org", True), ("+@apache.org", True), ("!@apache.org", True), ("*@apache.org", True), ("'@apache.org", True),
                                ("%@apache.org", True), ("?@apache.org", True), ("&@apache.org", True), ("=@apache.org", True), ("joe.@apache.org", False),
                                (".joe@apache.org", False), (".@apache.org", False), ("joe.ok@apache.org", True), ("joe..ok@apache.org", False), 
                                ("..@apache.org", False), ("joe(@apache.org", False), ("joe)@apache.org", False), ("joe,@apache.org", False),
                                ("joe;@apache.org", False), ("\"joe.\"@apache.org", True), ("\".joe\"@apache.org", True), ("\"joe+\"@apache.org", True),
                                ("\"joe@\"@apache.org", True), ("\"joe!\"@apache.org", True), ("\"joe*\"@apache.org", True), ("\"joe'\"@apache.org", True),
                                ("\"joe(\"@apache.org", True), ("\"joe)\"@apache.org", True), ("\"joe,\"@apache.org", True), ("\"joe%45\"@apache.org", True),
                                ("\"joe;\"@apache.org", True), ("\"joe?\"@apache.org", True), ("\"joe&\"@apache.org", True), ("\"joe=\"@apache.org", True),
                                ("\"..\"@apache.org", True), ("\"john\\\"doe\"@apache.org", True), ("john56789.john56789.john56789.john56789.john56789.john56789.john@example.com", True),
                                ("john56789.john56789.john56789.john56789.john56789.john56789.john5@example.com", False), ("\\>escape\\\\special\\^characters\\<@example.com", True),
                                ("Abc\\@def@example.com", True), ("Abc@def@example.com", False), ("space\\ monkey@example.com", True)])
    def test_email_username(self, test_input, expected):
        assert self.validator.is_valid(test_input) is expected

    @pytest.mark.parametrize("test_input,expected", [("andy.noble@\u008fdata-workshop.com", False), ("andy.o'reilly@data-workshop.com", True),
                                ("andy@o'reilly.data-workshop.com", False), ("foo+bar@i.am.not.in.us.example.com", True),
                                ("foo+bar@example+3.com", False), ("test@%*.com", False), ("test@^&#.com", False)])
    def test_email_with_bogus_char(self, test_input, expected):
        assert self.validator.is_valid(test_input) is expected
    
    def test_email_with_commas(self):
        assert self.validator.is_valid("joeblow@apa,che.org") is False
        assert self.validator.is_valid("joeblow@apache.o,rg") is False
        assert self.validator.is_valid("joeblow@apache,org") is False
    
    def test_email_with_control_chars(self):
        for c in range(0, 32):
            assert self.validator.is_valid("foo" + chr(c) + "bar@domain.com") is False
        # assert self.validator.is_valid("foo" + chr(127) + "bar@domain.com") is False # TODO
        assert self.validator.is_valid("foo" + chr(65) + "bar@domain.com") is True
    
    def test_email_with_dash(self):
        assert self.validator.is_valid("andy.noble@data-workshop.com") is True
        assert self.validator.is_valid("andy-noble@data-workshop.-com") is False
        assert self.validator.is_valid("andy-noble@data-workshop.c-om") is False
        assert self.validator.is_valid("andy-noble@data-workshop.co-m") is False
    
    def test_email_with_dot_end(self):
        assert self.validator.is_valid("andy.noble@data-workshop.com.") is False
    
    def test_email_with_numeric_address(self):
        assert self.validator.is_valid("someone@[216.109.118.76]") is True
        assert self.validator.is_valid("someone@yahoo.com") is True
    
    def test_email_with_slashes(self):
        assert self.validator.is_valid("joe!/blow@apache.org") is True
        assert self.validator.is_valid("joe@ap/ache.org") is False
        assert self.validator.is_valid("joe@apac!he.org") is False
    
    @pytest.mark.parametrize("test_input,expected", [("joeblow @apache.org", False), ("joeblow@ apache.org", False), (" joeblow@apache.org", False),
                                ("joeblow@apache.org ", False), ("joe blow@apache.org ", False), ("joeblow@apa che.org ", False),
                                ("\"joeblow \"@apache.org", True), ("\" joeblow\"@apache.org", True), ("\" joe blow \"@apache.org", True)])
    def test_email_with_spaces(self, test_input, expected):
        assert self.validator.is_valid(test_input) is expected
    
    @pytest.mark.parametrize("test_input,expected", [("someone@xn--d1abbgf6aiiy.xn--p1ai", True), ("someone@президент.рф", True),
                                ("someone@www.b\u00fccher.ch", True), ("someone@www.\uFFFD.ch", False), ("someone@www.b\u00fccher.ch", True),
                                ("someone@www.\uFFFD.ch", False)])
    def test_validator235(self, test_input, expected):
        assert self.validator.is_valid(test_input) is expected
    
    def test_validator278(self):
        assert self.validator.is_valid("someone@-test.com") is False
        assert self.validator.is_valid("someone@test-.com") is False
    
    @pytest.mark.parametrize("test_input,expected", [("abc-@abc.com", True), ("abc_@abc.com", True), ("abc-def@abc.com", True),
                                                    ("abc_def@abc.com", True), ("abc@abc_def.com", False)])
    def test_validator293(self, test_input, expected):
        assert self.validator.is_valid(test_input) is expected
    
    def test_validator315(self):
        assert self.validator.is_valid("me@at&t.net") is False
        assert self.validator.is_valid("me@att.net") is True
    
    def test_validator395(self):
        val = EmailValidator.get_instance(allow_local=False, allow_tld=True)
        assert val.is_valid("test@.com") is False

    def test_validator365(self):
        assert self.validator.is_valid("Loremipsumdolorsitametconsecteturadipiscingelit.Nullavitaeligulamattisrhoncusnuncegestasmattisleo."
                + "Donecnonsapieninmagnatristiquedictumaacturpis.Fusceorciduifacilisisutsapieneuconsequatpharetralectus."
                + "Quisqueenimestpulvinarutquamvitaeportamattisex.Nullamquismaurisplaceratconvallisjustoquisportamauris."
                + "Innullalacusconvalliseufringillautvenenatissitametdiam.Maecenasluctusligulascelerisquepulvinarfeugiat."
                + "Sedmolestienullaaliquetorciluctusidpharetranislfinibus.Suspendissemalesuadatinciduntduisitametportaarcusollicitudinnec."
                + "Donecetmassamagna.Curabitururnadiampretiumveldignissimporttitorfringillaeuneque."
                + "Duisantetelluspharetraidtinciduntinterdummolestiesitametfelis.Utquisquamsitametantesagittisdapibusacnonodio."
                + "Namrutrummolestiediamidmattis.Cumsociisnatoquepenatibusetmagnisdisparturientmontesnasceturridiculusmus."
                + "Morbiposueresedmetusacconsectetur.Etiamquisipsumvitaejustotempusmaximus.Sedultriciesplaceratvolutpat."
                + "Integerlacuslectusmaximusacornarequissagittissitametjusto."
                + "Cumsociisnatoquepenatibusetmagnisdisparturientmontesnasceturridiculusmus.Maecenasindictumpurussedrutrumex.Nullafacilisi."
                + "Integerfinibusfinibusmietpharetranislfaucibusvel.Maecenasegetdolorlacinialobortisjustovelullamcorpersem."
                + "Vivamusaliquetpurusidvariusornaresapienrisusrutrumnisitinciduntmollissemnequeidmetus."
                + "Etiamquiseleifendpurus.Nuncfelisnuncscelerisqueiddignissimnecfinibusalibero."
                + "Nuncsemperenimnequesitamethendreritpurusfacilisisac.Maurisdapibussemperfelisdignissimgravida."
                + "Aeneanultricesblanditnequealiquamfinibusodioscelerisqueac.Aliquamnecmassaeumaurisfaucibusfringilla."
                + "Etiamconsequatligulanisisitametaliquamnibhtemporquis.Nuncinterdumdignissimnullaatsodalesarcusagittiseu."
                + "Proinpharetrametusneclacuspulvinarsedvolutpatliberoornare.Sedligulanislpulvinarnonlectuseublanditfacilisisante."
                + "Sedmollisnislalacusauctorsuscipit.Inhachabitasseplateadictumst.Phasellussitametvelittemporvenenatisfeliseuegestasrisus."
                + "Aliquameteratsitametnibhcommodofinibus.Morbiefficiturodiovelpulvinariaculis."
                + "Aeneantemporipsummassaaconsecteturturpisfaucibusultrices.Praesentsodalesmaurisquisportafermentum."
                + "Etiamnisinislvenenatisvelauctorutullamcorperinjusto.Proinvelligulaerat.Phasellusvestibulumgravidamassanonfeugiat."
                + "Maecenaspharetraeuismodmetusegetefficitur.Suspendisseamet@gmail.com") is False
    
    def test_validator374(self):
        assert self.validator.is_valid("abc@school.school") is True
    
    def test_validator473_part1(self):
        with pytest.raises(Exception):
            EmailValidator(allow_local=False, allow_tld=False, domain_validator=None)
    
    def test_validator473_part2(self):
        with pytest.raises(Exception):
            EmailValidator(allow_local=False, allow_tld=False, domain_validator=DomainValidator.get_instance(allow_local=True, items=[]))
    
    def test_validator473_part3(self):
        with pytest.raises(Exception):
            EmailValidator(allow_local=True, allow_tld=False, domain_validator=DomainValidator.get_instance(allow_local=False, items=[]))
    
    def test_validator473_part4(self):
        assert self.validator._is_valid_domain("test.local") is False
        items = [DomainValidator.Item(DomainValidator.ArrayType.GENERIC_PLUS, ["local"])]
        val = EmailValidator(True, False, DomainValidator.get_instance(True, items))
        assert val._is_valid_domain("test.local") is True
