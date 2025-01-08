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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_0900_ai_ci;;
CREATE INDEX resume_idx1 on resume(`sex`);
CREATE INDEX resume_idx2 on resume(`age`);
CREATE INDEX resume_idx3 on resume(`currency`);
CREATE UNIQUE INDEX resume_idx4 on resume(`platform_id`, `platform_resume_id`);
