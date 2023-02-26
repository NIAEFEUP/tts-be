-- phpMyAdmin SQL Dump
-- version 4.7.7
-- https://www.phpmyadmin.net/
--
-- Host: db
-- Generation Time: Feb 04, 2018 at 01:27 PM
-- Server version: 5.7.20
-- PHP Version: 7.1.9

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `tts`
--

CREATE TABLE `faculty` (
  `acronym` varchar(10) DEFAULT NULL,
  `name` text,
  `last_updated` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


-- --------------------------------------------------------

--
-- Table structure for table `course`
--

CREATE TABLE `course` (
  `id` int(11) NOT NULL,
  `faculty_acronym` varchar(10) NOT NULL,
  `course_id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `acronym` varchar(10) NOT NULL,
  `course_type` varchar(2) NOT NULL,
  `year` int(11) NOT NULL,
  `url` varchar(2000) NOT NULL,
  `plan_url` varchar(2000) NOT NULL,
  `last_updated` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `course_unit`
--

CREATE TABLE `course_unit` (
  `id` int(11) NOT NULL,
  `course_unit_id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `acronym` varchar(16) NOT NULL,
  `url` varchar(2000) NOT NULL,
  `course_year` tinyint(4) NOT NULL,
  `semester` tinyint(4) NOT NULL,
  `year` smallint(6) NOT NULL,
  `schedule_url` varchar(2000) DEFAULT NULL,
  `last_updated` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------


--
-- Table structure for table `course_unit_year`
-- 
CREATE TABLE `course_unit_year` (
  `course_id` INTEGER NOT NULL,
  `course_unit_id` int(11) NOT NULL, 
  `course_unit_year` tinyint(4) NOT NULL
);


-- --------------------------------------------------------
--
-- Table structure for table `schedule`
--

CREATE TABLE `schedule` (
  `id` int(11) NOT NULL,
  `day` tinyint(3) UNSIGNED NOT NULL,
  `duration` decimal(3,1) UNSIGNED NOT NULL,
  `start_time` decimal(3,1) UNSIGNED NOT NULL,
  `location` varchar(31) NOT NULL,
  `lesson_type` varchar(3) NOT NULL,
  `teacher_acronym` varchar(16) NOT NULL,
  `course_unit_id` int(11) NOT NULL,
  `last_updated` datetime NOT NULL,
  `class_name` varchar(31) NOT NULL,
  `composed_class_name` varchar(16) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------
-- Table structure for table `statistics`
-- 

CREATE TABLE `statistics` (
  `id` int(11) NOT NULL,
  `acronym` varchar(10) NOT NULL,
  `course_unit_id` int(11) NOT NULL,
  `visited_times` int(11) NOT NULL,
  `last_updated` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


-- Add primary keys 
alter TABLE faculty ADD PRIMARY KEY (`acronym`);

alter TABLE course ADD PRIMARY KEY (`id`);
alter TABLE course ADD FOREIGN KEY (faculty_acronym) REFERENCES faculty(acronym) on DELETE CASCADE ON UPDATE CASCADE;

alter TABLE course_unit ADD PRIMARY KEY (`id`);
alter TABLE course_unit ADD FOREIGN KEY (`course_id`) REFERENCES `course`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;

alter TABLE course_unit_year ADD PRIMARY KEY (`course_id`, `course_unit_id`, `course_unit_year`);
alter TABLE course_unit_year ADD FOREIGN KEY (`course_unit_id`) REFERENCES `course_unit`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;
alter TABLE course_unit_year ADD FOREIGN KEY (`course_id`) REFERENCES `course`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;

alter TABLE schedule ADD PRIMARY KEY (`id`);
alter TABLE schedule ADD FOREIGN KEY (`course_unit_id`) REFERENCES `course_unit`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;

alter TABLE statistics ADD PRIMARY KEY (`id`);

-- Create index 

--
-- Indexes for dumped tables
--

--
-- Indexes for table `course`
--
CREATE UNIQUE INDEX `course_course_id` ON `course` (`course_id`,`faculty_acronym`,`year`);
CREATE INDEX `course_faculty_acronym` ON `course` (`faculty_acronym`); 

--
-- Indexes for table `course_unit`
--
CREATE UNIQUE INDEX `course_unit_uniqueness` ON `course_unit`  (`course_unit_id`,`course_id`,`year`,`semester`); 
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
CREATE INDEX `statistics` ON `statistics`(`id`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
