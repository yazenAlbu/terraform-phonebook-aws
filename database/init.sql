CREATE DATABASE IF NOT EXISTS phonebook_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE phonebook_db;

CREATE TABLE IF NOT EXISTS phonebook (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    number VARCHAR(30) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY unique_person_name (name)
);

INSERT IGNORE INTO phonebook (name, number)
VALUES
    ('ahmed ali', '0301234567'),
    ('sara hassan', '017612345678'),
    ('john smith', '015212345678');