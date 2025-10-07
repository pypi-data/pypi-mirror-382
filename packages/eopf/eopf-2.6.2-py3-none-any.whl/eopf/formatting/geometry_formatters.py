#
# Copyright (C) 2025 ESA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
geometry_formatters.py

geometry xml data formatter : coordinates/footprint etc


"""
import ast
from typing import Any, Dict, List, Union

from eopf.exceptions import FormattingError

from .abstract import EOAbstractSingleValueFormatter
from .utils import detect_pole_or_antemeridian, poly_coords_parsing, split_poly


class ToBbox(EOAbstractSingleValueFormatter):
    """Formatter for computing coordinates of a polygon bounding box"""

    # docstr-coverage: inherited
    name = "to_bbox"

    # docstr-coverage: inherited
    def _format(self, xpath_input: str) -> List[float]:
        """Computes coordinates of a polygon bounding box

        Parameters
        ----------
        path: str
            xpath

        Returns
        ----------
        List[float]:
            Returns a list with coordinates, longitude, latitude for SW/NE points

        Raises
        ----------
        FormattingError
            When formatting can not be performed
        """

        # when reconverting back to SAFE, the input can be directly evaluated as a list
        try:
            aux = ast.literal_eval(xpath_input)
            max_lon = max(aux, key=lambda x: x[0])[0]  # Return tuple with biggest value on index 0
            min_lon = min(aux, key=lambda x: x[0])[0]  # Return tuple with smallest value on index 0
            max_lat = max(aux, key=lambda x: x[1])[1]  # Return tuple with biggest value on index 1
            min_lat = min(aux, key=lambda x: x[1])[1]  # Return tuple with smallest value on index 1
            return [max_lon, min_lat, min_lon, max_lat]  # Order to be reviewed
        except (ValueError, SyntaxError):
            pass

        # when converting from SAFE, parse the input
        try:
            poly_coords = poly_coords_parsing(a_string=xpath_input)
            # Maybe use to_geojson to get coordinates
            max_lon = max(poly_coords, key=lambda x: x[0])[0]  # Return tuple with biggest value on index 0
            min_lon = min(poly_coords, key=lambda x: x[0])[0]  # Return tuple with smallest value on index 0
            max_lat = max(poly_coords, key=lambda x: x[1])[1]  # Return tuple with biggest value on index 1
            min_lat = min(poly_coords, key=lambda x: x[1])[1]  # Return tuple with smallest value on index 1
            return [max_lon, min_lat, min_lon, max_lat]  # Order to be reviewed
        except Exception as e:
            raise FormattingError(f"{e}") from e


class ToGeoJson(EOAbstractSingleValueFormatter):
    """Formatter for converting polygon coordinates to geoJson format"""

    # docstr-coverage: inherited
    name = "to_geoJson"

    # docstr-coverage: inherited
    def _format(self, xpath_input: str) -> Dict[str, Union[List[Any], str]]:
        """Computes polygon coordinates in geoJson format,
        from xml acquired coordinates

        Parameters
        ----------
        input: str

        Returns
        ----------
        List[List[float]]:
            Returns a list of lists(tuples) containing a pair (latitude, longitude) for each point of a polygon.

        Raises
        ----------
        FormattingError
            When formatting can not be performed
        """
        # when reconverting back to SAFE, the input can be directly evaluated as a list
        try:
            return {"type": "Polygon", "coordinates": [ast.literal_eval(xpath_input)]}
        except (ValueError, SyntaxError):
            pass

        # when converting from SAFE, parse the input
        try:
            poly_coords_str = xpath_input
            poly_coords = poly_coords_parsing(poly_coords_str)
            # as per geoJson, the first and last coords must match to close the Polygon
            if poly_coords[0] != poly_coords[-1]:
                poly_coords.append(poly_coords[0])
            # If polygon coordinates crosses any pole or antemeridian, split the polygon in a multipolygon
            if detect_pole_or_antemeridian(poly_coords):
                return {"type": "MultiPolygon", "coordinates": split_poly(poly_coords)}
            # Otherwise, just return computed coordinates
            return {"type": "Polygon", "coordinates": [poly_coords]}
        except Exception as e:
            raise FormattingError(f"{e}") from e
