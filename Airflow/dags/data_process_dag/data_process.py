from datetime import timedelta
import datetime as dt
import boto3
import pandas as pd  
import os 
import numpy as np
import keyring
from airflow import DAG 
from airflow.operators.python import PythonOperator
from sqlalchemy import create_engine

dag_path = os.getcwd() 

def data_process():
    engine = create_engine(keyring.get_password("aws", "database"))

    dataframe_list = []
    names_list = []
    dict={}

    #Conection to amazon S3
    s3 = boto3.Session(
        aws_access_key_id=keyring.get_password("aws", "access key"),
        aws_secret_access_key=keyring.get_password("aws", "secret key"),)
    s3_resource = s3.resource('s3')

    #Creation of the Audit table
    if not engine.has_table("Audit"):
        engine.execute('''CREATE TABLE Audit (
        timestamp TIMESTAMP DEFAULT NOW(),
        table_name VARCHAR(50),
        last_modified_dataset VARCHAR(50),
        new_rows VARCHAR(50),
        rows_range VARCHAR(50),
        detail VARCHAR(50)
        )''')

    #Load of all datasets from S3, removing duplicated and empty rows

    #First the dataset last modified date is check to see if there is a new modification
    csv_obj = s3_resource.Object("p-raw-datasets", "Datasets_original/olist_closed_deals_dataset.csv")
    last_modified_dataset = csv_obj.last_modified.strftime('%Y-%m-%d %H:%M:%S')

    #If the table already exist and the last modified date is diferent to the one in the Audit table in the database the new dataset is upload
    if engine.has_table("Closed_deals") == True:
        sql_query = f"SELECT * FROM Audit WHERE table_name='Closed_deals' AND last_modified_dataset='{last_modified_dataset}'"
        df_query = pd.read_sql(sql_query, con=engine)
        if df_query.empty == True:
            Closed_deals = pd.read_csv(csv_obj.get()['Body'])
            Closed_deals.drop_duplicates(inplace=True)
            #The column dtype is change to prevent a future error when comparing with the table in the database
            Closed_deals['has_gtin'] = Closed_deals['has_gtin'].astype('float64')
            Closed_deals['has_company'] = Closed_deals['has_company'].astype('float64')
            
            #The last modified date is saved for later inserting into Audit table
            dict["Closed_deals"]=last_modified_dataset      
            
            #The table name and the dataframe is add to a list that will be use to upload the data to the database
            dataframe_list.append(Closed_deals)
            names_list.append("Closed_deals")
    #if the table doesn´t exist then the dataset is loaded
    else:
        Closed_deals = pd.read_csv(csv_obj.get()['Body'])
        Closed_deals.drop_duplicates(inplace=True)

        Closed_deals['has_gtin'] = Closed_deals['has_gtin'].astype('float64')
        Closed_deals['has_company'] = Closed_deals['has_company'].astype('float64')
        
        dataframe_list.append(Closed_deals)
        names_list.append("Closed_deals")
        dict["Closed_deals"]=last_modified_dataset  
        
        
    csv_obj = s3_resource.Object("p-raw-datasets", "Datasets_original/olist_customers_dataset.csv")
    last_modified_dataset = csv_obj.last_modified.strftime('%Y-%m-%d %H:%M:%S')
    if engine.has_table("Customers") == True:
        sql_query = f"SELECT * FROM Audit WHERE table_name='Customers' AND last_modified_dataset='{last_modified_dataset}'"
        df_query = pd.read_sql(sql_query, con=engine)
        if df_query.empty == True:
            Customers = pd.read_csv(csv_obj.get()['Body'])
            Customers.drop_duplicates(inplace=True)
            dataframe_list.append(Customers)
            names_list.append("Customers")
            dict["Customers"]=last_modified_dataset
    else:
        Customers = pd.read_csv(csv_obj.get()['Body'])
        Customers.drop_duplicates(inplace=True)
        dataframe_list.append(Customers)
        names_list.append("Customers")
        dict["Customers"]=last_modified_dataset  
    
    csv_obj = s3_resource.Object("p-raw-datasets", "Datasets_original/olist_geolocation_dataset.csv")
    last_modified_dataset = csv_obj.last_modified.strftime('%Y-%m-%d %H:%M:%S')
    if engine.has_table("Geolocation") == True:
        sql_query = f"SELECT * FROM Audit WHERE table_name='Geolocation' AND last_modified_dataset='{last_modified_dataset}'"
        df_query = pd.read_sql(sql_query, con=engine)
        if df_query.empty == True:
            Geolocation = pd.read_csv(csv_obj.get()['Body'])
            Geolocation.drop_duplicates(inplace=True)
            dataframe_list.append(Geolocation)
            names_list.append("Geolocation")
            dict["Geolocation"]=last_modified_dataset  
    else:
        Geolocation = pd.read_csv(csv_obj.get()['Body'])
        Geolocation.drop_duplicates(inplace=True)
        dataframe_list.append(Geolocation)
        names_list.append("Geolocation")
        dict["Geolocation"]=last_modified_dataset  


    csv_obj = s3_resource.Object("p-raw-datasets", "Datasets_original/olist_marketing_qualified_leads_dataset.csv")
    last_modified_dataset = csv_obj.last_modified.strftime('%Y-%m-%d %H:%M:%S')
    if engine.has_table("Marketing") == True:
        sql_query = f"SELECT * FROM Audit WHERE table_name='Marketing' AND last_modified_dataset='{last_modified_dataset}'"
        df_query = pd.read_sql(sql_query, con=engine)
        if df_query.empty == True:
            Marketing = pd.read_csv(csv_obj.get()['Body'])
            Marketing.drop_duplicates(inplace=True)
            dataframe_list.append(Marketing)
            names_list.append("Marketing")
            dict["Marketing"]=last_modified_dataset  
    else:
        Marketing = pd.read_csv(csv_obj.get()['Body'])
        Marketing.drop_duplicates(inplace=True)
        dataframe_list.append(Marketing)
        names_list.append("Marketing")
        dict["Marketing"]=last_modified_dataset  

    csv_obj = s3_resource.Object("p-raw-datasets", "Datasets_original/olist_order_items_dataset.csv")
    last_modified_dataset = csv_obj.last_modified.strftime('%Y-%m-%d %H:%M:%S')
    if engine.has_table("Order_items") == True:
        sql_query = f"SELECT * FROM Audit WHERE table_name='Order_items' AND last_modified_dataset='{last_modified_dataset}'"
        df_query = pd.read_sql(sql_query, con=engine)
        if df_query.empty == True:
            Order_items = pd.read_csv(csv_obj.get()['Body'])
            Order_items.drop_duplicates(inplace=True)
            dataframe_list.append(Order_items)
            names_list.append("Order_items")
            dict["Order_items"]=last_modified_dataset  
        else:
            Order_items = pd.read_sql("select * from Order_items", con=engine)
            Order_items = Order_items.drop(columns=['surrogate_key'])
    else:
        Order_items = pd.read_csv(csv_obj.get()['Body'])
        Order_items.drop_duplicates(inplace=True)
        dataframe_list.append(Order_items)
        names_list.append("Order_items")
        dict["Order_items"]=last_modified_dataset 
        
    csv_obj = s3_resource.Object("p-raw-datasets", "Datasets_original/olist_order_payments_dataset.csv")
    last_modified_dataset = csv_obj.last_modified.strftime('%Y-%m-%d %H:%M:%S')
    if engine.has_table("Order_payments") == True:
        sql_query = f"SELECT * FROM Audit WHERE table_name='Order_payments' AND last_modified_dataset='{last_modified_dataset}'"
        df_query = pd.read_sql(sql_query, con=engine)
        if df_query.empty == True:
            Order_payments = pd.read_csv(csv_obj.get()['Body'])
            Order_payments.drop_duplicates(inplace=True)
            dataframe_list.append(Order_payments)
            names_list.append("Order_payments")
            dict["Order_payments"]=last_modified_dataset  
        else:
            Order_payments = pd.read_sql("select * from Order_payments", con=engine)
            Order_payments = Order_payments.drop(columns=['surrogate_key'])  
    else:
        Order_payments = pd.read_csv(csv_obj.get()['Body'])
        Order_payments.drop_duplicates(inplace=True)
        dataframe_list.append(Order_payments)
        names_list.append("Order_payments")
        dict["Order_payments"]=last_modified_dataset 

    csv_obj = s3_resource.Object("p-raw-datasets", "Datasets_original/olist_order_reviews_dataset.csv")
    last_modified_dataset = csv_obj.last_modified.strftime('%Y-%m-%d %H:%M:%S')
    if engine.has_table("Order_reviews") == True:
        sql_query = f"SELECT * FROM Audit WHERE table_name='Order_reviews' AND last_modified_dataset='{last_modified_dataset}'"
        df_query = pd.read_sql(sql_query, con=engine)
        if df_query.empty == True:
            Order_reviews = pd.read_csv(csv_obj.get()['Body'])
            Order_reviews.drop_duplicates(inplace=True)
            dataframe_list.append(Order_reviews)
            names_list.append("Order_reviews")
            dict["Order_reviews"]=last_modified_dataset  
        else:
            Order_reviews = pd.read_sql("select * from Order_reviews", con=engine)
            Order_reviews = Order_reviews.drop(columns=['surrogate_key'])
    else:
        Order_reviews = pd.read_csv(csv_obj.get()['Body'])
        Order_reviews.drop_duplicates(inplace=True)
        dataframe_list.append(Order_reviews)
        names_list.append("Order_reviews")
        dict["Order_reviews"]=last_modified_dataset 
            
            
    csv_obj = s3_resource.Object("p-raw-datasets", "Datasets_original/olist_sellers_dataset.csv")
    last_modified_dataset = csv_obj.last_modified.strftime('%Y-%m-%d %H:%M:%S')
    if engine.has_table("Sellers") == True:
        sql_query = f"SELECT * FROM Audit WHERE table_name='Sellers' AND last_modified_dataset='{last_modified_dataset}'"
        df_query = pd.read_sql(sql_query, con=engine)
        if df_query.empty == True:
            Sellers = pd.read_csv(csv_obj.get()['Body'])
            Sellers.drop_duplicates(inplace=True)
            dataframe_list.append(Sellers)
            names_list.append("Sellers")
            dict["Sellers"]=last_modified_dataset 
        else:
            Sellers = pd.read_sql("select * from Sellers", con=engine) 
            Sellers = Sellers.drop(columns=['surrogate_key'])        
    else:
        Sellers = pd.read_csv(csv_obj.get()['Body'])
        Sellers.drop_duplicates(inplace=True)
        dataframe_list.append(Sellers)
        names_list.append("Sellers")
        dict["Sellers"]=last_modified_dataset   
        
        
    csv_obj = s3_resource.Object("p-raw-datasets", "Datasets_original/olist_products_dataset.csv")
    last_modified_dataset = csv_obj.last_modified.strftime('%Y-%m-%d %H:%M:%S')
    if engine.has_table("Products") == True:
        sql_query = f"SELECT * FROM Audit WHERE table_name='Products' AND last_modified_dataset='{last_modified_dataset}'"
        df_query = pd.read_sql(sql_query, con=engine)
        if df_query.empty == True:
            Products = pd.read_csv(csv_obj.get()['Body'])
            Products.drop_duplicates(inplace=True)
            dataframe_list.append(Products)
            names_list.append("Products")
            dict["Products"]=last_modified_dataset  
        else:
            Products = pd.read_sql("select * from Products", con=engine)
            Products = Products.drop(columns=['surrogate_key'])
    else:
        Products = pd.read_csv(csv_obj.get()['Body'])
        Products.drop_duplicates(inplace=True)
        dataframe_list.append(Products)
        names_list.append("Products")
        dict["Products"]=last_modified_dataset  

    csv_obj = s3_resource.Object("p-raw-datasets", "Datasets_original/olist_orders_dataset.csv")
    last_modified_dataset = csv_obj.last_modified.strftime('%Y-%m-%d %H:%M:%S')
    if engine.has_table("Orders") == True:
        sql_query = f"SELECT * FROM Audit WHERE table_name='Orders' AND last_modified_dataset='{last_modified_dataset}'"
        df_query = pd.read_sql(sql_query, con=engine)
        if df_query.empty == True:
            Orders = pd.read_csv(csv_obj.get()['Body'])
            Orders.drop_duplicates(inplace=True)
            dataframe_list.append(Orders)
            names_list.append("Orders")
            dict["Orders"]=last_modified_dataset  
        else:
            Orders = pd.read_sql("select * from Orders", con=engine)
            Orders = Orders.drop(columns=['surrogate_key'])
    else:
        Orders = pd.read_csv(csv_obj.get()['Body'])
        Orders.drop_duplicates(inplace=True)
        dataframe_list.append(Orders)
        names_list.append("Orders")
        dict["Orders"]=last_modified_dataset 
            
    if len(names_list)>0:
        if any([n in names_list for n in ["Order_items", "Order_payments", "Order_reviews", "Sellers", "Products", "Orders"]]):
            #In the dataframe Orders a new column is added and calculated
            Orders['delivery_time'] = pd.to_datetime(Orders["order_approved_at"].dropna(),errors='coerce') - pd.to_datetime(Orders['order_delivered_customer_date'].dropna(),errors='coerce')
            Orders['delivery_time'] = -(Orders['delivery_time'].apply(lambda x: x.days + (x.seconds // 86400)))
            
            #Combination of the dataframes to create a new table
            datasets_combinados=Orders.merge(Order_reviews,on="order_id")
            datasets_combinados=datasets_combinados.merge(Order_payments,on="order_id")
            datasets_combinados=datasets_combinados.merge(Order_items,on="order_id")
            datasets_combinados=datasets_combinados.merge(Sellers,on="seller_id")
            datasets_combinados=datasets_combinados.merge(Products,on="product_id")

            #Adding column avg_price_month
            datasets_combinados["Month"] = pd.DatetimeIndex(datasets_combinados["order_approved_at"]).month
            datasets_combinados["Year"] = pd.DatetimeIndex(datasets_combinados["order_approved_at"]).year
            datasets_combinados['avg_income_month'] = datasets_combinados.groupby(['seller_id','Month',"Year"])['payment_value'].transform('mean')

            Evaluation = pd.DataFrame(columns=['seller_id'])
            Evaluation.seller_id = datasets_combinados.seller_id.unique()

            #Merge of all necesary columns by seller_id column.
            Evaluation = Evaluation.merge(datasets_combinados[['seller_id', 'seller_state']].groupby(['seller_id']).max(), on= 'seller_id')
            Evaluation = Evaluation.merge(datasets_combinados[['seller_id', 'seller_city']].groupby(['seller_id']).max(), on= 'seller_id')
            Evaluation = Evaluation.merge(datasets_combinados[['seller_id', 'product_id']].groupby(['seller_id']).count(), on= 'seller_id')
            Evaluation = Evaluation.merge(datasets_combinados[['seller_id', 'product_category_name']].groupby(['seller_id']).nunique(), on= 'seller_id')
            Evaluation = Evaluation.merge(datasets_combinados[['seller_id', 'delivery_time']].groupby(['seller_id']).mean().round(2), on= 'seller_id')
            Evaluation = Evaluation.merge(datasets_combinados[['seller_id', 'review_score']].groupby(['seller_id']).mean().round(2), on= 'seller_id')
            Evaluation = Evaluation.merge(datasets_combinados[['seller_id', 'order_id']].groupby(['seller_id']).count(), on= 'seller_id')
            Evaluation = Evaluation.merge(datasets_combinados[['seller_id', 'payment_value']].groupby(['seller_id']).sum(), on= 'seller_id')
            Evaluation = Evaluation.merge(datasets_combinados[['seller_id', 'avg_income_month']].groupby("seller_id").mean().reset_index().round(2), on= 'seller_id')
         
            Evaluation.drop_duplicates(inplace=True)

            #Rename of columns
            Evaluation.rename({'product_id':'distinct_prod', 'delivery_time':'delivery_avg', 'product_category_name':'distinct_categories',\
                        'review_score':'review_avg', 'order_id':'total_orders', 'payment_value':'total_income'}, axis=1, inplace=True)
            
            
            Evaluation= Evaluation[(Evaluation["delivery_avg"]<50)]
            
            #sort table by income
            Evaluation.sort_values("total_income", axis=0, ascending=True,inplace=True, na_position='first')
            Evaluation.replace('NaN', np.nan)
            
            #drop 125 rows with null values
            Evaluation = Evaluation.dropna()
            index=int(len(Evaluation)/4)
            df_low = Evaluation.iloc[0:index]
            df_mid_low = Evaluation.iloc[index:index*2]
            df_mid_high = Evaluation.iloc[index*2:index*3]
            df_high = Evaluation.iloc[index*3:len(Evaluation)]

            df_high.sort_values("total_income", axis=0, ascending=True,inplace=True, na_position='first')
            
            #split tier 4 into 4 sub-tiers
            index=int(len(df_high)/4)
            tier_1d = df_high.iloc[0:index]
            tier_1c = df_high.iloc[index:index*2]
            tier_1b = df_high.iloc[index*2:index*3]
            tier_1a = df_high.iloc[index*3:len(df_high)]
            
            df_low['tier'] = "4"
            df_mid_low['tier'] = '3'
            df_mid_high['tier'] = '2'
            tier_1d['tier'] = '1d'
            tier_1c['tier'] = '1c'
            tier_1b['tier'] = '1b'
            tier_1a ['tier'] = '1a'
            
            #This function recieves a dataframe and name of column to be extracted as parameter, returns list of values adjusted to curve
            def get_curve (df, column):
                list = df[column].values.tolist()
                normalized_list = []
                max_value = max(list)
                min_value = min(list)
                for i in list:
                    x = ((i - min_value)/(max_value - min_value) * 10)
                    normalized_list.append(x)
                
                return normalized_list  

            def get_curve2 (df, column):
                list = df[column].values.tolist()
                normalized_list = []
                max_value = max(list)
                min_value = min(list)
                for i in list:
                    x = ((i - max_value)/(max_value - min_value) * 10)*-1
                    normalized_list.append(x)
                
                return normalized_list  

            
            #Add income KPI as new column
            df_low['total_income_kpi'] = get_curve (df_low, 'total_income')
            df_mid_low['total_income_kpi'] = get_curve(df_mid_low, 'total_income')
            df_mid_high['total_income_kpi'] = get_curve(df_mid_high, "total_income")
            tier_1d['total_income_kpi'] = get_curve(tier_1d, 'total_income')
            tier_1c['total_income_kpi'] =  get_curve(tier_1c,'total_income')
            tier_1b['total_income_kpi'] = get_curve(tier_1b, 'total_income')
            tier_1a['total_income_kpi'] = get_curve(tier_1a, 'total_income')
            
            #Extract delivery average KPI 
            df_low['delivery_avg_kpi'] = get_curve2(df_low, 'delivery_avg')
            df_mid_low['delivery_avg_kpi'] = get_curve2(df_mid_low, 'delivery_avg')
            df_mid_high['delivery_avg_kpi'] = get_curve2(df_mid_high, "delivery_avg")
            tier_1d['delivery_avg_kpi'] = get_curve2(tier_1d, 'delivery_avg')
            tier_1c['delivery_avg_kpi'] =  get_curve2(tier_1c,'delivery_avg')
            tier_1b['delivery_avg_kpi'] = get_curve2(tier_1b, 'delivery_avg')
            tier_1a['delivery_avg_kpi'] = get_curve2(tier_1a, 'delivery_avg')
            
            #Extract review average KPI 
            df_low['review_avg_kpi'] = get_curve (df_low, 'review_avg')
            df_mid_low['review_avg_kpi'] = get_curve(df_mid_low, 'review_avg')
            df_mid_high['review_avg_kpi'] = get_curve(df_mid_high, "review_avg")
            tier_1d['review_avg_kpi'] = get_curve(tier_1d, 'review_avg')
            tier_1c['review_avg_kpi'] =  get_curve(tier_1c,'review_avg')
            tier_1b['review_avg_kpi'] = get_curve(tier_1b, 'review_avg')
            tier_1a['review_avg_kpi'] = get_curve(tier_1a, 'review_avg')
            
            df_high = pd.concat([tier_1a, tier_1b, tier_1c, tier_1d])
            
            Evaluation = pd.concat([df_low, df_mid_low, df_mid_high, df_high], axis=0)
                                     
            Evaluation['performance_kpi'] = Evaluation[['total_income_kpi', 'review_avg_kpi', 'delivery_avg_kpi']].mean(axis=1)

            dataframe_list.append(Evaluation)
            names_list.append("Evaluation")
            dict["Evaluation"]=dt.datetime.now().replace(microsecond=0) - timedelta(hours=3)
            
        #Upload only the new rows of each dataset to the database and only of the datasets that have changes
        for n,i in enumerate(dataframe_list):
            if engine.has_table(names_list[n]) == True:
                old_data = pd.read_sql(f"select * from {names_list[n]}", con=engine)
                old_data = old_data.drop(columns=['surrogate_key'])

                data_merged = pd.merge(i, old_data, how='left', indicator=True)
                data_appended = data_merged[data_merged['_merge'] == 'left_only']
                data_appended = data_appended.drop(columns=['_merge'])


                data_appended.to_sql(names_list[n], con=engine, if_exists='append', index=False, chunksize=1000)
                timestamp= dt.datetime.now()- timedelta(hours=3)
                
                if not data_appended.empty:
                    range_rows = f"{old_data.tail(1).index.values[0] + 1} - {data_appended.tail(1).index.values[0]}"
                    new_rows = len(i) - len(old_data)
                else:
                    range_rows = 0
                    new_rows = 0
                    
                engine.execute('''INSERT INTO Audit (timestamp, table_name, last_modified_dataset, new_rows, rows_range, detail) 
                                VALUES (%s,%s,%s,%s,%s,"Adding new data to table")''', (timestamp, names_list[n],dict[names_list[n]],new_rows,range_rows))
            else:
                i.to_sql(names_list[n], con=engine, index=False , chunksize=1000)
                new_rows= len(i)
                range_rows = f"0 - {new_rows -1}"
                timestamp= dt.datetime.now() - timedelta(hours=3)
                engine.execute('''INSERT INTO Audit (timestamp, table_name, last_modified_dataset, new_rows, rows_range, detail) 
                                VALUES (%s,%s,%s,%s,%s,"Creation of table and data load")''', (timestamp, names_list[n],dict[names_list[n]],new_rows,range_rows))
            
        print("Data succesfully loaded to database")
    else:
        print("No changes detected in the datasets")

def relations_tables():
    engine = create_engine(keyring.get_password("aws", "database"))
    tables = ["Order_items", "Order_payments", "Order_reviews", "Orders", "Sellers", "Closed_deals", "Evaluation", "Customers", "Products"]
    
    if not engine.has_table("surrogate_keys"):
        engine.execute("""CREATE TABLE surrogate_keys (
        id INT AUTO_INCREMENT PRIMARY KEY,
        original_value VARCHAR(255) UNIQUE
        )""")
    else:
        for table in tables:
            engine.execute(f"ALTER TABLE {table} DROP FOREIGN KEY {table}_ibfk_1")
            engine.execute(f"ALTER TABLE {table} DROP COLUMN surrogate_key")
        engine.execute("TRUNCATE TABLE surrogate_keys")

    engine.execute("""INSERT INTO surrogate_keys (original_value)
    SELECT DISTINCT order_id FROM Order_items
    WHERE NOT EXISTS (SELECT 1 FROM surrogate_keys WHERE original_value = order_id)
    UNION
    SELECT DISTINCT order_id FROM Order_payments
    WHERE NOT EXISTS (SELECT 1 FROM surrogate_keys WHERE original_value = order_id)
    UNION
    SELECT DISTINCT order_id FROM Order_reviews
    WHERE NOT EXISTS (SELECT 1 FROM surrogate_keys WHERE original_value = order_id)
    UNION
    SELECT DISTINCT order_id FROM Orders
    WHERE NOT EXISTS (SELECT 1 FROM surrogate_keys WHERE original_value = order_id)
    UNION
    SELECT DISTINCT seller_id FROM Sellers
    WHERE NOT EXISTS (SELECT 1 FROM surrogate_keys WHERE original_value = seller_id)
    UNION
    SELECT DISTINCT seller_id FROM Closed_deals
    WHERE NOT EXISTS (SELECT 1 FROM surrogate_keys WHERE original_value = seller_id)
    UNION
    SELECT DISTINCT seller_id FROM Evaluation
    WHERE NOT EXISTS (SELECT 1 FROM surrogate_keys WHERE original_value = seller_id)
    UNION
    SELECT DISTINCT customer_id FROM Customers
    WHERE NOT EXISTS (SELECT 1 FROM surrogate_keys WHERE original_value = customer_id)
    UNION
    SELECT DISTINCT product_id FROM Products
    WHERE NOT EXISTS (SELECT 1 FROM surrogate_keys WHERE original_value = product_id)""")
    
    for table in tables:
        engine.execute(f"ALTER TABLE {table} ADD COLUMN surrogate_key INT;")
    
    engine.execute("UPDATE Order_items SET surrogate_key = (SELECT id FROM surrogate_keys WHERE original_value = order_id)")
    engine.execute("UPDATE Order_payments SET surrogate_key = (SELECT id FROM surrogate_keys WHERE original_value = order_id)")
    engine.execute("UPDATE Order_reviews SET surrogate_key = (SELECT id FROM surrogate_keys WHERE original_value = order_id)")
    engine.execute("UPDATE Orders SET surrogate_key = (SELECT id FROM surrogate_keys WHERE original_value = order_id)")
    engine.execute("UPDATE Sellers SET surrogate_key = (SELECT id FROM surrogate_keys WHERE original_value = seller_id)")
    engine.execute("UPDATE Closed_deals SET surrogate_key = (SELECT id FROM surrogate_keys WHERE original_value = seller_id)")
    engine.execute("UPDATE Evaluation SET surrogate_key = (SELECT id FROM surrogate_keys WHERE original_value = seller_id)")
    engine.execute("UPDATE Customers SET surrogate_key = (SELECT id FROM surrogate_keys WHERE original_value = customer_id)")
    engine.execute("UPDATE Products SET surrogate_key = (SELECT id FROM surrogate_keys WHERE original_value = product_id)")
    
    for table in tables:
        engine.execute(f"""ALTER TABLE {table}
        ADD FOREIGN KEY (surrogate_key) REFERENCES surrogate_keys (id);""")
                      
    
data_process_dag = DAG(
    dag_id='data_process',
    start_date=dt.datetime.today(),
    schedule_interval=timedelta(days=1),
    catchup=False)
    
task1 = PythonOperator(
task_id="Data_process",
python_callable=data_process,
dag=data_process_dag)

task2 = PythonOperator(
task_id="relate_tables",
python_callable=relations_tables,
dag=data_process_dag)

task1 >> task2