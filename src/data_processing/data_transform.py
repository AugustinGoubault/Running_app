import pandas as pd
import datetime as dt



def preprocess_data(data:dict) -> pd.DataFrame:
    return pd.json_normalize(data)

class DataTransform:

    def process_strava_data(self, df:pd.DataFrame)-> pd.DataFrame:
        '''process strava data'''
        columns_to_keep = [
            "distance",
            "moving_time",
            "name",
            "total_elevation_gain",
            "type",
            "start_date_local",
            "average_speed",
            "start_latlng"]
        df = (
            df
            .pipe(self._keep_columns, columns=columns_to_keep)
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
        df["start_latlng"] = df["start_latlng"].astype(str)
        df[['latitude', 'longitude']] = df["start_latlng"].str.replace("[", "").str.replace("]", "").str.split(", ", expand=True)
        return df
    
    def _round_coordinates(self, df:pd.DataFrame, decimals:int)-> pd.DataFrame:
        df['latitude'] = df['latitude'].round(decimals)
        df['longitude'] = df['longitude'].round(decimals)
        return df

    def _create_isocalendar_columns(self, df:pd.DataFrame, date_column:str)-> pd.DataFrame:
        df[['year', 'week', 'day']] = df[date_column].dt.isocalendar()
        df = df.assign(month=df[date_column].dt.month)
        return df
    
    def format_pace(self, df:pd.DataFrame, distance_col:str, time_col:str)-> pd.DataFrame:
        pace_sec_per_km = df.distance_col / (1000 * df.time_col)  # Pace in seconds per kilometer
        pace_min = int(pace_sec_per_km // 60)  # Minutes part
        pace_sec = int(pace_sec_per_km % 60)  # Seconds part
        
        # Format the result as a string
        pace_str = f"{pace_min}:{pace_sec:02}"  # Format seconds as two digits
        
        return pace_str

    def _add_week_start_end(self, df:pd.DataFrame)-> pd.DataFrame:
        years = df['year']
        weeks = df['week']
        months = df['month']
        start_dates = pd.to_datetime(years.astype(str) + '-01-01') + pd.to_timedelta((weeks-1)*7, unit="D")
        start_dates = start_dates - pd.to_timedelta(start_dates.dt.weekday, unit='D')
        end_dates = start_dates + pd.to_timedelta(6, unit="D")

        month_start_dates = pd.to_datetime(years.astype(str) + '-' + months.astype(str).str.zfill(2) + '-01')

        df = df.assign(week_start=start_dates, week_end=end_dates, month_start=month_start_dates)
        df = df.astype({"week_start": str, "week_end": str, "month_start": str})
        return df

    def get_first_day_of_period(self, date:str=dt.date.today().strftime("%Y-%m-%d"), week_delta:int=0, month_delta:int=0)-> str:
        '''
        get first day of the week for the given date
        '''
        date = dt.datetime.strptime(date, "%Y-%m-%d").date()
        start_week = date - pd.DateOffset(days=date.weekday(), weeks=week_delta, months=month_delta)
        return start_week.strftime("%Y-%m-%d")

    def groupby_period(self, df:pd.DataFrame, period:list)-> pd.DataFrame:
        '''group by week/month and aggregate distance, moving_time, total_elevation_gain, average_speed'''
        groupby_columns = ["year"]
        for periods in period:
            groupby_columns.append(periods)
        df = (
            df
            .groupby(groupby_columns)
            .agg({
                "distance": lambda x:x.sum()/1e3,
                "moving_time": lambda x: pd.to_timedelta(x.sum(), unit='s'),
                "total_elevation_gain": "sum",
                "average_speed": "mean",
                "week_start": "first",
                "month_start": "first",
                "name": "count"})
            .reset_index()
            .rename(columns={"name": "activity_count"})
        )
        return df

    def mask_df(self, df:pd.DataFrame, column:str, value:int)-> pd.DataFrame:
        '''mask dataframe by column value'''
        return df.loc[df[column]==value]

    def _generate_date_df(self, column_name:str, freq:str, start_date:str, end_date:str)-> pd.DataFrame:
        '''generate weekly/monthly date dataframe'''
        date_df = pd.DataFrame({column_name: pd.date_range(start=start_date, end=end_date, freq=freq).strftime("%Y-%m-%d")})
        return date_df

    def merge_on_date_start(self, column_name:str, freq:str, data:pd.DataFrame)-> pd.DataFrame:
        '''merge dataframes on date_start'''
        date_df = self._generate_date_df(column_name=column_name, freq=freq, start_date='2023-01-01', end_date=self.get_first_day_of_period())
        return date_df.merge(data, on=column_name, how='left').fillna(0)