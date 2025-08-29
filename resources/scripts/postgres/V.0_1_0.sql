CREATE SCHEMA IF NOT EXISTS medication;

CREATE EXTENSION IF NOT EXISTS pgcrypto;-- dùng gen_random_uuid()


CREATE TABLE IF NOT EXISTS medication.medicine (
      medication_id         SERIAL PRIMARY KEY,
      atc_code              TEXT,                     -- mã ATC (nếu áp dụng)
      medicine_name                  TEXT NOT NULL,            -- tên thương mại hoặc tên hiển thị
      generic_name          TEXT,                     -- tên hoạt chất
      form                  TEXT,                     -- dạng bào chế (viên, ống, sirô,...)
      strength              TEXT,                     -- hàm lượng (e.g., 500 mg)
      unit                  TEXT,                     -- đơn vị định lượng dùng chung nếu cần
      stock                 NUMERIC(14,3) DEFAULT 0 NOT NULL,
      expiry_date           TIMESTAMP,
      is_active             BOOLEAN NOT NULL DEFAULT TRUE,
      created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
      updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS medication.prescription (
      prescription_id       SERIAL PRIMARY KEY,
      prescription_code                  TEXT UNIQUE,                -- mã đơn (nếu cần tra cứu nhanh)
      appointment_id INTEGER NOT NULL REFERENCES appointment_mgmt.appointments(id),
      status TEXT NOT NULL DEFAULT 'CREATED'
           CHECK (status IN ('CREATED','UPDATED','CANCELED','PARTIALLY_DISPENSED','DISPENSED')),
      valid_from            TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL ,
      valid_to              TIMESTAMP,                       -- hạn dùng đơn
      notes                 TEXT,
      created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
      created_by            INTEGER REFERENCES appointment_mgmt.appointments(doctor_id),                       -- user ID hệ thống
      updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
      updated_by            INTEGER REFERENCES appointment_mgmt.appointments(doctor_id),
      canceled_at           TIMESTAMP,
      canceled_by           INTEGER REFERENCES appointment_mgmt.appointments(doctor_id),
      canceled_reason       TEXT,
      CONSTRAINT prescription_valid_range_chk
        CHECK (valid_to IS NULL OR valid_to >= valid_from)
);

CREATE TABLE IF NOT EXISTS medication.prescription_item (
      item_id               SERIAL PRIMARY KEY,
      prescription_id       INTEGER NOT NULL REFERENCES medication.prescription(prescription_id),
      medication_id         INTEGER NOT NULL REFERENCES medication.medicine(medication_id),
      quantity_prescribed   NUMERIC(14,3) NOT NULL CHECK (quantity_prescribed > 0),
      unit_prescribed                 TEXT,                       -- đơn vị phát (viên, ống, ml…)
      dose                  TEXT,                       -- liều (e.g., 1 viên)
      frequency             TEXT,                       -- tần suất (e.g., 2 lần/ngày)
      duration              TEXT,                       -- thời gian dùng (e.g., 5 ngày)
      notes                 TEXT,
      created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
      updated_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 5) Dispense (phiếu cấp phát)
CREATE TABLE IF NOT EXISTS medication.dispense (
      dispense_id           SERIAL PRIMARY KEY,
      prescription_id       INTEGER NOT NULL REFERENCES medication.prescription(prescription_id),
      status TEXT NOT NULL DEFAULT 'PENDING'
           CHECK (status IN ('PENDING','COMPLETED')),
      dispensed_at          TIMESTAMP,               -- thời điểm hoàn tất (COMPLETED)
      dispensed_by          INTEGER REFERENCES appointment_mgmt.doctors(id),                      -- user dược sĩ
      notes                 TEXT
);

CREATE TABLE IF NOT EXISTS medication.dispense_line (
      line_id               SERIAL PRIMARY KEY,
      dispense_id           INTEGER NOT NULL REFERENCES medication.dispense(dispense_id),
      prescription_item_id  INTEGER NOT NULL REFERENCES medication.prescription_item(item_id),
      quantity_dispensed    NUMERIC(14,3) NOT NULL CHECK (quantity_dispensed > 0),
      notes                 TEXT,
      created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);
INSERT INTO medication.medicine (id, atc_code, medicine_name, generic_name, form, strength, unit,stock, expiry_date)
VALUES
    (1, 'A01', 'Paracetamol 500mg', 'Paracetamol', 'Tablet', '500 mg', 'mg',100,'2025-12-31T23:59:59'),
    (2, 'A02', 'Amoxicillin 250mg', 'Amoxicillin', 'Capsule', '250 mg', 'mg',100,'2025-12-31T23:59:59');
