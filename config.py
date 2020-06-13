#psql --host=zheyu-database-airbnb.cu2ky11rrces.us-east-2.rds.amazonaws.com --port=5432 --username=postgres --password --dbname=postgres


class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE = {
        'drivername': 'postgres',
        'host': 'localhost',
        'port': '5432',
        'username': 'zheyu',
        'password': 'zheyuliu',
        'database': 'airbnb'
    }
    yelp_api_client = "1Z7pW-aaIky9FFBlnexA5Q"
    yelp_api_key = "ZmEj9steQ0PDgTjOAg1KFjrvJXFvluGl78ZwYJQ0M1WUC-M_Rbr8i_xti1FmUw8Mrfx3S7QunOzaXBf-wJVmf_gLFX2rS3z0tFePZyNw5Fi9DINayM5TOSVcVdniXnYx"


class ProductionConfig(Config):
    DATABASE = {
        'drivername': 'postgres',
        'host': 'zheyu-database-airbnb.cu2ky11rrces.us-east-2.rds.amazonaws.com',
        'port': '5432',
        'username': 'zheyu',
        'password': 'zheyuliu',
        'database': 'airbnb'
    }


class DevelopmentConfig(Config):
    DEBUG = True