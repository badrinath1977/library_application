from app.models.db_models import SampleDBModel
from app.models.request_models import SampleRequest
from app.core.sqldbconnection import sql_connection


class SampleRepository:
    @staticmethod
    def get_connection():
        return sql_connection()

    async def create(self, payload: SampleRequest) -> SampleDBModel:
        # Use sql_connection() here for real SQL Server operations.
        # with self.get_connection() as connection:
        #     cursor = connection.cursor()
        #     cursor.execute("...")
        #     connection.commit()
        return SampleDBModel(name=payload.name, description=payload.description)
