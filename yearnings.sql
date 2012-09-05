SET FOREIGN_KEY_CHECKS=0;

CREATE DATABASE `yahoo_e`
    CHARACTER SET 'latin1'
    COLLATE 'latin1_swedish_ci';

USE `yahoo_e`;


CREATE TABLE `earnings_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `CO_NAME` varchar(255) NOT NULL,
  `CO_TICKER` varchar(255) NOT NULL,
  `CO_WHEN` varchar(255) NOT NULL,
  `DATE_EARNINGS` date NOT NULL,
  `DATE_ADDED` date NOT NULL,

  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;



CREATE TABLE `watchlist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `NAME` varchar(255) NOT NULL,
  `CO_TICKER` varchar(255),
  `DATE_ADDED` date NOT NULL,

  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE VIEW `yahoo_e`.`WATCHLISTRET` AS select DISTINCT `earnings_data`.`CO_NAME`
FROM `yahoo_e`.`earnings_data` JOIN `yahoo_e`.`watchlist`
on (`earnings_data`.`CO_NAME` LIKE concat('%',`watchlist`.`NAME`,'%'));
