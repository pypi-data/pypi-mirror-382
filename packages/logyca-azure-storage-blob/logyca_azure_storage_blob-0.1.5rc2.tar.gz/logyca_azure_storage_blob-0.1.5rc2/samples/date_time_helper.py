from datetime import datetime
from enum import StrEnum
import pytz

class App:
    class Time(StrEnum):
        POSTGRESQL_FORMAT_DATE="%Y-%m-%d %H:%M:%S%z" # 2024-04-26 20:56:31.420023+00:00
        STANDARD_FORMAT_DATE="%Y-%m-%d %H:%M:%S" # 2024-04-26 20:56:31

class TimeZonesPytz:
    class America(StrEnum):
        BOGOTA='America/Bogota'
    class US(StrEnum):
        AZURE_DEFAULT='UTC'
        VIRGINIA='UTC'

class DateTimeHelper:
    '''Description:
    Return current date in selected format

    ## Example:
    
    ```Python
    from date_time_helper import DateTimeHelper, App, TimeZonesPytz

    DateTimeHelper.print_console_timezones_pytz()
    print(f"date now: {DateTimeHelper.get_datetime_now(App.Time.POSTGRESQL_FORMAT_DATE,is_format_string=False)}")
    print(f"date timezone convert UTC to Bogotá: {DateTimeHelper.get_datetime_now_to_another_location(App.Time.STANDARD_FORMAT_DATE,TimeZonesPytz.US.AZURE_DEFAULT,TimeZonesPytz.America.BOGOTA)}")
    ```
    '''
    @classmethod
    def get_datetime_now(cls,format_date:str,is_format_string:bool=True) -> tuple[datetime,str]:
        '''Description
        Get the current time in type datetime.datetime or string format defined in the constant App.Time.FORMAT_DATE
        :param format_date:bool: example %Y-%m-%d %H:%M:%S
        :param is_format_string:str: if True return str format, otherwise format datetime.datetime

        ## Example

        ```Python
        from date_time_helper import DateTimeHelper, App

        print(f"date now: {DateTimeHelper.get_datetime_now(App.Time.POSTGRESQL_FORMAT_DATE,is_format_string=False)}")
        ```
        '''
        date_now=datetime.now()
        if is_format_string is True:
            date_now_with_format = date_now.strftime(format_date)
            return date_now_with_format
        else:
            return datetime.now()
    
    @classmethod
    def print_console_timezones_pytz(cls):
        for timezone in pytz.all_timezones:
            print(timezone)

    @classmethod
    def get_datetime_now_to_another_location(cls,format_date:str,origin_location:str,destination_location:str,is_format_string:bool=True) -> tuple[datetime,str]:
        '''Description
        Get the current time in type datetime.datetime or string format defined in the constant App.Time.FORMAT_DATE
        :param format_date:bool: example %Y-%m-%d %H:%M:%S
        :param origin_location:str: Known time zone where the current server is configured, example: America/Bogota
        :param destination_location:str: Time zone to which the current date is to be transformed, example: Canada/Eastern
        :param is_format_string:bool: if True return str format, otherwise format datetime.datetime

        ## Example

        ```Python
        from date_time_helper import DateTimeHelper, App, TimeZonesPytz
        
        print(f"date timezone convert UTC to Bogotá: {DateTimeHelper.get_datetime_now_to_another_location(App.Time.STANDARD_FORMAT_DATE,TimeZonesPytz.US.AZURE_DEFAULT,TimeZonesPytz.America.BOGOTA)}")
        ```

        '''
        date_now = datetime.now()
        date_origin:datetime = pytz.timezone(origin_location).localize(date_now)
        date_destination:datetime = date_origin.astimezone(pytz.timezone(destination_location))
        if is_format_string is True:
            date_now_canada_with_format:str = date_destination.strftime(format_date)
            return date_now_canada_with_format
        else:
            return date_destination

