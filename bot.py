# SPDX-License-Identifier: BSD-3-Clause

# flake8: noqa F401
from collections.abc import Callable

import numpy as np

from vendeeglobe import (
    Checkpoint,
    Heading,
    Instructions,
    Location,
    Vector,
    config,
)
from vendeeglobe.utils import distance_on_surface


class Bot:
    """
    This is the ship-controlling bot that will be instantiated for the competition.
    """

    def __init__(self):
        self.team = "ABoatingAccident"  # This is your team name

        self.course = [
            Checkpoint(latitude=38.928962, longitude=-29.901633, radius=50), # 0
            Checkpoint(latitude=18.677174, longitude=-63.668182, radius=50), # 1
            Checkpoint(latitude=17.355385, longitude=-64.297441, radius=50), # 2
            Checkpoint(latitude=9.468760, longitude=-80.265292, radius=50),# 3 
            Checkpoint(latitude=6.566362, longitude=-78.732970, radius=50), # 4
            Checkpoint(latitude=0.697582, longitude=-156.908280, radius=50), # 5
            Checkpoint(latitude=5.487077343928526, longitude=126.97826013731992, radius=50), # 6
            Checkpoint(latitude=0.8943043273826395, longitude=119.64370985998079 , radius=50), # 7
            Checkpoint(latitude=-9.192082956771523, longitude=115.57420879991402, radius=30), # 8
            Checkpoint(latitude=-9.80403836568785, longitude=94.98431811057729, radius=30), # 9
            Checkpoint(latitude=-5.141523842516368, longitude=78.59842933046924, radius=50), # 10
            Checkpoint(latitude=12.591779742351633, longitude=50.93666853797446, radius=50), # 11
            Checkpoint(latitude=12.10319809495949, longitude=43.51976068090509, radius=50), # 12
            Checkpoint(latitude=12.98804162692998, longitude=42.86416890074322 , radius=50), # 13
            Checkpoint(latitude=27.118790429173686, longitude=34.7089570042413, radius=50), # 14
            Checkpoint(latitude=28.135176741601782, longitude=33.33616470489151, radius=50), # 15
            Checkpoint(latitude=29.546402188408344, longitude=32.45334833295368, radius=50), # 16
            Checkpoint(latitude=29.558882503421046, longitude=32.419672786937205, radius=50), # 17
            Checkpoint(latitude=29.690592481026997, longitude=32.3962240979495, radius=50), # 18
            Checkpoint(latitude=29.586539241656073, longitude=32.39168175553029, radius=50), # 19
            Checkpoint(latitude=30.00741768544188, longitude=32.35381929715478 , radius=30), # 20
            Checkpoint(latitude=32.15420070036845, longitude=32.35381929715478, radius=30), # 21
            Checkpoint(latitude=31.750059040719893, longitude=31.628250697760066, radius=30), # 22
            Checkpoint(latitude=36.360876335435854, longitude=14.603450611417891, radius=25), # 23
            Checkpoint(latitude=38.021641064885735, longitude=8.78681357086634, radius=50), # 24
            Checkpoint(latitude=35.99194826343473, longitude=-5.293664432945284, radius=50), # 25
            Checkpoint(latitude=35.92692671250301, longitude=-6.41828139588345, radius=50), # 26
            Checkpoint(latitude=36.270678601096456, longitude=-10.988420977846186, radius=50), # 27
            Checkpoint(latitude=38.8375726341942, longitude=-10.196388980391959, radius=50), # 28
            Checkpoint(latitude=43.45451988515832, longitude=-10.687687955181907, radius=50), # 29
            Checkpoint(
                latitude=config.start.latitude,
                longitude=config.start.longitude,
                radius=5,
            ),
        ]


    def run(
        self,
        t: float,
        dt: float,
        longitude: float,
        latitude: float,
        heading: float,
        speed: float,
        vector: np.ndarray,
        forecast: Callable,
        world_map: Callable,
    ) -> Instructions:
        """
        This is the method that will be called at every time step to get the
        instructions for the ship.

        Parameters
        ----------
        t:
            The current time in hours.
        dt:
            The time step in hours.
        longitude:
            The current longitude of the ship.
        latitude:
            The current latitude of the ship.
        heading:
            The current heading of the ship.
        speed:
            The current speed of the ship.
        vector:
            The current heading of the ship, expressed as a vector.
        forecast:
            Method to query the weather forecast for the next 5 days.
            Example:
            current_position_forecast = forecast(
                latitudes=latitude, longitudes=longitude, times=0
            )
        world_map:
            Method to query map of the world: 1 for sea, 0 for land.
            Example:
            current_position_terrain = world_map(
                latitudes=latitude, longitudes=longitude
            )

        Returns
        -------
        instructions:
            A set of instructions for the ship. This can be:
            - a Location to go to
            - a Heading to point to
            - a Vector to follow
            - a number of degrees to turn Left
            - a number of degrees to turn Right

            Optionally, a sail value between 0 and 1 can be set.
        """
        # Initialize the instructions
        instructions = Instructions()

        # TODO: Remove this, it's only for testing =================
        current_position_forecast = forecast(
            latitudes=latitude, longitudes=longitude, times=0
        )
        current_position_terrain = world_map(latitudes=latitude, longitudes=longitude)
        # ===========================================================

        # Go through all checkpoints and find the next one to reach
        for i, ch in enumerate(self.course):
            # Compute the distance to the checkpoint
            dist = distance_on_surface(
                longitude1=longitude,
                latitude1=latitude,
                longitude2=ch.longitude,
                latitude2=ch.latitude,
            )
            # Consider slowing down if the checkpoint is close
            jump = dt * np.linalg.norm(speed)
            if dist < 2.0 * ch.radius + jump:
                instructions.sail = min(ch.radius / jump, 1)
            else:
                instructions.sail = 1.0
            # Check if the checkpoint has been reached
            if dist < ch.radius:
                ch.reached = True
            if not ch.reached:
                instructions.location = Location(
                    longitude=ch.longitude, latitude=ch.latitude
                )
                break

        return instructions
