-- MySQL dump 10.13  Distrib 8.0.41, for macos15.2 (arm64)

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `chat`
--

DROP TABLE IF EXISTS `chat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `chat` (
  `chat_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `message_id` int DEFAULT NULL,
  `message` text NOT NULL,
  `timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `video_id` int DEFAULT NULL,
  `video_path` text,
  `video_start_timestamp` datetime DEFAULT NULL,
  `video_end_timestamp` datetime DEFAULT NULL,
  `voice_id` int DEFAULT NULL,
  `voice_path` text,
  `voice_start_timestamp` datetime DEFAULT NULL,
  `voice_end_timestamp` datetime DEFAULT NULL,
  `e_id` int DEFAULT NULL,
  `pet_emotion` text,
  `reply_message` text,
  PRIMARY KEY (`chat_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_e_id` (`e_id`),
  CONSTRAINT `chat_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `chat_ibfk_2` FOREIGN KEY (`e_id`) REFERENCES `petemoticon` (`e_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `log`
--

DROP TABLE IF EXISTS `log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `log` (
  `log_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `log_type` varchar(100) NOT NULL,
  `timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `detail` text,
  `location` varchar(100) DEFAULT NULL,
  `device_info` text,
  `error_code` varchar(50) DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`log_id`),
  KEY `idx_log_user_id` (`user_id`),
  KEY `idx_log_type` (`log_type`),
  CONSTRAINT `log_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `petcharactersetting`
--

DROP TABLE IF EXISTS `petcharactersetting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `petcharactersetting` (
  `character_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `speech` text,
  `character_style` text,
  `res_setting` text,
  PRIMARY KEY (`character_id`),
  KEY `idx_character_user_id` (`user_id`),
  CONSTRAINT `petcharactersetting_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `petcharactersetting_chk_1` CHECK ((`character_style` in (_utf8mb4'외향적',_utf8mb4'내향적')))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `petemoticon`
--

DROP TABLE IF EXISTS `petemoticon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `petemoticon` (
  `e_id` int NOT NULL AUTO_INCREMENT,
  `emoticon` text NOT NULL,
  `text` text NOT NULL,
  PRIMARY KEY (`e_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pettrainingsetting`
--

DROP TABLE IF EXISTS `pettrainingsetting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pettrainingsetting` (
  `training_setting_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `training_text` text NOT NULL,
  `keyword_text` text,
  `gesture_video_path` text,
  `gesture_recognition_id` int DEFAULT NULL,
  `recognized_gesture` text,
  PRIMARY KEY (`training_setting_id`),
  KEY `idx_training_user_id` (`user_id`),
  CONSTRAINT `pettrainingsetting_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `nickname` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `useremotionanalysis`
--

DROP TABLE IF EXISTS `useremotionanalysis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `useremotionanalysis` (
  `emotion_analysis_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `chat_id` int NOT NULL,
  `face_emotion` varchar(50) DEFAULT NULL,
  `voice_emotion` varchar(50) DEFAULT NULL,
  `text_emotion` varchar(50) DEFAULT NULL,
  `summary` text,
  `time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`emotion_analysis_id`),
  KEY `idx_user_emotion_user_id` (`user_id`),
  KEY `idx_user_emotion_chat_id` (`chat_id`),
  CONSTRAINT `useremotionanalysis_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `useremotionanalysis_ibfk_2` FOREIGN KEY (`chat_id`) REFERENCES `chat` (`chat_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `usersetting`
--

DROP TABLE IF EXISTS `usersetting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usersetting` (
  `setting_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `font_size` int DEFAULT '16',
  PRIMARY KEY (`setting_id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `usersetting_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `usersetting_chk_1` CHECK ((`font_size` between 8 and 48))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-03-25 23:52:08
