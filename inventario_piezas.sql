-- =========================================================
-- Gestor de Inventario de Piezas Automotrices
-- Base de datos: solo administración de inventario (sin ventas, sin categorías)
-- Compatible con MySQL / MariaDB (importable desde phpMyAdmin)
-- =========================================================

CREATE DATABASE IF NOT EXISTS gestor_inventario_piezas
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE gestor_inventario_piezas;

-- ---------------------------------------------------------
-- Tabla: usuarios (administrador / empleado)
-- ---------------------------------------------------------
CREATE TABLE usuarios (
  id_usuario     INT AUTO_INCREMENT PRIMARY KEY,
  nombre         VARCHAR(100) NOT NULL,
  correo         VARCHAR(150) NOT NULL UNIQUE,
  contrasena     VARCHAR(255) NOT NULL,
  rol            ENUM('administrador', 'empleado') NOT NULL DEFAULT 'empleado',
  fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- Tabla: marcas
-- ---------------------------------------------------------
CREATE TABLE marcas (
  id_marca INT AUTO_INCREMENT PRIMARY KEY,
  nombre   VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- Tabla: piezas (catálogo)
-- ---------------------------------------------------------
CREATE TABLE piezas (
  id_pieza       INT AUTO_INCREMENT PRIMARY KEY,
  nombre         VARCHAR(150) NOT NULL,
  descripcion    TEXT,
  precio         DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  id_marca       INT,
  imagen         VARCHAR(255),
  fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_pieza_marca
    FOREIGN KEY (id_marca) REFERENCES marcas(id_marca)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- Tabla: inventario (existencia actual, 1 a 1 con piezas)
-- ---------------------------------------------------------
CREATE TABLE inventario (
  id_pieza             INT PRIMARY KEY,
  existencia           INT NOT NULL DEFAULT 0,
  stock_minimo         INT NOT NULL DEFAULT 0,
  ultima_actualizacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_inventario_pieza
    FOREIGN KEY (id_pieza) REFERENCES piezas(id_pieza)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- Tabla: movimientos_inventario (historial de entradas/salidas)
-- ---------------------------------------------------------
CREATE TABLE movimientos_inventario (
  id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
  id_pieza      INT NOT NULL,
  id_usuario    INT NOT NULL,
  tipo          ENUM('entrada', 'salida', 'ajuste') NOT NULL,
  cantidad      INT NOT NULL,
  fecha         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  motivo        VARCHAR(255),
  CONSTRAINT fk_movimiento_pieza
    FOREIGN KEY (id_pieza) REFERENCES piezas(id_pieza)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_movimiento_usuario
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- =========================================================
-- Datos de ejemplo (para ver cómo queda al importar)
-- Contraseñas en texto de ejemplo -- en la app real usar hash
-- (p. ej. werkzeug.security en Python, ya usado en el backend).
-- =========================================================

INSERT INTO usuarios (nombre, correo, contrasena, rol) VALUES
  ('Admin Principal', 'admin@martinez.com', 'admin123', 'administrador'),
  ('Juan Almacen',    'juan@martinez.com',  'empleado123', 'empleado');

INSERT INTO marcas (nombre) VALUES
  ('Chevrolet'), ('Nissan'), ('Ford'), ('Toyota'), ('Volkswagen');

INSERT INTO piezas (nombre, descripcion, precio, id_marca, imagen) VALUES
  ('Balatas delanteras', 'Juego de balatas delanteras cerámicas', 450.00, 1, NULL),
  ('Amortiguador trasero', 'Amortiguador hidráulico trasero', 780.00, 2, NULL),
  ('Filtro de aceite', 'Filtro de aceite motor 1.6L', 120.00, 3, NULL),
  ('Bujía de encendido', 'Bujía de iridio', 95.00, 4, NULL),
  ('Batería 12V', 'Batería 12V 650 CCA', 1850.00, 5, NULL),
  ('Disco de freno', 'Disco de freno ventilado delantero', 620.00, 1, NULL),
  ('Filtro de aire', 'Filtro de aire de motor', 150.00, 3, NULL),
  ('Rótula de suspensión', 'Rótula inferior de suspensión', 340.00, 2, NULL);

INSERT INTO inventario (id_pieza, existencia, stock_minimo) VALUES
  (1, 25, 5),
  (2, 8,  3),
  (3, 60, 10),
  (4, 100, 20),
  (5, 12, 4),
  (6, 15, 5),
  (7, 40, 10),
  (8, 3,  5);

INSERT INTO movimientos_inventario (id_pieza, id_usuario, tipo, cantidad, motivo) VALUES
  (1, 1, 'entrada', 30, 'Compra inicial a proveedor'),
  (1, 2, 'salida',  5,  'Uso en servicio de taller'),
  (8, 2, 'salida',  2,  'Uso en servicio de taller'),
  (5, 1, 'entrada', 12, 'Compra inicial a proveedor');
