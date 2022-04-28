import math
import pandas as pd
from first_criteria.models import Engine


def refreshBaseEngines():
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


def linear_regression(x, y):
    """ (X, Y) -> a, b: find linear regression coefficients for two vectors """ 
    r = x.shape[0]
    delta = r*sum(x ** 2) - sum(x)**2
    b = (sum(x ** 2)*sum(y) - sum(x)*(sum(x*y))) / delta
    a = (r*sum(x*y) - sum(x)*sum(y)) / delta
    return a,b


def plot_group(group, frequency, df):
    """ Find and plot the regression line of a given group and frequency
        df - a DataFrame with engine data """
    frequency = str(frequency)
    df = df[df.group == group].copy()
    C_1, c = linear_regression(df.B, df.D)

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


def calculate_vibration_for_engine(df, res, engine_data):
    frequencies = [int(x) for x in df.columns if x.isdigit()]
    vibrations = {}
    for frequency in frequencies:
        c, C_1 = res.loc["Group %i" % engine_data['group'], str(frequency)]
        V = C_1 * engine_data['S_n'] * engine_data['N_max'] * engine_data['delta'] / (engine_data['D_czvt'] + c*engine_data['D_czb'])
        vibrations[str(frequency)] = V
    return vibrations


def calculate_b_d(df, res):
    frequencies = [int(x) for x in df.columns if x.isdigit()]
    arrays = [
        ["Group %i" % (x // 2 + 1) for x in range(0,8)],
        ["c", "C_1"]*5
    ]
    tuples = list(zip(*arrays))
    index = pd.MultiIndex.from_tuples(tuples, names=['group', 'coefficient'])
    res = pd.DataFrame(columns=[str(x) for x in frequencies], index=index)

    for frequency in frequencies:
        frequency = str(frequency)
        df['V'] = df[frequency]
        df['D'] = -df.D_czvt / df.D_czb
        df['omega'] = 0

        for group in df.group.unique():
            omega = math.pi * df.loc[df.group == group, 'nu'].mean() / 30
            df.loc[df.group == group, 'omega'] = omega

        df['B'] = -df.S_n * df.omega * df.N_max * df.delta / (df.V * df.D_czb)

        for group in df.group.unique():
            df_group = df[df.group == group]
            res.loc["Group %i" % group, frequency] = linear_regression(df_group.B, df_group.D)
            # res.loc["Group %i" % group, frequency] = linear_regression(df_group.D, df_group.B)
    return df, res


def engine_data_loop(df, res):
    engine_data = get_engine_data()
    choice = 'y'
    while choice == 'y':
        print("\nДля более точного вычисления коэффициентов требуется увеличить количество сравниваемых двигателей.")
        print("\nДобавить двигатель?")
        choice = input("y/n: ")
        if choice == 'y':
            new_engine_data = get_engine_data()
            vibrations = calculate_vibration_for_engine(df, res, new_engine_data)
            new_engine_data.update(vibrations)
            df.loc[df.shape[0]] = new_engine_data
            df, res = calculate_b_d(df, res)
    vibrations = calculate_vibration_for_engine(df, res, engine_data)
    engine_data.update(vibrations)
    df.loc[df.shape[0]] = engine_data
    return df, res


if __name__ == '__main__':
    df = pd.read_csv('data/input.csv')
    res = pd.DataFrame()

    print_theory(df)
    df, res = calculate_b_d(df, res)

    print_linreg(res)

    ans = input('Расчитать коэффициенты для двигателя?')
    if ans == 'y':
        df, res = engine_data_loop(df, res)

    df.to_excel('results/engine_data.xlsx')
    res.to_excel('results/lin_reg_coefficients.xlsx')

    print('\nЗначения вибрации для исследуемого двигателя:')
    print(df[[col for col in df.columns if col.isdigit()]].iloc[-1,])
    print('\nРезультаты расчетов были помещены в папку results')
    ask_to_continue()

