-- Still working on actual column instructions in table creation

CREATE TABLE users (
    brand_id VARCHAR(5) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    founded INTEGER,
    headquarters VARCHAR(50),
    discontinued INTEGER
);

CREATE TABLE posts (
    brand_id VARCHAR(5) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    founded INTEGER,
    headquarters VARCHAR(50),
    discontinued INTEGER
);

CREATE TABLE tags (
    brand_id VARCHAR(5) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    founded INTEGER,
    headquarters VARCHAR(50),
    discontinued INTEGER
);

CREATE TABLE posts_tags (
    model_id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    brand_id VARCHAR(5) REFERENCES brands(brand_id) NOT NULL,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE users_tags (
    model_id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    brand_id VARCHAR(5) REFERENCES brands(brand_id) NOT NULL,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE zipcodes (
    model_id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    brand_id VARCHAR(5) REFERENCES brands(brand_id) NOT NULL,
    name VARCHAR(50) NOT NULL
);


INSERT INTO zipcodes (valid_zipcode) VALUES
(),
