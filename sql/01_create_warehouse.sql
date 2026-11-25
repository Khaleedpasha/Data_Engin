CREATE SCHEMA IF NOT EXISTS warehouse;

DROP TABLE IF EXISTS warehouse.fact_order_items;
DROP TABLE IF EXISTS warehouse.fact_orders;
DROP TABLE IF EXISTS warehouse.dim_customer;
DROP TABLE IF EXISTS warehouse.dim_product;
DROP TABLE IF EXISTS warehouse.dim_seller;
DROP TABLE IF EXISTS warehouse.dim_date;

CREATE TABLE warehouse.dim_customer AS
SELECT customer_id, customer_unique_id, customer_city,
       customer_state, customer_zip_code_prefix
FROM staging.customers;
ALTER TABLE warehouse.dim_customer ADD PRIMARY KEY (customer_id);

CREATE TABLE warehouse.dim_product AS
SELECT product_id,
       product_category_name_english AS category,
       product_weight_g, product_photos_qty
FROM staging.products;
ALTER TABLE warehouse.dim_product ADD PRIMARY KEY (product_id);

CREATE TABLE warehouse.dim_seller AS
SELECT seller_id, seller_city, seller_state, seller_zip_code_prefix
FROM staging.sellers;
ALTER TABLE warehouse.dim_seller ADD PRIMARY KEY (seller_id);

CREATE TABLE warehouse.dim_date AS
SELECT d::date AS date_key,
       EXTRACT(YEAR FROM d)::int AS year,
       EXTRACT(QUARTER FROM d)::int AS quarter,
       EXTRACT(MONTH FROM d)::int AS month,
       TO_CHAR(d, 'Month') AS month_name,
       EXTRACT(DOW FROM d)::int AS day_of_week
FROM generate_series('2016-01-01'::date, '2018-12-31'::date, '1 day') AS d;
ALTER TABLE warehouse.dim_date ADD PRIMARY KEY (date_key);

CREATE TABLE warehouse.fact_orders AS
WITH pay AS (
    SELECT order_id, SUM(payment_value) AS payment_total
    FROM staging.payments GROUP BY order_id
),
rev AS (
    SELECT order_id, AVG(review_score) AS review_score
    FROM staging.reviews GROUP BY order_id
)
SELECT o.order_id,
       o.customer_id,
       o.order_status,
       o.order_purchase_timestamp::timestamp AS purchase_ts,
       o.order_purchase_timestamp::timestamp::date AS purchase_date,
       o.order_delivered_customer_date::timestamp AS delivered_ts,
       o.delivery_days,
       o.is_late,
       COALESCE(p.payment_total, 0) AS payment_total,
       r.review_score
FROM staging.orders o
LEFT JOIN pay p ON p.order_id = o.order_id
LEFT JOIN rev r ON r.order_id = o.order_id;
ALTER TABLE warehouse.fact_orders ADD PRIMARY KEY (order_id);

CREATE TABLE warehouse.fact_order_items AS
SELECT i.order_id,
       i.order_item_id,
       i.product_id,
       i.seller_id,
       o.customer_id,
       o.order_purchase_timestamp::timestamp::date AS purchase_date,
       i.price,
       i.freight_value,
       i.total_item_value
FROM staging.order_items i
JOIN staging.orders o ON o.order_id = i.order_id;
ALTER TABLE warehouse.fact_order_items ADD PRIMARY KEY (order_id, order_item_id);