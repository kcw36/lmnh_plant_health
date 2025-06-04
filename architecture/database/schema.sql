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
DROP TABLE IF EXISTS image;
GO
DROP TABLE IF EXISTS species;
GO
DROP TABLE IF EXISTS origin_city;
GO
DROP TABLE IF EXISTS origin_country;
GO

CREATE TABLE origin_country (
    country_id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);
GO

CREATE TABLE botanist (
    botanist_id SMALLINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL
);
GO

CREATE TABLE species (
    species_id BIGINT PRIMARY KEY,
    scientific_name VARCHAR(255) NOT NULL
);
GO

CREATE TABLE image (
    image_id SMALLINT PRIMARY KEY,
    original_url TEXT NOT NULL
);
GO

CREATE TABLE origin_city (
    city_id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country_id BIGINT NOT NULL,
    FOREIGN KEY (country_id) REFERENCES origin_country(country_id)
);
GO

CREATE TABLE plant (
    plant_id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    city_id BIGINT NOT NULL,
    botanist_id SMALLINT NOT NULL,
    image_id SMALLINT,
    species_id BIGINT NOT NULL,
    FOREIGN KEY (city_id) REFERENCES origin_city(city_id),
    FOREIGN KEY (botanist_id) REFERENCES botanist(botanist_id),
    FOREIGN KEY (image_id) REFERENCES image(image_id),
    FOREIGN KEY (species_id) REFERENCES species(species_id)
);
GO

CREATE TABLE botanist_plant (
    botanist_plant_id BIGINT PRIMARY KEY,
    plant_id BIGINT NOT NULL,
    botanist_id SMALLINT NOT NULL,
    FOREIGN KEY (plant_id) REFERENCES plant(plant_id),
    FOREIGN KEY (botanist_id) REFERENCES botanist(botanist_id)
);
GO

CREATE TABLE record (
    record_id BIGINT PRIMARY KEY,
    temperature BIGINT,
    last_watered DATETIME,
    soil_moisture BIGINT,
    recording_taken DATETIME,
    plant_id BIGINT NOT NULL,
    FOREIGN KEY (plant_id) REFERENCES plant(plant_id)
);
GO