-- phpMyAdmin SQL Dump
-- version 4.7.9
-- https://www.phpmyadmin.net/
--
-- Host: db
-- Generation Time: Feb 24, 2022 at 12:39 PM
-- Server version: 5.7.37
-- PHP Version: 7.2.2

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

-- --------------------------------------------------------

--
-- Table structure for table `faculty`
--

CREATE TABLE `faculty` (
  `id` int(11) NOT NULL,
  `acronym` varchar(10) DEFAULT NULL,
  `name` text,
  `last_updated` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `faculty`
--

INSERT INTO `faculty` (`id`, `acronym`, `name`, `last_updated`) VALUES
(1, 'faup', 'Página da Faculdade de Arquitectura', '2022-02-19 14:41:13'),
(2, 'fbaup', 'Página da Faculdade de Belas Artes (FBAUP)', '2022-02-19 14:41:13'),
(3, 'fcup', 'Página da Faculdade de Ciências (FCUP)', '2022-02-19 14:41:13'),
(4, 'fcnaup', 'Página da Faculdade de Ciências da Nutrição e da Alimentação (FCNAUP)', '2022-02-19 14:41:13'),
(5, 'fadeup', 'Página da Faculdade de Desporto (FADEUP)', '2022-02-19 14:41:13'),
(6, 'fdup', 'Página da Faculdade de Direito (FDUP)', '2022-02-19 14:41:13'),
(7, 'fep', 'Página da Faculdade de Economia (FEP)', '2022-02-19 14:41:13'),
(8, 'feup', 'Página da Faculdade de Engenharia (FEUP)', '2022-02-19 14:41:13'),
(9, 'ffup', 'Página da Faculdade de Farmácia (FFUP)', '2022-02-19 14:41:13'),
(10, 'flup', 'Página da Faculdade de Letras (FLUP)', '2022-02-19 14:41:13'),
(11, 'fmup', 'Página da Faculdade de Medicina (FMUP)', '2022-02-19 14:41:13'),
(12, 'fmdup', 'Página da Faculdade de Medicina Dentária (FMDUP)', '2022-02-19 14:41:13'),
(13, 'fpceup', 'Página da Faculdade de Psicologia e de Ciências da Educação (FPCEUP)', '2022-02-19 14:41:13'),
(14, 'icbas', 'Página do Instituto de Ciências Biomédicas Abel Salazar (ICBAS)', '2022-02-19 14:41:13'),
(15, 'pbs', 'Página Web do Porto Business School', '2022-02-19 14:41:13');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `faculty`
--
ALTER TABLE `faculty`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `acronym` (`acronym`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `faculty`
--
ALTER TABLE `faculty`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
