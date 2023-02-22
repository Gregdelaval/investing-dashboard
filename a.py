from helpers.data_provider import DataProvier

###Fetching full
#limit queried cols -> arg -> {transaction_type vs acquistion_or_disposition}
#limit queried cols -> arg -> {include price y/n}
#limit queried cols -> arg -> {scale to index y/n}
# r = DataProvier().query( #, acquistion_or_disposition, price, symbol
# 	sql_query='''
# 	SELECT transaction_date, securities_transacted, transaction_type
# 	FROM `pre_dl_company_information`.`insider_transactions_transformed_snapshot`
# 	''',
# 	cache=False,
# )

r = DataProvier().fetch_insider_transactions(
	group_by='transaction_type',
	aggregate_on='volume',
	scale_to_index='S&P 500',
)
# print(r.to_string())
