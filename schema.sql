
-- HemoLink Pro Database Schema

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT CHECK(role IN ('donor', 'seeker', 'admin')) NOT NULL,
    phone TEXT NOT NULL,
    city TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Donors Table
CREATE TABLE IF NOT EXISTS donors (
    donor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    blood_group TEXT CHECK(
        blood_group IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')
    ) NOT NULL,
    age INTEGER NOT NULL CHECK(age >= 18),
    gender TEXT CHECK(gender IN ('Male', 'Female', 'Other')),
    last_donation_date DATE,
    status TEXT DEFAULT 'Available'
        CHECK(status IN ('Available', 'Unavailable')),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 3. Blood Inventory Table
CREATE TABLE IF NOT EXISTS blood_inventory (
    inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
    blood_group TEXT UNIQUE NOT NULL,
    units_available INTEGER DEFAULT 0 CHECK(units_available >= 0),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Blood Requests Table
CREATE TABLE IF NOT EXISTS blood_requests (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    seeker_id INTEGER NOT NULL,
    blood_group TEXT NOT NULL,
    units_requested INTEGER NOT NULL CHECK(units_requested > 0),
    hospital_name TEXT NOT NULL,
    city TEXT NOT NULL,
    urgency TEXT DEFAULT 'Normal'
        CHECK(urgency IN ('Normal', 'Urgent', 'Critical')),
    status TEXT DEFAULT 'Pending'
        CHECK(status IN ('Pending', 'Approved', 'Fulfilled', 'Rejected')),
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (seeker_id) REFERENCES users(user_id)
);

-- 5. Donor Responses Table
CREATE TABLE IF NOT EXISTS donor_responses (
    response_id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id INTEGER NOT NULL,
    donor_id INTEGER NOT NULL,
    response_status TEXT DEFAULT 'Pending'
        CHECK(response_status IN ('Pending', 'Accepted', 'Declined')),
    responded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(request_id, donor_id),
    FOREIGN KEY (request_id) REFERENCES blood_requests(request_id),
    FOREIGN KEY (donor_id) REFERENCES donors(donor_id)
);
