import psycopg2

conn = psycopg2.connect(
    host='bedrock-pgvector.clu0e4osuz67.ap-south-1.rds.amazonaws.com',
    database='bedrock_db',
    user='postgres',
    password='Hari1234',
    port=5432,
    sslmode='verify-full',
    sslrootcert='./global-bundle.pem'
)

print('Connected successfully!')
conn.close()