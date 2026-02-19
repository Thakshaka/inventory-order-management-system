"""
Initial database schema migration.

Revision: 0001
Creates: products, orders, order_items tables
         orderstatus enum type
         All FK constraints, indexes, and CheckConstraints

ENUM strategy: use raw SQL `DO $$ ... IF NOT EXISTS` block to create the
PostgreSQL ENUM type. This is 100% idempotent and bypasses SQLAlchemy's
internal CREATE TYPE event hooks that fire on op.create_table(), which
were causing DuplicateObject errors regardless of checkfirst=True.
"""
from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # Create PostgreSQL ENUM type — idempotent raw SQL
    # Using DO block because CREATE TYPE does not support IF NOT EXISTS
    # in PostgreSQL < 14. This works on all supported versions.
    # ------------------------------------------------------------------
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'orderstatus') THEN
                CREATE TYPE orderstatus AS ENUM ('Pending', 'Shipped', 'Cancelled');
            END IF;
        END
        $$;
    """)

    # ------------------------------------------------------------------
    # products table
    # ------------------------------------------------------------------
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("stock_quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "stock_quantity >= 0",
            name="ck_product_stock_non_negative",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_products_name", "products", ["name"])

    # ------------------------------------------------------------------
    # orders table
    # Use sa.Text() for the status column and rely on the ENUM type
    # already created above via raw SQL. This avoids SQLAlchemy firing
    # its own CREATE TYPE event hook during op.create_table().
    # ------------------------------------------------------------------
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "status",
            sa.Text(),
            nullable=False,
            server_default="Pending",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Cast the column to the orderstatus ENUM type after table creation.
    # This is the cleanest way to attach a named ENUM without triggering
    # SQLAlchemy's automatic CREATE TYPE hook.
    op.execute(
        "ALTER TABLE orders ALTER COLUMN status DROP DEFAULT"
    )
    op.execute(
        "ALTER TABLE orders ALTER COLUMN status TYPE orderstatus USING status::orderstatus"
    )
    op.execute(
        "ALTER TABLE orders ALTER COLUMN status SET DEFAULT 'Pending'::orderstatus"
    )
    op.create_index("ix_orders_status", "orders", ["status"])

    # ------------------------------------------------------------------
    # order_items table
    # ------------------------------------------------------------------
    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("price_at_time", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"],
            name="fk_order_items_order_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_order_items_product_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])
    op.create_index("ix_order_items_product_id", "order_items", ["product_id"])


def downgrade() -> None:
    op.drop_index("ix_order_items_product_id", table_name="order_items")
    op.drop_index("ix_order_items_order_id", table_name="order_items")
    op.drop_table("order_items")

    op.drop_index("ix_orders_status", table_name="orders")
    op.drop_table("orders")

    op.drop_index("ix_products_name", table_name="products")
    op.drop_table("products")

    # Drop the enum type last (after all tables referencing it are gone)
    op.execute("DROP TYPE IF EXISTS orderstatus")
