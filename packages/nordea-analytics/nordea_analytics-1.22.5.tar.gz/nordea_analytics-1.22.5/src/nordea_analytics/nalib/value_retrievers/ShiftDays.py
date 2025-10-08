from datetime import datetime
import typing
from typing import Optional, Dict, Union

import pandas as pd

from nordea_analytics.convention_variable_names import (
    DateRollConvention,
    DayCountConvention,
    Exchange,
)
from nordea_analytics.nalib.data_retrieval_client import (
    DataRetrievalServiceClient,
)
from nordea_analytics.nalib.util import (
    convert_to_variable_string,
    get_config,
)
from nordea_analytics.nalib.value_retriever import ValueRetriever

config = get_config()


class ShiftDays(ValueRetriever):
    """Shifts a datetime by a given number of days."""

    def __init__(
        self,
        client: DataRetrievalServiceClient,
        date: datetime,
        days: int,
        exchange: Optional[Union[str, Exchange]] = None,
        day_count_convention: Optional[Union[str, DayCountConvention]] = None,
        date_roll_convention: Optional[Union[str, DateRollConvention]] = None,
    ) -> None:
        """Initialization of class.

        Args:
            client: The client used to retrieve data.
            date: The date that will be shifted.
            days: The number of days to shift 'date' with.
                Negative values move date back in time.
            exchange: The exchange's holiday calendar to be used.
            day_count_convention: The convention to use for counting days.
            date_roll_convention: The convention to use for rolling
                when a holiday is encountered.
        """
        super(ShiftDays, self).__init__(client)
        self._client = client
        self.date = date
        self.days = days
        self.exchange = (
            convert_to_variable_string(exchange, Exchange)
            if isinstance(exchange, Exchange)
            else exchange
        )
        self.day_count_convention = (
            convert_to_variable_string(day_count_convention, DayCountConvention)
            if isinstance(day_count_convention, DayCountConvention)
            else day_count_convention
        )
        self.date_roll_convention = (
            convert_to_variable_string(date_roll_convention, DateRollConvention)
            if isinstance(date_roll_convention, DateRollConvention)
            else date_roll_convention
        )
        self._data = self.shift_days()

    def shift_days(self) -> Dict:
        """Shifts the date by the specified number of days and retrieves the response with the shifted date.

        Returns:
            The JSON response with the shifted date.
        """
        json_response = self.get_response(self.request)

        return json_response[config["results"]["shift_days"]]

    @property
    def url_suffix(self) -> str:
        """Get the URL suffix for the API endpoint.

        Returns:
            The URL suffix for the API endpoint.
        """
        return config["url_suffix"]["shift_days"]

    @property
    def request(self) -> dict:
        """Construct the request dictionary for the API call.

        Returns:
            The request dictionary for the API call.
        """
        date = self.date.strftime("%Y-%m-%d")
        days = self.days
        exchange = self.exchange
        day_count_convention = self.day_count_convention
        date_roll_convention = self.date_roll_convention

        request_dict = {
            "date": date,
            "days": days,
            "exchange": exchange,
            "day-count-convention": day_count_convention,
            "date-roll-convention": date_roll_convention,
        }

        return request_dict

    def to_datetime(self) -> datetime:
        """Convert the JSON response to a datetime object.

        Returns:
            The datetime object representing the shifted date.
        """
        shifted_date_string = typing.cast(str, self._data["date"])

        shifted_date = datetime.strptime(shifted_date_string, "%Y-%m-%d")
        return shifted_date

    def to_dict(self) -> Dict:
        """Convert the JSON response to a dictionary.

        Returns:
            The dictionary representing the JSON response.
        """
        pass

    def to_df(self) -> pd.DataFrame:
        """Convert the JSON response to a pandas DataFrame.

        Returns:
            The pandas DataFrame representing the JSON response.
        """
        pass
