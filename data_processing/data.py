import pandas as pd

def load_data():
    ftx_recovery_model_xlsx = pd.read_excel('FTX Public Overview.xlsx', sheet_name=None, header=0, index_col=0)

    # Read Excel sheets into DataFrames
    cash_df = ftx_recovery_model_xlsx['Cash']
    assets_df = ftx_recovery_model_xlsx['Assets']
    liabilities_df = ftx_recovery_model_xlsx['Liabilities']

    ftx_intl_crypto_df = ftx_recovery_model_xlsx['FTX International Crypto']
    ftx_us_crypto_df = ftx_recovery_model_xlsx['FTX US Crypto']
    ftx_international_related_party_df = ftx_recovery_model_xlsx['FTX International Related Party']
    ftx_us_related_party_df = ftx_recovery_model_xlsx['FTX US Related Party']

    dataframes = {
        "cash_df": cash_df,
        "assets_df": assets_df,
        "liabilities_df": liabilities_df,
        "ftx_intl_crypto_df": ftx_intl_crypto_df,
        "ftx_us_crypto_df": ftx_us_crypto_df,
        "ftx_international_related_party_df": ftx_international_related_party_df,
        "ftx_us_related_party_df": ftx_us_related_party_df
    }

    return dataframes