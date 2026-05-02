-- =====================================================
-- Database: palee_elite_training_center
-- Updated : ENUM values converted from Lao to English
-- =====================================================

CREATE DATABASE IF NOT EXISTS palee_elite_training_center
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_general_ci;

USE palee_elite_training_center;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- -----------------------------------------------------
-- 1. province (ແຂວງ)
-- -----------------------------------------------------
CREATE TABLE province (
  province_id   INT(11)     NOT NULL AUTO_INCREMENT,
  province_name VARCHAR(30) NOT NULL UNIQUE,
  PRIMARY KEY (province_id)
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 2. district (ເມືອງ)
-- -----------------------------------------------------
CREATE TABLE district (
  district_id   INT(11)     NOT NULL AUTO_INCREMENT,
  district_name VARCHAR(30) NOT NULL,
  province_id   INT(11)     NOT NULL,
  PRIMARY KEY (district_id),
  FOREIGN KEY (province_id) REFERENCES province (province_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 3. academic_years (ສົກຮຽນ)
-- -----------------------------------------------------
CREATE TABLE academic_years (
  academic_id   CHAR(5)      NOT NULL,
  academic_year VARCHAR(10)  NOT NULL,
  start_date_at DATE         NOT NULL,
  end_date_at   DATE         NOT NULL,
  status        ENUM('ACTIVE', 'ENDED') NOT NULL,
  -- ACTIVE = ກຳລັງດຳເນີນ, ENDED = ສິ້ນສຸດແລ້ວ
  PRIMARY KEY (academic_id),
  UNIQUE KEY uq_academic_year (academic_year)
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 4. subject_category (ໝວດວິຊາ)
-- -----------------------------------------------------
CREATE TABLE subject_category (
  subject_category_id   CHAR(5)     NOT NULL,
  subject_category_name VARCHAR(20) NOT NULL,
  PRIMARY KEY (subject_category_id),
  UNIQUE KEY uq_subject_category_name (subject_category_name)
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 5. subject (ວິຊາ)
-- -----------------------------------------------------
CREATE TABLE subject (
  subject_id          CHAR(5)     NOT NULL,
  subject_name        VARCHAR(20) NOT NULL,
  subject_category_id CHAR(5)     NOT NULL,
  PRIMARY KEY (subject_id),
  UNIQUE KEY uq_subject_name (subject_name),
  FOREIGN KEY (subject_category_id) REFERENCES subject_category (subject_category_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 6. level (ຊັ້ນຮຽນ / ລະດັບ)
-- -----------------------------------------------------
CREATE TABLE level (
  level_id   CHAR(5)     NOT NULL,
  level_name VARCHAR(20) NOT NULL,
  PRIMARY KEY (level_id),
  UNIQUE KEY uq_level_name (level_name)
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 7. subject_detail (ລາຍລະອຽດວິຊາ)
-- -----------------------------------------------------
CREATE TABLE subject_detail (
  subject_detail_id CHAR(5) NOT NULL,
  subject_id        CHAR(5) NOT NULL,
  level_id          CHAR(5) NOT NULL,
  PRIMARY KEY (subject_detail_id),
  UNIQUE KEY uq_subject_level (subject_id, level_id),
  FOREIGN KEY (subject_id) REFERENCES subject (subject_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (level_id)   REFERENCES level   (level_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 8. fee (ຄ່າຮຽນ)
-- -----------------------------------------------------
CREATE TABLE fee (
  fee_id            CHAR(5)        NOT NULL,
  subject_detail_id CHAR(5)        NOT NULL,
  academic_id       CHAR(5)        NOT NULL,
  fee               DECIMAL(10, 2) NOT NULL,
  PRIMARY KEY (fee_id),
  UNIQUE KEY uq_fee (subject_detail_id, academic_id),
  FOREIGN KEY (subject_detail_id) REFERENCES subject_detail (subject_detail_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (academic_id)       REFERENCES academic_years  (academic_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 9. discount (ສ່ວນລຸດ)
-- -----------------------------------------------------
CREATE TABLE discount (
  discount_id          CHAR(5)        NOT NULL,
  academic_id          CHAR(5)        NOT NULL,
  discount_amount      DECIMAL(10, 2) NOT NULL,
  discount_description ENUM(
    'MULTI_SUBJECT',     -- ຮຽນ 3 ວິຊາຂຶ້ນໄປ (Enrolling 3+ subjects)
    'LATE_REGISTRATION'  -- ລົງທະບຽນຮຽນຊ້າ (Late registration)
  )                                   NOT NULL,
  PRIMARY KEY (discount_id),
  UNIQUE KEY uq_discount (academic_id, discount_description),
  FOREIGN KEY (academic_id) REFERENCES academic_years (academic_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 10. user (ຜູ້ໃຊ້ລະບົບ)
-- -----------------------------------------------------
CREATE TABLE user (
  user_id       INT(11)      NOT NULL AUTO_INCREMENT,
  user_name     VARCHAR(30)  NOT NULL UNIQUE,
  user_password VARCHAR(255) NOT NULL,
  role          ENUM('DIRECTOR', 'TEACHER') NOT NULL,
  -- DIRECTOR = ຜູ້ອຳນວຍການ, TEACHER = ອາຈານ
  PRIMARY KEY (user_id)
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 11. teacher (ອາຈານ)
-- -----------------------------------------------------
CREATE TABLE teacher (
  teacher_id       CHAR(5)     NOT NULL,
  teacher_name     VARCHAR(30) NOT NULL,
  teacher_lastname VARCHAR(30) NOT NULL,
  gender           ENUM('MALE', 'FEMALE') NOT NULL,
  -- MALE = ຊາຍ, FEMALE = ຍິງ
  teacher_contact  VARCHAR(20) NOT NULL,
  district_id      INT(11)     NOT NULL,
  PRIMARY KEY (teacher_id),
  UNIQUE KEY uq_teacher_contact (teacher_contact),
  FOREIGN KEY (district_id) REFERENCES district (district_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 12. teacher_assignment (ການມອບໝາຍສອນ)
-- -----------------------------------------------------
CREATE TABLE teacher_assignment (
  assignment_id     CHAR(5)        NOT NULL,
  teacher_id        CHAR(5)        NOT NULL,
  subject_detail_id CHAR(5)        NOT NULL,
  academic_id       CHAR(5)        NOT NULL,
  hourly_rate       DECIMAL(10, 2) NOT NULL,
  PRIMARY KEY (assignment_id),
  UNIQUE KEY uq_assignment (teacher_id, subject_detail_id, academic_id),
  FOREIGN KEY (teacher_id)        REFERENCES teacher        (teacher_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (subject_detail_id) REFERENCES subject_detail (subject_detail_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (academic_id)       REFERENCES academic_years  (academic_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 13. teaching_log (ບັນທຶກການສອນ)
-- -----------------------------------------------------
CREATE TABLE teaching_log (
  teaching_log_id              INT(11)      NOT NULL AUTO_INCREMENT,
  assignment_id                CHAR(5)      NOT NULL,
  substitute_for_assignment_id CHAR(5)      DEFAULT NULL,
  teaching_date                TIMESTAMP    NOT NULL,
  hourly                       DECIMAL(5,2) NOT NULL,
  status                       ENUM('TEACHING', 'ABSENT') NOT NULL,
  -- TEACHING = ຂຶ້ນສອນ, ABSENT = ຂາດສອນ
  PRIMARY KEY (teaching_log_id),
  FOREIGN KEY (assignment_id) REFERENCES teacher_assignment (assignment_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (substitute_for_assignment_id) REFERENCES teacher_assignment (assignment_id)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 14. salary_payment (ການເບີກຈ່າຍເງິນສອນ)
-- -----------------------------------------------------
CREATE TABLE salary_payment (
  salary_payment_id VARCHAR(20)    NOT NULL,
  teacher_id        CHAR(5)        NOT NULL,
  user_id           INT(11)        NOT NULL,
  month             INT            NOT NULL,            -- Teaching period month (1-12)
  total_amount      DECIMAL(10, 2) NOT NULL,
  payment_date      TIMESTAMP      NOT NULL,
  status            ENUM('PAID', 'PARTIAL') NOT NULL,
  -- PAID = ຈ່າຍແລ້ວ, PARTIAL = ຈ່າຍບາງສ່ວນ
  PRIMARY KEY (salary_payment_id),
  FOREIGN KEY (teacher_id) REFERENCES teacher (teacher_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (user_id)    REFERENCES user    (user_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 15. student (ນັກຮຽນ)
-- -----------------------------------------------------
CREATE TABLE student (
  student_id       CHAR(10)     NOT NULL,
  student_name     VARCHAR(30)  NOT NULL,
  student_lastname VARCHAR(30)  NOT NULL,
  gender           ENUM('MALE', 'FEMALE') NOT NULL,
  -- MALE = ຊາຍ, FEMALE = ຍິງ
  student_contact  VARCHAR(20)  NOT NULL,
  parents_contact  VARCHAR(20)  NOT NULL,
  school           VARCHAR(100) NOT NULL,
  district_id      INT(11)      NOT NULL,
  PRIMARY KEY (student_id),
  FOREIGN KEY (district_id)  REFERENCES district  (district_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 16. registration (ການລົງທະບຽນ)
-- -----------------------------------------------------
CREATE TABLE registration (
  registration_id   VARCHAR(20)    NOT NULL,
  student_id        CHAR(10)       NOT NULL,
  discount_id       CHAR(5)        DEFAULT NULL,
  total_amount      DECIMAL(10, 2) NOT NULL,
  final_amount      DECIMAL(10, 2) NOT NULL,
  status            ENUM('PAID', 'UNPAID', 'PARTIAL') NOT NULL,
  -- PAID = ຈ່າຍແລ້ວ, UNPAID = ຍັງບໍ່ທັນຈ່າຍ, PARTIAL = ຈ່າຍບາງສ່ວນ
  registration_date TIMESTAMP      NOT NULL,
  PRIMARY KEY (registration_id),
  FOREIGN KEY (student_id)  REFERENCES student  (student_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (discount_id) REFERENCES discount (discount_id)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 17. registration_detail (ລາຍລະອຽດການລົງທະບຽນ)
-- -----------------------------------------------------
CREATE TABLE registration_detail (
  regis_detail_id INT(11)     NOT NULL AUTO_INCREMENT,
  registration_id VARCHAR(20) NOT NULL,
  fee_id          CHAR(5)     NOT NULL,
  scholarship     ENUM('SCHOLARSHIP', 'NO_SCHOLARSHIP') NOT NULL,
  -- SCHOLARSHIP = ໄດ້ຮັບທຶນ, NO_SCHOLARSHIP = ບໍ່ໄດ້ຮັບທຶນ
  PRIMARY KEY (regis_detail_id),
  UNIQUE KEY uq_registration_fee (registration_id, fee_id),
  FOREIGN KEY (registration_id) REFERENCES registration (registration_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (fee_id)          REFERENCES fee          (fee_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 18. tuition_payment (ການຈ່າຍຄ່າຮຽນ)
-- -----------------------------------------------------
CREATE TABLE tuition_payment (
  tuition_payment_id VARCHAR(20)    NOT NULL,
  registration_id    VARCHAR(20)    NOT NULL,
  paid_amount        DECIMAL(10, 2) NOT NULL,
  payment_method     ENUM('CASH', 'TRANSFER') NOT NULL,
  -- CASH = ເງິນສົດ, TRANSFER = ເງິນໂອນ
  pay_date           TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (tuition_payment_id),
  FOREIGN KEY (registration_id) REFERENCES registration (registration_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 19. evaluation (ການປະເມີນຜົນ)
-- -----------------------------------------------------
CREATE TABLE evaluation (
  evaluation_id   CHAR(10) NOT NULL,
  semester        ENUM('MIDTERM', 'FINAL') NOT NULL,
  -- MIDTERM = ກາງພາກ, FINAL = ທ້າຍພາກ
  evaluation_date TIMESTAMP   NOT NULL,
  PRIMARY KEY (evaluation_id)
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 20. evaluation_detail (ລາຍລະອຽດການປະເມີນ)
-- -----------------------------------------------------
CREATE TABLE evaluation_detail (
  eval_detail_id  INT(11)       NOT NULL AUTO_INCREMENT,
  evaluation_id   CHAR(10)   NOT NULL,
  regis_detail_id INT(11)       NOT NULL,
  score           DECIMAL(5,2)  NOT NULL,
  ranking         CHAR(10)       NOT NULL,
  prize           DECIMAL(10,2) DEFAULT NULL,
  PRIMARY KEY (eval_detail_id),
  FOREIGN KEY (evaluation_id)   REFERENCES evaluation         (evaluation_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (regis_detail_id) REFERENCES registration_detail (regis_detail_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 21. expense_category (ປະເພດລາຍຈ່າຍ)
-- -----------------------------------------------------
CREATE TABLE expense_category (
  expense_category_id INT(11)     NOT NULL AUTO_INCREMENT,
  expense_category    VARCHAR(30) NOT NULL,
  PRIMARY KEY (expense_category_id),
  UNIQUE KEY uq_expense_category (expense_category)
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 22. expense (ລາຍຈ່າຍ)
-- -----------------------------------------------------
CREATE TABLE expense (
  expense_id          INT(11)        NOT NULL AUTO_INCREMENT,
  expense_category_id INT(11)        NOT NULL,
  salary_payment_id   VARCHAR(20)    DEFAULT NULL,
  amount              DECIMAL(10, 2) NOT NULL,
  description         VARCHAR(255)   DEFAULT NULL,
  expense_date        TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (expense_id),
  FOREIGN KEY (expense_category_id) REFERENCES expense_category (expense_category_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (salary_payment_id)   REFERENCES salary_payment   (salary_payment_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 23. income (ລາຍຮັບ)
-- -----------------------------------------------------
CREATE TABLE income (
  income_id          INT(11)        NOT NULL AUTO_INCREMENT,
  tuition_payment_id VARCHAR(20)    DEFAULT NULL,
  donation_id        INT(11)        DEFAULT NULL,
  amount             DECIMAL(10, 2) NOT NULL,
  description        VARCHAR(255)   DEFAULT NULL,
  income_date        TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (income_id),
  FOREIGN KEY (tuition_payment_id) REFERENCES tuition_payment (tuition_payment_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 24. donor (ຜູ້ບໍລິຈາກ)
-- -----------------------------------------------------
CREATE TABLE donor (
  donor_id       CHAR(5)      NOT NULL,
  donor_name     VARCHAR(30)  NOT NULL,
  donor_lastname VARCHAR(30)  NOT NULL,
  donor_contact  VARCHAR(20)  NOT NULL,
  section        VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (donor_id),
  UNIQUE KEY uq_donor_contact (donor_contact)
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 25. donation_category (ປະເພດການບໍລິຈາກ)
-- -----------------------------------------------------
CREATE TABLE donation_category (
  donation_category_id   INT(11)     NOT NULL AUTO_INCREMENT,
  donation_category_name VARCHAR(30) NOT NULL,
  PRIMARY KEY (donation_category_id),
  UNIQUE KEY uq_donation_category_name (donation_category_name)
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 26. donation (ການບໍລິຈາກ)
-- -----------------------------------------------------
CREATE TABLE donation (
  donation_id          INT(11)     NOT NULL AUTO_INCREMENT,
  donor_id             CHAR(5)     NOT NULL,
  donation_category_id INT(11)     NOT NULL,
  donation_name        VARCHAR(30) NOT NULL,
  amount               FLOAT       NOT NULL,
  unit                 VARCHAR(10) NOT NULL,
  donation_date        DATE        NOT NULL,
  PRIMARY KEY (donation_id),
  FOREIGN KEY (donor_id)             REFERENCES donor             (donor_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (donation_category_id) REFERENCES donation_category (donation_category_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

ALTER TABLE income
  ADD CONSTRAINT fk_income_donation
  FOREIGN KEY (donation_id) REFERENCES donation (donation_id)
    ON DELETE CASCADE ON UPDATE CASCADE;

SET FOREIGN_KEY_CHECKS = 1;