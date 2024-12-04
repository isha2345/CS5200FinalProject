-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Nov 20, 2024 at 04:24 PM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `Remo_Books`
--

-- --------------------------------------------------------

--
-- Table structure for table `Books`
--

CREATE TABLE `Books` (
  `title` varchar(50) NOT NULL,
  `author` varchar(40) NOT NULL,
  `genre` varchar(30) NOT NULL,
  `subgenre` varchar(30) NOT NULL,
  `awards` varchar(50) NOT NULL,
  `contributors` varchar(300) NOT NULL,
  `lexileLevel` varchar(30) NOT NULL,
  `copyrightDate` varchar(4) NOT NULL,
  `summary` text NOT NULL,
  `type` varchar(30) NOT NULL,
  `seriesName` varchar(50) NOT NULL,
  `seriesNumber` varchar(3) NOT NULL,
  `form` varchar(30) NOT NULL,
  `subtitle` varchar(50) NOT NULL,
  `altTitle` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `Books`
--

INSERT INTO `Books` (`title`, `author`, `genre`, `subgenre`, `awards`, `contributors`, `lexileLevel`, `copyrightDate`, `summary`, `type`, `seriesName`, `seriesNumber`, `form`, `subtitle`, `altTitle`) VALUES
('Miosotis Flores Never Forgets', 'Hilda Eunice Burgos', 'Contemporary', '', '', '', '', '', 'Miosotis Flores is excited about three things: fostering rescue dogs, goofy horror movies, and her sister Amarilis\'s upcoming wedding. School? Not on that list. But her papi cares about school more than anything else, so they strike a deal: If Miosotis improves her grades in two classes, she can adopt a dog of her own in the summer.\r\n\r\nMiosotis dives into her schoolwork, and into nurturing a fearful little pup called Freckles. Could he become her forever dog? At the same time, she notices Amarilis behaving strangely--wearing thick clothes in springtime, dropping her friends in favor of her fiancé, even avoiding Miosotis and the rest of their family.\r\n\r\nWhen she finally discovers her sister\'s secret, Miosotis faces some difficult choices. What do you do if someone is in danger, but doesn\'t want your help? When should you ask for support, and when should you try to handle things on your own? And what ultimately matters most--what Miosotis wants, or what\'s right for the ones she loves?', 'fiction', '', '', 'book', '', '');

-- --------------------------------------------------------

--
-- Table structure for table `Edition`
--

CREATE TABLE `Edition` (
  `isbn` bigint(13) NOT NULL,
  `title` varchar(50) NOT NULL,
  `author` varchar(40) NOT NULL,
  `format` varchar(30) NOT NULL,
  `publisher` varchar(30) NOT NULL,
  `pubDate` year(4) NOT NULL,
  `time` time NOT NULL,
  `pages` int(4) NOT NULL,
  `illustrators` varchar(50) NOT NULL,
  `textFeatures` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `Edition`
--

INSERT INTO `Edition` (`isbn`, `title`, `author`, `format`, `publisher`, `pubDate`, `time`, `pages`, `illustrators`, `textFeatures`) VALUES
(9781643790657, 'Miosotis Flores Never Forgets', 'Hilda Eunice Burgos', 'hardcover', 'Lee & Low', '2021', '00:00:00', 304, '', '');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `Books`
--
ALTER TABLE `Books`
  ADD PRIMARY KEY (`title`,`author`);

--
-- Indexes for table `Edition`
--
ALTER TABLE `Edition`
  ADD PRIMARY KEY (`isbn`),
  ADD KEY `title` (`title`,`author`);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `Edition`
--
ALTER TABLE `Edition`
  ADD CONSTRAINT `edition_ibfk_1` FOREIGN KEY (`title`,`author`) REFERENCES `Books` (`title`, `author`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
