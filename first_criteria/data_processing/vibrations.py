import math
import pandas as pd
import numpy as np
from first_criteria.models import Engine

# TODO: make new engines change the statisctics for b and d calculation
FREQUENCIES = [63, 140, 250, 500, 1000, 2000, 4000, 8000]


def _refreshBaseEngines():
    """ Upload default engine data to the database from a csv file """
    # TODO: solution is unstable towards floats/ints, decimal separator
    tmp_data=pd.read_csv(f'first_criteria/data_processing/base_engines.csv',sep=',',decimal='.')
    engines = [
        Engine(
            name = tmp_data.loc[row]['name'], 
            N_e = float(tmp_data.loc[row]['N_e'].replace(',', '.')),
            nu = tmp_data.loc[row]['nu'],
            pe = float(tmp_data.loc[row]['pe'].replace(',', '.')),
            pz = float(tmp_data.loc[row]['pz']),
            N_max = float(tmp_data.loc[row]['N_max']),
            delta = float(tmp_data.loc[row]['delta']),
            D_czvt = float(tmp_data.loc[row]['D_czvt']),
            D_czb   = float(tmp_data.loc[row]['D_czb']),
            group = float(tmp_data.loc[row]['group']),
            f63 = float(tmp_data.loc[row]['63']),
            f140 = float(tmp_data.loc[row]['140']),
            f250 = float(tmp_data.loc[row]['250']),
            f500 = float(tmp_data.loc[row]['500']),
            f1000 = float(tmp_data.loc[row]['1000']),
            f2000 = float(tmp_data.loc[row]['2000']),
            f4000 = float(tmp_data.loc[row]['4000']),
            f8000 = float(tmp_data.loc[row]['8000']),
            S_n = float(tmp_data.loc[row]['S_n']),
        )
        for row in tmp_data['ID']
    ]
    Engine.objects.bulk_create(engines)


def _linear_regression(x, y):
    A = np.vstack([x, np.ones(len(x))]).T
    m, c = np.linalg.lstsq(A, y, rcond=None)[0]
    C_1 = m
    return C_1, c


def _old_linear_regression(x, y):
    """ (X, Y) -> a, b: find linear regression coefficients for two vectors """ 
    r = x.shape[0]
    delta = r*sum(x ** 2) - sum(x)**2
    b = (sum(x ** 2)*sum(y) - sum(x)*(sum(x*y))) / delta
    a = (r*sum(x*y) - sum(x)*sum(y)) / delta
    return a,b


def _plot_group(group, frequency, df):
    """ Find and plot the regression line of a given group and frequency
        df - a DataFrame with engine data """
    frequency = str(frequency)
    df = df[df.group == group].copy()
    C_1, c = _linear_regression(df.B, df.D)

    df['V'] = df[frequency]
    df['B'] = -df.S_n * df.omega * df.N_max * df.delta / (df.V * df.D_czb)
    df['D'] = -df.D_czvt / df.D_czb
    
    fig,ax = plt.subplots()
    ax.scatter(df.B, df.D)
    ax.plot(df.B, df.B*c + C_1)
    plt.show()
    

def assignGroup(n):
    """ Return the group that the engine with 'n' belongs to
        n - frequency of the engine """
    groups = {
        1:(0,500),
        2:(500,750),
        3:(750,1500),
        4:(1500,10000)
    }
    n = int(n)
    for group in groups.keys():
        if n >= groups[group][0] and n < groups[group][1]:
            return group
    return -1


def _calculate_vibration_for_engine(res, engine_data):
    """ res : take regression coefficients
        engine_data : take engine parameters 
        -> vibrations: Dict{frequency:str: vibration:float} """
    ed = engine_data
    vibrations = {}
    
    for frequency in FREQUENCIES:
        omega = 2 * math.pi * frequency / 60
        C_1, c = res.loc["Group %i" % ed['group'], str(frequency)]
        # TODO: this formula might be the source of evil
        V = C_1 * omega * ed['S_n'] * ed['N_max'] * ed['delta'] / (c*ed['D_czb'] + ed['D_czvt'])
        V = 20 * math.log10(abs(V * 10**3)) + 86
        vibrations[str(frequency)] = V

    return vibrations


def _calculate_frequency_b_d(frequency):
    """ df: initial engine data
        frequency: int
        -> df with B and D and res with regression coefficients
    """
    df = pd.read_csv('first_criteria/data_processing/base_engines.csv')
    df['omega'] = 0
    for group in df.group.unique():
        omega = math.pi * df.loc[df.group == group, 'nu'].mean() / 30
        df.loc[df.group == group, 'omega'] = omega

    group = assignGroup(frequency)

    min_diff = float('inf')
    min_index = 0
    for i, freq in enumerate(FREQUENCIES):
        if abs(frequency - freq) < min_diff:
            min_diff = abs(frequency - freq)
            min_index = i
    frequency = str(FREQUENCIES[min_index])

    df = df[df.group == group].copy()
    df['V'] = df[frequency]
    df.V = 10**((df.V - 86) / 20) / 10**3
    df['D'] = -df.D_czvt / df.D_czb
    df['B'] = -df.S_n * df.omega * df.N_max * df.delta / (df.V * df.D_czb)
    C_1, c = _linear_regression(df.B, df.D)
    V = C_1 * omega * df['S_n'] * df['N_max'] * df['delta'] / (c*df['D_czb'] + df['D_czvt'])

    return {
        'group': group,
        'df': df,
        'C_1': C_1,
        'c': c,
        'frequency': frequency
    }


def _calculate_b_d(df):
    """ df : initial engine data
        -> df with B and D and res with regression coefficients
    """
    # create a MultiIndex for res dataframe
    arrays = [
        ["Group %i" % (x // 2 + 1) for x in range(0,8)],
        ["C_1", "c"]*5
    ]
    tuples = list(zip(*arrays))
    index = pd.MultiIndex.from_tuples(tuples, names=['group', 'coefficient'])
    res = pd.DataFrame(columns=[str(x) for x in FREQUENCIES], index=index)

    for frequency in FREQUENCIES:
        frequency = str(frequency)
        df['V'] = df[frequency]
        df.V = 10**((df.V - 86) / 20) / 10**3
        df['D'] = -df.D_czvt / df.D_czb
        df['B'] = -df.S_n * df.omega * df.N_max * df.delta / (df.V * df.D_czb)

        for group in df.group.unique():
            df_group = df[df.group == group]
            res.loc["Group %i" % group, frequency] = _linear_regression(df_group.B, df_group.D)
    return df, res


def getVibrations(engine_data):
    df = pd.read_csv('first_criteria/data_processing/base_engines.csv')
    df['omega'] = 0
    for group in df.group.unique():
        omega = math.pi * df.loc[df.group == group, 'nu'].mean() / 30
        df.loc[df.group == group, 'omega'] = omega
    df, res = _calculate_b_d(df)
    
    vibrations = _calculate_vibration_for_engine(res, engine_data)
    engine_data.update(vibrations)

    engine = Engine.objects.get(id=engine_data['id'])
    engine.f63 = engine_data['63']
    engine.f140 = engine_data['140']
    engine.f250 = engine_data['250']
    engine.f500 = engine_data['500']
    engine.f1000 = engine_data['1000']
    engine.f2000 = engine_data['2000']
    engine.f4000 = engine_data['4000']
    engine.f8000 = engine_data['8000']
    engine.save()