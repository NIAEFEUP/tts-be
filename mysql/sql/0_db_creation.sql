SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";
SET NAMES 'utf8' COLLATE 'utf8_general_ci'; 

CREATE TABLE `faculty` (
    `id` int(11) PRIMARY KEY, 
    `acronym` varchar(10) NOT NULL UNIQUE KEY,
    `name` varchar(200) NOT NULL
);


CREATE TABLE `course` (
    `id` int (11) PRIMARY KEY,   
    `course_id` int (11) NOT NULL UNIQUE,
    `acronym` varchar(10) NOT NULL, 
    `name` varchar(200) NOT NULL,
    `course_type` varchar(2) NOT NULL,  
    `url` varchar(2000) NOT NULL,
    `plan_url` varchar(2000) NOT NULL,  
    `plan_id` int (11) NOT NULL,
    `year` int(12) NOT NULL 
);


CREATE TABLE `course_faculty` (
    `faculty_id` int(11) NOT NULL, 
    `course_id` int(11) NOT NULL,
    CONSTRAINT fk_course FOREIGN KEY (`course_id`) REFERENCES `course` (`id`) ON DELETE CASCADE ON UPDATE CASCADE, 
    CONSTRAINT fk_faculty FOREIGN KEY (`faculty_id`) REFERENCES `faculty`(`id`) ON DELETE CASCADE ON UPDATE CASCADE 
);

COMMIT;