SET NAMES 'utf8mb4';


CREATE TABLE `platform` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(30),
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `city` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(30),
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `profession` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(30),
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
CREATE INDEX profession_idx1 on profession(`name`);


CREATE TABLE `resume` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `platform_id` INT,
    `platform_resume_id` VARCHAR(100),
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
    PRIMARY KEY (`id`),
    FOREIGN KEY (platform_id) REFERENCES platform(id),
    FOREIGN KEY (city_id) REFERENCES city(id),
    FOREIGN KEY (profession_id) REFERENCES profession(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
CREATE INDEX resume_idx1 on resume(`sex`);
CREATE INDEX resume_idx2 on resume(`age`);
CREATE INDEX resume_idx3 on resume(`currency`);
