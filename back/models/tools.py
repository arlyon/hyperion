from json import JSONDecodeError
import requests
from peewee import DoesNotExist

from models.location import Location
from models.neighbourhood import Neighbourhood, Link
from models.postcode import PostCodeMapping


def get_postcode_mapping(postcode: str) -> PostCodeMapping or None:
    """
    Gets the postcode mapping for a given postcode.
    Acts as a middleware between us and the API, caching results.
    :param postcode: The postcode.
    :return: the Mapping.
    """
    postcode = postcode.replace(" ", "")
    try:
        return PostCodeMapping.get(PostCodeMapping.postcode == postcode)
    except DoesNotExist:
        postcode_lookup = f"https://api.postcodes.io/postcodes/{postcode}"
        postcode_request = requests.get(postcode_lookup).json()

        if postcode_request["status"] == 404:
            return None

        lat = round(postcode_request["result"]["latitude"], 6)
        long = round(postcode_request["result"]["longitude"], 6)
        country = postcode_request["result"]["country"]
        district = postcode_request["result"]["admin_district"]
        zone = postcode_request["result"]["msoa"]

        return PostCodeMapping.create(
            postcode=postcode,
            lat=lat,
            long=long,
            country=country,
            district=district,
            zone=zone
        )  # the peewee function for creating new entities


def get_neighbourhood_from_db(postcode: str) -> Neighbourhood or None:
    """
    Gets a police neighbourhood from the database.
    Acts as a middleware between us and the API, caching results.
    :param postcode: The postcode to look up.
    :return: The Neighbourhood or None if not found.
    """
    postcode = postcode.replace(" ", "")
    mapping = get_postcode_mapping(postcode)
    if mapping is None:
        return None
    elif mapping.neighbourhood is not None:
        return mapping.neighbourhood
    else:
        neighbourhood_find_url = f"https://data.police.uk/api/locate-neighbourhood?q={mapping.lat},{mapping.long}"

        try:
            neighbourhood_name = requests.get(neighbourhood_find_url).json()  # get the json and parse it immediately
        except JSONDecodeError:
            # the neighbourhood is not in the police database
            return None

        neighbourhood_lookup_url = f"https://data.police.uk/api/{neighbourhood_name['force']}/{neighbourhood_name['neighbourhood']}"
        neighbourhood_data = requests.get(neighbourhood_lookup_url).json()  # get the json and parse it immediately

        neighbourhood = Neighbourhood.create(
            code=neighbourhood_data["id"],
            email=neighbourhood_data["contact_details"]["email"] if "email" in neighbourhood_data[
                "contact_details"] else None,
            facebook=neighbourhood_data["contact_details"]["facebook"] if "facebook" in neighbourhood_data[
                "contact_details"] else None,
            telephone=neighbourhood_data["contact_details"]["telephone"] if "telephone" in neighbourhood_data[
                "contact_details"] else None,
            twitter=neighbourhood_data["contact_details"]["twitter"] if "twitter" in neighbourhood_data[
                "contact_details"] else None,
            name=neighbourhood_data["name"],
            description=neighbourhood_data["description"] if "description" in neighbourhood_data else None
        )

        for link in neighbourhood_data["links"]:
            Link.create(
                name=link["title"],
                url=link["url"],
                neighbourhood=neighbourhood,
            )

        for location in neighbourhood_data["locations"]:
            Location.create(
                address=location["address"],
                description=location["description"],
                latitude=location["latitude"],
                longitude=location["longitude"],
                name=location["name"],
                neighbourhood=neighbourhood,
                postcode=mapping,
                type=location["type"],
            )

        mapping.neighbourhood = neighbourhood
        mapping.save()

        return neighbourhood
