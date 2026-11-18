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

def clean_dispute(dispute_df):
    countries = ['United States', 'Russia', 'United Kingdom', 'China', 'Pakistan', 'India',
                 'North Korea', 'South Africa', 'France']
    dispute_df = dispute_df[(dispute_df['styear'] >= 1930) & 
                            (dispute_df['styear'] <= 2014)]
    
    dispute_df = dispute_df.replace({'stabb': {'USR': 'Russia', 'USA': 'United States',
                                               'UK': 'United Kingdom', 'RUS': 'Russia',
                                                          'FRN': 'France',
                                                          'CHN': 'China',
                                                          'PAK': 'Pakistan',
                                                          'IND': 'India',
                                                          'PRK': 'North Korea',
                                                          'SAF': 'South Africa'}})
    
    dispute_df = dispute_df[dispute_df['stabb'].isin(countries)]
    dispute_df = dispute_df.groupby(['stabb', 'styear']).agg(max_hostility=('hiact', 'max'),
                                                             num_conflicts=('dispnum', 'nunique'))
    return dispute_df.reset_index()

def merge_dispute_and_stockpile(dispute_df, stockpile_df):
    merged = stockpile_df.merge(dispute_df, left_on=['Entity', 'Year'],
                                right_on=['stabb', 'styear'], how='left')
    merged = merged.fillna(0)
    return merged

def plot_conflict_stockpile_correlation(df, country):
    fig, ax1 = plt.subplots(figsize=(15, 10))
    df2 = df[df['Entity'] == country]
    sns.lineplot(x='Year', y='Number of nuclear warheads', ax=ax1, color='red', data=df2)
    ax1.set_ylabel('Number of Nuclear Warheads', color='red', fontsize=12)
    ax2 = ax1.twinx()
    sns.lineplot(x='Year', y='num_conflicts', ax=ax2, color='blue', data=df2)
    ax2.set_ylabel('Number of conflicts engaged in', color='blue', fontsize=12)
    plt.savefig('plots/' + country + '_conflicts.png', bbox_inches='tight')


def conflicts_among_nuclear_states(merged, dispute_df):
    countries = ['United States', 'Russia', 'United Kingdom', 'China', 'Pakistan', 'India',
                 'North Korea', 'South Africa', 'France']
    dispute_df = dispute_df[(dispute_df['styear'] >= 1930) & 
                            (dispute_df['styear'] <= 2014)]
    dispute_df = dispute_df.replace({'stabb': {'USR': 'Russia', 'USA': 'United States',
                                               'UKG': 'United Kingdom', 'RUS': 'Russia',
                                               'FRN': 'France', 'CHN': 'China',
                                               'PAK': 'Pakistan', 'IND': 'India',
                                               'PRK': 'North Korea', 'SAF': 'South Africa'}})
    
    dispute_df = dispute_df[dispute_df['stabb'].isin(countries)]
    dispute_df = dispute_df.loc[:, ['stabb', 'styear', 'hiact', 'dispnum']]
    merged['is_armed'] = merged['Number of nuclear warheads'] > 0
    dispute_df = dispute_df.merge(merged, left_on=['stabb', 'styear'],
                                  right_on=['Entity', 'Year'], how='inner')
    dispute_df = dispute_df.loc[:, ['Entity', 'Year', 'hiact', 'dispnum', 'is_armed']]

    npc1 = dispute_df.groupby('dispnum')['is_armed'].sum().reset_index()
    npc1['multiple_nps'] = (npc1['is_armed'] > 1).astype(int)

    dispute_df = dispute_df.loc[:, ['Entity', 'Year', 'hiact', 'dispnum']]

    dispute_df = dispute_df.merge(npc1[['dispnum', 'multiple_nps']], on='dispnum', how='inner')
    dispute_df = dispute_df[dispute_df['multiple_nps'] == 1]
    npc_df = dispute_df.groupby(['Entity', 'Year'])['dispnum'].nunique().reset_index()

    npc_df = merged[['Entity', 'Year']].merge(npc_df, on=['Entity', 'Year'], how='left')
    npc_df['dispnum'] = npc_df['dispnum'].fillna(0).astype(int)
    return npc_df

def plot_nuclear_power_conflicts(df):
    plt.figure()
    df = df[df['Entity'] == 'Russia']
    sns.lineplot(data=df, x='Year', y='dispnum', hue='Entity')
    plt.savefig('plots/RUSSIA_NUCLEAR_CONFLICT.png', bbox_inches='tight')
    plt.close()


def plot_conflictlvl_stockpile_correlation(df, country):
    fig, ax1 = plt.subplots(figsize=(15, 10))
    df2 = df[df['Entity'] == country]
    sns.lineplot(x='Year', y='Number of nuclear warheads', ax=ax1, color='red', data=df2)
    ax1.set_ylabel('Number of Nuclear Warheads', color='red', fontsize=12)
    ax2 = ax1.twinx()
    sns.lineplot(x='Year', y='max_hostility', ax=ax2, color='blue', data=df2)
    ax2.set_ylabel('Max hostility reached', color='blue', fontsize=12)
    plt.savefig('plots/' + country + '_conflictlvl.png', bbox_inches='tight')


def plot_nuclear_tests(tests_df, map_data):
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
    stockpile_df2 = stockpile_df[stockpile_df['Year'] <= 1998]
    tests_df2 = tests_df[['Location.Country', 'Date.Year']]
    tests_df2 = tests_df2.groupby(['Location.Country', 'Date.Year']).size().reset_index()
    tests_df2 = tests_df2.rename(columns={0: 'Test Count'})
    merged = stockpile_df2.merge(tests_df2, left_on=['Entity', 'Year'],
                                 right_on=['Location.Country', 'Date.Year'], how='inner')
    return merged


def plot_test_stockpile_correlation(df): 
    plt.figure()
    sns.lineplot(data=df, x='Year', y='Test Count', hue='Entity')
    plt.savefig('plots/test_count_annual.png', bbox_inches='tight')
    plt.close()
    plt.figure()
    sns.lineplot(data=df, x='Year', y='Number of nuclear warheads', hue='Entity')
    plt.savefig('plots/stockpile_tests_correlation.png', bbox_inches='tight')
    plt.close()

def plot_test_stockpile_correlation2(df, country):
    fig, ax1 = plt.subplots(figsize=(15, 10))
    df2 = df[df['Entity'] == country]
    sns.lineplot(x='Year', y='Number of nuclear warheads', ax=ax1, color='red', data=df2)
    ax1.set_ylabel('Number of Nuclear Warheads', color='red', fontsize=12)

    ax2 = ax1.twinx()
    sns.lineplot(x='Year', y='Test Count', ax=ax2, color='blue', data=df2)
    ax2.set_ylabel('Test Count', color='blue', fontsize=12)
    plt.savefig('plots/' + country + '.png', bbox_inches='tight')
    #plt.close()

def main():
    tests_df = pd.read_csv(NUCLEAR_TESTS_FILE)
    stockpile_df = pd.read_csv(STOCKPILE_FILE)
    dispute_df = pd.read_csv(DISPUTE_FILE)
    map_data = gpd.read_file(MAP_DATA_FILE)
    tests_df = tests_df.replace({'Location.Country': {'USSR': 'Russia', 'USA': 'United States',
                                                      'UK': 'United Kingdom',
                                                      'FRANCE': 'France',
                                                      'CHINA': 'China',
                                                      'PAKIST': 'Pakistan',
                                                      'INDIA': 'India'}})
    plot_nuclear_tests(tests_df, map_data)
    merged_df1 = merge_tests_and_stockpile(tests_df, stockpile_df)
    plot_test_stockpile_correlation(merged_df1)
    #plot_test_stockpile_correlation2(merged_df1, 'United States')
    #plot_test_stockpile_correlation2(merged_df1, 'Russia')
    #plot_test_stockpile_correlation2(merged_df1, 'France')
    #plot_test_stockpile_correlation2(merged_df1, 'China')
    #plot_test_stockpile_correlation2(merged_df1, 'Pakistan')
    #plot_test_stockpile_correlation2(merged_df1, 'India')

    dispute_df2 = clean_dispute(dispute_df)
    merged_df2 = merge_dispute_and_stockpile(dispute_df2, stockpile_df)
    plot_conflict_stockpile_correlation(merged_df2, 'United States')
    plot_conflict_stockpile_correlation(merged_df2, 'Russia')
    #plot_conflictlvl_stockpile_correlation(merged_df2, 'United States')
    #plot_conflictlvl_stockpile_correlation(merged_df2, 'Russia')
    nk = conflicts_among_nuclear_states(merged_df2, dispute_df)
    plot_nuclear_power_conflicts(nk)
    
if __name__ == '__main__':
    main()