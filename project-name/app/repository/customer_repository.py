from app.core.sqldbconnection import sql_connection
from app.models.db_models import CustomerDBModel
from app.models.request_models import CustomerCreateRequest, CustomerUpdateRequest


class CustomerRepository:
    def __init__(self) -> None:
        self._ensure_table()

    @staticmethod
    def get_connection():
        return sql_connection()

    def _ensure_table(self) -> None:
        with self.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                IF NOT EXISTS (
                    SELECT 1
                    FROM sys.tables
                    WHERE name = 'Customers'
                )
                BEGIN
                    CREATE TABLE Customers (
                        Id INT IDENTITY(1,1) PRIMARY KEY,
                        FirstName NVARCHAR(100) NOT NULL,
                        LastName NVARCHAR(100) NOT NULL,
                        Email NVARCHAR(255) NOT NULL,
                        Phone NVARCHAR(30) NULL,
                        CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
                        UpdatedAt DATETIME2 NULL
                    )
                END
                """
            )
            connection.commit()

    async def create(self, payload: CustomerCreateRequest) -> CustomerDBModel:
        with self.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO Customers (FirstName, LastName, Email, Phone)
                OUTPUT INSERTED.Id, INSERTED.FirstName, INSERTED.LastName, INSERTED.Email,
                       INSERTED.Phone, INSERTED.CreatedAt, INSERTED.UpdatedAt
                VALUES (?, ?, ?, ?)
                """,
                payload.first_name,
                payload.last_name,
                payload.email,
                payload.phone,
            )
            row = cursor.fetchone()
            connection.commit()
            return self._map_row(row)

    async def get_by_id(self, customer_id: int) -> CustomerDBModel | None:
        with self.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT Id, FirstName, LastName, Email, Phone, CreatedAt, UpdatedAt
                FROM Customers
                WHERE Id = ?
                """,
                customer_id,
            )
            row = cursor.fetchone()
            return self._map_row(row) if row else None

    async def list_all(self) -> list[CustomerDBModel]:
        with self.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT Id, FirstName, LastName, Email, Phone, CreatedAt, UpdatedAt
                FROM Customers
                ORDER BY Id DESC
                """
            )
            return [self._map_row(row) for row in cursor.fetchall()]

    async def update(self, customer_id: int, payload: CustomerUpdateRequest) -> CustomerDBModel | None:
        existing = await self.get_by_id(customer_id)
        if existing is None:
            return None

        first_name = payload.first_name if payload.first_name is not None else existing.first_name
        last_name = payload.last_name if payload.last_name is not None else existing.last_name
        email = payload.email if payload.email is not None else existing.email
        phone = payload.phone if payload.phone is not None else existing.phone

        with self.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE Customers
                SET FirstName = ?,
                    LastName = ?,
                    Email = ?,
                    Phone = ?,
                    UpdatedAt = SYSUTCDATETIME()
                OUTPUT INSERTED.Id, INSERTED.FirstName, INSERTED.LastName, INSERTED.Email,
                       INSERTED.Phone, INSERTED.CreatedAt, INSERTED.UpdatedAt
                WHERE Id = ?
                """,
                first_name,
                last_name,
                email,
                phone,
                customer_id,
            )
            row = cursor.fetchone()
            connection.commit()
            return self._map_row(row) if row else None

    async def delete(self, customer_id: int) -> bool:
        with self.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM Customers WHERE Id = ?", customer_id)
            deleted = cursor.rowcount > 0
            connection.commit()
            return deleted

    @staticmethod
    def _map_row(row) -> CustomerDBModel:
        return CustomerDBModel(
            id=row.Id,
            first_name=row.FirstName,
            last_name=row.LastName,
            email=row.Email,
            phone=row.Phone,
            created_at=row.CreatedAt,
            updated_at=row.UpdatedAt,
        )
