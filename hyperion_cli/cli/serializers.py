import json
from abc import ABC, abstractmethod
from typing import List

from click import echo
from colorama import Fore

from .util import PostcodeData


class PostcodeSerializer(ABC):

    @abstractmethod
    def __init__(self, postcode_datas):
        pass

    @abstractmethod
    def serialize(self):
        pass


class PostcodeSerializerJSON(PostcodeSerializer):

    def __init__(self, postcode_datas):
        super().__init__(postcode_datas)
        self.postcodes = postcode_datas

    def serialize(self):
        return json.dumps(self.postcodes)


class PostcodeSerializerHuman(PostcodeSerializer):

    def __init__(self, postcode_datas: List[PostcodeData]) -> None:
        super().__init__(postcode_datas)
        self.postcode_datas = postcode_datas

    def serialize(self):
        for data in self.postcode_datas:
            echo(f"Data for: {Fore.GREEN}{data.postcode.postcode}{Fore.RESET}")
            echo(f"  Coordinates: {data.postcode.lat}, {data.postcode.long}")
            echo(f"  District: {data.postcode.district}")
            echo(f"  Country: {data.postcode.country}")

            if data.bikes is not None:
                echo(f"  Stolen Bikes: {Fore.GREEN}{len(data.bikes)}{Fore.RESET}")
                echo("\n".join(
                    f"    {bike.model} {bike.make}: {bike.distance}m away" for bike in data.bikes[:10]))
                if len(data.bikes) > 10:
                    echo(f"    {Fore.BLUE}(limited to 10){Fore.RESET}")
            if data.crime is not None:
                echo(f"  Crimes Committed: {len(data['crimes'])}")
            if data.nearby is not None:
                echo("  Points of Interest:")
                for x in data.nearby:
                    echo(f"    {x['dist']}m - {x['title']}")
