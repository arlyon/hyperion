import re

postcode_regex = re.compile("^([Gg][Ii][Rr] 0[Aa]{2})|"
                            "((([A-Za-z][0-9]{1,2})|"
                            "(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|"
                            "(([A-Za-z][0-9][A-Za-z])|"
                            "([A-Za-z][A-Ha-hJ-Yj-y][0-9]?[A-Za-z])))) ?"
                            "[0-9][A-Za-z]{2})$")


def is_uk_postcode(postcode: str) -> bool:
    return re.match(postcode_regex, postcode) is not None


