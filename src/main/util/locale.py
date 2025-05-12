import locale

class Locale:
    """Python wrapper of locale that implements some java.util.Locale functionality with getters and setters."""
    
    # Mapping ISO 2-letter to 3-letter language codes
    ISO3_LANGUAGE_MAP = {
        "en": "eng", "fr": "fra", "de": "deu", "es": "spa", "zh": "zho", "ja": "jpn"
    }
    # Mapping ISO 2-letter to 3-letter country codes
    ISO3_COUNTRY_MAP = {
        "US": "USA", "FR": "FRA", "DE": "DEU", "ES": "ESP", "CN": "CHN", "JP": "JPN"
    }
    # Display names for common languages
    LANGUAGE_NAMES = {
        "en": "English", "fr": "French", "de": "German", "es": "Spanish", "zh": "Chinese", "ja": "Japanese"
    }
    # Display names for common countries
    COUNTRY_NAMES = {
        "US": "United States", "FR": "France", "DE": "Germany", "ES": "Spain", "CN": "China", "JP": "Japan"
    }

    @classmethod
    def getdefaultlocale(cls):
        """ Mimics Java's Locale.getDefault() """

        locale.setlocale(locale.LC_CTYPE, None)
        lang, _ = locale.getlocale()
        encoding = locale.getencoding()
        if lang:
            return Locale(lang)
        else:
            return Locale("en_US")

    def __init__(self, locale_str=None, language=None, country="" , variant=""):
        """ Parses a Java-style locale string like 'en_US_POSIX'"""
        if locale_str is not None and language is None and country == "" and variant == "":
            parts = locale_str.split('_')
            self._language = parts[0] if len(parts) > 0 else None
            self._country = parts[1] if len(parts) > 1 else None
            self._variant = parts[2] if len(parts) > 2 else None
        elif locale_str is None and language is not None: 
            self._language = language
            self._country = country
            self._variant = variant
        else:
            raise ValueError("Error")

    # ---- LANGUAGE PROPERTY ----
    @property
    def language(self):
        """ Returns the language code (e.g., 'en') """
        return self._language

    @language.setter
    def language(self, value):
        """ Sets the language code """
        if value and len(value) == 2:
            self._language = value.lower()
        else:
            raise ValueError("Language must be a 2-letter ISO code (e.g., 'en')")

    # ---- COUNTRY PROPERTY ----
    @property
    def country(self):
        """ Returns the country code (e.g., 'US') """
        return self._country

    @country.setter
    def country(self, value):
        """ Sets the country code """
        if value and len(value) == 2:
            self._country = value.upper()
        else:
            raise ValueError("Country must be a 2-letter ISO code (e.g., 'US')")

    # ---- VARIANT PROPERTY ----
    @property
    def variant(self):
        """ Returns the variant code (e.g., 'POSIX') if available """
        return self._variant

    @variant.setter
    def variant(self, value):
        """ Sets the variant code """
        self._variant = value if value else None

    # ---- ISO3 LANGUAGE & COUNTRY ----
    @property
    def iso3_language(self):
        """ Converts 2-letter language code to ISO 639-2 (3-letter) code """
        return self.ISO3_LANGUAGE_MAP.get(self._language, self._language)

    @property
    def iso3_country(self):
        """ Converts 2-letter country code to ISO 3166-1 alpha-3 code """
        return self.ISO3_COUNTRY_MAP.get(self._country, self._country)

    # ---- DISPLAY NAMES ----
    @property
    def display_language(self):
        """ Returns a human-readable language name """
        return self.LANGUAGE_NAMES.get(self._language, self._language)

    @property
    def display_country(self):
        """ Returns a human-readable country name """
        return self.COUNTRY_NAMES.get(self._country, self._country)

    @property
    def display_variant(self):
        """ Returns a human-readable variant (if applicable) """
        return self._variant or ""

    def __str__(self):
        """ Returns the locale in Java's format (e.g., 'en_US_POSIX') """
        parts = [self._language, self._country, self._variant]
        return '_'.join(filter(None, parts))
        # THis appears to be Python formatted.
        # TODO: Verify documentation.


# ---- Example Usage ----
locale_obj = Locale("en_US_POSIX")

# Get values
print("Language:", locale_obj.language)   # "en"
print("Country:", locale_obj.country)     # "US"
print("Variant:", locale_obj.variant)     # "POSIX"

# Modify values (setters)
locale_obj.language = "fr"
locale_obj.country = "CA"
locale_obj.variant = "EURO"

print("Modified Locale String:", str(locale_obj))  # "fr_CA_EURO"

# ISO Codes
print("ISO3 Language:", locale_obj.iso3_language)  # "fra"
print("ISO3 Country:", locale_obj.iso3_country)    # "CAN"

# Display Names
print("Display Language:", locale_obj.display_language)  # "French"
print("Display Country:", locale_obj.display_country)    # "Canada"
print("Display Variant:", locale_obj.display_variant)    # "EURO"

# Get default system locale
default_locale = Locale.getdefaultlocale()
print("Default Locale:", default_locale)