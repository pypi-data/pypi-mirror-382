import datetime
import pytz
from pytz import timezone


class date_handler:
    """
    A utility class that provides methods for converting date to different formats.
    """

    # noinspection PyMethodMayBeStatic
    def get_local_datetime_pst(self):
        """
        Gets the current system datetime, converts it to PST and returns the PST
        datetime.

        Parameters
        ----------
        self

        Returns
        -------
        Current datetime based on PST.

        Exceptions
        ----------
        None
        """
        # Get current system datetime
        # AWS datetime is based on UTC and needs to be converted to US Pacific
        los_angeles = timezone('America/Los_Angeles')
        return datetime.datetime.now(los_angeles)

    # noinspection PyMethodMayBeStatic
    def get_local_date_pst(self):
        """
        Gets the current system time, converts it to PST and returns the date
        portion in YYYY-MM-DD format.

        Parameters
        ----------
        self

        Returns
        -------
        Current date based on PST in YYYY-MM-DD format

        Exceptions
        ----------
        None
        """
        # Get current system datetime
        # AWS datetime is based on UTC and needs to be converted to US Pacific
        los_angeles = timezone('America/Los_Angeles')
        now = datetime.datetime.now(los_angeles)

        # Strip time portion from datetime to get the date only
        return now.strftime('%Y-%m-%d')

    # noinspection PyMethodMayBeStatic
    def get_local_time_pst(self):
        """
        Gets the current system time, converts it to PST and returns the time
        portion in YYYY-MM-DD format.

        Parameters
        ----------
        self

        Returns
        -------
        Current time based on PST in YYYY-MM-DD format

        Exceptions
        ----------
        None
        """
        # Get current system datetime
        # AWS datetime is based on UTC and needs to be converted to US Pacific
        los_angeles = timezone('America/Los_Angeles')
        now = datetime.datetime.now(los_angeles)

        # Strip date portion from datetime to get the time only
        return now.strftime('%H.%M.%S')

    # noinspection PyMethodMayBeStatic
    def is_dst(self, dt=None):
        """
        Based on a datetime object that is passed as an argument, determines if Daylight Saving Time (DST)
        is in effect. If no argument is passed, it determines if DST is in effect based on the current system
        time.

        Parameters
        ----------
        datetime value (dt)

        Returns
        -------
        True or False.

        Exceptions
        ----------
        None
        """
        # If dt argument is not passed, use the current system time.
        if dt is None:
            dt = datetime.datetime.now()

        # Get the argument time in GMT and convert it to local time (America/Los_Angeles).
        pst_timezone = pytz.timezone('America/Los_Angeles')
        pst_time = dt.astimezone(pst_timezone)
        # This will show the offset in seconds for Daylight Saving Time (DST).
        # If it's zero, we're not in DST.
        is_dst = pst_time.tzinfo._dst.seconds != 0

        return is_dst


def main():
    """
    Main entry point to class
    """
    current_datetime = date_handler().get_local_datetime_pst()
    print('Current datetime={}'.format(current_datetime))
    current_date = date_handler().get_local_date_pst()
    print('Current date={}'.format(current_date))
    current_time = date_handler().get_local_time_pst()
    print('Current time={}'.format(current_time))

    is_dst_value = date_handler().is_dst()
    print('DST value={} for current datetime'.format(is_dst_value))

    is_dst_value = date_handler().is_dst(datetime.datetime.now() + datetime.timedelta(days=30))
    print('DST value={} for {}'.format(is_dst_value, datetime.datetime.now() + datetime.timedelta(days=30)))

    is_dst_value = date_handler().is_dst(datetime.datetime.now())
    print('DST value={} for {}'.format(is_dst_value, datetime.datetime.now()))

    temp = datetime.datetime(2016, 3, 13, 2, 59, 59)
    is_dst_value = date_handler().is_dst(temp)
    print('DST value={} for {}'.format(is_dst_value, temp))

    temp = datetime.datetime(2016, 3, 13, 3, 0, 0)
    is_dst_value = date_handler().is_dst(temp)
    print('DST value={} for {}'.format(is_dst_value, temp))


if __name__ == '__main__':
    main()
