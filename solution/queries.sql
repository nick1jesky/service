-- 1.1 номенклатура
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    quantity INT NOT NULL CHECK (quantity >= 0),
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    category_id BIGINT REFERENCES categories(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 1.2 - каталог номенклатуры/дерево категорий - используем смежные вершины
CREATE TABLE categories (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    parent_id BIGINT REFERENCES categories(id) ON DELETE CASCADE,
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

-- 2.1
SELECT 
    c.name AS client_name,
    SUM(i.quantity * p.price) AS total_amount
FROM clients c
JOIN orders o ON c.id = o.client_id
JOIN order_items i ON o.id = i.order_id
JOIN products p ON i.product_id = p.id
WHERE o.closed_at IS NOT NULL
GROUP BY c.id, c.name;

-- 2.2
SELECT
    parent.id,
    parent.name AS category,
    COUNT(child.id) AS first_level_childs_count
FROM categories parent
LEFT JOIN categories child on child.parent_id = parent.id
GROUP BY parent.id, parent.name;

-- 2.3

-- 2.3.1
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

-- 2.3.2 
-- Так как данные top_five_sold_last_month являются историческими я использовал физическое хранение данных на диске с помощью MATERIALIZED;
-- Для оптимизации следует созать индексы по полям, используемым в WHERE, JOIN, GROUP BY
-- Также я решил добавить представление для сопоставления продуктов и их корневых каталогов.

CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_categories_parent_id ON categories(parent_id);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_categories_name ON categories(name);
CREATE INDEX idx_top_five_sold_last_month ON top_five_sold_last_month(total_sold DESC);
