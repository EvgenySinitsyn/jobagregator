SET NAMES 'utf8mb4';


CREATE TABLE `platform` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(30),
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_0900_ai_ci;;


CREATE TABLE `city` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255),
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE UNIQUE INDEX city_idx1 on city(`name`);


CREATE TABLE `profession` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255),
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_0900_ai_ci;;
CREATE UNIQUE INDEX profession_idx1 on profession(`name`);


CREATE TABLE `resume` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `platform_id` INT,
    `platform_resume_id` VARCHAR(100),
    `platform_resume_tm_create` DATETIME,
    `platform_resume_tm_update` DATETIME,
    `city_id` INT,
    `profession_id` INT,
    `sex` ENUM('male', 'female'),
    `age` INT,
    `salary_from` INT,
    `salary_to` INT,
    `currency` ENUM('RUB', 'EUR', 'USD'),
    `experience_months` INT,
    `summary_info` JSON,
    `link` VARCHAR(255),
    `tm` DATETIME DEFAULT NOW(),
    PRIMARY KEY (`id`),
    FOREIGN KEY (platform_id) REFERENCES platform(id) ON DELETE CASCADE,
    FOREIGN KEY (city_id) REFERENCES city(id) ON DELETE CASCADE,
    FOREIGN KEY (profession_id) REFERENCES profession(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE INDEX resume_idx1 on resume(`sex`);
CREATE INDEX resume_idx2 on resume(`age`);
CREATE INDEX resume_idx3 on resume(`currency`);
CREATE UNIQUE INDEX resume_idx4 on resume(`platform_id`, `platform_resume_id`);


CREATE TABLE `platform_city` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `platform_id` INT,
    `city_id` INT,
    `platform_city_id` VARCHAR(65),
    PRIMARY KEY (`id`),
    FOREIGN KEY (platform_id) REFERENCES platform(id) ON DELETE CASCADE,
    FOREIGN KEY (city_id) REFERENCES city(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE UNIQUE INDEX platform_city_idx1 on platform_city(`platform_id`, `city_id`, `platform_city_id`);


CREATE TABLE `vacancy` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `platform_id` INT,
    `platform_vacancy_id` VARCHAR(100),
    `platform_vacancy_tm_create` DATETIME,
    `city_id` INT,
    `profession_id` INT,
    `salary_from` INT,
    `salary_to` INT,
    `schedule` VARCHAR(255),
    `currency` ENUM('RUB', 'EUR', 'USD'),
    `experience_months_from` INT,
    `experience_months_to` INT,
    `summary_info` JSON,
    `link` VARCHAR(255),
    `employer_name` VARCHAR(255),
    `contact_email` VARCHAR(255),
    `contact_phone` VARCHAR(30),
    `contact_person` VARCHAR(255),
    `tm` DATETIME DEFAULT NOW(),
    PRIMARY KEY (`id`),
    FOREIGN KEY (platform_id) REFERENCES platform(id) ON DELETE CASCADE,
    FOREIGN KEY (city_id) REFERENCES city(id) ON DELETE CASCADE,
    FOREIGN KEY (profession_id) REFERENCES profession(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE UNIQUE INDEX vacancy_idx1 on vacancy(`platform_id`, `platform_vacancy_id`);
