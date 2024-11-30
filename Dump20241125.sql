-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: localhost    Database: simuladoapp
-- ------------------------------------------------------
-- Server version	9.1.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `accounts_customuser`
--

DROP TABLE IF EXISTS `accounts_customuser`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts_customuser` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `email` varchar(254) NOT NULL,
  `email_verified` tinyint(1) NOT NULL,
  `activation_token` char(32) NOT NULL,
  `activation_token_expiry` datetime(6) DEFAULT NULL,
  `is_teacher` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_customuser`
--

LOCK TABLES `accounts_customuser` WRITE;
/*!40000 ALTER TABLE `accounts_customuser` DISABLE KEYS */;
INSERT INTO `accounts_customuser` VALUES (1,'bcrypt_sha256$$2b$12$Yw0A43bQxL.1muO4fK3PreNjuxzzs9EmOL4SnKbf49dVP8ecXZ0J.',1,'luizteste','','',1,1,'luizgabrieltrader@outlook.com',0,'f7a00b234fe94f33baf50a55b2c19bb2','2024-11-25 01:38:25.056435',1,'2024-11-18 01:38:24.164795','2024-11-18 01:39:08.694345'),(2,'',0,'isaiasmouta1@gmail.com','Isaias','Mouta',0,1,'isaiasmouta1@gmail.com',0,'6b2d07f7aca046d2a62ee9ed0a54e516','2024-11-26 18:24:34.316759',1,'2024-11-19 18:24:34.316759',NULL),(3,'bcrypt_sha256$$2b$12$FDjmWK98TyMGK4Q91qreKePlacP67eg6K8vkMN80TJki1MzpmDYMS',0,'raquel','Raquel','Melo',0,1,'r.saraivamelo@gmail.com',1,'d00e01de304f41b28f227c74fcd4b240','2024-11-21 19:48:25.699766',1,'2024-11-19 19:48:23.889137','2024-11-19 19:49:29.780671'),(4,'',0,'alberto.kennedy.da.silva.do.amaral@escola.com','ALBERTO','KENNEDY DA SILVA DO AMARAL',0,1,'alberto.kennedy.da.silva.do.amaral@escola.com',0,'9fad7d3e7b714c0089a5ce2173fe31db','2024-11-30 19:30:08.668215',1,'2024-11-23 19:30:08.668215',NULL),(5,'',0,'amanda.pereira.mota@escola.com','AMANDA','PEREIRA MOTA',0,1,'amanda.pereira.mota@escola.com',0,'b5890f75ce714f1fb12532fb04492a58','2024-11-30 19:30:08.778189',1,'2024-11-23 19:30:08.778189',NULL),(6,'',0,'anielly.da.conceicao.cunha@escola.com','ANIELLY','DA CONCEICAO CUNHA',0,1,'anielly.da.conceicao.cunha@escola.com',0,'5f8d7819c12c417eb6603a0568a01f1b','2024-11-30 19:30:08.801508',1,'2024-11-23 19:30:08.801508',NULL),(7,'',0,'arlyla.nascimento.dos.santos@escola.com','ARLYLA','NASCIMENTO DOS SANTOS',0,1,'arlyla.nascimento.dos.santos@escola.com',0,'84ea13913a26456a8ce95ad3c3f993cf','2024-11-30 19:30:08.838952',1,'2024-11-23 19:30:08.837954',NULL),(8,'',0,'ayra.santos.vieira@escola.com','AYRA','SANTOS VIEIRA',0,1,'ayra.santos.vieira@escola.com',0,'ebcf063e126c4a94806021b4a763663d','2024-11-30 19:30:08.864572',1,'2024-11-23 19:30:08.864572',NULL),(9,'',0,'clara.giuliana.da.silva.rodrigues@escola.com','CLARA','GIULIANA DA SILVA RODRIGUES',0,1,'clara.giuliana.da.silva.rodrigues@escola.com',0,'588a9d7053df4ce2a3a744b8e06697e8','2024-11-30 19:30:08.893485',1,'2024-11-23 19:30:08.893485',NULL),(10,'',0,'cristhoph.alexandre.silva.sousa@escola.com','CRISTHOPH','ALEXANDRE SILVA SOUSA',0,1,'cristhoph.alexandre.silva.sousa@escola.com',0,'c36f17ec5a2849938095d7f37dc1b39b','2024-11-30 19:30:08.915605',1,'2024-11-23 19:30:08.915605',NULL),(11,'',0,'dayandra.santana.ferreira@escola.com','DAYANDRA','SANTANA FERREIRA',0,1,'dayandra.santana.ferreira@escola.com',0,'f4aa2fbd49ae42f291dda098bcb5a695','2024-11-30 19:30:08.934604',1,'2024-11-23 19:30:08.934604',NULL),(12,'',0,'deivison.augusto.miranda.pereira@escola.com','DEIVISON','AUGUSTO MIRANDA PEREIRA',0,1,'deivison.augusto.miranda.pereira@escola.com',0,'5f8bbdf9bcec4eb993354767cafdbae0','2024-11-30 19:30:08.969290',1,'2024-11-23 19:30:08.969290',NULL),(13,'',0,'eduardo.victor.pinheiro.costa@escola.com','EDUARDO','VICTOR PINHEIRO COSTA',0,1,'eduardo.victor.pinheiro.costa@escola.com',0,'ecc5e65513ae440da4747a596ccfbfc4','2024-11-30 19:30:08.982228',1,'2024-11-23 19:30:08.982228',NULL),(14,'',0,'emanuel.silva.de.lima@escola.com','EMANUEL','SILVA DE LIMA',0,1,'emanuel.silva.de.lima@escola.com',0,'649b1ea884d546ccb68b1c4d3c70586a','2024-11-30 19:30:09.019737',1,'2024-11-23 19:30:09.019737',NULL),(15,'',0,'emily.telma.lobato.moura@escola.com','EMILY','TELMA LOBATO MOURA',0,1,'emily.telma.lobato.moura@escola.com',0,'20806c3e486a48b3bcfc10b54a641364','2024-11-30 19:30:09.041851',1,'2024-11-23 19:30:09.041851',NULL),(16,'',0,'evelyn.macedo.da.silva@escola.com','EVELYN','MACEDO DA SILVA',0,1,'evelyn.macedo.da.silva@escola.com',0,'576aa576025046a4973f604f30340ef5','2024-11-30 19:30:09.068099',1,'2024-11-23 19:30:09.068099',NULL),(17,'',0,'guilherme.do.carmo.antunes@escola.com','GUILHERME','DO CARMO ANTUNES',0,1,'guilherme.do.carmo.antunes@escola.com',0,'a3b3414eec554b42bbacf3a5ea854b47','2024-11-30 19:30:09.092454',1,'2024-11-23 19:30:09.092454',NULL),(18,'',0,'joao.pedro.santos.lima@escola.com','JOAO','PEDRO SANTOS LIMA',0,1,'joao.pedro.santos.lima@escola.com',0,'7064601a00f54155aae70c16251e9295','2024-11-30 19:30:09.115569',1,'2024-11-23 19:30:09.115569',NULL),(19,'',0,'kassiane.oliveira.dos.santos@escola.com','KASSIANE','OLIVEIRA DOS SANTOS',0,1,'kassiane.oliveira.dos.santos@escola.com',0,'205ebd6b321b403496454ce4e9e436a6','2024-11-30 19:30:09.134823',1,'2024-11-23 19:30:09.134823',NULL),(20,'',0,'kauany.vitoria.sousa.braga@escola.com','KAUANY','VITORIA SOUSA BRAGA',0,1,'kauany.vitoria.sousa.braga@escola.com',0,'acb1de1ece0d4f3f86c173861b50d9e1','2024-11-30 19:30:09.201425',1,'2024-11-23 19:30:09.201425',NULL),(21,'',0,'kaua.ronaldo.pantoja.de.sousa@escola.com','KAUA','RONALDO PANTOJA DE SOUSA',0,1,'kaua.ronaldo.pantoja.de.sousa@escola.com',0,'f65a97602874462bb1d47b60529e6da4','2024-11-30 19:30:09.235826',1,'2024-11-23 19:30:09.235826',NULL),(22,'',0,'keyrrison.kaio.barata.barbosa@escola.com','KEYRRISON','KAIO BARATA BARBOSA',0,1,'keyrrison.kaio.barata.barbosa@escola.com',0,'3aaa0454342d43a88228c22d6ef78688','2024-11-30 19:30:09.248936',1,'2024-11-23 19:30:09.248936',NULL),(23,'',0,'livya.menezes.da.silva@escola.com','LIVYA','MENEZES DA SILVA',0,1,'livya.menezes.da.silva@escola.com',0,'1cd8cda9b6204d4da398404798993a2e','2024-11-30 19:30:09.283339',1,'2024-11-23 19:30:09.283339',NULL),(24,'',0,'luisa.keytheleen.mendes.capela@escola.com','LUISA','KEYTHELEEN MENDES CAPELA',0,1,'luisa.keytheleen.mendes.capela@escola.com',0,'d583fd1e0a924780bdc6bd9d8963ee61','2024-11-30 19:30:09.309461',1,'2024-11-23 19:30:09.309461',NULL),(25,'',0,'maria.aparecida.rocha.pereira@escola.com','MARIA','APARECIDA ROCHA PEREIRA',0,1,'maria.aparecida.rocha.pereira@escola.com',0,'e6d58530f63b43298fbece9225473fcd','2024-11-30 19:30:09.334721',1,'2024-11-23 19:30:09.334721',NULL),(26,'',0,'maria.eduarda.silva.de.sousa@escola.com','MARIA','EDUARDA SILVA DE SOUSA',0,1,'maria.eduarda.silva.de.sousa@escola.com',0,'cf7bca4f628a4b5381b7f4b8539e8e91','2024-11-30 19:30:09.359973',1,'2024-11-23 19:30:09.359973',NULL),(27,'',0,'matheus.alves.siqueira@escola.com','MATHEUS','ALVES SIQUEIRA',0,1,'matheus.alves.siqueira@escola.com',0,'22a2c8467ed9475e8276c1a1d696719a','2024-11-30 19:30:09.382131',1,'2024-11-23 19:30:09.382131',NULL),(28,'',0,'reinaldo.ferreira.barbosa.filho@escola.com','REINALDO','FERREIRA BARBOSA FILHO',0,1,'reinaldo.ferreira.barbosa.filho@escola.com',0,'2386ff7ccd5a4047861b51f559638532','2024-11-30 19:30:09.404536',1,'2024-11-23 19:30:09.404536',NULL),(29,'',0,'samya.vitoria.trindade.de.morais@escola.com','SAMYA','VITORIA TRINDADE DE MORAIS',0,1,'samya.vitoria.trindade.de.morais@escola.com',0,'ae816a010e8744a88c5fd82e134d32f1','2024-11-30 19:30:09.435784',1,'2024-11-23 19:30:09.435784',NULL),(30,'',0,'sophia.barata.da.cruz@escola.com','SOPHIA','BARATA DA CRUZ',0,1,'sophia.barata.da.cruz@escola.com',0,'3494f18c342149a1aac329aa788b4c0a','2024-11-30 19:30:09.448782',1,'2024-11-23 19:30:09.448782',NULL),(31,'',0,'willian.ramon.da.silva.nascimento@escola.com','WILLIAN','RAMON DA SILVA NASCIMENTO',0,1,'willian.ramon.da.silva.nascimento@escola.com',0,'6deab61dd4804f468d5571bf5d4d523d','2024-11-30 19:30:09.485297',1,'2024-11-23 19:30:09.485297',NULL),(32,'',0,'yasmin.gomes.siqueira@escola.com','YASMIN','GOMES SIQUEIRA',0,1,'yasmin.gomes.siqueira@escola.com',0,'1a92b63a7db1484f9097461ba395b711','2024-11-30 19:30:09.506360',1,'2024-11-23 19:30:09.506360',NULL),(33,'',0,'yasmin.souza.de.oliveira@escola.com','YASMIN','SOUZA DE OLIVEIRA',0,1,'yasmin.souza.de.oliveira@escola.com',0,'92f106b46993422a825776046ba20b98','2024-11-30 19:30:09.515426',1,'2024-11-23 19:30:09.515426',NULL),(34,'',0,'professor@escola.com','PROFESSOR','',0,1,'professor@escola.com',0,'ca48d3e02b5e4be08523e729197f19f1','2024-11-30 19:31:27.760572',1,'2024-11-23 19:31:27.760572',NULL),(35,'',0,'adrian.cardoso.soares@escola.com','ADRIAN','CARDOSO SOARES',0,1,'adrian.cardoso.soares@escola.com',0,'b82a3b99fa12492ca957af97f391857b','2024-11-30 20:22:05.220966',1,'2024-11-23 20:22:05.220966',NULL),(36,'',0,'sadf@sdhafuisd.com','Maria Fernanda','asdfsdfads',0,1,'sadf@sdhafuisd.com',0,'543d6564c0b043f68519a45d78449834','2024-12-01 08:52:39.547329',1,'2024-11-24 08:52:39.547329',NULL);
/*!40000 ALTER TABLE `accounts_customuser` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_customuser_groups`
--

DROP TABLE IF EXISTS `accounts_customuser_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts_customuser_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `customuser_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_customuser_groups_customuser_id_group_id_c074bdcb_uniq` (`customuser_id`,`group_id`),
  KEY `accounts_customuser_groups_group_id_86ba5f9e_fk_auth_group_id` (`group_id`),
  CONSTRAINT `accounts_customuser__customuser_id_bc55088e_fk_accounts_` FOREIGN KEY (`customuser_id`) REFERENCES `accounts_customuser` (`id`),
  CONSTRAINT `accounts_customuser_groups_group_id_86ba5f9e_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_customuser_groups`
--

LOCK TABLES `accounts_customuser_groups` WRITE;
/*!40000 ALTER TABLE `accounts_customuser_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounts_customuser_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accounts_customuser_user_permissions`
--

DROP TABLE IF EXISTS `accounts_customuser_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts_customuser_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `customuser_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_customuser_user_customuser_id_permission_9632a709_uniq` (`customuser_id`,`permission_id`),
  KEY `accounts_customuser__permission_id_aea3d0e5_fk_auth_perm` (`permission_id`),
  CONSTRAINT `accounts_customuser__customuser_id_0deaefae_fk_accounts_` FOREIGN KEY (`customuser_id`) REFERENCES `accounts_customuser` (`id`),
  CONSTRAINT `accounts_customuser__permission_id_aea3d0e5_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_customuser_user_permissions`
--

LOCK TABLES `accounts_customuser_user_permissions` WRITE;
/*!40000 ALTER TABLE `accounts_customuser_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounts_customuser_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add usuário',6,'add_customuser'),(22,'Can change usuário',6,'change_customuser'),(23,'Can delete usuário',6,'delete_customuser'),(24,'Can view usuário',6,'view_customuser'),(25,'Can add Questão',7,'add_questao'),(26,'Can change Questão',7,'change_questao'),(27,'Can delete Questão',7,'delete_questao'),(28,'Can view Questão',7,'view_questao'),(29,'Can add questao simulado',8,'add_questaosimulado'),(30,'Can change questao simulado',8,'change_questaosimulado'),(31,'Can delete questao simulado',8,'delete_questaosimulado'),(32,'Can view questao simulado',8,'view_questaosimulado'),(33,'Can add Simulado',9,'add_simulado'),(34,'Can change Simulado',9,'change_simulado'),(35,'Can delete Simulado',9,'delete_simulado'),(36,'Can view Simulado',9,'view_simulado'),(37,'Can add student',10,'add_student'),(38,'Can change student',10,'change_student'),(39,'Can delete student',10,'delete_student'),(40,'Can view student',10,'view_student'),(41,'Can add class',11,'add_class'),(42,'Can change class',11,'change_class'),(43,'Can delete class',11,'delete_class'),(44,'Can view class',11,'view_class');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `classes_class`
--

DROP TABLE IF EXISTS `classes_class`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `classes_class` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `classes_class`
--

LOCK TABLES `classes_class` WRITE;
/*!40000 ALTER TABLE `classes_class` DISABLE KEYS */;
INSERT INTO `classes_class` VALUES (1,'101','','2024-11-24 09:49:21.733531','2024-11-24 09:49:21.733531'),(2,'302','','2024-11-24 09:49:56.221118','2024-11-24 09:49:56.221118');
/*!40000 ALTER TABLE `classes_class` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `classes_student`
--

DROP TABLE IF EXISTS `classes_student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `classes_student` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(254) DEFAULT NULL,
  `student_id` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `classes_student`
--

LOCK TABLES `classes_student` WRITE;
/*!40000 ALTER TABLE `classes_student` DISABLE KEYS */;
INSERT INTO `classes_student` VALUES (1,'ALBERTO KENNEDY DA SILVA DO AMARAL','alberto.kennedy.da.silva.do.amaral@escola.com',1),(2,'AMANDA PEREIRA MOTA','amanda.pereira.mota@escola.com',2),(3,'ANIELLY DA CONCEICAO CUNHA','anielly.da.conceicao.cunha@escola.com',3),(4,'ARLYLA NASCIMENTO DOS SANTOS','arlyla.nascimento.dos.santos@escola.com',4),(5,'AYRA SANTOS VIEIRA','ayra.santos.vieira@escola.com',5),(6,'CLARA GIULIANA DA SILVA RODRIGUES','clara.giuliana.da.silva.rodrigues@escola.com',6),(7,'CRISTHOPH ALEXANDRE SILVA SOUSA','cristhoph.alexandre.silva.sousa@escola.com',7),(8,'DAYANDRA SANTANA FERREIRA','dayandra.santana.ferreira@escola.com',8),(9,'DEIVISON AUGUSTO MIRANDA PEREIRA','deivison.augusto.miranda.pereira@escola.com',9),(10,'EDUARDO VICTOR PINHEIRO COSTA','eduardo.victor.pinheiro.costa@escola.com',10),(11,'EMANUEL SILVA DE LIMA','emanuel.silva.de.lima@escola.com',11),(12,'EMILY TELMA LOBATO MOURA','emily.telma.lobato.moura@escola.com',12),(13,'EVELYN MACEDO DA SILVA','evelyn.macedo.da.silva@escola.com',13),(14,'GUILHERME DO CARMO ANTUNES','guilherme.do.carmo.antunes@escola.com',14),(15,'JOAO PEDRO SANTOS LIMA','joao.pedro.santos.lima@escola.com',15),(16,'KASSIANE OLIVEIRA DOS SANTOS','kassiane.oliveira.dos.santos@escola.com',16),(17,'KAUANY VITORIA SOUSA BRAGA','kauany.vitoria.sousa.braga@escola.com',17),(18,'KAUA RONALDO PANTOJA DE SOUSA','kaua.ronaldo.pantoja.de.sousa@escola.com',18),(19,'KEYRRISON KAIO BARATA BARBOSA','keyrrison.kaio.barata.barbosa@escola.com',19),(20,'LIVYA MENEZES DA SILVA','livya.menezes.da.silva@escola.com',20),(21,'LUISA KEYTHELEEN MENDES CAPELA','luisa.keytheleen.mendes.capela@escola.com',21),(22,'MARIA APARECIDA ROCHA PEREIRA','maria.aparecida.rocha.pereira@escola.com',22),(23,'MARIA EDUARDA SILVA DE SOUSA','maria.eduarda.silva.de.sousa@escola.com',23),(24,'MATHEUS ALVES SIQUEIRA','matheus.alves.siqueira@escola.com',24),(25,'REINALDO FERREIRA BARBOSA FILHO','reinaldo.ferreira.barbosa.filho@escola.com',25),(26,'SAMYA VITORIA TRINDADE DE MORAIS','samya.vitoria.trindade.de.morais@escola.com',26),(27,'SOPHIA BARATA DA CRUZ','sophia.barata.da.cruz@escola.com',27),(28,'WILLIAN RAMON DA SILVA NASCIMENTO','willian.ramon.da.silva.nascimento@escola.com',28),(29,'YASMIN GOMES SIQUEIRA','yasmin.gomes.siqueira@escola.com',29),(30,'YASMIN SOUZA DE OLIVEIRA','yasmin.souza.de.oliveira@escola.com',30),(31,'ADRIAN CARDOSO SOARES','adrian.cardoso.soares@escola.com',1),(32,'ADRIANO PEREIRA CORREA','adriano.pereira.correa@escola.com',2),(33,'ALICIANE BARBOSA AMADOR','aliciane.barbosa.amador@escola.com',3),(34,'ANDRE LUIZ DA SILVA FERNANDES','andre.luiz.da.silva.fernandes@escola.com',4),(35,'ANDSON CONCEICAO DA SILVA','andson.conceicao.da.silva@escola.com',5),(36,'DANIELI SANTOS DA LUZ','danieli.santos.da.luz@escola.com',6),(37,'DAVI ATAIDE DOS SANTOS','davi.ataide.dos.santos@escola.com',7),(38,'DAVID LUCAS BRAGA DA CONCEICAO','david.lucas.braga.da.conceicao@escola.com',8),(39,'EDINEY BORRALHOS TORRES','ediney.borralhos.torres@escola.com',9),(40,'ELAINE CRISTINA REIS DA CRUZ','elaine.cristina.reis.da.cruz@escola.com',10),(41,'EMILLY DE OLIVEIRA ARAUJO','emilly.de.oliveira.araujo@escola.com',11),(42,'FABRICIO SILVA DA COSTA','fabricio.silva.da.costa@escola.com',12),(43,'FELIPE FERNANDO ROCHA DA COSTA','felipe.fernando.rocha.da.costa@escola.com',13),(44,'HELOISA RAIOL DA CRUZ','heloisa.raiol.da.cruz@escola.com',14),(45,'ISAIAS DOS SANTOS MOUTA','isaias.dos.santos.mouta@escola.com',15),(46,'JADSON ALEX SILVA E SILVA','jadson.alex.silva.e.silva@escola.com',16),(47,'JESSICA DA CONCEICAO CUNHA','jessica.da.conceicao.cunha@escola.com',17),(48,'JORGE JEUDE WARISS GAIA','jorge.jeude.wariss.gaia@escola.com',18),(49,'LUIS FELIPE GABRIEL SOUSA COUTINHO','luis.felipe.gabriel.sousa.coutinho@escola.com',19),(50,'MARIA FERNANDA SANTOS DE OLIVEIRA','maria.fernanda.santos.de.oliveira@escola.com',20),(51,'MONNA ZAFFIRA DA SILVA PIMENTEL','monna.zaffira.da.silva.pimentel@escola.com',21),(52,'MURILO HENRIQUE DA CRUZ SOUTO','murilo.henrique.da.cruz.souto@escola.com',22),(53,'NATHALIA PRISCILA DA SILVA CARDOSO','nathalia.priscila.da.silva.cardoso@escola.com',23),(54,'RYZON DIAS DA SILVA','ryzon.dias.da.silva@escola.com',24),(55,'VINICIUS DE SOUSA MONTEIRO FERREIRA','vinicius.de.sousa.monteiro.ferreira@escola.com',25);
/*!40000 ALTER TABLE `classes_student` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `classes_student_classes`
--

DROP TABLE IF EXISTS `classes_student_classes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `classes_student_classes` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `student_id` bigint NOT NULL,
  `class_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `student_id` (`student_id`),
  KEY `class_id` (`class_id`),
  CONSTRAINT `classes_student_classes_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `classes_student` (`id`) ON DELETE CASCADE,
  CONSTRAINT `classes_student_classes_ibfk_2` FOREIGN KEY (`class_id`) REFERENCES `classes_class` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `classes_student_classes`
--

LOCK TABLES `classes_student_classes` WRITE;
/*!40000 ALTER TABLE `classes_student_classes` DISABLE KEYS */;
INSERT INTO `classes_student_classes` VALUES (1,1,1),(2,2,1),(3,3,1),(4,4,1),(5,5,1),(6,6,1),(7,7,1),(8,8,1),(9,9,1),(10,10,1),(11,11,1),(12,12,1),(13,13,1),(14,14,1),(15,15,1),(16,16,1),(17,17,1),(18,18,1),(19,19,1),(20,20,1),(21,21,1),(22,22,1),(23,23,1),(24,24,1),(25,25,1),(26,26,1),(27,27,1),(28,28,1),(29,29,1),(30,30,1),(31,31,2),(32,32,2),(33,33,2),(34,34,2),(35,35,2),(36,36,2),(37,37,2),(38,38,2),(39,39,2),(40,40,2),(41,41,2),(42,42,2),(43,43,2),(44,44,2),(45,45,2),(46,46,2),(47,47,2),(48,48,2),(49,49,2),(50,50,2),(51,51,2),(52,52,2),(53,53,2),(54,54,2),(55,55,2);
/*!40000 ALTER TABLE `classes_student_classes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_accounts_customuser_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_accounts_customuser_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_customuser` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (6,'accounts','customuser'),(1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(11,'classes','class'),(10,'classes','student'),(4,'contenttypes','contenttype'),(7,'questions','questao'),(8,'questions','questaosimulado'),(9,'questions','simulado'),(5,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2024-11-18 01:36:11.461778'),(2,'contenttypes','0002_remove_content_type_name','2024-11-18 01:36:11.682559'),(3,'auth','0001_initial','2024-11-18 01:36:12.496740'),(4,'auth','0002_alter_permission_name_max_length','2024-11-18 01:36:12.644563'),(5,'auth','0003_alter_user_email_max_length','2024-11-18 01:36:12.664332'),(6,'auth','0004_alter_user_username_opts','2024-11-18 01:36:12.677687'),(7,'auth','0005_alter_user_last_login_null','2024-11-18 01:36:12.700606'),(8,'auth','0006_require_contenttypes_0002','2024-11-18 01:36:12.708631'),(9,'auth','0007_alter_validators_add_error_messages','2024-11-18 01:36:12.727981'),(10,'auth','0008_alter_user_username_max_length','2024-11-18 01:36:12.745684'),(11,'auth','0009_alter_user_last_name_max_length','2024-11-18 01:36:12.761067'),(12,'auth','0010_alter_group_name_max_length','2024-11-18 01:36:12.798281'),(13,'auth','0011_update_proxy_permissions','2024-11-18 01:36:12.833253'),(14,'auth','0012_alter_user_first_name_max_length','2024-11-18 01:36:12.848986'),(15,'accounts','0001_initial','2024-11-18 01:36:13.666490'),(16,'admin','0001_initial','2024-11-18 01:36:13.938770'),(17,'admin','0002_logentry_remove_auto_add','2024-11-18 01:36:13.953329'),(18,'admin','0003_logentry_add_action_flag_choices','2024-11-18 01:36:14.004350'),(19,'questions','0001_initial','2024-11-18 01:36:14.612212'),(20,'sessions','0001_initial','2024-11-18 01:36:14.672315'),(21,'classes','0001_initial','2024-11-19 13:18:25.679017'),(22,'classes','0002_alter_class_options_alter_student_options_and_more','2024-11-19 18:45:31.028892'),(23,'classes','0003_alter_student_options_student_active_and_more','2024-11-23 19:07:20.942857'),(24,'classes','0004_alter_student_name_alter_student_registration_number_and_more','2024-11-23 19:40:31.982363'),(25,'classes','0005_alter_student_options_remove_student_id_and_more','2024-11-23 20:13:01.710390'),(26,'classes','0006_alter_student_options_alter_student_student_id','2024-11-23 20:13:02.163389'),(27,'classes','0007_alter_student_student_id','2024-11-24 08:47:02.853150'),(28,'classes','0001_initial','2024-11-24 06:48:58.000000');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('hcqj0yvlvfa06b2spepeyd6oo8lnt2ei','.eJxVjEEOwiAQRe_C2pAAMoBL956BDAwjVQNJaVfGu9smXej2v_f-W0RclxrXUeY4kbgII06_W8L8LG0H9MB27zL3tsxTkrsiDzrkrVN5XQ_376DiqFud2bG21hSPGiBkUgjInJMDRSZp740F4jOjAu1MgUCKNikrHxQVFp8v_Hs4oQ:1tDUE5:gXmW5sm5CTPIrvIOCaaheRdxLNU3fXmB5ly9X3YyTys','2024-12-03 19:49:29.795313');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `questions_questao`
--

DROP TABLE IF EXISTS `questions_questao`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `questions_questao` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `disciplina` varchar(100) NOT NULL,
  `conteudo` varchar(100) NOT NULL,
  `enunciado` longtext NOT NULL,
  `imagem` varchar(100) DEFAULT NULL,
  `alternativa_a` longtext NOT NULL,
  `alternativa_b` longtext NOT NULL,
  `alternativa_c` longtext NOT NULL,
  `alternativa_d` longtext NOT NULL,
  `alternativa_e` longtext NOT NULL,
  `resposta_correta` varchar(1) NOT NULL,
  `nivel_dificuldade` varchar(1) NOT NULL,
  `data_criacao` datetime(6) NOT NULL,
  `ultima_modificacao` datetime(6) NOT NULL,
  `professor_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `questions_questao_professor_id_d99af72d_fk_accounts_` (`professor_id`),
  CONSTRAINT `questions_questao_professor_id_d99af72d_fk_accounts_` FOREIGN KEY (`professor_id`) REFERENCES `accounts_customuser` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `questions_questao`
--

LOCK TABLES `questions_questao` WRITE;
/*!40000 ALTER TABLE `questions_questao` DISABLE KEYS */;
INSERT INTO `questions_questao` VALUES (1,'Matemática','Porcentagem','<p>Em determinado m&ecirc;s, o consumo de energia el&eacute;trica da resid&ecirc;ncia de uma fam&iacute;lia foi de 400 kWh. Achando que o valor da conta estava alto, os membros da fam&iacute;lia decidiram diminu&iacute;-lo e estabeleceram a meta de reduzir o consumo em 40%. Come&ccedil;aram trocando a geladeira, de consumo mensal igual a 90 kWh, por outra, de consumo mensal igual a 54 kWh, e realizaram algumas mudan&ccedil;as na rotina de casa:</p>\r\n\r\n<p>&nbsp;</p>\r\n\r\n<p>&nbsp;</p>\r\n\r\n<p>&bull; reduzir o tempo de banho dos moradores, economizando 30 kWh por m&ecirc;s;</p>\r\n\r\n<p>&nbsp;</p>\r\n\r\n<p>&bull; reduzir o tempo em que o ferro de passar roupas fica ligado, economizando 14 kWh por m&ecirc;s;</p>\r\n\r\n<p>&nbsp;</p>\r\n\r\n<p>&bull; diminuir a quantidade de l&acirc;mpadas acesas no per&iacute;odo da noite, conseguindo uma redu&ccedil;&atilde;o de 10 kWh mensais.</p>\r\n\r\n<p>&nbsp;</p>\r\n\r\n<p>&nbsp;</p>\r\n\r\n<p>&nbsp;</p>\r\n\r\n<p>No entanto, observaram que, mesmo assim, n&atilde;o atingiriam a meta estabelecida e precisariam decidir outras maneiras para diminuir o consumo de energia.</p>\r\n\r\n<p>&nbsp;</p>\r\n\r\n<p>&nbsp;</p>\r\n\r\n<p>De modo a atingir essa meta, o consumo mensal de energia, em quilowatt-hora, ainda precisa diminui</p>','','<p>j</p>','<p>&nbsp;</p>\r\n\r\n<p>&nbsp;</p>','<p>&nbsp;</p>\r\n\r\n<p>&nbsp;</p>','<p>&nbsp;</p>\r\n\r\n<p>&nbsp;</p>','<p>&nbsp;</p>\r\n\r\n<p>&nbsp;</p>','C','F','2024-11-18 01:44:46.497222','2024-11-18 01:44:46.497222',1),(2,'Matemática','l','<p>Um atleta produz sua pr&oacute;pria refei&ccedil;&atilde;o com custo fixo de R$ 10,00. Ela &eacute; composta por 400 g de frango, 600 g de batata-doce e uma hortali&ccedil;a. Atualmente, os pre&ccedil;os dos produtos para essa refei&ccedil;&atilde;o s&atilde;o:<br />\r\n<img alt=\"Imagem associada para resolução da questão\" src=\"https://arquivos.qconcursos.com/images/provas/85794/58b25d5160b0da0f04a1.png\" /><br />\r\n&nbsp;&nbsp;&nbsp;&nbsp;Em rela&ccedil;&atilde;o a esses pre&ccedil;os, haver&aacute; um aumento de 50% no pre&ccedil;o do quilograma de batata-doce, e os outros pre&ccedil;os n&atilde;o ser&atilde;o alterados. O atleta deseja manter o custo da refei&ccedil;&atilde;o, a quantidade de batata-doce e a hortali&ccedil;a. Portanto, ter&aacute; que reduzir a quantidade de frango.<br />\r\nQual deve ser a redu&ccedil;&atilde;o percentual da quantidade de frango para que o atleta alcance seu objetivo?</p>','','<p>s</p>\r\n\r\n<p>&nbsp;</p>','<p>jh</p>','<p>&nbsp;k</p>','<p>n</p>','<p>h</p>','E','M','2024-11-18 01:45:30.652720','2024-11-18 01:45:30.652720',1),(3,'Matemática','Porcentagem','<p>Em uma campanha promocional de uma loja, um cliente gira uma roleta, conforme a apresentada no esquema, almejando obter um desconto sobre o valor total de sua compra. O resultado &eacute; o que est&aacute; marcado na regi&atilde;o apontada pela seta, sendo que todas as regi&otilde;es s&atilde;o congruentes. Al&eacute;m disso, um dispositivo impede que a seta venha a apontar exatamente para a linha de fronteira entre duas regi&otilde;es adjacentes. Um cliente realiza uma compra e gira a roleta, torcendo para obter o desconto m&aacute;ximo.<br />\r\n<img alt=\"Imagem associada para resolução da questão\" src=\"https://arquivos.qconcursos.com/images/provas/79768/8cdd43f93d76ef6bbd50.png\" /><br />\r\n<br />\r\nA probabilidade, em porcentagem, de esse cliente ganhar o desconto m&aacute;ximo com um &uacute;nico giro da roleta &eacute; melhor aproximada por</p>','','<p>n</p>','<p>k</p>','<p>b</p>','<p>n</p>','<p>k</p>','C','D','2024-11-18 01:46:13.563975','2024-11-18 01:46:13.563975',1),(4,'Biologia','Citologia','<p>Qual a organela respons&aacute;vel pela respira&ccedil;&atilde;o celular?</p>\r\n\r\n<p>&nbsp;</p>','','<p>Mitocondria</p>','<p>askjh</p>','<p>hj</p>','<p>hlj</p>','<p>jh</p>','A','M','2024-11-19 11:53:18.588318','2024-11-19 11:53:18.589319',1),(5,'Matemática','Análise de Gráficos e Tabelas','<p>A &aacute;gua para o abastecimento de um pr&eacute;dio &eacute; armazenada em um sistema formado por dois reservat&oacute;rios id&ecirc;nticos, em formato de bloco retangular, ligados entre si por um cano igual ao cano de entrada, conforme ilustra a figura.</p>\r\n\r\n<p>&nbsp;</p>\r\n\r\n<p><img alt=\"Imagem associada para resolução da questão\" src=\"https://arquivos.qconcursos.com/images/provas/56023/eb9ef597838880e43051.png\" /></p>\r\n\r\n<p>A &aacute;gua entra no sistema pelo cano de entrada no Reservat&oacute;rio 1 a uma vaz&atilde;o constante e, ao atingir o n&iacute;vel do cano de liga&ccedil;&atilde;o, passa a abastecer o Reservat&oacute;rio 2. Suponha que, inicialmente, os dois reservat&oacute;rios estejam vazios.</p>\r\n\r\n<p>Qual dos gr&aacute;ficos melhor descrever&aacute; a altura&nbsp;h&nbsp;do n&iacute;vel da &aacute;gua no Reservat&oacute;rio 1, em fun&ccedil;&atilde;o do volume&nbsp;V&nbsp;de &aacute;gua no sistema?</p>','','<p><img alt=\"Imagem associada para resolução da questão\" src=\"https://s3.amazonaws.com/qcon-assets-production/images/provas/56023/e576217dcffd5893eb5e.png\" /></p>','<p><img alt=\"Imagem associada para resolução da questão\" src=\"https://s3.amazonaws.com/qcon-assets-production/images/provas/56023/2d8ae19f5cb104f10cc9.png\" /></p>','<p><img alt=\"Imagem associada para resolução da questão\" src=\"https://s3.amazonaws.com/qcon-assets-production/images/provas/56023/65c435699bd282a0e377.png\" /></p>','<p><img alt=\"Imagem associada para resolução da questão\" src=\"https://s3.amazonaws.com/qcon-assets-production/images/provas/56023/65c435699bd282a0e377.png\" /></p>','<p><img alt=\"Imagem associada para resolução da questão\" src=\"https://s3.amazonaws.com/qcon-assets-production/images/provas/56023/3998ebb3b45aa859ce37.png\" /></p>','D','F','2024-11-19 19:53:31.669213','2024-11-19 19:53:31.669213',3),(6,'Matemática','Geometria Plana','<p>A manchete demonstra que o transporte de grandes cargas representa cada vez mais preocupa&ccedil;&atilde;o quando feito em vias urbanas.</p>\r\n\r\n<p><strong>Caminh&atilde;o entala em viaduto no Centro</strong></p>\r\n\r\n<p>Um caminh&atilde;o de grande porte entalou embaixo do viaduto no cruzamento das avenidas Borges de Medeiros e Loureiro da Silva no sentido Centro-Bairro, pr&oacute;ximo &agrave; Ponte de Pedra, na capital. Esse ve&iacute;culo vinha de S&atilde;o Paulo para Porto Alegre e transportava tr&ecirc;s grandes tubos, conforme ilustrado na foto.</p>\r\n\r\n<figure>&nbsp;</figure>\r\n\r\n<p><img alt=\"Questão 153 - ENEM 2017 - Questão 153,Geometria Plana\" data-lazyloaded=\"1\" data-ll-status=\"loaded\" data-sizes=\"(max-width: 332px) 100vw, 332px\" data-src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/A-manchete-demonstra-que-o-transporte-de-grandes-cargas-representa-cada-vez-mais-preocupacao-quando-feito-em-vias-urbanas.png\" data-srcset=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/A-manchete-demonstra-que-o-transporte-de-grandes-cargas-representa-cada-vez-mais-preocupacao-quando-feito-em-vias-urbanas.png 332w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/A-manchete-demonstra-que-o-transporte-de-grandes-cargas-representa-cada-vez-mais-preocupacao-quando-feito-em-vias-urbanas-300x167.png 300w\" decoding=\"async\" fetchpriority=\"high\" height=\"185\" sizes=\"(max-width: 332px) 100vw, 332px\" src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/A-manchete-demonstra-que-o-transporte-de-grandes-cargas-representa-cada-vez-mais-preocupacao-quando-feito-em-vias-urbanas.png\" srcset=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/A-manchete-demonstra-que-o-transporte-de-grandes-cargas-representa-cada-vez-mais-preocupacao-quando-feito-em-vias-urbanas.png 332w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/A-manchete-demonstra-que-o-transporte-de-grandes-cargas-representa-cada-vez-mais-preocupacao-quando-feito-em-vias-urbanas-300x167.png 300w\" title=\"Questão 153 - ENEM 2017 - Questão 153,Geometria Plana\" width=\"332\" /></p>\r\n\r\n<p>Considere que o&nbsp;<strong>raio externo de cada cano da imagem seja 0,60 m</strong>&nbsp;e que eles estejam em cima de uma carroceria cuja parte&nbsp;<strong>superior est&aacute; a 1,30 m do solo</strong>. O desenho representa a vista traseira do empilhamento dos canos.</p>\r\n\r\n<figure>&nbsp;</figure>\r\n\r\n<p><img alt=\"Questão 153 - ENEM 2017 - Questão 153,Geometria Plana\" data-lazyloaded=\"1\" data-ll-status=\"loaded\" data-src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/UMCAMI1.png\" decoding=\"async\" height=\"202\" src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/UMCAMI1.png\" title=\"Questão 153 - ENEM 2017 - Questão 153,Geometria Plana\" width=\"290\" /></p>\r\n\r\n<p>A margem de seguran&ccedil;a recomendada para que um ve&iacute;culo passe sob um viaduto &eacute; que a altura total do ve&iacute;culo com a carga seja, no&nbsp;<strong>m&iacute;nimo, 0,50 m menor do que a altura do v&atilde;o do viaduto</strong>.</p>\r\n\r\n<p>Considere&nbsp;<strong>1,7 como aproxima&ccedil;&atilde;o para&nbsp;</strong><strong>&radic;3.</strong></p>\r\n\r\n<p>Qual deveria ser a&nbsp;<strong>altura m&iacute;nima do viaduto,</strong>&nbsp;em metro, para que esse caminh&atilde;o pudesse passar com seguran&ccedil;a sob seu v&atilde;o?</p>','','<p>2,82.</p>','<p>3,52.</p>','<p>3,70.</p>','<p>4,02.</p>','<p>4,20.</p>','D','M','2024-11-19 19:54:54.180555','2024-11-19 19:54:54.180555',3),(7,'Matemática','Geometria Plana','<p>Um menino acaba de se mudar para um novo bairro e deseja ir &agrave; padaria. Pediu ajuda a um amigo que lhe forneceu um mapa com pontos numerados, que representam cinco locais de interesse,&nbsp;<strong>entre os quais est&aacute; a padaria</strong>. Al&eacute;m disso, o amigo passou as seguintes instru&ccedil;&otilde;es: a&nbsp;<strong>partir do ponto em que voc&ecirc; se encontra, representado pela letra X</strong>,&nbsp;<strong>ande para oeste, vire &agrave; direita na primeira rua que encontrar, siga em frente e vire &agrave; esquerda na pr&oacute;xima rua</strong>. A padaria estar&aacute; logo a seguir</p>\r\n\r\n<figure><img alt=\"Questão 154 - ENEM 2017 - Questão 154,Geometria Plana\" data-lazyloaded=\"1\" data-ll-status=\"loaded\" data-src=\"https://lh5.googleusercontent.com/zpKDSEMHCL5-vVA2BzesEu6DkmGGlBblt0Uix_v3g8Mt71yiO3UeQZ9s0gp79xFHpChQ_OisTJhiIztQUPVAtlD3Z7-dcqD9F-nOA5Q10YsmqNPIZzaV9fbPDiOOmQJY9n4fcRo35j3-tjMYqr5GnGw\" decoding=\"async\" height=\"226\" src=\"https://lh5.googleusercontent.com/zpKDSEMHCL5-vVA2BzesEu6DkmGGlBblt0Uix_v3g8Mt71yiO3UeQZ9s0gp79xFHpChQ_OisTJhiIztQUPVAtlD3Z7-dcqD9F-nOA5Q10YsmqNPIZzaV9fbPDiOOmQJY9n4fcRo35j3-tjMYqr5GnGw\" title=\"Questão 154 - ENEM 2017 - Questão 154,Geometria Plana\" width=\"338\" /></figure>\r\n\r\n<p>A&nbsp;<strong>padaria est&aacute; representada pelo ponto numerado</strong>&nbsp;com</p>','','<p>1.</p>','<p>2.</p>','<p>3.</p>','<p>4.</p>','<p>5.</p>','A','F','2024-11-19 19:56:00.685248','2024-11-19 19:56:00.685248',3),(8,'Matemática','Estatística','<p>Tr&ecirc;s alunos, X, Y e Z, est&atilde;o matriculados em um curso de ingl&ecirc;s. Para avaliar esses alunos, o professor optou por fazer cinco provas. Para que seja aprovado nesse curso, o&nbsp;<strong>aluno dever&aacute; ter a m&eacute;dia aritm&eacute;tica das notas das cinco provas maior ou igual a 6</strong>. Na tabela, est&atilde;o dispostas as notas que cada aluno tirou em cada prova.</p>\r\n\r\n<p><img alt=\"Questão 155 - ENEM 2017 - Questão 155,Estatística\" data-lazyloaded=\"1\" data-ll-status=\"loaded\" data-sizes=\"(max-width: 380px) 100vw, 380px\" data-src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Tres-alunos-X-Y-e-Z-estao-matriculados-em-um-curso-de-ingles.-Para-avaliar-esses-alunos-o-professor-optou-por-fazer-cinco-provas.png\" data-srcset=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Tres-alunos-X-Y-e-Z-estao-matriculados-em-um-curso-de-ingles.-Para-avaliar-esses-alunos-o-professor-optou-por-fazer-cinco-provas.png 380w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Tres-alunos-X-Y-e-Z-estao-matriculados-em-um-curso-de-ingles.-Para-avaliar-esses-alunos-o-professor-optou-por-fazer-cinco-provas-300x105.png 300w\" decoding=\"async\" fetchpriority=\"high\" height=\"133\" sizes=\"(max-width: 380px) 100vw, 380px\" src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Tres-alunos-X-Y-e-Z-estao-matriculados-em-um-curso-de-ingles.-Para-avaliar-esses-alunos-o-professor-optou-por-fazer-cinco-provas.png\" srcset=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Tres-alunos-X-Y-e-Z-estao-matriculados-em-um-curso-de-ingles.-Para-avaliar-esses-alunos-o-professor-optou-por-fazer-cinco-provas.png 380w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Tres-alunos-X-Y-e-Z-estao-matriculados-em-um-curso-de-ingles.-Para-avaliar-esses-alunos-o-professor-optou-por-fazer-cinco-provas-300x105.png 300w\" title=\"Questão 155 - ENEM 2017 - Questão 155,Estatística\" width=\"380\" /></p>\r\n\r\n<p>Com base nos dados da tabela e nas informa&ccedil;&otilde;es dadas,&nbsp;<strong>ficar&aacute;(&atilde;o) reprovado(s)</strong></p>','','<p>apenas o aluno Y</p>','<p>apenas o aluno Z</p>','<p>apenas os alunos x e y</p>','<p>apenas os alunos x e z</p>','<p>os alunos x, y, z</p>','B','M','2024-11-19 19:57:22.766268','2024-11-19 19:57:22.766268',3),(13,'Matemática','Lógica','<p>Uma bicicleta do tipo mountain bike tem uma&nbsp;<strong>coroa com 3 engrenagens e uma catraca com 6 engrenagens,</strong>&nbsp;que, combinadas entre si,&nbsp;<strong>determinam 18 marchas</strong>&nbsp;(n&uacute;mero de engrenagens da coroa vezes o n&uacute;mero de engrenagens da catraca).</p>\r\n\r\n<p><img alt=\"Questão 159 - ENEM 2017 - Questão 159,Lógica\" data-lazyloaded=\"1\" data-ll-status=\"loaded\" data-sizes=\"(max-width: 516px) 100vw, 516px\" data-src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Uma-bicicleta-do-tipo-mountain-bike-tem-uma-coroa-com-3-engrenagens-e-uma-catraca-com-6-engrenagens.png\" data-srcset=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Uma-bicicleta-do-tipo-mountain-bike-tem-uma-coroa-com-3-engrenagens-e-uma-catraca-com-6-engrenagens.png 516w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Uma-bicicleta-do-tipo-mountain-bike-tem-uma-coroa-com-3-engrenagens-e-uma-catraca-com-6-engrenagens-300x151.png 300w\" decoding=\"async\" fetchpriority=\"high\" height=\"260\" sizes=\"(max-width: 516px) 100vw, 516px\" src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Uma-bicicleta-do-tipo-mountain-bike-tem-uma-coroa-com-3-engrenagens-e-uma-catraca-com-6-engrenagens.png\" srcset=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Uma-bicicleta-do-tipo-mountain-bike-tem-uma-coroa-com-3-engrenagens-e-uma-catraca-com-6-engrenagens.png 516w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Uma-bicicleta-do-tipo-mountain-bike-tem-uma-coroa-com-3-engrenagens-e-uma-catraca-com-6-engrenagens-300x151.png 300w\" title=\"Questão 159 - ENEM 2017 - Questão 159,Lógica\" width=\"516\" /></p>\r\n\r\n<p>Os&nbsp;<strong>n&uacute;meros de dentes</strong>&nbsp;das engrenagens das coroas e das catracas dessa bicicleta est&atilde;o listados no quadro.</p>\r\n\r\n<p><img alt=\"Questão 159 - ENEM 2017 - Questão 159,Lógica\" data-lazyloaded=\"1\" data-ll-status=\"loaded\" data-sizes=\"(max-width: 619px) 100vw, 619px\" data-src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/que-combinadas-entre-si-determinam-18-marchas-numero-de-engrenagens-da-coroa-vezes-o-numero-de-engrenagens-da-catraca.png\" data-srcset=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/que-combinadas-entre-si-determinam-18-marchas-numero-de-engrenagens-da-coroa-vezes-o-numero-de-engrenagens-da-catraca.png 619w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/que-combinadas-entre-si-determinam-18-marchas-numero-de-engrenagens-da-coroa-vezes-o-numero-de-engrenagens-da-catraca-300x43.png 300w\" decoding=\"async\" height=\"88\" sizes=\"(max-width: 619px) 100vw, 619px\" src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/que-combinadas-entre-si-determinam-18-marchas-numero-de-engrenagens-da-coroa-vezes-o-numero-de-engrenagens-da-catraca.png\" srcset=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/que-combinadas-entre-si-determinam-18-marchas-numero-de-engrenagens-da-coroa-vezes-o-numero-de-engrenagens-da-catraca.png 619w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/que-combinadas-entre-si-determinam-18-marchas-numero-de-engrenagens-da-coroa-vezes-o-numero-de-engrenagens-da-catraca-300x43.png 300w\" title=\"Questão 159 - ENEM 2017 - Questão 159,Lógica\" width=\"619\" /></p>\r\n\r\n<p>Sabe-se que o&nbsp;<strong>n&uacute;mero de voltas efetuadas pela roda traseira a cada pedalada &eacute; calculado dividindo-se a quantidade de dentes da coroa pela quantidade de dentes da catraca.</strong></p>\r\n\r\n<p>Durante um passeio em uma bicicleta desse tipo, deseja-se fazer um&nbsp;<strong>percurso o mais devagar poss&iacute;vel, escolhendo, para isso, uma das seguintes combina&ccedil;&otilde;es de engrenagens (coroa x catraca):</strong></p>\r\n\r\n<p><img alt=\"Questão 159 - ENEM 2017 - Questão 159,Lógica\" data-lazyloaded=\"1\" data-ll-status=\"loaded\" data-sizes=\"(max-width: 457px) 100vw, 457px\" data-src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Os-numeros-de-dentes-das-engrenagens-das-coroas-e-das-catracas-dessa-bicicleta-estao-listados-no-quadro.png\" data-srcset=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Os-numeros-de-dentes-das-engrenagens-das-coroas-e-das-catracas-dessa-bicicleta-estao-listados-no-quadro.png 457w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Os-numeros-de-dentes-das-engrenagens-das-coroas-e-das-catracas-dessa-bicicleta-estao-listados-no-quadro-300x39.png 300w\" decoding=\"async\" height=\"60\" sizes=\"(max-width: 457px) 100vw, 457px\" src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Os-numeros-de-dentes-das-engrenagens-das-coroas-e-das-catracas-dessa-bicicleta-estao-listados-no-quadro.png\" srcset=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Os-numeros-de-dentes-das-engrenagens-das-coroas-e-das-catracas-dessa-bicicleta-estao-listados-no-quadro.png 457w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Os-numeros-de-dentes-das-engrenagens-das-coroas-e-das-catracas-dessa-bicicleta-estao-listados-no-quadro-300x39.png 300w\" title=\"Questão 159 - ENEM 2017 - Questão 159,Lógica\" width=\"457\" /></p>\r\n\r\n<p>A&nbsp;<strong>combina&ccedil;&atilde;o escolhida</strong>&nbsp;para realizar esse passeio da forma desejada &eacute;</p>','','<p>I</p>','<p>II</p>','<p>II</p>','<p>IV</p>','<p>V</p>','D','F','2024-11-19 20:24:09.208817','2024-11-19 20:24:09.208817',3),(17,'Matemática','Porcentagem','<p>Uma desenhista projetista dever&aacute; desenhar uma tampa de panela em forma circular. Para realizar esse desenho, ela disp&otilde;e, no momento, de apenas um compasso, cujo&nbsp;<strong>comprimento das hastes &eacute; de 10 cm</strong>, um transferidor e uma folha de papel com um plano cartesiano. Para esbo&ccedil;ar o desenho dessa tampa, ela afastou as hastes do compasso de forma que o &acirc;ngulo formado por&nbsp;<strong>elas fosse de 120</strong><strong><sup>o</sup></strong>. A ponta seca est&aacute; representada pelo ponto C, a ponta do grafite est&aacute; representada pelo ponto B e a cabe&ccedil;a do compasso est&aacute; representada pelo ponto A conforme a figura.</p>\r\n\r\n<p><img alt=\"Questão 156 - ENEM 2017 - Questão 156,Trigonometria\" src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Uma-desenhista-projetista-devera-desenhar-uma-tampa-de-panela-em-forma-circular.png\" /></p>\r\n\r\n<p>Ap&oacute;s concluir o desenho, ela o encaminha para o setor de produ&ccedil;&atilde;o. Ao receber o desenho com a indica&ccedil;&atilde;o do raio da tampa,&nbsp;<strong>verificar&aacute; em qual intervalo este se encontra e decidir&aacute; o tipo de material&nbsp;</strong>a ser utilizado na sua fabrica&ccedil;&atilde;o, de acordo com os dados.</p>\r\n\r\n<p><img alt=\"Questão 156 - ENEM 2017 - Questão 156,Trigonometria\" data-lazyloaded=\"1\" data-ll-status=\"loaded\" data-sizes=\"(max-width: 341px) 100vw, 341px\" data-src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Para-realizar-esse-desenho-ela-dispoe-no-momento-de-apenas-um-compasso-cujo-comprimento-das-hastes-e-de-10-cm.png\" data-srcset=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Para-realizar-esse-desenho-ela-dispoe-no-momento-de-apenas-um-compasso-cujo-comprimento-das-hastes-e-de-10-cm.png 341w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Para-realizar-esse-desenho-ela-dispoe-no-momento-de-apenas-um-compasso-cujo-comprimento-das-hastes-e-de-10-cm-300x149.png 300w\" decoding=\"async\" height=\"169\" sizes=\"(max-width: 341px) 100vw, 341px\" src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Para-realizar-esse-desenho-ela-dispoe-no-momento-de-apenas-um-compasso-cujo-comprimento-das-hastes-e-de-10-cm.png\" srcset=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Para-realizar-esse-desenho-ela-dispoe-no-momento-de-apenas-um-compasso-cujo-comprimento-das-hastes-e-de-10-cm.png 341w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Para-realizar-esse-desenho-ela-dispoe-no-momento-de-apenas-um-compasso-cujo-comprimento-das-hastes-e-de-10-cm-300x149.png 300w\" title=\"Questão 156 - ENEM 2017 - Questão 156,Trigonometria\" width=\"341\" /></p>\r\n\r\n<p>O&nbsp;<strong>tipo de material a ser utilizado pelo setor de produ&ccedil;&atilde;o&nbsp;</strong>ser&aacute;</p>','','<p>I</p>','<p>II</p>','<p>III</p>','<p>IV</p>','<p>V</p>','D','M','2024-11-19 20:43:26.105087','2024-11-19 20:43:26.105087',3),(19,'Matemática','Análise de Gráficos e Tabelas','<p>O comit&ecirc; organizador da Copa do Mundo 2014 criou a logomarca da Copa, composta de uma figura plana e o slogan &ldquo;Juntos num s&oacute; ritmo&rdquo;, com m&atilde;os que se unem formando a ta&ccedil;a Fifa.&nbsp;<strong>Considere que o comit&ecirc; organizador resolvesse utilizar todas as cores da bandeira nacional (verde, amarelo, azul e branco)</strong>&nbsp;para colorir a logomarca, de forma que&nbsp;<strong>regi&otilde;es vizinhas tenham cores diferentes.</strong></p>\r\n\r\n<p><img alt=\"Questão 160 - ENEM 2017 - Questão 160,Análise Combinatória\" data-lazyloaded=\"1\" data-ll-status=\"loaded\" data-sizes=\"(max-width: 513px) 100vw, 513px\" data-src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/O-comite-organizador-da-Copa-do-Mundo-2014-criou-a-logomarca-da-Copa-composta-de-uma-figura-plana-e-o-slogan-Juntos-num-so-ritmo-com-maos-que-se-unem-formando-a-taca-Fifa.png\" data-srcset=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/O-comite-organizador-da-Copa-do-Mundo-2014-criou-a-logomarca-da-Copa-composta-de-uma-figura-plana-e-o-slogan-Juntos-num-so-ritmo-com-maos-que-se-unem-formando-a-taca-Fifa.png 513w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/O-comite-organizador-da-Copa-do-Mundo-2014-criou-a-logomarca-da-Copa-composta-de-uma-figura-plana-e-o-slogan-Juntos-num-so-ritmo-com-maos-que-se-unem-formando-a-taca-Fifa-300x204.png 300w\" decoding=\"async\" fetchpriority=\"high\" height=\"349\" sizes=\"(max-width: 513px) 100vw, 513px\" src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/O-comite-organizador-da-Copa-do-Mundo-2014-criou-a-logomarca-da-Copa-composta-de-uma-figura-plana-e-o-slogan-Juntos-num-so-ritmo-com-maos-que-se-unem-formando-a-taca-Fifa.png\" srcset=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/O-comite-organizador-da-Copa-do-Mundo-2014-criou-a-logomarca-da-Copa-composta-de-uma-figura-plana-e-o-slogan-Juntos-num-so-ritmo-com-maos-que-se-unem-formando-a-taca-Fifa.png 513w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/O-comite-organizador-da-Copa-do-Mundo-2014-criou-a-logomarca-da-Copa-composta-de-uma-figura-plana-e-o-slogan-Juntos-num-so-ritmo-com-maos-que-se-unem-formando-a-taca-Fifa-300x204.png 300w\" title=\"Questão 160 - ENEM 2017 - Questão 160,Análise Combinatória\" width=\"513\" /></p>\r\n\r\n<p>De&nbsp;<strong>quantas maneiras diferentes o comit&ecirc; organizador da Copa poderia pintar&nbsp;</strong>a logomarca com as cores citadas?</p>','','<p>15</p>','<p>30</p>','<p>108</p>','<p>360</p>','<p>792</p>','C','M','2024-11-19 20:46:25.046473','2024-11-19 20:46:25.046473',3),(21,'Matemática','Geometria Plana','<p>Viveiros de lagostas s&atilde;o constru&iacute;dos, por cooperativas locais de pescadores, em formato de prismas reto-retangulares, fixados ao solo e com telas flex&iacute;veis de mesma altura, capazes de suportar a corros&atilde;o marinha. Para cada viveiro a ser constru&iacute;do, a cooperativa utiliza integralmente&nbsp;<strong>100 metros lineares dessa tela, que &eacute; usada apenas nas laterais.</strong></p>\r\n\r\n<p><img alt=\"Questão 161 - ENEM 2017 - Questão 161,Geometria Espacial\" data-lazyloaded=\"1\" data-ll-status=\"loaded\" data-sizes=\"(max-width: 430px) 100vw, 430px\" data-src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Viveiros-de-lagostas-sao-construidos-por-cooperativas-locais-de-pescadores-em-formato-de-prismas-reto-retangulares.png\" data-srcset=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Viveiros-de-lagostas-sao-construidos-por-cooperativas-locais-de-pescadores-em-formato-de-prismas-reto-retangulares.png 430w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Viveiros-de-lagostas-sao-construidos-por-cooperativas-locais-de-pescadores-em-formato-de-prismas-reto-retangulares-300x177.png 300w\" decoding=\"async\" fetchpriority=\"high\" height=\"254\" sizes=\"(max-width: 430px) 100vw, 430px\" src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Viveiros-de-lagostas-sao-construidos-por-cooperativas-locais-de-pescadores-em-formato-de-prismas-reto-retangulares.png\" srcset=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Viveiros-de-lagostas-sao-construidos-por-cooperativas-locais-de-pescadores-em-formato-de-prismas-reto-retangulares.png 430w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Viveiros-de-lagostas-sao-construidos-por-cooperativas-locais-de-pescadores-em-formato-de-prismas-reto-retangulares-300x177.png 300w\" title=\"Questão 161 - ENEM 2017 - Questão 161,Geometria Espacial\" width=\"430\" /></p>\r\n\r\n<p><strong>Quais devem ser os valores de X e de Y,</strong>&nbsp;em metro, para que a &aacute;rea da base do viveiro seja&nbsp;<strong>m&aacute;xima</strong>?</p>','','<p>afsd</p>','<p>jlk hiv</p>','<p>uvy</p>','<p>iuyl</p>','<p>yyyy</p>','C','D','2024-11-19 20:49:49.772260','2024-11-19 20:49:49.772260',3),(22,'Matemática','Análise de Gráficos e Tabelas','<p>O fisiologista ingl&ecirc;s Archibald Vivian Hill prop&ocirc;s, em seus estudos, que a&nbsp;<strong>velocidade V de contra&ccedil;&atilde;o de um m&uacute;sculo ao ser submetido a um peso p &eacute; dada pela equa&ccedil;&atilde;o (p + a) (v +b) = K</strong>, com a, b e K constantes.</p>\r\n\r\n<p>Um fisioterapeuta, com o intuito de maximizar o efeito ben&eacute;fico dos exerc&iacute;cios que recomendaria a um de seus pacientes, quis estudar essa equa&ccedil;&atilde;o e a classificou desta forma:</p>\r\n\r\n<p><img alt=\"Questão 162 - ENEM 2017 - Questão 162,Geometria Analítica\" data-lazyloaded=\"1\" data-ll-status=\"loaded\" data-sizes=\"(max-width: 958px) 100vw, 958px\" data-src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/O-fisiologista-ingles-Archibald-Vivian-Hill-propos-em-seus-estudos-que-a-velocidade-V-de-contracao-de-um-musculo-ao-ser-submetido-a-um-peso-p-e-dada-pela-equacao.png\" data-srcset=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/O-fisiologista-ingles-Archibald-Vivian-Hill-propos-em-seus-estudos-que-a-velocidade-V-de-contracao-de-um-musculo-ao-ser-submetido-a-um-peso-p-e-dada-pela-equacao.png 958w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/O-fisiologista-ingles-Archibald-Vivian-Hill-propos-em-seus-estudos-que-a-velocidade-V-de-contracao-de-um-musculo-ao-ser-submetido-a-um-peso-p-e-dada-pela-equacao-300x202.png 300w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/O-fisiologista-ingles-Archibald-Vivian-Hill-propos-em-seus-estudos-que-a-velocidade-V-de-contracao-de-um-musculo-ao-ser-submetido-a-um-peso-p-e-dada-pela-equacao-768x517.png 768w\" decoding=\"async\" fetchpriority=\"high\" height=\"645\" sizes=\"(max-width: 958px) 100vw, 958px\" src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/O-fisiologista-ingles-Archibald-Vivian-Hill-propos-em-seus-estudos-que-a-velocidade-V-de-contracao-de-um-musculo-ao-ser-submetido-a-um-peso-p-e-dada-pela-equacao.png\" srcset=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/O-fisiologista-ingles-Archibald-Vivian-Hill-propos-em-seus-estudos-que-a-velocidade-V-de-contracao-de-um-musculo-ao-ser-submetido-a-um-peso-p-e-dada-pela-equacao.png 958w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/O-fisiologista-ingles-Archibald-Vivian-Hill-propos-em-seus-estudos-que-a-velocidade-V-de-contracao-de-um-musculo-ao-ser-submetido-a-um-peso-p-e-dada-pela-equacao-300x202.png 300w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/O-fisiologista-ingles-Archibald-Vivian-Hill-propos-em-seus-estudos-que-a-velocidade-V-de-contracao-de-um-musculo-ao-ser-submetido-a-um-peso-p-e-dada-pela-equacao-768x517.png 768w\" title=\"Questão 162 - ENEM 2017 - Questão 162,Geometria Analítica\" width=\"958\" /></p>\r\n\r\n<p>O fisioterapeuta analisou a depend&ecirc;ncia entre v e p na equa&ccedil;&atilde;o de Hill e a classificou de acordo com sua representa&ccedil;&atilde;o geom&eacute;trica no plano cartesiano, utilizando o par de coordenadas (p. V). Admita que K&gt; 0.</p>\r\n\r\n<p>Dispon&iacute;vel em: http://rspb.royalsocietypublishing.org. Acesso em: 14jul2015 (adaptado).</p>\r\n\r\n<p>O&nbsp;<strong>gr&aacute;fico da equa&ccedil;&atilde;o que o fisioterapeuta utilizou para maximizar o efeito dos exerc&iacute;cios &eacute; do tipo</strong></p>','','<p>j kdshkf h</p>','<p>luhui</p>','<p>&nbsp;uig&nbsp;</p>','<p>lgi</p>','<p>ygl</p>','E','M','2024-11-19 20:50:34.196506','2024-11-19 20:50:34.196506',3),(23,'Matemática','Análise de Gráficos e Tabelas','<p>Uma pessoa ganhou uma pulseira formada por&nbsp;<strong>p&eacute;rolas esf&eacute;ricas</strong>, na qual&nbsp;<strong>faltava uma das p&eacute;rolas</strong>. A figura indica a posi&ccedil;&atilde;o em que estaria faltando esta p&eacute;rola.</p>\r\n\r\n<p><img src=\"data:image/png;base64,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\" /></p>\r\n\r\n<p>Ela levou a j&oacute;ia a um joalheiro que verificou que a medida do di&acirc;metro dessas&nbsp;<strong>p&eacute;rolas era 4 mil&iacute;metros</strong>.&nbsp;<strong>Em seu estoque, as p&eacute;rolas do mesmo tipo e formato, dispon&iacute;veis para reposi&ccedil;&atilde;o, tinham di&acirc;metros iguais a: 4,025 mm; 4,100 mm; 3,970 mm; 4,080 mm e 3,099 mm.</strong></p>\r\n\r\n<p>O joalheiro ent&atilde;o colocou na pulseira a&nbsp;<strong>p&eacute;rola cujo di&acirc;metro era o mais pr&oacute;ximo</strong>&nbsp;do di&acirc;metro das p&eacute;rolas originais.</p>\r\n\r\n<p>A&nbsp;<strong>p&eacute;rola colocada na pulseira pelo joalheiro tem di&acirc;metro</strong>, em mil&iacute;metro, igual a</p>','','<p>&nbsp;h</p>','<p>lk</p>','<p>&nbsp;h</p>','<p>jk&nbsp;</p>','<p>x</p>','E','D','2024-11-19 20:53:40.999619','2024-11-19 20:53:41.000621',3),(24,'Matemática','Geometria Plana','<p>Em um parque h&aacute; dois mirantes de alturas distintas que s&atilde;o acessados por elevador panor&acirc;mico. O&nbsp;<strong>topo do mirante 1 &eacute; acessado pelo elevador 1, enquanto que o topo do mirante 2 &eacute; acessado pelo elevador 2.</strong>&nbsp;Eles encontram-se a uma dist&acirc;ncia poss&iacute;vel de ser percorrida a p&eacute;, e entre os mirantes h&aacute; um telef&eacute;rico que os liga que pode ou n&atilde;o ser utilizado pelo visitante.</p>\r\n\r\n<p><img alt=\"Questão 163 - ENEM 2017 - Questão 163,Matemática Básica\" data-lazyloaded=\"1\" data-ll-status=\"loaded\" data-sizes=\"(max-width: 471px) 100vw, 471px\" data-src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Em-um-parque-ha-dois-mirantes-de-alturas-distintas-que-sao-acessados-por-elevador-panoramico.png\" data-srcset=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Em-um-parque-ha-dois-mirantes-de-alturas-distintas-que-sao-acessados-por-elevador-panoramico.png 471w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Em-um-parque-ha-dois-mirantes-de-alturas-distintas-que-sao-acessados-por-elevador-panoramico-300x194.png 300w\" decoding=\"async\" fetchpriority=\"high\" height=\"305\" sizes=\"(max-width: 471px) 100vw, 471px\" src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Em-um-parque-ha-dois-mirantes-de-alturas-distintas-que-sao-acessados-por-elevador-panoramico.png\" srcset=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Em-um-parque-ha-dois-mirantes-de-alturas-distintas-que-sao-acessados-por-elevador-panoramico.png 471w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Em-um-parque-ha-dois-mirantes-de-alturas-distintas-que-sao-acessados-por-elevador-panoramico-300x194.png 300w\" title=\"Questão 163 - ENEM 2017 - Questão 163,Matemática Básica\" width=\"471\" /></p>\r\n\r\n<p>O acesso aos elevadores tem os&nbsp;<strong>seguintes custos</strong>:</p>\r\n\r\n<p>&bull; Subir pelo elevador 1: R$ 0,15;</p>\r\n\r\n<p>&bull; Subir pelo elevador 2: R$ 1,80;</p>\r\n\r\n<p>&bull; Descer pelo elevador 1: R$ 0,10;</p>\r\n\r\n<p>&bull; Descer pelo elevador 2: R$ 2,30.</p>\r\n\r\n<p>O&nbsp;<strong>custo da passagem do telef&eacute;rico partindo do topo do mirante 1 para o topo do mirante 2 &eacute; de R$ 2,00,</strong>&nbsp;e&nbsp;<strong>do topo do mirante 2 para o topo do mirante 1 &eacute; de R$ 2,50.</strong></p>\r\n\r\n<p>Qual &eacute; o&nbsp;<strong>menor custo,</strong>&nbsp;em real, para uma pessoa&nbsp;<strong>visitar os topos dos dois mirantes</strong>&nbsp;e retornar ao solo?</p>','','<p>&nbsp;hl</p>','<p>hl</p>','<p>hbuh</p>','<p>i</p>','<p>u</p>','D','M','2024-11-19 20:54:46.569350','2024-11-19 20:54:46.575142',3),(27,'A','as','<p>Um cientista, em seus estudos para modelar a press&atilde;o arterial de uma pessoa, utiliza uma fun&ccedil;&atilde;o do tipo&nbsp;<strong>P(t) = A + Bcos(kt) em que A, B e K&nbsp;</strong>s&atilde;o constantes reais&nbsp;<strong>positivas e t representa a vari&aacute;vel tempo, medida em segundo.</strong>&nbsp;Considere que&nbsp;<strong>um batimento card&iacute;aco representa o intervalo de tempo entre duas sucessivas press&otilde;es m&aacute;ximas.</strong></p>\r\n\r\n<p>Ao analisar um caso espec&iacute;fico, o cientista obteve os dados:</p>\r\n\r\n<p><img alt=\"Questão 166 - ENEM 2017 - Questão 166,Função Trigonométrica,SENO,COSSENO\" data-lazyloaded=\"1\" data-ll-status=\"loaded\" data-sizes=\"(max-width: 481px) 100vw, 481px\" data-src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Um-cientista-em-seus-estudos-para-modelar-a-pressao-arterial-de-uma-pessoa-utiliza-uma-funcao-do-tipo-Pt-A-Bcoskt-em-que-A-B-e-K.png\" data-srcset=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Um-cientista-em-seus-estudos-para-modelar-a-pressao-arterial-de-uma-pessoa-utiliza-uma-funcao-do-tipo-Pt-A-Bcoskt-em-que-A-B-e-K.png 481w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Um-cientista-em-seus-estudos-para-modelar-a-pressao-arterial-de-uma-pessoa-utiliza-uma-funcao-do-tipo-Pt-A-Bcoskt-em-que-A-B-e-K-300x64.png 300w\" decoding=\"async\" height=\"103\" sizes=\"(max-width: 481px) 100vw, 481px\" src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Um-cientista-em-seus-estudos-para-modelar-a-pressao-arterial-de-uma-pessoa-utiliza-uma-funcao-do-tipo-Pt-A-Bcoskt-em-que-A-B-e-K.png\" srcset=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Um-cientista-em-seus-estudos-para-modelar-a-pressao-arterial-de-uma-pessoa-utiliza-uma-funcao-do-tipo-Pt-A-Bcoskt-em-que-A-B-e-K.png 481w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Um-cientista-em-seus-estudos-para-modelar-a-pressao-arterial-de-uma-pessoa-utiliza-uma-funcao-do-tipo-Pt-A-Bcoskt-em-que-A-B-e-K-300x64.png 300w\" title=\"Questão 166 - ENEM 2017 - Questão 166,Função Trigonométrica,SENO,COSSENO\" width=\"481\" /></p>\r\n\r\n<p>A fun&ccedil;&atilde;o P(t) obtida, por este cientista, ao analisar o caso espec&iacute;fico foi</p>','','<p>b&ccedil;jBJKjb</p>','<p>jbj</p>','<p>kj</p>','<p>&ccedil;</p>','<p>bl</p>','E','M','2024-11-19 21:02:51.124473','2024-11-19 21:02:51.124473',3),(28,'Matemática','Geometria Plana','<p>Para decorar uma mesa de festa infantil, um chefe de cozinha usar&aacute; um mel&atilde;o esf&eacute;rico com&nbsp;<strong>di&acirc;metro medindo 10 cm,</strong>&nbsp;o qual servir&aacute; de suporte para espetar diversos doces. Ele&nbsp;<strong>ir&aacute; retirar uma calota esf&eacute;rica do mel&atilde;o</strong>, conforme ilustra a figura, e, para garantir a estabilidade deste suporte, dificultando que o mel&atilde;o role sobre a mesa,&nbsp;<strong>o chefe far&aacute; o corte de modo que o raio r da se&ccedil;&atilde;o circular de corte seja de pelo menos 3 cm</strong>. Por outro lado, o chefe&nbsp;<strong>desejar&aacute; dispor da maior &aacute;rea poss&iacute;vel da regi&atilde;o em que ser&atilde;o afixados os doces.</strong></p>\r\n\r\n<p><img alt=\"Questão 167 - ENEM 2017 - Questão 167,Geometria Espacial,ESFERA\" data-lazyloaded=\"1\" data-ll-status=\"loaded\" data-sizes=\"(max-width: 475px) 100vw, 475px\" data-src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Para-decorar-uma-mesa-de-festa-infantil-um-chefe-de-cozinha-usara-um-melao-esferico-com-diametro-medindo-10-cm.png\" data-srcset=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Para-decorar-uma-mesa-de-festa-infantil-um-chefe-de-cozinha-usara-um-melao-esferico-com-diametro-medindo-10-cm.png 475w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Para-decorar-uma-mesa-de-festa-infantil-um-chefe-de-cozinha-usara-um-melao-esferico-com-diametro-medindo-10-cm-300x176.png 300w\" decoding=\"async\" fetchpriority=\"high\" height=\"279\" sizes=\"(max-width: 475px) 100vw, 475px\" src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Para-decorar-uma-mesa-de-festa-infantil-um-chefe-de-cozinha-usara-um-melao-esferico-com-diametro-medindo-10-cm.png\" srcset=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Para-decorar-uma-mesa-de-festa-infantil-um-chefe-de-cozinha-usara-um-melao-esferico-com-diametro-medindo-10-cm.png 475w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Para-decorar-uma-mesa-de-festa-infantil-um-chefe-de-cozinha-usara-um-melao-esferico-com-diametro-medindo-10-cm-300x176.png 300w\" title=\"Questão 167 - ENEM 2017 - Questão 167,Geometria Espacial,ESFERA\" width=\"475\" /></p>\r\n\r\n<p>Para atingir todos os seus objetivos, o&nbsp;<strong>chefe dever&aacute; cortar a calota do mel&atilde;o numa altura h</strong>, em cent&iacute;metro, igual a</p>','','<p>asd</p>','<p>j</p>','<p>bh</p>','<p>jh</p>','<p>b</p>','D','D','2024-11-19 21:27:38.720479','2024-11-19 21:27:38.720479',3),(29,'Matemática','Geometria Plana','<p>Para decorar uma mesa de festa infantil, um chefe de cozinha usar&aacute; um mel&atilde;o esf&eacute;rico com&nbsp;<strong>di&acirc;metro medindo 10 cm,</strong>&nbsp;o qual servir&aacute; de suporte para espetar diversos doces. Ele&nbsp;<strong>ir&aacute; retirar uma calota esf&eacute;rica do mel&atilde;o</strong>, conforme ilustra a figura, e, para garantir a estabilidade deste suporte, dificultando que o mel&atilde;o role sobre a mesa,&nbsp;<strong>o chefe far&aacute; o corte de modo que o raio r da se&ccedil;&atilde;o circular de corte seja de pelo menos 3 cm</strong>. Por outro lado, o chefe&nbsp;<strong>desejar&aacute; dispor da maior &aacute;rea poss&iacute;vel da regi&atilde;o em que ser&atilde;o afixados os doces.</strong></p>\r\n\r\n<p><img alt=\"Questão 167 - ENEM 2017 - Questão 167,Geometria Espacial,ESFERA\" data-lazyloaded=\"1\" data-ll-status=\"loaded\" data-sizes=\"(max-width: 475px) 100vw, 475px\" data-src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Para-decorar-uma-mesa-de-festa-infantil-um-chefe-de-cozinha-usara-um-melao-esferico-com-diametro-medindo-10-cm.png\" data-srcset=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Para-decorar-uma-mesa-de-festa-infantil-um-chefe-de-cozinha-usara-um-melao-esferico-com-diametro-medindo-10-cm.png 475w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Para-decorar-uma-mesa-de-festa-infantil-um-chefe-de-cozinha-usara-um-melao-esferico-com-diametro-medindo-10-cm-300x176.png 300w\" decoding=\"async\" fetchpriority=\"high\" height=\"279\" sizes=\"(max-width: 475px) 100vw, 475px\" src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Para-decorar-uma-mesa-de-festa-infantil-um-chefe-de-cozinha-usara-um-melao-esferico-com-diametro-medindo-10-cm.png\" srcset=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Para-decorar-uma-mesa-de-festa-infantil-um-chefe-de-cozinha-usara-um-melao-esferico-com-diametro-medindo-10-cm.png 475w, https://xequematenem.com.br/blog/wp-content/uploads/2023/09/Para-decorar-uma-mesa-de-festa-infantil-um-chefe-de-cozinha-usara-um-melao-esferico-com-diametro-medindo-10-cm-300x176.png 300w\" title=\"Questão 167 - ENEM 2017 - Questão 167,Geometria Espacial,ESFERA\" width=\"475\" /></p>\r\n\r\n<p>Para atingir todos os seus objetivos, o&nbsp;<strong>chefe dever&aacute; cortar a calota do mel&atilde;o numa altura h</strong>, em cent&iacute;metro, igual a</p>','','<p>asd</p>','<p>j</p>','<p>bh</p>','<p>jh</p>','<p>b</p>','D','D','2024-11-19 21:27:42.257221','2024-11-19 21:27:42.257221',3),(30,'Matemática','Geometria Plana','<p>A Igreja de S&atilde;o Francisco de Assis, obra arquitet&ocirc;nica modernista de Oscar Niemeyer, localizada na Lagoa da Pampulha, em Belo Horizonte, possui ab&oacute;badas parab&oacute;licas. A seta na Figura 1 ilustra uma das ab&oacute;badas na entrada principal da capela. A Figura 2&nbsp;<strong>fornece uma vista frontal desta ab&oacute;bada, com medidas hipot&eacute;ticas para simplificar os c&aacute;lculos</strong>.</p>\r\n\r\n<p><img alt=\"Questão 168 - ENEM 2017 - Questão 168,Geometria Analítica,Igreja de São Francisco de Assis\" src=\"https://xequematenem.com.br/blog/wp-content/uploads/2023/09/A-Igreja-de-Sao-Francisco-de-Assis-obra-arquitetonica-modernista-de-Oscar-Niemeyer-localizada-na-Lagoa-da-Pampulha-em-Belo-Horizonte-possui-abobadas-parabolicas.png\" /></p>\r\n\r\n<p>Qual a&nbsp;<strong>medida da altura H, em metro, indicada na Figura 2</strong>?</p>','','<p>niioni</p>','<p>onio</p>','<p>i</p>','<p>on</p>','<p>in</p>','C','D','2024-11-19 21:28:40.554947','2024-11-19 21:28:40.554947',3),(31,'Química','saDCs','<p>QUAL A MOLECULA PRESENTE NA &Aacute;GUA?</p>','','<p>ADSFSDAFSDFDS</p>','<p>SDAF</p>','<p>FSADFS</p>','<p>SDAF</p>','<p>DSAF</p>','D','M','2024-11-24 09:57:11.922178','2024-11-24 09:57:11.922178',3);
/*!40000 ALTER TABLE `questions_questao` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `questions_questaosimulado`
--

DROP TABLE IF EXISTS `questions_questaosimulado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `questions_questaosimulado` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `ordem` int unsigned NOT NULL,
  `questao_id` bigint NOT NULL,
  `simulado_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `questions_questaosimulado_simulado_id_ordem_3e50b07d_uniq` (`simulado_id`,`ordem`),
  UNIQUE KEY `questions_questaosimulado_simulado_id_questao_id_8ed6cc1a_uniq` (`simulado_id`,`questao_id`),
  KEY `questions_questaosim_questao_id_cfcaf1c9_fk_questions` (`questao_id`),
  CONSTRAINT `questions_questaosim_questao_id_cfcaf1c9_fk_questions` FOREIGN KEY (`questao_id`) REFERENCES `questions_questao` (`id`),
  CONSTRAINT `questions_questaosim_simulado_id_fa7369f2_fk_questions` FOREIGN KEY (`simulado_id`) REFERENCES `questions_simulado` (`id`),
  CONSTRAINT `questions_questaosimulado_chk_1` CHECK ((`ordem` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=150 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `questions_questaosimulado`
--

LOCK TABLES `questions_questaosimulado` WRITE;
/*!40000 ALTER TABLE `questions_questaosimulado` DISABLE KEYS */;
INSERT INTO `questions_questaosimulado` VALUES (9,1,4,2),(10,2,2,2),(11,3,1,2),(12,4,3,2),(134,1,7,3),(135,2,5,3),(136,3,8,3),(137,4,6,3),(138,5,13,3),(139,6,19,3),(140,7,22,3),(141,8,23,3),(142,9,21,3),(143,10,24,3),(144,11,28,3),(145,12,29,3),(146,13,30,3),(147,14,17,3),(148,15,27,3),(149,16,31,3);
/*!40000 ALTER TABLE `questions_questaosimulado` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `questions_simulado`
--

DROP TABLE IF EXISTS `questions_simulado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `questions_simulado` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `titulo` varchar(200) NOT NULL,
  `descricao` longtext NOT NULL,
  `data_criacao` datetime(6) NOT NULL,
  `ultima_modificacao` datetime(6) NOT NULL,
  `cabecalho` longtext,
  `instrucoes` longtext,
  `professor_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `questions_simulado_professor_id_00fe72de_fk_accounts_` (`professor_id`),
  CONSTRAINT `questions_simulado_professor_id_00fe72de_fk_accounts_` FOREIGN KEY (`professor_id`) REFERENCES `accounts_customuser` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `questions_simulado`
--

LOCK TABLES `questions_simulado` WRITE;
/*!40000 ALTER TABLE `questions_simulado` DISABLE KEYS */;
INSERT INTO `questions_simulado` VALUES (2,'Teste','asD','2024-11-19 18:46:47.745301','2024-11-19 18:46:54.882716','<p>AsdAS</p>','<p>Asdsa D AJD a]ad</p>\r\n\r\n<p>a sd as</p>\r\n\r\n<p>O JAD AS</p>\r\n\r\n<p>D JASdo ASJ</p>\r\n\r\n<p>Dajsod</p>\r\n\r\n<p>AJSODasjodsaDSADAS</p>',1),(3,'Teste','Primeiro teste','2024-11-19 19:50:59.227685','2024-11-19 21:36:11.330934','<p><br />\r\nCOL&Eacute;GIO CELSO RODRIGUES</p>\r\n\r\n<p>PROFESSOR : LUIZ GABRIE</p>\r\n\r\n<p>ALUNO : __________________</p>\r\n\r\n<p>DATA: ______________</p>','<p>INSTRU&Ccedil;&Otilde;ES PARA REALIZA&Ccedil;&Atilde;O DA PROVA<br />\r\n1. Esta prova cont&eacute;m 52 quest&otilde;es, cada uma com 5 alternativas, das quais somente uma &eacute; correta.<br />\r\nAssinale, no cart&atilde;o de respostas, a alternativa que voc&ecirc; julgar correta.<br />\r\n2. O cart&atilde;o de respostas ser&aacute; entregue com o caderno de quest&otilde;es. Ele deve ser preenchido e devolvido<br />\r\nao examinador ao t&eacute;rmino da prova<br />\r\n3. Assinale apenas uma alternativa para cada quest&atilde;o. Ser&aacute; anulada a quest&atilde;o em que for assinalada<br />\r\nmais de uma alternativa ou que estiver em branco.<br />\r\n4. Assinale a resposta preenchendo totalmente, a caneta preta, o respectivo alv&eacute;olo, com o cuidado de<br />\r\nn&atilde;o ultrapassar o espa&ccedil;o dele. N&atilde;o assinale as respostas com &quot;X&quot;, pois essa sinaliza&ccedil;&atilde;o n&atilde;o ser&aacute;<br />\r\nconsiderada. N&atilde;o use, em hip&oacute;tese alguma, l&aacute;pis ou caneta vermelha para assinalar a resposta</p>',3);
/*!40000 ALTER TABLE `questions_simulado` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-11-25  8:00:05
