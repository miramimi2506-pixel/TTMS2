CREATE DATABASE IF NOT EXISTS timetable_db4;
USE timetable_db4;

CREATE TABLE users(
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(255),
    role ENUM('admin', 'faculty', 'student')
NOT NULL
);

CREATE TABLE courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    weekly_hours INT NOT NULL,
    year ENUM('I','II','III','IV') NOT NULL,
    course_id INT NOT NULL,
    semester ENUM('ODD','EVEN') NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

CREATE TABLE staff (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    max_hours INT DEFAULT 20
);

CREATE TABLE staff_subjects (
    staff_id INT NOT NULL,
    subject_id INT NOT NULL,
    PRIMARY KEY (staff_id, subject_id),
    FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);
CREATE TABLE classrooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_code VARCHAR(20) UNIQUE NOT NULL,
    room_type ENUM('CLASSROOM','LAB') NOT NULL,
    capacity INT DEFAULT 60
);
CREATE TABLE periods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    period_no INT NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL
);
CREATE TABLE timetable (
    id INT AUTO_INCREMENT PRIMARY KEY,
    day ENUM('Monday','Tuesday','Wednesday','Thursday','Friday') NOT NULL,
    period_id INT NOT NULL,
    subject_id INT NOT NULL,
    staff_id INT NOT NULL,
    classroom_id INT NOT NULL,
    year ENUM('I','II','III','IV') NOT NULL,
    course_id INT NOT NULL,
    semester ENUM('ODD','EVEN') NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (period_id) REFERENCES periods(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    FOREIGN KEY (staff_id) REFERENCES staff(id),
    FOREIGN KEY (classroom_id) REFERENCES classrooms(id),
    FOREIGN KEY (course_id) REFERENCES courses(id),

    UNIQUE(day, period_id, staff_id),
    UNIQUE(day, period_id, classroom_id),
    UNIQUE(day, period_id, year, course_id, semester)
);
ALTER TABLE subjects
ADD COLUMN required_room ENUM('CLASSROOM','LAB') NOT NULL DEFAULT 'CLASSROOM';
CREATE VIEW faculty_workload AS
SELECT
    st.id AS staff_id,
    st.staff_code,
    st.name AS faculty_name,
    st.department,
    st.max_hours,
    COUNT(t.id) AS assigned_hours,
    (st.max_hours - COUNT(t.id)) AS remaining_hours
FROM staff st
LEFT JOIN timetable t ON st.id = t.staff_id
GROUP BY st.id;
INSERT INTO users (username, password, role) VALUES
('admin', 'admin123', 'admin'),
('faculty1', 'faculty123', 'faculty'),
('student1', 'student123', 'student');

INSERT INTO courses (name) VALUES
('AI & DS'),
('CSE');

INSERT INTO periods (period_no, start_time, end_time) VALUES
(1, '09:30:00', '10:20:00'),
(2, '10:20:00', '11:10:00'),
(3, '11:20:00', '12:10:00'),
(4, '12:10:00', '01:00:00'),
(5, '02:00:00', '02:50:00'),
(6, '02:50:00', '03:40:00');

INSERT INTO classrooms (room_code, room_type, capacity) VALUES
('C101', 'CLASSROOM', 60),
('C102', 'CLASSROOM', 60),
('AI_LAB', 'LAB', 40),
('DS_LAB', 'LAB', 40);

INSERT INTO staff (staff_code, name, department, max_hours) VALUES
('FAC001', 'Mrs. R. Nadhiya', 'AI & DS', 18),
('FAC002', 'Mr. S. Kumar', 'CSE', 20);

INSERT INTO subjects(code, name, weekly_hours, year, course_id, required_room) VALUES
('CS3691', 'Embedded Systems and IoT', 4, 'III', 1, 'LAB'),
('CS3541', 'Data Warehousing', 4, 'III', 1, 'CLASSROOM'),
('CS3401', 'Computer Networks', 4, 'III', 2, 'CLASSROOM');

INSERT INTO staff_subjects(staff_id, subject_id) VALUES
(1, 1),
(1, 2),
(2, 3);
CREATE OR REPLACE VIEW faculty_workload AS
SELECT
    st.id AS staff_id,
    st.staff_code,
    st.name AS faculty_name,
    st.department,
    st.max_hours,
    COUNT(t.id) AS assigned_hours,
    (st.max_hours - COUNT(t.id)) AS remaining_hours
FROM staff st
LEFT JOIN timetable t ON st.id = t.staff_id
GROUP BY st.id;

