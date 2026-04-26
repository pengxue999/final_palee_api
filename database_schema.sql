-- =====================================================
-- Database: palee_elite_training_center
-- Updated : ON DELETE RESTRICT ON UPDATE CASCADE
-- =====================================================

CREATE DATABASE IF NOT EXISTS palee_elite_training_center
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_general_ci;

USE palee_elite_training_center;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- -----------------------------------------------------
-- 1. ແຂວງ
-- -----------------------------------------------------
CREATE TABLE province (
  province_id   INT(11)     NOT NULL AUTO_INCREMENT,
  province_name VARCHAR(30) NOT NULL,
  PRIMARY KEY (province_id)
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 2. ເມືອງ
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
-- 3. ສົກຮຽນ
-- -----------------------------------------------------
CREATE TABLE academic_years (
  academic_id   char(5)     NOT NULL,
  academic_year VARCHAR(10) NOT NULL,
  start_date_at DATE        DEFAULT NULL,
  end_date_at   DATE        DEFAULT NULL,
  status        ENUM('ດໍາເນີນການ', 'ສິ້ນສຸດ') NOT NULL,
  PRIMARY KEY (academic_id),
  UNIQUE KEY uq_academic_year (academic_year)
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 4. ໝວດວິຊາ
-- -----------------------------------------------------
CREATE TABLE subject_category (
  subject_category_id   CHAR(5)     NOT NULL,
  subject_category_name VARCHAR(20) NOT NULL,
  PRIMARY KEY (subject_category_id),
  UNIQUE KEY uq_subject_category_name (subject_category_name)
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 5. ວິຊາ
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
-- 6. ຊັ້ນຮຽນ/ລະດັບ
-- -----------------------------------------------------
CREATE TABLE level (
  level_id   CHAR(5)     NOT NULL,
  level_name VARCHAR(20) NOT NULL,
  PRIMARY KEY (level_id),
  UNIQUE KEY uq_level_name (level_name)
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 7. ລາຍລະອຽດວິຊາ
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
-- 8. ຄ່າຮຽນ
-- -----------------------------------------------------
CREATE TABLE fee (
  fee_id            CHAR(5)        NOT NULL,
  subject_detail_id CHAR(5)        NOT NULL,
  academic_id       char(5)        NOT NULL,
  fee               DECIMAL(10, 2) NOT NULL,
  PRIMARY KEY (fee_id),
  UNIQUE KEY uq_fee (subject_detail_id, academic_id),
  FOREIGN KEY (subject_detail_id) REFERENCES subject_detail (subject_detail_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (academic_id)       REFERENCES academic_years  (academic_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 9. ສ່ວນລຸດ
-- -----------------------------------------------------
CREATE TABLE discount (
  discount_id          CHAR(5)        NOT NULL,
  academic_id          char(5)        NOT NULL,
  discount_amount      DECIMAL(10, 2) NOT NULL,
  discount_description ENUM(
    'ຮຽນ3ວິຊາຂື້ນໄປ(ສະເພາະສາຍຄິດໄລ່)',
    'ລົງທະບຽນຮຽນຊ້າ'
  )                                   NOT NULL,
  PRIMARY KEY (discount_id),
  UNIQUE KEY uq_discount (academic_id, discount_description),
  FOREIGN KEY (academic_id) REFERENCES academic_years (academic_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 10. ຜູ້ໃຊ້ລະບົບ
-- -----------------------------------------------------
CREATE TABLE user (
  user_id       INT(11)      NOT NULL AUTO_INCREMENT,
  user_name     VARCHAR(30)  NOT NULL,
  user_password VARCHAR(255) NOT NULL,
  role          VARCHAR(20)  NOT NULL,
  PRIMARY KEY (user_id)
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 11. ອາຈານ
-- -----------------------------------------------------
CREATE TABLE teacher (
  teacher_id       CHAR(5)     NOT NULL,
  teacher_name     VARCHAR(30) NOT NULL,
  teacher_lastname VARCHAR(30) NOT NULL,
  gender           VARCHAR(10) NOT NULL,
  teacher_contact  VARCHAR(20) NOT NULL,
  district_id      INT(11)     NOT NULL,
  PRIMARY KEY (teacher_id),
  UNIQUE KEY uq_teacher_contact (teacher_contact),
  FOREIGN KEY (district_id) REFERENCES district (district_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 12. ການມອບໝາຍສອນ
-- -----------------------------------------------------
CREATE TABLE teacher_assignment (
  assignment_id     CHAR(5)        NOT NULL,
  teacher_id        CHAR(5)        NOT NULL,
  subject_detail_id CHAR(5)        NOT NULL,
  academic_id       char(5)        NOT NULL,
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
-- 13. ບັນທຶກການສອນ
-- -----------------------------------------------------
CREATE TABLE teaching_log (
  teaching_log_id              INT(11)      NOT NULL AUTO_INCREMENT,
  assignment_id                CHAR(5)      NOT NULL,
  substitute_for_assignment_id CHAR(5)      DEFAULT NULL,
  teaching_date                TIMESTAMP    NOT NULL,
  hourly                       DECIMAL(5,2) NOT NULL,
  remark                       VARCHAR(255) DEFAULT NULL,
  status                       ENUM('ຂຶ້ນສອນ','ຂາດສອນ'),
  PRIMARY KEY (teaching_log_id),
  FOREIGN KEY (assignment_id) REFERENCES teacher_assignment (assignment_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (substitute_for_assignment_id) REFERENCES teacher_assignment (assignment_id)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 14. ການເບີກຈ່າຍເງິນສອນ
-- -----------------------------------------------------
CREATE TABLE salary_payment (
  salary_payment_id VARCHAR(20)    NOT NULL,
  teacher_id        CHAR(5)        NOT NULL,
  user_id           INT(11)        NOT NULL,
  month             INT            NOT NULL,            -- Teaching period month (1-12)
  total_amount      DECIMAL(10, 2) NOT NULL,            -- Amount paid in this transaction
  payment_date      TIMESTAMP           NOT NULL,
  status            ENUM('ຈ່າຍແລ້ວ','ຈ່າຍບາງສ່ວນ') NOT NULL,
  PRIMARY KEY (salary_payment_id),
  FOREIGN KEY (teacher_id) REFERENCES teacher (teacher_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (user_id)    REFERENCES user    (user_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 15. ນັກຮຽນ
-- -----------------------------------------------------
CREATE TABLE student (
  student_id       CHAR(10)     NOT NULL,
  student_name     VARCHAR(30)  NOT NULL,
  student_lastname VARCHAR(30)  NOT NULL,
  gender           VARCHAR(10)  NOT NULL,
  student_contact  VARCHAR(20)  NOT NULL,
  parents_contact  VARCHAR(20)  NOT NULL,
  school           VARCHAR(100) NOT NULL,
  district_id      INT(11)      NOT NULL,
  PRIMARY KEY (student_id),
  FOREIGN KEY (district_id)  REFERENCES district  (district_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 16. ການລົງທະບຽນ
-- -----------------------------------------------------
CREATE TABLE registration (
  registration_id   VARCHAR(20)    NOT NULL,
  student_id        CHAR(10)       NOT NULL,
  discount_id       CHAR(5)        DEFAULT NULL,
  total_amount      DECIMAL(10, 2) NOT NULL,
  final_amount      DECIMAL(10, 2) NOT NULL,
  status            ENUM('ຈ່າຍແລ້ວ', 'ຍັງບໍ່ທັນຈ່າຍ','ຈ່າຍບາງສ່ວນ') NOT NULL,
  registration_date TIMESTAMP      NOT NULL,
  PRIMARY KEY (registration_id),
  FOREIGN KEY (student_id)  REFERENCES student  (student_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (discount_id) REFERENCES discount (discount_id)
    ON DELETE SET NULL ON UPDATE CASCADE  -- ⚠️ SET NULL: ລຶບສ່ວນລຸດໄດ້ໂດຍບໍ່ກະທົບ registration
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 18. ລາຍລະອຽດການລົງທະບຽນ
-- -----------------------------------------------------
CREATE TABLE registration_detail (
  regis_detail_id INT(11)     NOT NULL AUTO_INCREMENT,
  registration_id VARCHAR(20) NOT NULL,
  fee_id          CHAR(5)     NOT NULL,
  scholarship     ENUM('ໄດ້ຮັບທຶນ', 'ບໍ່ໄດ້ຮັບທຶນ') NOT NULL,
  PRIMARY KEY (regis_detail_id),
  UNIQUE KEY uq_registration_fee (registration_id, fee_id),
  FOREIGN KEY (registration_id) REFERENCES registration (registration_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (fee_id)          REFERENCES fee          (fee_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 19. ການຈ່າຍຄ່າຮຽນ
-- -----------------------------------------------------
CREATE TABLE tuition_payment (
  tuition_payment_id VARCHAR(20)    NOT NULL,
  registration_id    VARCHAR(20)    NOT NULL,
  paid_amount        DECIMAL(10, 2) NOT NULL,
  payment_method     ENUM('ເງິນສົດ', 'ເງິນໂອນ') NOT NULL,
  pay_date           TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (tuition_payment_id),
  FOREIGN KEY (registration_id) REFERENCES registration (registration_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 20. ການປະເມີນຜົນການຮຽນ
-- -----------------------------------------------------
CREATE TABLE evaluation (
  evaluation_id   VARCHAR(20) NOT NULL,
  semester        ENUM('ກາງພາກ', 'ທ້າຍພາກ') NOT NULL,
  evaluation_date TIMESTAMP    NOT NULL,
  PRIMARY KEY (evaluation_id)
 ) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 22. ລາຍລະອຽດການປະເມີນ
-- -----------------------------------------------------
CREATE TABLE evaluation_detail (
  eval_detail_id  INT(11)      NOT NULL AUTO_INCREMENT,
  evaluation_id   VARCHAR(20) NOT NULL,
  regis_detail_id INT(11)     NOT NULL,
  score           DECIMAL(5,2) NOT NULL,
  ranking         INT(11)  NOT NULL,
  prize           DECIMAL(10,2)DEFAULT NULL,
  PRIMARY KEY (eval_detail_id),
  FOREIGN KEY (evaluation_id) REFERENCES evaluation (evaluation_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (regis_detail_id) REFERENCES registration_detail (regis_detail_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 23. ປະເພດລາຍຈ່າຍ
-- -----------------------------------------------------
CREATE TABLE expense_category (
  expense_category_id INT(11)     NOT NULL AUTO_INCREMENT,
  expense_category    VARCHAR(30) NOT NULL,
  PRIMARY KEY (expense_category_id),
  UNIQUE KEY uq_expense_category (expense_category)
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 24. ລາຍຈ່າຍ
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
  FOREIGN KEY (salary_payment_id) REFERENCES salary_payment (salary_payment_id)
    ON DELETE CASCADE ON UPDATE CASCADE
    
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 25. ລາຍຮັບ
-- -----------------------------------------------------
CREATE TABLE income (
  income_id   INT(11)        NOT NULL AUTO_INCREMENT,
  tuition_payment_id VARCHAR(20)    DEFAULT NULL,
  donation_id       INT(11)        DEFAULT NULL,
  amount      DECIMAL(10, 2) NOT NULL,
  description VARCHAR(255)   DEFAULT NULL,
  income_date TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (income_id),
  FOREIGN KEY (tuition_payment_id) REFERENCES tuition_payment (tuition_payment_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 26. ຜູ້ບໍລິຈາກ
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
-- 27. ຫົວໜ່ວຍ
-- -----------------------------------------------------
CREATE TABLE unit (
  unit_id   INT(11)     NOT NULL AUTO_INCREMENT,
  unit_name VARCHAR(30) NOT NULL,
  PRIMARY KEY (unit_id),
  UNIQUE KEY uq_unit_name (unit_name)
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- 28. ການບໍລິຈາກ
-- -----------------------------------------------------
CREATE TABLE donation (
  donation_id          INT(11)        NOT NULL AUTO_INCREMENT,
  donor_id             CHAR(5)        NOT NULL,
  donation_category    VARCHAR(30)    NOT NULL,
  donation_name        VARCHAR(30)    NOT NULL,
  amount               DECIMAL(10, 2) NOT NULL,
  unit_id              INT(11)        NOT NULL,
  description          VARCHAR(255)   DEFAULT NULL,
  donation_date        DATE           NOT NULL,
  PRIMARY KEY (donation_id),
  FOREIGN KEY (donor_id)             REFERENCES donor             (donor_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (unit_id)              REFERENCES unit              (unit_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

ALTER TABLE income
  ADD CONSTRAINT fk_income_donation
  FOREIGN KEY (donation_id) REFERENCES donation (donation_id)
    ON DELETE CASCADE ON UPDATE CASCADE;

SET FOREIGN_KEY_CHECKS = 1;