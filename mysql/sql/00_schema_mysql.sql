-- phpMyAdmin SQL Dump
-- version 4.7.7


SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

--
-- Database: `tts`
--


CREATE TABLE `faculty` (
  `acronym` varchar(10) DEFAULT NULL,
  `name` text,
  `last_updated` datetime NOT NULL
) ENGINE=InnoDB CHARSET = utf8 COLLATE = utf8_general_ci;


-- --------------------------------------------------------

--
-- Table structure for table `course`
--

CREATE TABLE `course` (
  `id` int(11) NOT NULL,
  `faculty_id` varchar(10) NOT NULL,
  `sigarra_id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `acronym` varchar(10) NOT NULL,
  `course_type` varchar(2) NOT NULL,  
  `year` int(11) NOT NULL,
  `url` varchar(2000) NOT NULL,
  `plan_url` varchar(2000) NOT NULL,
  `last_updated` datetime NOT NULL
) ENGINE=InnoDB CHARSET = utf8 COLLATE = utf8_general_ci;


-- --------------------------------------------------------

--
-- Table structure for table `course_unit`
--

CREATE TABLE `course_unit` (
  `id` int(11) NOT NULL,
  `sigarra_id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `acronym` varchar(16) NOT NULL,
  `url` varchar(2000) NOT NULL,
  `semester` int(4) NOT NULL,
  `year` smallint(6) NOT NULL,
  `schedule_url` varchar(2000) DEFAULT NULL,
  `last_updated` datetime NOT NULL
) ENGINE=InnoDB CHARSET = utf8 COLLATE = utf8_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `course_metadata`
--

CREATE TABLE `course_metadata` (
  `course_id` int(11) NOT NULL,
  `course_unit_id` int(11) NOT NULL,
  `course_unit_year` int(4) NOT NULL,
  `ects` float(4) NOT NULL
) ENGINE=InnoDB CHARSET = utf8 COLLATE = utf8_general_ci;

-- --------------------------------------------------------
--
-- Table structure for table `schedule`
--

CREATE TABLE `schedule` (
  `id` INTEGER NOT NULL,
  `day` int(3) NOT NULL,
  `duration` decimal(3,1) NOT NULL,
  `start_time` decimal(3,1) NOT NULL,
  `location` varchar(31) NOT NULL,
  `lesson_type` varchar(3) NOT NULL,
  `is_composed` boolean NOT NULL,
  `professor_sigarra_id` INTEGER,
  `course_unit_id` int(11) NOT NULL,
  `last_updated` datetime NOT NULL,
  `class_name` varchar(31) NOT NULL,
  `composed_class_name` varchar(16) DEFAULT NULL
) ENGINE=InnoDB CHARSET = utf8 COLLATE = utf8_general_ci;



-- alter TABLE course_metadata ADD FOREIGN KEY (`course_unit_id`) REFERENCES `course_unit`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;

-- -------------------------------------------------------- 

--
-- Table structure for table `schedule_professor`
--

CREATE TABLE `schedule_professor` (
  `schedule_id` INTEGER NOT NULL,
  `professor_sigarra_id` INTEGER NOT NULL
) ENGINE=InnoDB CHARSET = utf8 COLLATE = utf8_general_ci;

-- -------------------------------------------------------- 

--
-- Table structure for table `professor`
--

CREATE TABLE `professor` (
  `sigarra_id` INTEGER,
  `professor_acronym` varchar(16),
  `professor_name` varchar(100)
) ENGINE=InnoDB CHARSET = utf8 COLLATE = utf8_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `info`
--

CREATE TABLE `info` (
  `date` datetime
) ENGINE=InnoDB CHARSET = utf8 COLLATE = utf8_general_ci;

-- --------------------------------------------------------

-- Table structure for table `statistics`
-- 

CREATE TABLE `statistics` (
  `course_unit_id` int(11) NOT NULL,
  `acronym` varchar(10) NOT NULL,
  `visited_times` int(11) NOT NULL,
  `last_updated` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `direct_exchange` (
  `id` INTEGER NOT NULL AUTO_INCREMENT,
  `issuer` varchar(32) NOT NULL,
  `accepted` boolean NOT NULL,
  `date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(`id`)
) ENGINE=InnoDB CHARSET = utf8 COLLATE = utf8_general_ci;

CREATE TABLE `direct_exchange_participants` (
  `id` INTEGER NOT NULL AUTO_INCREMENT,
  `participant` varchar(32) NOT NULL,
  `old_class` varchar(16) NOT NULL,
  `new_class` varchar(16) NOT NULL,
  `course_unit` varchar(64) NOT NULL,
  `course_unit_id` varchar(16) NOT NULL,
  `direct_exchange` INTEGER NOT NULL,
  `accepted` boolean NOT NULL,
  `date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(`id`),
  FOREIGN KEY (`direct_exchange`) REFERENCES `direct_exchange`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB CHARSET = utf8 COLLATE = utf8_general_ci;

-- Add primary keys 
alter TABLE faculty ADD PRIMARY KEY (`acronym`);

alter TABLE course ADD PRIMARY KEY (`id`);
alter TABLE course ADD FOREIGN KEY (`faculty_id`) REFERENCES `faculty`(`acronym`) on DELETE CASCADE ON UPDATE CASCADE;

alter TABLE course_unit ADD PRIMARY KEY (`id`);
alter TABLE course_unit ADD FOREIGN KEY (`course_id`) REFERENCES `course`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;

alter TABLE course_metadata ADD PRIMARY KEY (`course_id`, `course_unit_id`, `course_unit_year`);
alter TABLE course_metadata ADD FOREIGN KEY (`course_unit_id`) REFERENCES `course_unit`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;
alter TABLE course_metadata ADD FOREIGN KEY (`course_id`) REFERENCES `course`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;

alter TABLE schedule ADD PRIMARY KEY (`id`);
alter TABLE schedule ADD FOREIGN KEY (`course_unit_id`) REFERENCES `course_unit`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;

alter TABLE info ADD PRIMARY KEY (`date`);

alter TABLE statistics ADD PRIMARY KEY (`course_unit_id`);

alter TABLE professor ADD PRIMARY KEY (`sigarra_id`);

alter TABLE schedule_professor ADD PRIMARY KEY (`schedule_id`, `professor_sigarra_id`); 
alter TABLE schedule_professor ADD FOREIGN KEY (`schedule_id`) REFERENCES `schedule`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;


--
-- Indexes for table `course`
--
CREATE UNIQUE INDEX `course_course_id` ON `course` (`sigarra_id`,`faculty_id`,`year`);
CREATE INDEX `course_faculty_acronym` ON `course` (`faculty_id`); 

--
-- Indexes for table `course_unit`
--
CREATE UNIQUE INDEX `course_unit_uniqueness` ON `course_unit`  (`sigarra_id`,`course_id`,`year`,`semester`); 
CREATE INDEX `course_unit_course_id` ON `course_unit` (`course_id`);

--
-- Indexes for table `faculty`
--
CREATE UNIQUE INDEX `faculty_acronym` ON `faculty`(`acronym`);

--
-- Indexes for table `schedule`
--
CREATE INDEX `schedule_course_unit_id` ON `schedule`(`course_unit_id`);

--
-- Indexes for table `schedule`
--
CREATE INDEX `statistics` ON `statistics`(`course_unit_id`);

--
-- Indexes for table `course_metadata`
-- 
CREATE INDEX `course_metadata_index` ON `course_metadata`(`course_id`, `course_unit_id`, `course_unit_year`); 
