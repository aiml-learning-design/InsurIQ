import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

class SnowflakeClient:
    def __init__(self):
        self.conn = snowflake.connector.connect(
            user='INSURIQ_USER',
            password='password',
            account='your_account',
            warehouse='UNDERWRITING_WH',
            database='INSURIQ_DB',
            schema='UNDERWRITING'
        )

    def get_historical_claims(self, lat: float, lon: float, radius_km: float = 5):
        query = f"""
        SELECT * 
        FROM claims_history
        WHERE ST_DISTANCE(
            ST_MAKEPOINT({lon}, {lat}),
            ST_MAKEPOINT(longitude, latitude)
        ) <= {radius_km * 1000}
        ORDER BY claim_date DESC
        LIMIT 100
        """
        return self._execute_query(query)

    def _execute_query(self, query):
        cur = self.conn.cursor()
        try:
            cur.execute(query)
            return cur.fetchall()
        finally:
            cur.close()

    def log_underwriting_decision(self, decision_data):
        df = pd.DataFrame([decision_data])
        write_pandas(self.conn, df, "UNDERWRITING_DECISIONS")

    def __del__(self):
        self.conn.close()