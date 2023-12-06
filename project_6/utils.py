import numpy as np
import pandas as pd


def top_unique_values(df, topvals=5, dropna=True):
    max_width = pd.get_option("display.max_colwidth") - 10
    col_names = ['Unique values'] + ['Top ' + str(num) for num in range(1, topvals + 1)] + ['Other']
    df_out = pd.DataFrame(columns=col_names)
    cols = df.columns
    for col in cols:
        top_values = pd.DataFrame(df[col].value_counts(dropna=dropna, normalize=True)).iloc[0:topvals]
        lst = []
        lst.append(df[col].nunique(dropna=dropna))
        for r in top_values.itertuples():
            i = str(r[0])[0:max_width] + ' (' + str(f'{r[1]:.1%}') + ')'
            lst.append(i)
        while len(lst) <= topvals:
            lst.append('\u2013')
        remainder = 1 - top_values.sum().iloc[0]
        if remainder != 0:
            lst.append(str(f'{remainder:.1%}'))
        else:
            lst.append('\u2013')
        row = (col, lst)
        df_out = pd.concat(
            [df_out, pd.DataFrame.from_dict(dict([row]), orient='index', columns=col_names)], 
            axis=0
        )
    return df_out


def iqr_outliers(df):
    vars = df.select_dtypes(include=[np.number]).columns
    df_out = df[vars].agg(
                lambda x: [
                    np.min(x), 
                    np.nanpercentile(x, 25), 
                    np.nanmean(x), 
                    np.nanmedian(x),
                    np.nanpercentile(x, 75), 
                    np.max(x),
                    np.nanstd(x)
                ])
    df_out.index = ['min', 'Q1', 'mean', 'median', 'Q3', 'max', 'std']
    df_out = df_out.transpose()
    
    lst = []
    for idx in df_out.index:
        row = (np.sum(df[idx] < df_out.loc[idx, 'Q1'] 
                      - 1.5 * (df_out.loc[idx, 'Q3'] - df_out.loc[idx, 'Q1'])),
               np.sum(df[idx] > df_out.loc[idx, 'Q3'] 
                      + 1.5 * (df_out.loc[idx, 'Q3'] - df_out.loc[idx, 'Q1']))
            )
        lst.append(row)
    outliers = pd.DataFrame(
        lst, 
        columns=['Values < 1.5IQR', 'Values > 1.5IQR'], 
        index=vars
    )
    df_out = (pd.concat([df_out, outliers], axis=1))
    return df_out


def quantity_canceled(df):
    qty_cancelled = pd.Series(np.zeros(df.shape[0]), index=df.index)
    df_tmp = df.loc[(df['Quantity'] > 0) &
                    (df['CustomerID'].isin(df.loc[df['Quantity'] < 0, 'CustomerID'].unique())),
                    ['CustomerID', 'StockCode', 'InvoiceDate', 'Quantity']].copy()
    qty_negative = df[(df['Quantity'] < 0)].copy()
    for r in qty_negative.itertuples():
        df_test = df_tmp[(df_tmp['CustomerID'] == r.CustomerID) &
                       (df_tmp['StockCode']  == r.StockCode) &
                       (df_tmp['InvoiceDate'] < r.InvoiceDate) &
                       (df_tmp['Quantity'] > 0)].copy()
        if (df_test.shape[0] == 0):
            qty_cancelled.at[r.Index] = np.nan
        elif (df_test.shape[0] == 1):
            qty_cancelled.at[df_test.index[0]] = -r.Quantity
        elif (df_test.shape[0] > 1):
            df_test.sort_index(axis=0, ascending=False, inplace=True)
            for rec in df_test.itertuples():
                if rec.Quantity < -r.Quantity:
                    continue
                qty_cancelled.at[rec.Index] = -r.Quantity
                break
    return qty_cancelled


def highlight_max(s, props=''):
    return np.where(s == np.nanmax(s.values), props, '')