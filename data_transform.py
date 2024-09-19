import pandas as pd
import datetime as dt

class DataTransform:

    def process_strava_data(self, df:pd.DataFrame)-> pd.DataFrame:
        '''process strava data'''
        columns_to_keep = [
            "distance",
            "moving_time",
            "total_elevation_gain",
            "type",
            "start_date_local",
            "average_speed",
            "start_latlng"]
        df = (
            df
            .pipe(self._keep_columns, columns=['distance', 'moving_time', 'total_elevation_gain','type', 'sport_type', 'start_date_local', 'average_speed','start_latlng'])
            .pipe(self._convert_to_datetime, columns=['start_date_local'])
            .pipe(self._create_coordinates)
            .pipe(self._convert_to_numeric, columns=['distance', 'moving_time', 'total_elevation_gain','latitude', 'longitude'])
            .pipe(self._round_coordinates, decimals=3)
            .pipe(self._drop_columns, columns=['start_latlng'])
            .pipe(self._create_isocalendar_columns, date_column='start_date_local')
            .pipe(self._add_week_start_end)
        )
   
        return df

    def _keep_columns(self, df:pd.DataFrame, columns:list)-> pd.DataFrame:
        return df.loc[:, columns]

    def _drop_columns(self, df:pd.DataFrame, columns:list)-> pd.DataFrame:
        return df.drop(columns=columns)

    def _convert_to_datetime(self,df: pd.DataFrame, columns:list)-> pd.DataFrame:
        for column in columns:
            df[column] = pd.to_datetime(df[column])
        return df

    def _convert_to_numeric(self, df:pd.DataFrame, columns:list)-> pd.DataFrame:
        for column in columns:
            df[column] = pd.to_numeric(df[column])
        return df
    
    def _create_coordinates(self, df:pd.DataFrame)-> pd.DataFrame:
        df[['latitude', 'longitude']] = df["start_latlng"].str.replace("[", "").str.replace("]", "").str.split(", ", expand=True)
        return df
    
    def _round_coordinates(self, df:pd.DataFrame, decimals:int)-> pd.DataFrame:
        df['latitude'] = df['latitude'].round(decimals)
        df['longitude'] = df['longitude'].round(decimals)
        return df

    def _create_isocalendar_columns(self, df:pd.DataFrame, date_column:str)-> pd.DataFrame:
        df[['year', 'week', 'day']] = df[date_column].dt.isocalendar()
        return df
    
    def format_pace(self, df:pd.DataFrame, distance_col:str, time_col:str)-> pd.DataFrame:
        pace_sec_per_km = df.distance_col / (1000 * df.time_col)  # Pace in seconds per kilometer
        pace_min = int(pace_sec_per_km // 60)  # Minutes part
        pace_sec = int(pace_sec_per_km % 60)  # Seconds part
        
        # Format the result as a string
        pace_str = f"{pace_min}:{pace_sec:02}"  # Format seconds as two digits
        
        return pace_str

    def _add_week_start_end(self, df:pd.DataFrame):
        years = df['year']
        weeks = df['week']
        start_dates = pd.to_datetime(years.astype(str) + '-01-01') + pd.to_timedelta((weeks-1)*7, unit="D")
        start_dates = start_dates - pd.to_timedelta(start_dates.dt.weekday, unit='D')
        end_dates = start_dates + pd.to_timedelta(6, unit="D")
        df = df.assign(week_start=start_dates, week_end=end_dates)
        return df
