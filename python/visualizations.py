import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from workspace import (
    clean_tests,
    merge_tests_and_stockpile,
    merge_conflict_stockpile_correlation,
    plot_test_stockpile_correlation, 
    plot_conflictnum_stockpile_correlation,
    plot_conflictlvl_stockpile_correlation
)

NUCLEAR_TESTS_FILE = 'data/nuclear_explosions.csv'
STOCKPILE_FILE = 'data/nuclear-warhead-stockpiles.csv'
DISPUTE_FILE = 'data/MIDB 5.0.csv'
MAP_DATA_FILE = 'data/map_data/ne_50m_admin_0_countries.shp'

tests_df = pd.read_csv(NUCLEAR_TESTS_FILE)
tests_df = clean_tests(tests_df)
stockpile_df = pd.read_csv(STOCKPILE_FILE)
dispute_df = pd.read_csv(DISPUTE_FILE)
merged_df1 = merge_tests_and_stockpile(tests_df, stockpile_df)
merged_df2 = merge_conflict_stockpile_correlation( dispute_df, stockpile_df)

"""
Nuclear Tests
"""

def plot_tests_per_year(df):
    df = df.groupby('Date.Year').size().reset_index(name='Test Count')
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=df, x='Date.Year', y='Test Count')
    plt.title('Number of Nuclear Tests per Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Tests')
    plt.savefig('plots/tests_per_year.png', dpi=300, bbox_inches='tight')
    plt.close()


def plot_tests_by_country(df):
    country_tests = df['Location.Country'].value_counts().reset_index()
    country_tests.columns = ['Country', 'Test Count']
    plt.figure(figsize=(10, 5))
    sns.barplot(data=country_tests, x='Country', y='Test Count')
    plt.title('Nuclear Tests by Country')
    plt.xlabel('Country')
    plt.ylabel('Number of Tests')
    plt.xticks(rotation=45)
    plt.savefig('plots/tests_by_country.png', dpi=300, bbox_inches='tight')
    plt.close()

"""
Stockpiles 
"""

def plot_stockpiles_over_time(df):
    plot_df = df[df['Entity'] != 'World']
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=plot_df, x='Year', y='Number of nuclear warheads', 
                 hue='Entity')
    plt.title('Nuclear Warhead Stockpiles Over Time')
    plt.xlabel('Year')
    plt.ylabel('Number of Warheads')
    plt.legend(title='Country', bbox_to_anchor=(1.05, 1))
    plt.savefig('plots/stockpiles_over_time.png', dpi=300, bbox_inches='tight')
    plt.close()


def plot_global_stockpiles(df):
    df = df[df['Entity'] == 'World']
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=df, x='Year', y='Number of nuclear warheads')
    plt.title('Global Nuclear Warhead Stockpile Over Time')
    plt.xlabel('Year')
    plt.ylabel('Number of Warheads')
    plt.savefig('plots/global_stockpiles.png', dpi=300, bbox_inches='tight')
    plt.close()

"""
Disputes
"""

def plot_disputes_per_year(df):
    df = df.groupby('styear')['dispnum'].nunique().reset_index(name='Dispute Count')
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=df, x='styear', y='Dispute Count')
    plt.title('Militarized Interstate Disputes Over Time')
    plt.xlabel('Year')
    plt.ylabel('Number of Disputes')
    plt.savefig('plots/disputes_per_year.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_top_dispute_participants(df):
    top_ten = df['stabb'].value_counts().head(10).reset_index()
    top_ten.columns = 'Country Code', 'Dispute Participation'
    plt.figure(figsize=(10, 5))
    sns.barplot(data=top_ten, x='Dispute Participation', y='Country Code')
    plt.title('Top 10 Countries by Dispute Participation')
    plt.xlabel('Number of Participant Records')
    plt.ylabel('Country Code')
    plt.savefig('plots/top_dispute_participants.png', dpi=300, bbox_inches='tight')
    plt.close()

"""
Tests and Stockpiles
(Imported from workspace)
(plot_test_stockpile_correlation)
"""

"""
Disputes and Stockpiles
(Imported from workspace)
(plot_conflictnum_stockpile_correlation, plot_conflictlvl_stockpile_correlation)
"""

def main():
    plot_tests_per_year(tests_df)
    plot_tests_by_country(tests_df)

    plot_stockpiles_over_time(stockpile_df)
    plot_global_stockpiles(stockpile_df)

    plot_disputes_per_year(dispute_df)
    plot_top_dispute_participants(dispute_df)

    plot_test_stockpile_correlation(merged_df1, 'United States')
    plot_test_stockpile_correlation(merged_df1, 'Russia')

    plot_conflictnum_stockpile_correlation(merged_df2, 'United States')
    plot_conflictlvl_stockpile_correlation(merged_df2, 'China')
    print('Done')


if __name__ == '__main__':
    main()