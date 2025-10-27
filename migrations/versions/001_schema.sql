-- Migration: 001_schema
-- Description: Initial database schema

BEGIN;

-- 1.2 - каталог номенклатуры/дерево категорий
CREATE TABLE categories (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    parent_id BIGINT REFERENCES categories(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 1.1 номенклатура
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    quantity INT NOT NULL CHECK (quantity >= 0),
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    category_id BIGINT REFERENCES categories(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 1.3 - клиенты
CREATE TABLE clients (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 1.4 - заказы
CREATE TABLE orders(
    id BIGSERIAL PRIMARY KEY,
    client_id BIGINT REFERENCES clients(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP NULL
);

CREATE TABLE order_items (
    order_id BIGINT REFERENCES orders(id) ON DELETE CASCADE,
    product_id BIGINT REFERENCES products(id),
    quantity INT NOT NULL CHECK (quantity > 0),
    PRIMARY KEY(order_id, product_id)
);

-- Таблица для отслеживания миграций
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(50) PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Представление для корневых категорий продуктов
CREATE MATERIALIZED VIEW product_top_level_categories AS
WITH RECURSIVE category_path AS (
    SELECT 
        id, name, 
        id as top_level_category_id, 
        name as top_level_category_name
    FROM categories
    WHERE categories.parent_id is NULL

    UNION ALL
    SELECT 
        c.id, 
        c.name, 
        cp.top_level_category_id, 
        cp.top_level_category_name
    FROM categories c
    JOIN category_path cp ON c.parent_id = cp.id
)
SELECT 
    p.id as product_id,
    p.name as product_name,
    cp.top_level_category_id,
    cp.top_level_category_name
FROM products p
JOIN category_path cp ON p.category_id = cp.id;

-- Материализованное представление для топ-5 товаров
CREATE MATERIALIZED VIEW top_five_sold_last_month AS
SELECT
    ptlc.product_name,
    ptlc.top_level_category_name,
    SUM(i.quantity) AS total_sold
FROM order_items i
JOIN orders o ON i.order_id = o.id
JOIN product_top_level_categories ptlc ON i.product_id = ptlc.product_id
WHERE 
    o.created_at >= date_trunc('month', CURRENT_DATE - INTERVAL '1 month')
    AND o.created_at < date_trunc('month', CURRENT_DATE)
GROUP BY ptlc.product_id, ptlc.product_name, ptlc.top_level_category_name
ORDER BY total_sold DESC
LIMIT 5;

CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_categories_parent_id ON categories(parent_id);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_categories_name ON categories(name);
CREATE INDEX idx_top_five_sold_last_month ON top_five_sold_last_month(total_sold DESC);

INSERT INTO schema_migrations (version) VALUES ('001_schema');

COMMIT;
