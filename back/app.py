from json import JSONDecodeError

from flask import Flask, jsonify, render_template, json
import requests

from back.orm import db, PostCodeMapping, DoesNotExist, Neighbourhood, Location, Link

# create a new instance of the flask class
app = Flask(__name__)


@app.route('/')
def index():
    """
    Returns the index.html template using Jinja.
    :return: The html we want to render.
    """
    return render_template('index.html')


@app.route('/api/bikes/')
def get_bikes():
    with open("../stolenbikes.json", "r") as f:
        bikesdata = json.load(f)
    return jsonify(bikesdata[:100])


@app.route('/api/crime/<string:postcode>')  # assign function to specified route
def get_crime(postcode):
    """
    Gets the crime nearby to a given postcode.
    :param postcode: The postcode to lookup.
    :return: A json representation of the crimes near the postcode.
    """
    mapping = get_postcode_mapping(postcode)

    crime_lookup = f"https://data.police.uk/api/stops-street?lat={mapping.lat}&lng={mapping.long}"
    crime_request = requests.get(crime_lookup).json()

    return jsonify(crime_request)


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


@app.route('/api/nearby/<string:postcode>')
@app.route('/api/nearby/<string:postcode>/<int:limit>')
def get_nearby(postcode: str, limit=10):
    """
    Gets wikipedia articles near a given postcode.
    :param postcode: The UK postcode to look up.
    :param limit: The number of results to return.
    :return: The data or an error.
    """
    mapping = get_postcode_mapping(postcode)
    if mapping is None:
        return jsonify(error=404, message="Invalid Postcode"), 404
    request_url = f"https://en.wikipedia.org/w/api.php?action=query&list=geosearch&gscoord={mapping.lat}%7C{mapping.long}&gsradius=10000&gslimit={limit}&format=json"
    request = requests.get(request_url)
    try:
        return jsonify(request.json()["query"]["geosearch"])
    except KeyError:
        return jsonify(message="No Results"), 404


@app.route('/api/postcode/<string:postcode>')
def get_postcode(postcode):
    """
    Gets data from a postcode.
    :param postcode: The postcode to look up.
    :return: The mapping for the postcode.
    """
    mapping = get_postcode_mapping(postcode)
    return jsonify(mapping.serialize()) if mapping is not None else (jsonify(message="Invalid Postcode"), 404)


@app.route('/api/neighbourhood/<string:postcode>')
def get_neighbourhood(postcode):
    """
    Gets police data about a neighbourhood.
    :param postcode: The postcode to look up.
    :return: The police data for that post code.
    """
    neighbourhood = get_neighbourhood_from_db(postcode)
    return jsonify(neighbourhood.serialize()) if neighbourhood is not None else (jsonify(message="No Police Data"), 404)


if __name__ == '__main__':
    db.connect()
    db.create_tables([PostCodeMapping, Neighbourhood, Location, Link], safe=True)
    app.run(port=2020)
