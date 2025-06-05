USE plants;
GO

DROP TABLE IF EXISTS botanist_plant;
GO
DROP TABLE IF EXISTS record;
GO
DROP TABLE IF EXISTS plant;
GO
DROP TABLE IF EXISTS botanist;
GO
DROP TABLE IF EXISTS origin_city;
GO
DROP TABLE IF EXISTS origin_country;
GO

CREATE TABLE origin_country (
    country_id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);
GO

CREATE TABLE botanist (
    botanist_id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL
);
GO

CREATE TABLE origin_city (
    city_id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country_id INT NOT NULL,
    FOREIGN KEY (country_id) REFERENCES origin_country(country_id)
);
GO

CREATE TABLE plant (
    plant_id INT PRIMARY KEY,  -- Manual input
    name VARCHAR(255) NOT NULL,
    city_id INT NOT NULL,
    FOREIGN KEY (city_id) REFERENCES origin_city(city_id)
);
GO

CREATE TABLE botanist_plant (
    botanist_plant_id INT IDENTITY(1,1) PRIMARY KEY,
    plant_id INT NOT NULL,
    botanist_id INT NOT NULL,
    FOREIGN KEY (plant_id) REFERENCES plant(plant_id),
    FOREIGN KEY (botanist_id) REFERENCES botanist(botanist_id)
);
GO

CREATE TABLE record (
    record_id INT IDENTITY(1,1) PRIMARY KEY,
    temperature FLOAT,
    last_watered DATETIME,
    soil_moisture FLOAT,
    recording_taken DATETIME,
    plant_id INT NOT NULL,
    FOREIGN KEY (plant_id) REFERENCES plant(plant_id)
);
GO
