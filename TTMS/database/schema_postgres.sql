-- PostgreSQL Schema for TTMS
-- Run this in your Render PostgreSQL database

CREATE TABLE IF NOT EXISTS users(
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(255),
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'faculty', 'student'))
);

CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS subjects (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    weekly_hours INT NOT NULL,
    year VARCHAR(5) NOT NULL CHECK (year IN ('I','II','III','IV')),
    course_id INT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    semester VARCHAR(10) NOT NULL DEFAULT 'ODD',
    required_room VARCHAR(20) NOT NULL DEFAULT 'CLASSROOM' CHECK (required_room IN ('CLASSROOM','LAB'))
);

CREATE TABLE IF NOT EXISTS staff (
    id SERIAL PRIMARY KEY,
    staff_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    max_hours INT DEFAULT 20
);

CREATE TABLE IF NOT EXISTS staff_subjects (
    staff_id INT NOT NULL REFERENCES staff(id) ON DELETE CASCADE,
    subject_id INT NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    PRIMARY KEY (staff_id, subject_id)
);

CREATE TABLE IF NOT EXISTS classrooms (
    id SERIAL PRIMARY KEY,
    room_code VARCHAR(20) UNIQUE NOT NULL,
    room_type VARCHAR(20) NOT NULL CHECK (room_type IN ('CLASSROOM','LAB')),
    capacity INT DEFAULT 60
);

CREATE TABLE IF NOT EXISTS periods (
    id SERIAL PRIMARY KEY,
    period_no INT NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL
);

CREATE TABLE IF NOT EXISTS timetable (
    id SERIAL PRIMARY KEY,
    day VARCHAR(20) NOT NULL CHECK (day IN ('Monday','Tuesday','Wednesday','Thursday','Friday')),
    period_id INT NOT NULL REFERENCES periods(id),
    subject_id INT NOT NULL REFERENCES subjects(id),
    staff_id INT NOT NULL REFERENCES staff(id),
    classroom_id INT NOT NULL REFERENCES classrooms(id),
    year VARCHAR(5) NOT NULL CHECK (year IN ('I','II','III','IV')),
    course_id INT NOT NULL REFERENCES courses(id),
    semester VARCHAR(10) NOT NULL DEFAULT 'ODD',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(day, period_id, staff_id),
    UNIQUE(day, period_id, classroom_id),
    UNIQUE(day, period_id, year, course_id, semester)
);

-- Create faculty_workload view
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
GROUP BY st.id, st.staff_code, st.name, st.department, st.max_hours;

-- Insert initial data
INSERT INTO users (username, password, role) VALUES
('admin', 'admin123', 'admin'),
('faculty1', 'faculty123', 'faculty'),
('student1', 'student123', 'student')
ON CONFLICT (username) DO NOTHING;

INSERT INTO courses (name) VALUES
('AI & DS'),
('CSE')
ON CONFLICT (name) DO NOTHING;

INSERT INTO periods (period_no, start_time, end_time) VALUES
(1, '09:30:00', '10:20:00'),
(2, '10:20:00', '11:10:00'),
(3, '11:20:00', '12:10:00'),
(4, '12:10:00', '13:00:00'),
(5, '14:00:00', '14:50:00'),
(6, '14:50:00', '15:40:00')
ON CONFLICT DO NOTHING;

INSERT INTO classrooms (room_code, room_type, capacity) VALUES
('C101', 'CLASSROOM', 60),
('C102', 'CLASSROOM', 60),
('AI_LAB', 'LAB', 40),
('DS_LAB', 'LAB', 40)
ON CONFLICT (room_code) DO NOTHING;

INSERT INTO staff (staff_code, name, department, max_hours) VALUES
('FAC001', 'Mrs. R. Nadhiya', 'AI & DS', 18),
('FAC002', 'Mr. S. Kumar', 'CSE', 20)
ON CONFLICT (staff_code) DO NOTHING;

INSERT INTO subjects(code, name, weekly_hours, year, course_id, required_room, semester) VALUES
('CS3691', 'Embedded Systems and IoT', 4, 'III', 1, 'LAB', 'ODD'),
('CS3541', 'Data Warehousing', 4, 'III', 1, 'CLASSROOM', 'ODD'),
('CS3401', 'Computer Networks', 4, 'III', 2, 'CLASSROOM', 'ODD')
ON CONFLICT (code) DO NOTHING;

INSERT INTO staff_subjects(staff_id, subject_id) VALUES
(1, 1),
(1, 2),
(2, 3)
ON CONFLICT (staff_id, subject_id) DO NOTHING;
