import pandas as pd
import pyarrow.parquet as pq
from sqlalchemy import create_engine
<<<<<<< HEAD
=======
import pymysql

>>>>>>> 6e9210d6302019e745e39c15c6b86ba08d1ea9d4

# Move the parquet files into the database
cnx = create_engine('mysql+pymysql://root:password@localhost:3306/webapp', echo=False)

# ATC_UMLS (side effect)
<<<<<<< HEAD
print("atc_side_effect_result.snappy.parquet")
filename1 = "atc_side_effect_result.snappy.parquet"
table1 = pq.read_table(filename1).to_pandas().to_sql(name='atc_umls', con=cnx, if_exists='append', index=False)

# NDC_ATC
print("ndc_atc_code_only.snappy.parquet")
filename2 = "ndc_atc_code_only.snappy.parquet"
table2 = pq.read_table(filename2).to_pandas().to_sql(name='ndc_atc', con=cnx, if_exists='append', index=False)

# ATC_LABEL
print("atc_label.snappy.parquet")
filename3 = 'atc_label.snappy.parquet'
table3 = pq.read_table(filename3).to_pandas().to_sql(name='atc_label', con=cnx, if_exists='append', index=False)

# UMLS_LABEL
print("umls_label.snappy.parquet")
filename4 = 'umls_label.snappy.parquet'
table4 = pq.read_table(filename4).to_pandas().to_sql(name='umls_label', con=cnx, if_exists='append', index=False)

# NDC_LABEL
print("ndc_label.snappy.parquet")
filename5 = 'ndc_label.snappy.parquet'
table5 = pq.read_table(filename5).to_pandas().to_sql(name='ndc_label', con=cnx, if_exists='append', index=False)

# ATC_INDEX
print("atc_index.csv")
filename6 = 'atc_index.csv'
table6 = pd.read_csv(filename6)
table6.to_sql(name='atc_index', con=cnx, if_exists='append', index=False)

# Freq_side
print("freq_side.snappy.parquet")
filename7 = 'freq_side.snappy.parquet'
table7 = pq.read_table(filename7).to_pandas().to_sql(name='freq_side', con=cnx, if_exists='append', index=False)
=======
# filename1 = "atc_side_effect_result.snappy.parquet"
# table1 = pq.read_table(filename1).to_pandas().to_sql(name='atc_umls', con=cnx, if_exists='append', index=False)
# table1 = pq.read_table(filename1).to_pandas().to_csv('atc_umls.csv', index=False)

# # NDC_ATC
# filename2 = "ndc_atc_code_only.snappy.parquet"
# table2 = pq.read_table(filename2).to_pandas().to_sql(name='ndc_atc', con=cnx, if_exists='append', index=False)
#
# # NDC_UMLS
# filename3 = "ndc_side_effect_result.snappy.parquet"
# table3 = pq.read_table(filename3).to_pandas().to_sql(name='ndc_umls', con=cnx, if_exists='append', index=False)
# table3 = pq.read_table(filename3).to_pandas().to_csv('ndc_umls.csv', index=False)

# # ATC_LABEL
# filename4 = 'atc_label.snappy.parquet'
# table4 = pq.read_table(filename4).to_pandas().to_sql(name='atc_label', con=cnx, if_exists='append', index=False)

# UMLS_LABEL
# filename5 = 'umls_label.snappy.parquet'
# table5 = pq.read_table(filename5).to_pandas().to_sql(name='umls_label', con=cnx, if_exists='append', index=False)
#
# # # NDC_LABEL
# filename6 = 'ndc_label.snappy.parquet'
# table6 = pq.read_table(filename6).to_pandas().to_sql(name='ndc_label', con=cnx, if_exists='append', index=False)

## ATC_INDEX
# filename7 = 'atc_index.csv'
# table7 = pd.read_csv(filename7)
# table7.to_sql(name='atc_index', con=cnx, if_exists='append', index=False)

filename8 = 'freq_side.snappy.parquet'
table8 = pq.read_table(filename8).to_pandas().to_sql(name='freq_side', con=cnx, if_exists='append', index=False)
>>>>>>> 6e9210d6302019e745e39c15c6b86ba08d1ea9d4
