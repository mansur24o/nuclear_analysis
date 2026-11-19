import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from shapely.geometry import Point

sns.set_theme()

NUCLEAR_TESTS_FILE = 'data/nuclear_explosions.csv'
STOCKPILE_FILE = 'data/nuclear-warhead-stockpiles.csv'
DISPUTE_FILE = 'data/MIDB 5.0.csv'
MAP_DATA_FILE = 'data/map_data/ne_50m_admin_0_countries.shp'


def clean_tests(tests_df):
    """
    Given a dataset, replaces the labels for certain countries in order to align
    them with the labels from other datasets.
    """
    return tests_df.replace({'Location.Country': {'USSR': 'Russia', 'USA': 'United States',
                                                  'UK': 'United Kingdom', 'FRANCE': 'France',
                                                  'CHINA': 'China', 'PAKIST': 'Pakistan',
                                                  'INDIA': 'India'}})


def clean_dispute(dispute_df):
    """
    Given a dataset containing an extensive record of international conflicts from 1816 to
    2014, filters the dataset to only track disputes from 1930 to 2014 (inclusive) that involved
    at least one state that was/would become a nuclear power. 
    """
    countries = ['United States', 'Russia', 'United Kingdom', 'China', 'Pakistan', 'India',
                 'North Korea', 'South Africa', 'France']
    dispute_df = dispute_df[(dispute_df['styear'] >= 1930) & 
                            (dispute_df['styear'] <= 2014)]
    dispute_df = dispute_df.replace({'stabb': {'USR': 'Russia', 'USA': 'United States',
                                               'UK': 'United Kingdom', 'RUS': 'Russia',
                                               'FRN': 'France', 'CHN': 'China',
                                               'PAK': 'Pakistan', 'IND': 'India', 
                                               'PRK': 'North Korea', 'SAF': 'South Africa'}})
    dispute_df = dispute_df[dispute_df['stabb'].isin(countries)]
    return dispute_df


def merge_conflict_stockpile_correlation(dispute_df, stockpile_df):
    """
    Given a dataset containing international dispute data and another containing nuclear 
    stockpile data, merges the datasets based on matching country-year columns, with all
    data from stockpile being retained if there isn't a match in the dispute dataset. 
    Returns the merged dataset with all missing values filled by 0.
    """
    dispute_df = clean_dispute(dispute_df)
    dispute_df = dispute_df.groupby(['stabb', 'styear']).agg(max_hostility=('hiact', 
                                                                            'max'),
                                                             num_conflicts=('dispnum', 
                                                                            'nunique'))
    dispute_df = dispute_df.reset_index()
    merged = stockpile_df.merge(dispute_df, left_on=['Entity', 'Year'],
                                right_on=['stabb', 'styear'], how='left')
    merged = merged.drop(columns=['stabb', 'styear'])
    merged = merged.fillna(0)
    return merged


def plot_conflictnum_stockpile_correlation(df, country):
    """
    Given a merged dataset and a country, plots a dual-axis graph that tracks 
    the country's stockpile count in red and the number of conflicts engaged in
    in blue. Both plots share a common x-axis, which represents years.
    """
    fig, ax1 = plt.subplots(figsize=(15, 10))
    df2 = df[df['Entity'] == country]
    sns.lineplot(x='Year', y='Number of nuclear warheads', ax=ax1, color='red', data=df2)
    ax1.set_ylabel('Number of Nuclear Warheads', color='red', fontsize=12)
    ax2 = ax1.twinx()
    sns.lineplot(x='Year', y='num_conflicts', ax=ax2, color='blue', data=df2)
    ax2.set_ylabel('Number of conflicts engaged in', color='blue', fontsize=12)
    plt.title(country + ': Nuclear Stockpiles vs. Conflict Frequency', fontsize=16)
    plt.savefig('plots/' + country + '_conflicts.png', bbox_inches='tight')
    plt.close(fig)


def plot_conflictlvl_stockpile_correlation(df, country):
    """
    Given a merged dataset and a country, plots a dual-axis graph that tracks 
    the country's stockpile count in red and its maximum hostility level reached
    in blue. Both plots share a common x-axis, which represents years.
    """
    fig, ax1 = plt.subplots(figsize=(15, 10))
    df2 = df[df['Entity'] == country]
    sns.lineplot(x='Year', y='Number of nuclear warheads', ax=ax1, color='red', 
                 data=df2)
    ax1.set_ylabel('Number of Nuclear Warheads', color='red', fontsize=12)
    ax2 = ax1.twinx()
    sns.lineplot(x='Year', y='max_hostility', ax=ax2, color='blue', data=df2)
    ax2.set_ylabel('Max hostility reached', color='blue', fontsize=12)
    plt.title(country + ': Nuclear Stockpiles vs. Max Hostility Level', fontsize=16)
    plt.savefig('plots/' + country + '_conflictlvl.png', bbox_inches='tight')
    plt.close(fig)


def plot_nuclear_tests(tests_df, map_data):
    """
    Given a dataset containing information about all nuclear recorded nuclear tests
    and another geospatial dataset of the world map, plots the locations of every
    recorded nuclear tests onto their corresponding location on the map.
    """
    coordinates = zip(tests_df['Location.Coordinates.Longitude'],
                      tests_df['Location.Coordinates.Latitude']) 
    tests_df['coordinates'] = [Point(lon, lat) for lon, lat in coordinates]
    tests_gdf = gpd.GeoDataFrame(tests_df, geometry='coordinates',
                                 crs='EPSG:4326')
    fig, ax = plt.subplots(figsize=(15, 10))
    map_data.plot(ax=ax, color='lightgrey', edgecolor='black')
    tests_gdf.plot(ax=ax, column='Data.Yield.Upper',
                   markersize=tests_gdf['Data.Yield.Upper'] ** 0.5, alpha=0.7,
                   cmap='plasma')
    plt.savefig('plots/global_tests.png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print('Done')


def merge_tests_and_stockpile(tests_df, stockpile_df):
    """
    Given a dataset containing information about all nuclear recorded nuclear tests 
    and another containing nuclear stockpile data, merges the datasetsbased on matching 
    country-year columns,  with all data from stockpile being retained if there isn't a
    match in the tests dataset. Returns the merged dataset with all missing values 
    filled by 0.
    """
    stockpile_df2 = stockpile_df[stockpile_df['Year'] <= 1998]
    tests_df2 = tests_df[['Location.Country', 'Date.Year']]
    tests_df2 = tests_df2.groupby(['Location.Country', 'Date.Year']).size().reset_index()
    tests_df2 = tests_df2.rename(columns={0: 'Test Count'})
    merged = stockpile_df2.merge(tests_df2, left_on=['Entity', 'Year'],
                                 right_on=['Location.Country', 'Date.Year'], how='left')
    merged = merged.drop(columns=['Location.Country', 'Date.Year'])
    merged = merged.fillna(0)
    return merged


def plot_test_stockpile_correlation(df, country):
    """
    Given a merged dataset and a country, plots a dual-axis graph that tracks 
    the country's stockpile count in red and the number of tests it conducted
    in blue. Both plots share a common x-axis, which represents years.
    """
    fig, ax1 = plt.subplots(figsize=(15, 10))
    df2 = df[df['Entity'] == country]
    sns.lineplot(x='Year', y='Number of nuclear warheads', ax=ax1, color='red', data=df2)
    ax1.set_ylabel('Number of Nuclear Warheads', color='red', fontsize=12)
    ax2 = ax1.twinx()
    sns.lineplot(x='Year', y='Test Count', ax=ax2, color='blue', data=df2)
    ax2.set_ylabel('Test Count', color='blue', fontsize=12)
    plt.savefig('plots/' + country + 'test_stockpile.png', bbox_inches='tight')
    plt.close(fig)


def main():
    tests_df = pd.read_csv(NUCLEAR_TESTS_FILE)
    stockpile_df = pd.read_csv(STOCKPILE_FILE)
    dispute_df = pd.read_csv(DISPUTE_FILE)
    map_data = gpd.read_file(MAP_DATA_FILE)
    tests_df = clean_tests(tests_df)
    merged_df1 = merge_tests_and_stockpile(tests_df, stockpile_df)
    merged_df2 = merge_conflict_stockpile_correlation(dispute_df, stockpile_df)


if __name__ == '__main__':
    main()