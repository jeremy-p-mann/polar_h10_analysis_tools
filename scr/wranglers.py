import numpy as np
import pandas as pd
import os


class polar_h10_running_wrangler:
    '''
    Wrangles running data
    Note that it considers anything slower than 60 min/mi as still.
    '''

    def __init__(self, filepath):
        self.filepath = filepath
        self.meta_df = self.wrangle_meta_df()
        self.data_df = self.wrangle_data_df()

    def wrangle_meta_df(self):
        """
        Extracts and wrangle session metadata
        """
        meta_df = pd.read_csv(self.filepath)[:1]

        meta_df.dropna(axis=1, inplace=True)

        meta_df['Date'] = pd.to_datetime(meta_df['Date'], format='%d-%m-%Y')
        meta_df['Start time'] = pd.to_datetime(
            meta_df['Start time'], infer_datetime_format=True)
        meta_df['Duration'] = pd.to_timedelta(meta_df['Duration'])

        meta_df.drop(columns=['Date'], inplace=True)

        renaming_dict = {'Start time': 'Start Datetime'}
        meta_df.rename(columns=renaming_dict, inplace=True)

        meta_df.loc[0, 'Sport'] = meta_df.loc[0, 'Sport'].title()
        meta_df.loc[0, 'Name'] = meta_df.loc[0, 'Name'].title()

        return meta_df

    def wrangle_data_df(self, pace_threshold=75):
        '''
        Extracts and wrangles the session data
        '''
        data_df = pd.read_csv(self.filepath, header=2)

        data_df.dropna(axis=1, inplace=True)

        data_df['Pace (min/mi)'] = '00:' + data_df['Pace (min/mi)']
        data_df['Pace (min/mi)'] = pd.to_timedelta(
            data_df['Pace (min/mi)']
        ).dt.total_seconds() / 60

        data_df['Pace (min/mi)'] = np.round(
            data_df['Pace (min/mi)'],  decimals=1
        )

        data_df[data_df['Pace (min/mi)'] > pace_threshold] = 0

        data = np.full(shape=data_df.index.shape,
                       fill_value=self.get_start_datetime())
        start_datetime_series = pd.Series(data=data, index=data_df.index)

        data_df['Time'] = pd.to_timedelta(
            data_df['Time']) + start_datetime_series

        data_df.set_index('Time', inplace=True)

        return data_df

    def get_activity(self):
        activity = self.meta_df.loc[0, 'Sport'].lower()
        return activity

    def get_name(self):
        name = self.meta_df.loc[0, 'Name'].replace(' ', '_').lower()
        return name

    def get_start_datetime(self):
        start_datetime = self.meta_df.loc[0, 'Start Datetime']
        return start_datetime

    def save_wrangled_data(self):
        '''
        Saves the session data. Format is:
        <date>_<start_time>_<activity>_<last_name>_<first_name>
        '''

        start_dt_str = self.get_start_datetime().strftime('%Y-%m-%d_%H:%M')
        activity = self.get_activity()
        name = self.get_name()
        save_filename = '{}_{}_{}.csv'.format(start_dt_str, activity, name)
        filepath = os.path.join('..', 'data', 'wrangled_data', save_filename)
        self.data_df.to_csv(filepath)
