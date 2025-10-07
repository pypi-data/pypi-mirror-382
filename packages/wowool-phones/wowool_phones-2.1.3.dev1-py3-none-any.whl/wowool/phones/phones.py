import phonenumbers
from phonenumbers import geocoder, carrier
import re
import pycountry
from wowool.diagnostic import Diagnostics
from wowool.phones.app_id import APP_ID
from wowool.document.analysis.document import AnalysisDocument
import logging
from wowool.native.core.analysis import get_internal_concept
from wowool.utility.apps.decorators import (
    exceptions_to_diagnostics,
    requires_analysis,
    check_requires_concepts,
)

DEFAULT_CONCEPTS = set(["PhoneNr", "City", "Country", "GeoCoordinate", "GeoTag", "Address"])
DEFAULT_ATTRIBUTES = set(["country"])

logger = logging.getLogger(__name__)
country_code_map = {"UK": "GB", "UAE": "ARE"}


class Phones:
    """Phone component that can be use in a Pipeline"""

    ID = APP_ID

    def __init__(self, countries: list[str] | None = None, distance: int = 200):
        """Initialize the Phones application.

        :param countries: list of default country names that could resolve a local phone number
        :param countries: list[str]
        :param distance: The maximum distance between a location and the phone number to be considered. default = 200
        :param distance: int

        """

        self._filter = DEFAULT_CONCEPTS
        self._attributes = DEFAULT_ATTRIBUTES
        self.locations = {}
        self.countries = countries if countries else []
        self.distance = distance

    def in_range(self, concept, country_concept):
        if country_concept is None:
            return False
        distance = abs(concept.begin_offset - country_concept.begin_offset)
        return distance <= self.distance

    def resolve_unknown_numbers_distance(self, document, phone_nrs, unknown_numbers, countries, country_concept):
        logger.debug(f"resolve_unknown_numbers_distance {countries} {unknown_numbers}")
        if unknown_numbers and countries:
            for phone_info in unknown_numbers:
                for country_name in countries:
                    phone_nr_str = phone_info["phone_nr_str"]
                    if phone_nr_str:
                        concept = phone_info["concept"]
                        if country_concept:
                            if not self.in_range(concept, country_concept):
                                continue

                        country_code = None
                        logger.debug(f"pycountry.countries.get(name={country_name})")
                        country = pycountry.countries.get(name=country_name)
                        if country:
                            country_code = country.alpha_2
                        try:
                            logger.debug(f"phonenumbers.parse({phone_nr_str}, region={country_code}) 1")
                            phone_nr = phonenumbers.parse(phone_nr_str, region=country_code)
                            logger.debug(f"phonenumbers.format_number({phone_nr}, E164) 1")
                            canonical = phonenumbers.format_number(phone_nr, phonenumbers.PhoneNumberFormat.E164)
                            phone_info["phone_nr_str"] = ""
                        except phonenumbers.phonenumberutil.NumberParseException as ex:
                            logger.debug(f"Could not resolve PhoneNr phone_nr={phone_nr_str}, {country_code=} , Exception {ex}")
                            continue

                        self._add_phone_number(document, phone_nrs, phone_nr, canonical, concept)
                        break
        logger.debug(f"resolve_unknown_numbers_distance RETURN")

    def resolve_unknown_numbers(self, document, phone_nrs, unknown_numbers):
        logger.debug(f"resolve_unknown_numbers {unknown_numbers}")
        if unknown_numbers:
            for phone_info in unknown_numbers:
                for country_name in self.countries:
                    phone_nr_str = phone_info["phone_nr_str"]
                    if phone_nr_str:
                        concept = phone_info["concept"]
                        if phone_info["country_name"]:
                            country_name = phone_info["country_name"]

                        logger.debug(country_name)
                        country_code = None
                        if len(country_name) == 2:
                            country_code = country_name
                        elif country_name:
                            logger.debug(f"pycountry.countries.get(name={country_name})")
                            country = pycountry.countries.get(name=country_name)
                            if country:
                                country_code = country.alpha_2
                            else:
                                logger.debug(f"Unknown country code : {country_code}")

                        if country_code:
                            try:
                                logger.debug(f"phonenumbers.parse({phone_nr_str}, region={country_code}) 2")
                                phone_nr = phonenumbers.parse(phone_nr_str, country_code)
                                logger.debug(f"phonenumbers.format_number({phone_nr}, E164) 2")
                                canonical = phonenumbers.format_number(phone_nr, phonenumbers.PhoneNumberFormat.E164)
                                phone_info["phone_nr_str"] = ""
                            except phonenumbers.phonenumberutil.NumberParseException as ex:
                                logger.debug(f"Could not resolve PhoneNr phone_nr={phone_nr_str}, {country_code=} , Exception {ex}")
                                continue
                            self._add_phone_number(document, phone_nrs, phone_nr, canonical, concept)
                        else:
                            logger.debug(f"Country code not set")
                        break

    def _add_phone_number(self, document, phone_nrs, phone_nr, canonical, concept):
        try:
            logger.debug(f"geocoder.country_name_for_number({phone_nr}, 'en')")
            phone_country = geocoder.country_name_for_number(phone_nr, "en")
        except AttributeError:
            phone_country = None
        try:
            logger.debug(f"geocoder.description_for_number({phone_nr}, 'en')")
            location = geocoder.description_for_number(phone_nr, "en")
        except AttributeError:
            location = None

        try:
            logger.debug(f"carrier.name_for_number({phone_nr}, 'en')")
            carrier_name = carrier.name_for_number(phone_nr, "en")
        except AttributeError:
            carrier_name = None

        logger.debug(f"getting internal concept for {concept}")
        internal_concept = get_internal_concept(document.analysis, concept)
        if internal_concept:
            phone_entry = {}
            if hasattr(phone_nr, "country_code"):
                phone_entry = {"country_code": phone_nr.country_code}
                internal_concept.add_attribute("country_code", str(phone_nr.country_code))
            internal_concept.add_attribute("canonical", canonical)

            if phone_country:
                phone_entry["country"] = phone_country
                internal_concept.add_attribute("country", phone_country)

            if location and location != phone_country:
                phone_entry["location"] = location
                internal_concept.add_attribute("location", location)
            if carrier_name:
                phone_entry["carrier"] = carrier_name
                internal_concept.add_attribute("carrier", carrier_name)

            if canonical not in phone_nrs:
                phone_nrs[canonical] = phone_entry
        logger.debug(f"DONE getting internal concept for {concept}")

    def get_country(self, country_name):
        if len(country_name) == 2:
            country_name = country_code_map.get(country_name, country_name)
            logger.debug(f"pycountry.countries.get( alpha_2={country_name} )")
            country = pycountry.countries.get(alpha_2=country_name)
        elif len(country_name) == 3:
            country_name = country_code_map.get(country_name, country_name)
            logger.debug(f"pycountry.countries.get( alpha_3={country_name} )")
            country = pycountry.countries.get(alpha_3=country_name)
        else:
            logger.debug(f"pycountry.countries.get( name={country_name} )")
            country = pycountry.countries.get(name=country_name)
        logger.debug(f"pycountry.countries.get() = RETURN {country}")
        return country

    @exceptions_to_diagnostics
    @requires_analysis
    def __call__(self, document: AnalysisDocument, diagnostics: Diagnostics) -> AnalysisDocument:
        """
        Normalize phone number in the E164 format and collect information in the document object.

        :param document:  The document we want to enrich with phone number information.
        :type document: AnalysisDocument

        :returns: The given document with the new annotations. See the :ref:`json format <json_apps_phones>`
        """

        check_requires_concepts(APP_ID, document, diagnostics, {"PhoneNr"})

        phone_nrs = {}
        unknown_numbers = []
        country_name = ""
        country_code = ""
        country_concept = None
        for concept in document.analysis.concepts(lambda concept: concept.uri in self._filter):
            if concept.uri == "City":
                if "country" in concept.attributes:
                    country_name = concept.attributes["country"][0]
                    country_concept = concept
                    self.resolve_unknown_numbers_distance(
                        document,
                        phone_nrs,
                        unknown_numbers,
                        [country_name],
                        country_concept,
                    )
                    country_code = None
            elif concept.uri == "Country":
                country_name = concept.canonical
                country_concept = concept
                self.resolve_unknown_numbers_distance(
                    document,
                    phone_nrs,
                    unknown_numbers,
                    [country_name],
                    country_concept,
                )
                country_code = None
            elif concept.uri == "PhoneNr":
                if "country" in concept.attributes:
                    for country_name in concept.attributes["country"]:
                        country = self.get_country(country_name)
                        if country:
                            country_name = country.name
                            country_code = country.alpha_2
                        country_concept = concept

                phone_nr_str = concept.literal
                if phone_nr_str.startswith("00"):
                    phone_nr_str = re.sub("^00", "+", phone_nr_str)
                try:
                    if country_concept and not self.in_range(concept, country_concept):
                        unknown_numbers.append(
                            {
                                "phone_nr_str": phone_nr_str,
                                "concept": concept,
                                "country_name": country_name,
                                "country_concept": country_concept,
                            }
                        )
                        continue
                    else:
                        if country_name:
                            if not country_code:
                                country = self.get_country(country_name)
                                if country:
                                    country_code = country.alpha_2

                        logger.debug(f"phonenumbers.parse({phone_nr_str}, {country_code=}) 3")
                        phone_nr = phonenumbers.parse(phone_nr_str, country_code)
                        logger.debug(f"phonenumbers.format_number({phone_nr}, E164) 3")
                        canonical = phonenumbers.format_number(phone_nr, phonenumbers.PhoneNumberFormat.E164)
                except phonenumbers.phonenumberutil.NumberParseException as ex:
                    logger.debug(f"Could not resolve PhoneNr phone_nr={phone_nr_str}, {country_code=} , Exception {ex}")
                    unknown_numbers.append(
                        {
                            "phone_nr_str": phone_nr_str,
                            "concept": concept,
                            "country_name": country_name,
                            "country_concept": country_concept,
                        }
                    )
                    continue

                self._add_phone_number(document, phone_nrs, phone_nr, canonical, concept)

        logger.debug(f"unknown_numbers: {unknown_numbers}")
        self.resolve_unknown_numbers(document, phone_nrs, unknown_numbers)
        logger.debug(f"phone_nrs {phone_nrs}")
        document.add_results(APP_ID, [{"phone_nr": k, **v} for k, v in phone_nrs.items()])
        document.analysis.reset()

        return document
