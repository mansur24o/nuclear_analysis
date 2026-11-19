import pandas as pd
import workspace

def test_merge_tests_and_stockpile():
    stockpile_df = pd.DataFrame({
        'Entity': ['United States', 'United States',
                   'United States', 'France'],
        'Code': ['USA', 'USA', 'USA', 'FRA'],
        'Year': [1995, 1996, 1997, 1995],
        'Number of nuclear warheads': [1000, 1100, 1200, 300]
    })
    tests_df = pd.DataFrame({
        'Location.Country': ['United States', 'United States',
                             'United States', 'France'],
        'Date.Year': [1995, 1995, 1996, 1995]
    })
    result = workspace.merge_tests_and_stockpile(tests_df, stockpile_df)

    # Check that years after 1998 are excluded
    assert result['Year'].max() <= 1998

    # Check test counts
    us_1995 = result[(result['Entity'] == 'United States') &
                     (result['Year'] == 1995)]
    assert us_1995['Test Count'].iloc[0] == 2
    us_1996 = result[(result['Entity'] == 'United States') &
                     (result['Year'] == 1996)]
    assert us_1996['Test Count'].iloc[0] == 1

    # Check that years without tests get a zero
    us_1997 = result[(result['Entity'] == 'United States') &
                     (result['Year'] == 1997)]
    assert us_1997['Test Count'].iloc[0] == 0


def test_merge_conflict_stockpile_correlation():
    stockpile_df = pd.DataFrame({
        'Entity': ['United States', 'United States', 'France'],
        'Code': ['USA', 'USA', 'FRA'],
        'Year': [1995, 1996, 1995],
        'Number of nuclear warheads': [1000, 1100, 300]
    })
    dispute_df = pd.DataFrame({
        'stabb': ['United States', 'United States',
                  'United States', 'France'],
        'styear': [1995, 1995, 1995, 1995],
        'dispnum': [10, 10, 11, 12],
        'hiact': [5, 7, 3, 9]
    })
    result = workspace.merge_conflict_stockpile_correlation(dispute_df,
                                                            stockpile_df)
    # Check max military action
    us_1995 = result[
        (result['Entity'] == 'United States') &
        (result['Year'] == 1995)
    ]
    assert us_1995['max_hostility'].iloc[0] == 7

    # Check number of unique disputes
    assert us_1995['num_conflicts'].iloc[0] == 2

    # Check years w/o disputes
    us_1996 = result[(result['Entity'] == 'United States') &
                     (result['Year'] == 1996)]
    assert us_1996['max_hostility'].iloc[0] == 0
    assert us_1996['num_conflicts'].iloc[0] == 0

    # Check France
    france_1995 = result[(result['Entity'] == 'France') &
                         (result['Year'] == 1995)]
    assert france_1995['max_hostility'].iloc[0] == 9
    assert france_1995['num_conflicts'].iloc[0] == 1

def main():
    test_merge_tests_and_stockpile()
    test_merge_conflict_stockpile_correlation()
    print('Success')


if __name__ == '__main__':
    main()