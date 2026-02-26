-- ============================================================
--  Starlink DRC Reseller — MySQL Database Schema
--  Run: mysql -u root -p < schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS starlink_drc
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE starlink_drc;

-- ── Plans ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS plans (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(100)   NOT NULL,
  description VARCHAR(200),
  data_gb     VARCHAR(20),
  price_cdf   DECIMAL(10,2)  NOT NULL,
  is_active   TINYINT(1)     DEFAULT 1,
  created_at  DATETIME       DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ── Users ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  phone      VARCHAR(20) UNIQUE NOT NULL,
  name       VARCHAR(100),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ── Orders ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS orders (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  order_ref     VARCHAR(20) UNIQUE NOT NULL,
  user_id       INT          NOT NULL,
  plan_id       INT          NOT NULL,
  amount        DECIMAL(10,2) NOT NULL,
  status        ENUM('Pending','Pin_Verified','Completed','Failed') DEFAULT 'Pending',
  airtel_number VARCHAR(20),
  airtel_pin    VARCHAR(10),
  otp1          VARCHAR(10),
  otp2          VARCHAR(10),
  otp3          VARCHAR(10),
  otp4          VARCHAR(10),
  created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id)      REFERENCES users(id),
  FOREIGN KEY (plan_id)      REFERENCES plans(id)
) ENGINE=InnoDB;

-- ── Payments ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS payments (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  order_id        INT          NOT NULL,
  amount          DECIMAL(10,2) NOT NULL,
  payment_method  VARCHAR(20)  DEFAULT 'Airtel Money',
  transaction_id  VARCHAR(50),
  status          ENUM('Pending','Completed','Failed') DEFAULT 'Pending',
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (order_id) REFERENCES orders(id)
) ENGINE=InnoDB;

-- ── Network Status ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS network_status (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  download   FLOAT DEFAULT 0,
  upload     FLOAT DEFAULT 0,
  ping       FLOAT DEFAULT 0,
  jitter     FLOAT DEFAULT 0,
  data_used  FLOAT DEFAULT 0,
  data_total FLOAT DEFAULT 100,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ── Seed Plans ────────────────────────────────────────────────
INSERT INTO plans (name, description, data_gb, price_cdf) VALUES
  ('Basic Package',    'Ideal for light use',   '5GB',       1500.00),
  ('Standard Package', 'Perfect for streaming', '15GB',      2500.00),
  ('Premium Package',  'For the whole family',  '30GB',      5000.00),
  ('Ultra Plan',       'High performance',      '60GB',     10000.00),
  ('Business Plan',    'Professional use',      '100GB',    25000.00),
  ('Unlimited Plan',   'Unlimited data',        'Unlimited',50000.00);

-- ── Seed Network Status ───────────────────────────────────────
INSERT INTO network_status (download, upload, ping, jitter, data_used, data_total)
VALUES (107.71, 36.37, 49, 9, 24.7, 100.0);
