import polars as pl

def file_format(
        df,
        workbook: str='output.xlsx',
        worksheet: str='Sheet1',
        **kwargs
        ):
    """
    Apply formatting to an Excel file using Polars and XlsxWriter.
    
    :param df: The pandas DataFrame to be written to Excel.
    :param workbook: The name of the Excel file to create.
    :param worksheet: The name of the worksheet within the Excel file.
    :param kwargs: Additional keyword arguments for formatting options.
    """
    pl_df = pl.DataFrame(df)

    # Set default table style
    if "table_style" not in kwargs:
        kwargs["table_style"] = "Table Style Medium9"

    pl_df.write_excel(
        workbook=workbook,
        worksheet=worksheet,
        **kwargs
    )