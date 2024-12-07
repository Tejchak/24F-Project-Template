# Creating the database
DROP DATABASE if exists coopConnect;
CREATE DATABASE if not exists coopConnect;

show databases;

Use coopConnect;

CREATE table if not exists Category
(
    CategoryID int auto_increment not null,
    CategoryName varchar(75) not null ,
    Primary Key(CategoryID),
    UNIQUE index uq_cat_idx (CategoryName)
);

Create table if not exists City
(
    City_ID int auto_increment not null,
    Avg_Cost_Of_Living integer,
    Avg_Rent double default 0.0,
    Avg_Wage double default 0.0,
    Name varchar(25),
    Population int,
    Prop_Hybrid_Workers decimal(5,4),
    check (Prop_Hybrid_Workers >= 0 and Prop_Hybrid_Workers <=1),
    PRIMARY KEY(City_ID)
);


Create table if not exists User
(
    UserID int auto_increment not null,
    CategoryID int not null,
    name varchar(75),
    email varchar(75),
    Phone_Number varchar(25),
    Date_Created datetime not null default current_timestamp,
    Date_Last_Login datetime not null default current_timestamp
        on update current_timestamp,
    Current_City_ID int not null,
    Primary Key(UserID),
    Unique Index uq_idx_email (email),
    Unique Index uq_idx_pn (Phone_Number),
    CONSTRAINT fk_1
        FOREIGN KEY (CategoryID) references Category (CategoryID)
            ON UPDATE cascade
            on delete cascade,
    CONSTRAINT fk_2
        FOREIGN KEY (Current_City_ID) references City (City_ID)
            on update cascade
            on delete restrict
);

ALTER TABLE User 
ADD CONSTRAINT chk_email_format 
CHECK (email LIKE '%_@__%.__%');

ALTER TABLE User
ADD CONSTRAINT chk_phone_format
CHECK (Phone_Number REGEXP '^[0-9]{3}-[0-9]{3}-[0-9]{4}$');

CREATE table if not exists Location
(
    Zip int not null,
    City_ID int not null,
    Student_pop int,
    Safety_Rating int,
    PRIMARY KEY(Zip),
    constraint loc_city
        FOREIGN KEY (City_ID) references City (City_ID)

);

Create table if not exists Housing
(
    Housing_ID int auto_increment not null,
    City_ID int not null,
    zipID int not null,
    Address varchar(75) not null,
    Rent int,
    Sq_Ft int not null,
    PRIMARY KEY (Housing_ID),
    Unique Index uq_idx_addy (Address),
    CONSTRAINT fk_03
        foreign key (City_ID) references City (City_ID),
    CONSTRAINT fk_04
        foreign key (zipID) references Location (Zip)
);

CREATE table if not exists Sublet
(
    Sublet_ID int auto_increment not null,
    Housing_ID int not null,
    Subleter_ID int,
    Start_Date datetime,
    End_Date datetime,
    PRIMARY KEY(Sublet_ID, Subleter_ID),
    CONSTRAINT fk_05
        foreign key (Housing_ID) references Housing (Housing_ID)
            ON UPDATE CASCADE
            ON DELETE CASCADE,
    CONSTRAINT fk_06
        foreign key (Subleter_ID) references User (UserID)
);

CREATE table if not exists Job
(
    Job_ID int auto_increment not null,
    Wage int not null,
    User_ID int not null,
    Employment_Status varchar(30),
    start_date datetime,
    PRIMARY KEY(Job_ID),
    CONSTRAINT fk_08
        foreign key (User_ID) references User (UserID)
);

Create table if not exists Performance
(
    PID int auto_increment not null,
    Date datetime default current_timestamp,
    Avg_Speed int,
    Median_Speed int,
    Top_Speed int,
    Low_Speed int,
    PRIMARY KEY(PID)
);

CREATE table if not exists Airport
(
    Air_ID int auto_increment not null,
    Name varchar(50) not null,
    City_ID int not null,
    Zip int not null,
    PRIMARY KEY(Air_ID),
    constraint fk_air_city
        foreign key (City_ID) references City (City_ID),
    constraint fk_air_zip
        foreign key (Zip) references Location (Zip)
);

Create table if not exists Hospital (
    HospitalID int auto_increment not null PRIMARY KEY,
    Name varchar(50) not null,
    City_ID int not null,
    Zip int not null,
    CONSTRAINT fk_07
        foreign key  (City_ID) references City (City_ID),
    CONSTRAINT fk_11
        foreign key (Zip) references Location (Zip)
);

Create table if not exists JobPosting (
    Title varchar(75) not null, 
    Post_ID int auto_increment not null,
    Compensation int,
    Location_ID int not null,
    User_ID int not null,
    Bio Text not null,

    Primary Key (Post_ID),
    Constraint jp_loc
        foreign key (Location_ID) references Location (Zip),
    Constraint jp_user
        foreign key (User_ID) references User (UserID)
);

#We set the delimiter to be a double // here since when we looked up how to do trigger statements
#we found that they each contain a begin and end statement, but inside the trigger statement there are
#semicolons, so if the delimiter was still a semicolon mysql would try end the trigger definition early
#we change the delimiter back to semicolons after we define all our triggers
DELIMITER //
DROP TRIGGER IF EXISTS update_city_avg_rent_insert;
CREATE TRIGGER update_city_avg_rent_insert
AFTER INSERT ON Housing
FOR EACH ROW
BEGIN
    UPDATE City
    SET Avg_Rent = (
        SELECT AVG(Rent)
        FROM Housing
        WHERE City_ID = NEW.City_ID
    )
    WHERE City_ID = NEW.City_ID;
END;//

DROP TRIGGER IF EXISTS update_city_avg_rent_update;
CREATE TRIGGER update_city_avg_rent_update
AFTER UPDATE ON Housing
FOR EACH ROW
BEGIN
    UPDATE City
    SET Avg_Rent = (
        SELECT AVG(Rent)
        FROM Housing
        WHERE City_ID = NEW.City_ID
    )
    WHERE City_ID = NEW.City_ID;
END;//

DROP TRIGGER IF EXISTS update_city_avg_rent_delete;
CREATE TRIGGER update_city_avg_rent_delete
AFTER DELETE ON Housing
FOR EACH ROW
BEGIN
    UPDATE City
    SET Avg_Rent = (
        SELECT AVG(Rent)
        FROM Housing
        WHERE City_ID = OLD.City_ID
    )
    WHERE City_ID = OLD.City_ID;
END;//

DROP TRIGGER IF EXISTS update_city_avg_wage_insert;
CREATE TRIGGER update_city_avg_wage_insert
AFTER INSERT ON Job
FOR EACH ROW
BEGIN
    UPDATE City
    SET Avg_Wage = (
        SELECT AVG(j.Wage)
        FROM Job j
        JOIN User u ON j.User_ID = u.UserID
        WHERE u.Current_City_ID = (
            SELECT Current_City_ID
            FROM User
            WHERE UserID = NEW.User_ID
        )
    )
    WHERE City_ID = (
        SELECT Current_City_ID
        FROM User
        WHERE UserID = NEW.User_ID
    );
END;//

DROP TRIGGER IF EXISTS update_city_avg_wage_update;
CREATE TRIGGER update_city_avg_wage_update
AFTER UPDATE ON Job
FOR EACH ROW
BEGIN
    UPDATE City
    SET Avg_Wage = (
        SELECT AVG(j.Wage)
        FROM Job j
        JOIN User u ON j.User_ID = u.UserID
        WHERE u.Current_City_ID = (
            SELECT Current_City_ID
            FROM User
            WHERE UserID = NEW.User_ID
        )
    )
    WHERE City_ID = (
        SELECT Current_City_ID
        FROM User
        WHERE UserID = NEW.User_ID
    );
END;//

DROP TRIGGER IF EXISTS update_city_avg_wage_delete;
CREATE TRIGGER update_city_avg_wage_delete
AFTER DELETE ON Job
FOR EACH ROW
BEGIN
    UPDATE City
    SET Avg_Wage = (
        SELECT AVG(j.Wage)
        FROM Job j
        JOIN User u ON j.User_ID = u.UserID
        WHERE u.Current_City_ID = (
            SELECT Current_City_ID
            FROM User
            WHERE UserID = OLD.User_ID
        )
    )
    WHERE City_ID = (
        SELECT Current_City_ID
        FROM User
        WHERE UserID = OLD.User_ID
    );
END;//

DELIMITER ;

#Category data
INSERT INTO Category (CategoryName) VALUES
('Student'),
('Employer'),
('Administrator'),
('Financial Advisor'),
('Parent'),
('System Administrator');

#City data
INSERT INTO City (Avg_Cost_Of_Living, Avg_Rent, Avg_Wage, Name, Population, Prop_Hybrid_Workers) VALUES
(3000, 1500, 3500, 'Boston', 700000, 0.2500),
(2000, 1000, 2500, 'Chicago', 2700000, 0.1500),
(4000, 2500, 4500, 'New York', 8000000, 0.4000),
(2500, 1200, 3000, 'Seattle', 800000, 0.3000),
(1800, 900, 2200, 'Atlanta', 500000, 0.2000),
(2200, 1100, 2400, 'San Francisco', 880000, 0.3500),
(2700, 1300, 3200, 'Los Angeles', 4000000, 0.3000),
(2300, 1150, 2800, 'Miami', 470000, 0.2800),
(2100, 1050, 2600, 'Dallas', 1300000, 0.2200),
(1900, 950, 2300, 'Houston', 2300000, 0.2100),
(3000, 1500, 3500, 'Phoenix', 1600000, 0.2400),
(2800, 1400, 3300, 'Philadelphia', 1600000, 0.2600),
(3200, 1600, 3700, 'Washington D.C.', 700000, 0.3000),
(3600, 1800, 4100, 'San Diego', 1400000, 0.3200),
(3700, 1900, 4200, 'Orlando', 300000, 0.2900),
(3800, 2000, 4300, 'Las Vegas', 600000, 0.3000),
(3900, 2100, 4400, 'Denver', 700000, 0.3100),
(4000, 2200, 4500, 'Portland', 650000, 0.3300),
(4100, 2300, 4600, 'Salt Lake City', 200000, 0.3400),
(4200, 2400, 4700, 'Nashville', 700000, 0.3500),
(4300, 2500, 4800, 'Charlotte', 900000, 0.3600),
(4400, 2600, 4900, 'Indianapolis', 800000, 0.3700),
(4500, 2700, 5000, 'Cleveland', 400000, 0.3800),
(4600, 2800, 5100, 'Detroit', 670000, 0.3900),
(4700, 2900, 5200, 'Baltimore', 600000, 0.4000),
(4800, 3000, 5300, 'Milwaukee', 600000, 0.4100),
(4900, 3100, 5400, 'Kansas City', 500000, 0.4200),
(5000, 3200, 5500, 'Omaha', 500000, 0.4300),
(5100, 3300, 5600, 'Tampa', 400000, 0.4400),
(5200, 3400, 5700, 'Louisville', 600000, 0.4500),
(5300, 3500, 5800, 'Virginia Beach', 450000, 0.4600);

#Location data
INSERT INTO Location (Zip, City_ID, Student_pop, Safety_Rating) VALUES
(02115, 1, 500, 8),
(60616, 2, 300, 7),
(10001, (SELECT City_ID FROM City WHERE Name = 'New York'), 200, 6),
(94103, 4, 150, 8),
(98101, 5, 800, 9),
(33101, 6, 600, 7),
(48201, 7, 400, 6),
(02130, 1, 700, 8),
(60614, 2, 900, 7),
(10002, 3, 350, 9),
(94105, 4, 250, 8),
(98102, 5, 950, 9),
(33102, 6, 100, 7),
(48202, 7, 120, 6),
(02131, 1, 180, 8),
(60615, 2, 110, 7),
(10003, 3, 130, 9),
(94104, 4, 140, 8),
(98103, 5, 150, 9),
(33103, 6, 160, 7),
(48203, 7, 170, 6),
(02132, 1, 190, 8),
(60617, 2, 200, 7),
(10004, 3, 220, 9),
(94106, 4, 210, 8),
(98104, 5, 230, 9),
(33104, 6, 240, 7),
(48204, 7, 250, 6),
(02133, 1, 260, 8),
(60618, 2, 270, 7),
(10005, 3, 280, 9),
(94107, 4, 290, 8),
(98105, 5, 300, 6),
(33105, 6, 310, 1),
(48205, 7, 320, 2),
(02134, 1, 330, 8),
(60619, 2, 340, 2),
(10006, 3, 350, 1),
(94108, 4, 360, 2),
(98106, 5, 370, 4),
(33106, 6, 380, 1),
(48206, 7, 390, 3),
(02135, 1, 400, 2),
(60620, 2, 410, 4),
(10007, 3, 420, 4),
(94109, 4, 430, 2),
(98107, 5, 440, 3),
(33107, 6, 450, 1),
(48207, 7, 460, 5),
(90001, 7, 200, 7),  -- Los Angeles
(90002, 7, 250, 6),
(90003, 7, 300, 8),
(90004, 7, 180, 7),
(90005, 7, 220, 6),
(90006, 7, 270, 8),
(90007, 7, 310, 7),
(75201, 9, 150, 8),  -- Dallas
(75202, 9, 200, 7),
(75203, 9, 250, 6),
(75204, 9, 180, 8),
(75205, 9, 220, 7),
(75206, 9, 270, 6),
(75207, 9, 310, 8),
(77001, 10, 160, 7),  -- Houston
(77002, 10, 210, 6),
(77003, 10, 260, 8),
(77004, 10, 190, 7),
(77005, 10, 230, 6),
(77006, 10, 280, 8),
(77007, 10, 320, 7);

#User data
INSERT INTO User (CategoryID, name, email, Phone_Number, Current_City_ID, Date_Created, Date_Last_Login) VALUES
(1, 'John Doe', 'john.doe@example.com', '123-456-7890', 1, '2024-07-01', '2024-12-04'),
(2, 'Jane Smith', 'jane.smith@example.com', '987-654-3210', 2, '2024-07-05', '2024-12-03'),
(1, 'Alice Walker', 'alice.walker@example.com', '555-123-4561', 3, '2024-07-10', '2024-12-02'),
(2, 'Bob Brown', 'bob.brown@example.com', '555-123-4562', 4, '2024-07-15', '2024-12-01'),
(1, 'Charlie Johnson', 'charlie.johnson@example.com', '555-123-4563', 5, '2024-07-20', '2024-11-30'),
(2, 'Diana Prince', 'diana.prince@example.com', '555-123-4564', 6, '2024-07-25', '2024-11-29'),
(1, 'Edward Elric', 'edward.elric@example.com', '555-123-4565', 7, '2024-08-01', '2024-11-28'),
(2, 'Fiona Gallagher', 'fiona.gallagher@example.com', '555-123-4566', 8, '2024-08-05', '2024-11-27'),
(1, 'George Washington', 'george.washington@example.com', '555-123-4567', 9, '2024-08-10', '2024-11-26'),
(2, 'Hannah Montana', 'hannah.montana@example.com', '555-123-4568', 10, '2024-08-15', '2024-11-25'),
(1, 'Ivy League', 'ivy.league@example.com', '555-123-4569', 11, '2024-08-20', '2024-11-24'),
(2, 'Jack Sparrow', 'jack.sparrow@example.com', '555-123-4570', 12, '2024-08-25', '2024-11-23'),
(1, 'Katherine Johnson', 'katherine.johnson@example.com', '555-123-4571', 13, '2024-09-01', '2024-11-22'),
(2, 'Liam Neeson', 'liam.neeson@example.com', '555-123-4572', 14, '2024-09-05', '2024-11-21'),
(1, 'Mia Wallace', 'mia.wallace@example.com', '555-123-4573', 15, '2024-09-10', '2024-11-20'),
(2, 'Nina Simone', 'nina.simone@example.com', '555-123-4574', 16, '2024-09-15', '2024-11-19'),
(1, 'Oscar Wilde', 'oscar.wilde@example.com', '555-123-4575', 17, '2024-09-20', '2024-11-18'),
(2, 'Peter Parker', 'peter.parker@example.com', '555-123-4576', 18, '2024-09-25', '2024-11-17'),
(1, 'Quinn Fabray', 'quinn.fabray@example.com', '555-123-4577', 19, '2024-10-01', '2024-11-16'),
(2, 'Ron Weasley', 'ron.weasley@example.com', '555-123-4578', 20, '2024-10-05', '2024-11-15'),
(1, 'Steve Rogers', 'steve.rogers@example.com', '555-123-4579', 21, '2024-10-10', '2024-11-14'),
(2, 'Tony Stark', 'tony.stark@example.com', '555-123-4580', 22, '2024-10-15', '2024-11-13'),
(1, 'Uma Thurman', 'uma.thurman@example.com', '555-123-4581', 23, '2024-10-20', '2024-11-12'),
(2, 'Vince Vaughn', 'vince.vaughn@example.com', '555-123-4582', 24, '2024-10-25', '2024-11-11'),
(1, 'Will Smith', 'will.smith@example.com', '555-123-4583', 25, '2024-11-01', '2024-11-10'),
(2, 'Xena Warrior', 'xena.warrior@example.com', '555-123-4584', 26, '2024-11-05', '2024-11-09'),
(1, 'Yoda Jedi', 'yoda.jedi@example.com', '555-123-4585', 27, '2024-11-10', '2024-11-08'),
(2, 'Zoe Saldana', 'zoe.saldana@example.com', '555-123-4586', 28, '2024-11-15', '2024-11-07'),
(1, 'Albus Dumbledore', 'albus.dumbledore@example.com', '555-123-4587', 29, '2024-11-20', '2024-11-06'),
(2, 'Bella Swan', 'bella.swan@example.com', '555-123-4588', 30, '2024-11-25', '2024-11-05'),
(1, 'Cinderella', 'cinderella@example.com', '555-123-4589', 27, '2024-11-27', '2024-11-04'),
(2, 'Darth Vader', 'darth.vader@example.com', '555-123-4590', 6, '2024-11-29', '2024-11-03'),
(1, 'Eleanor Rigby', 'eleanor.rigby@example.com', '555-123-4591', 8, '2024-12-01', '2024-11-02'),
(2, 'Frodo Baggins', 'frodo.baggins@example.com', '555-123-4592', 2, '2024-12-01', '2024-11-01'),
(1, 'Gandalf Grey', 'gandalf.grey@example.com', '555-123-4593', 3, '2024-12-02', '2024-10-31'),
(2, 'Hermione Granger', 'hermione.granger@example.com', '555-123-4594', 3, '2024-12-02', '2024-10-30'),
(1, 'Icarus Flight', 'icarus.flight@example.com', '555-123-4595', 3, '2024-12-03', '2024-10-29'),
(2, 'Jasmine Aladdin', 'jasmine.aladdin@example.com', '555-123-4596', 8, '2024-12-03', '2024-10-28'),
(1, 'Klaus Mikaelson', 'klaus.mikaelson@example.com', '555-123-4597', 21, '2024-12-04', '2024-10-27'),
(2, 'Luna Lovegood', 'luna.lovegood@example.com', '555-123-4598', 2, '2024-12-04', '2024-10-26'),
(4, 'Michael Bloomberg', 'michael.bloomberg@finance.com', '555-123-4599', 3, '2024-11-15', '2024-12-04'),
(4, 'Warren Buffett', 'warren.buffett@finance.com', '555-123-4600', 2, '2024-11-20', '2024-12-03'),
(5, 'Sarah Connor', 'sarah.connor@family.com', '555-123-4601', 1, '2024-11-25', '2024-12-02'),
(5, 'Molly Weasley', 'molly.weasley@family.com', '555-123-4602', 4, '2024-11-28', '2024-12-01'),
(6, 'Neo Matrix', 'neo.matrix@sysadmin.com', '555-123-4603', 5, '2024-12-01', '2024-11-30'),
(6, 'Barbara Gordon', 'barbara.gordon@sysadmin.com', '555-123-4604', 3, '2024-12-02', '2024-11-29'),
(4, 'Peter Lynch', 'peter.lynch@finance.com', '555-123-4605', 1, '2024-12-03', '2024-11-28'),
(5, 'Marge Simpson', 'marge.simpson@family.com', '555-123-4606', 2, '2024-12-03', '2024-11-27'),
(6, 'Elliot Alderson', 'elliot.alderson@sysadmin.com', '555-123-4607', 4, '2024-12-04', '2024-11-26');


#Housing data
INSERT INTO Housing (City_ID, zipID, Address, Rent, Sq_Ft) VALUES
(1, 02115, '123 Beacon St, Boston', 2500, 800),
(1, 02130, '456 Commonwealth Ave, Boston', 2700, 850),
(1, 02131, '789 Newbury St, Boston', 2800, 900),
(1, 02132, '321 Boylston St, Boston', 2900, 850),
(1, 02133, '654 Marlborough St, Boston', 3000, 900),
(1, 02134, '987 Huntington Ave, Boston', 3100, 850),
(1, 02135, '135 Harvard Ave, Boston', 3200, 875),

(2, 60616, '123 Michigan Ave, Chicago', 2200, 800),
(2, 60614, '456 State St, Chicago', 2400, 850),
(2, 60615, '789 Wacker Dr, Chicago', 2600, 900),
(2, 60617, '321 Lake Shore Dr, Chicago', 2800, 850),
(2, 60618, '654 Clark St, Chicago', 3000, 900),
(2, 60619, '987 Rush St, Chicago', 3200, 850),
(2, 60620, '741 Wells St, Chicago', 3300, 875),

(3, 10001, '123 Broadway, New York', 3500, 750),
(3, 10002, '456 5th Avenue, New York', 3700, 800),
(3, 10003, '789 Madison Ave, New York', 3800, 850),
(3, 10004, '321 Park Avenue, New York', 3900, 800),
(3, 10005, '654 Lexington Ave, New York', 4000, 900),
(3, 10006, '987 3rd Avenue, New York', 4100, 850),
(3, 10007, '159 7th Avenue, New York', 4200, 875),

(4, 98101, '123 Pike St, Seattle', 2800, 800),
(4, 98102, '456 Pine St, Seattle', 3000, 850),
(4, 98103, '789 Union St, Seattle', 3200, 900),
(4, 98104, '321 Madison St, Seattle', 3400, 850),
(4, 98105, '654 Spring St, Seattle', 3600, 900),
(4, 98106, '987 Seneca St, Seattle', 3800, 850),
(4, 98107, '258 Mercer St, Seattle', 4000, 875),

(5, 94103, '123 Market St, Atlanta', 3800, 750),
(5, 94104, '456 Mission St, Atlanta', 4000, 800),
(5, 94105, '789 Howard St, Atlanta', 4200, 850),
(5, 94106, '321 Folsom St, Atlanta', 4400, 800),
(5, 94107, '654 Valencia St, Atlanta', 4600, 900),
(5, 94108, '987 Harrison St, Atlanta', 4800, 850),
(5, 94109, '147 Brannan St, Atlanta', 5000, 875),

(6, 33101, '123 Ocean Drive, San Francisco', 2600, 800),
(6, 33102, '456 Collins Ave, San Francisco', 2800, 850),
(6, 33103, '789 Washington Ave, San Francisco', 3000, 900),
(6, 33104, '321 Lincoln Rd, San Francisco', 3200, 850),
(6, 33105, '654 Alton Rd, San Francisco', 3400, 900),
(6, 33106, '987 Biscayne Blvd, San Francisco', 3600, 850),
(6, 33107, '369 Collins Ave, San Francisco', 3800, 875),

(7, 90001, '123 Sunset Blvd, Los Angeles', 3300, 750),
(7, 90002, '456 Hollywood Blvd, Los Angeles', 3500, 800),
(7, 90003, '789 Venice Blvd, Los Angeles', 3700, 850),
(7, 90004, '321 Wilshire Blvd, Los Angeles', 3900, 800),
(7, 90005, '654 Santa Monica Blvd, Los Angeles', 4100, 900),
(7, 90006, '987 Melrose Ave, Los Angeles', 4300, 850),
(7, 90007, '147 Rodeo Dr, Los Angeles', 4500, 875),

(8, 75201, '123 Main St, Miami', 2100, 800),
(8, 75202, '456 Commerce St, Miami', 2300, 850),
(8, 75203, '789 Elm St, Miami', 2500, 900),
(8, 75204, '321 McKinney Ave, Miami', 2700, 850),
(8, 75205, '654 Ross Ave, Miami', 2900, 900),
(8, 75206, '987 Live Oak St, Miami', 3100, 850),
(8, 75207, '369 Pearl St, Miami', 3300, 875),

(9, 77001, '123 Main St, Dallas', 2000, 800),
(9, 77002, '456 Travis St, Dallas', 2200, 850),
(9, 77003, '789 Congress Ave, Dallas', 2400, 900),
(9, 77004, '321 Louisiana St, Dallas', 2600, 850),
(9, 77005, '654 Smith St, Dallas', 2800, 900),
(9, 77006, '987 Milam St, Dallas', 3000, 850),
(9, 77007, '258 Washington Ave, Dallas', 3200, 875);

#Sublet data
INSERT INTO Sublet (Housing_ID, Subleter_ID, Start_Date, End_Date) VALUES
(1, 1, '2024-01-01', '2024-06-01'),
(2, 2, '2024-02-01', '2024-07-01'),
(3, 3, '2024-02-01', '2024-07-01'),
(4, 4, '2024-03-01', '2024-08-01'),
(5, 5, '2024-04-01', '2024-09-01'),
(6, 6, '2024-05-01', '2024-10-01'),
(7, 7, '2024-06-01', '2024-11-01'),
(1, 8, '2024-07-01', '2024-12-01'),
(2, 9, '2024-08-01', '2024-01-01'),
(3, 10, '2024-09-01', '2024-02-01'),
(4, 11, '2024-10-01', '2024-03-01'),
(5, 12, '2024-11-01', '2024-04-01'),
(6, 13, '2024-12-01', '2024-05-01'),
(7, 14, '2024-01-01', '2024-06-01'),
(1, 15, '2024-02-01', '2024-07-01'),
(2, 16, '2024-03-01', '2024-08-01'),
(3, 17, '2024-04-01', '2024-09-01'),
(4, 18, '2024-05-01', '2024-10-01'),
(5, 19, '2024-06-01', '2024-11-01'),
(6, 20, '2024-07-01', '2024-12-01'),
(7, 21, '2024-08-01', '2024-01-01'),
(1, 22, '2024-09-01', '2024-02-01'),
(2, 23, '2024-10-01', '2024-03-01'),
(3, 24, '2024-11-01', '2024-04-01'),
(4, 25, '2024-12-01', '2024-05-01'),
(5, 26, '2024-01-01', '2024-06-01'),
(6, 27, '2024-02-01', '2024-07-01'),
(7, 28, '2024-03-01', '2024-08-01'),
(1, 29, '2024-04-01', '2024-09-01'),
(2, 30, '2024-05-01', '2024-10-01'),
(3, 31, '2024-06-01', '2024-11-01'),
(4, 32, '2024-07-01', '2024-12-01'),
(5, 33, '2024-08-01', '2024-01-01'),
(6, 34, '2024-09-01', '2024-02-01'),
(7, 35, '2024-10-01', '2024-03-01'),
(1, 36, '2024-11-01', '2024-04-01'),
(2, 37, '2024-12-01', '2024-05-01'),
(3, 38, '2024-01-01', '2024-06-01'),
(4, 39, '2024-02-01', '2024-07-01'),
(6, 1, '2024-04-01', '2024-09-01'),
(7, 2, '2024-05-01', '2024-10-01'),
(1, 3, '2024-06-01', '2024-11-01'),
(2, 4, '2024-07-01', '2024-12-01'),
(3, 5, '2024-08-01', '2024-01-01'),
(4, 6, '2024-09-01', '2024-02-01'),
(5, 7, '2024-10-01', '2024-03-01'),
(6, 8, '2024-11-01', '2024-04-01'),
(7, 9, '2024-12-01', '2024-05-01'),
(1, 10, '2024-01-01', '2024-06-01'),
(2, 11, '2024-02-01', '2024-07-01'),
(3, 12, '2024-03-01', '2024-08-01'),
(4, 13, '2024-04-01', '2024-09-01'),
(5, 14, '2024-05-01', '2024-10-01'),
(6, 15, '2024-06-01', '2024-11-01'),
(7, 16, '2024-07-01', '2024-12-01'),
(1, 17, '2024-08-01', '2024-01-01'),
(2, 18, '2024-09-01', '2024-02-01'),
(3, 19, '2024-10-01', '2024-03-01'),
(4, 20, '2024-11-01', '2024-04-01'),
(5, 21, '2024-12-01', '2024-05-01'),
(6, 22, '2024-01-01', '2024-06-01'),
(7, 23, '2024-02-01', '2024-07-01'),
(1, 24, '2024-03-01', '2024-08-01'),
(2, 25, '2024-04-01', '2024-09-01'),
(3, 26, '2024-05-01', '2024-10-01'),
(4, 27, '2024-06-01', '2024-11-01'),
(5, 28, '2024-07-01', '2024-12-01'),
(6, 29, '2024-08-01', '2024-01-01'),
(7, 30, '2024-09-01', '2024-02-01'),
(1, 31, '2024-10-01', '2024-03-01'),
(2, 32, '2024-11-01', '2024-04-01'),
(3, 33, '2024-12-01', '2024-05-01'),
(4, 34, '2024-01-01', '2024-06-01'),
(5, 35, '2024-02-01', '2024-07-01'),
(6, 36, '2024-03-01', '2024-08-01'),
(7, 37, '2024-04-01', '2024-09-01'),
(1, 38, '2024-05-01', '2024-10-01'),
(2, 39, '2024-06-01', '2024-11-01'),
(4, 1, '2024-08-01', '2024-01-01'),
(5, 2, '2024-09-01', '2024-02-01'),
(6, 3, '2024-10-01', '2024-03-01'),
(7, 4, '2024-11-01', '2024-04-01'),
(1, 5, '2024-12-01', '2024-05-01'),
(2, 6, '2024-01-01', '2024-06-01'),
(3, 7, '2024-02-01', '2024-07-01'),
(4, 8, '2024-03-01', '2024-08-01'),
(5, 9, '2024-04-01', '2024-09-01'),
(6, 10, '2024-05-01', '2024-10-01'),
(7, 11, '2024-06-01', '2024-11-01'),
(1, 12, '2024-07-01', '2024-12-01'),
(2, 13, '2024-08-01', '2024-01-01'),
(3, 14, '2024-09-01', '2024-02-01'),
(4, 15, '2024-10-01', '2024-03-01'),
(5, 16, '2024-11-01', '2024-04-01'),
(6, 17, '2024-12-01', '2024-05-01'),
(7, 18, '2024-01-01', '2024-06-01'),
(1, 19, '2024-02-01', '2024-07-01'),
(2, 20, '2024-03-01', '2024-08-01'),
(3, 21, '2024-04-01', '2024-09-01'),
(4, 22, '2024-05-01', '2024-10-01'),
(5, 23, '2024-06-01', '2024-11-01'),
(6, 24, '2024-07-01', '2024-12-01'),
(7, 25, '2024-08-01', '2024-01-01'),
(1, 26, '2024-09-01', '2024-02-01'),
(2, 27, '2024-10-01', '2024-03-01'),
(3, 28, '2024-11-01', '2024-04-01'),
(4, 29, '2024-12-01', '2024-05-01'),
(5, 30, '2024-01-01', '2024-06-01'),
(6, 31, '2024-02-01', '2024-07-01'),
(7, 32, '2024-03-01', '2024-08-01'),
(1, 33, '2024-04-01', '2024-09-01'),
(2, 34, '2024-05-01', '2024-10-01'),
(3, 35, '2024-06-01', '2024-11-01'),
(4, 36, '2024-07-01', '2024-12-01'),
(5, 37, '2024-08-01', '2024-01-01'),
(2, 1, '2024-12-01', '2024-05-01'),
(3, 2, '2024-01-01', '2024-06-01'),
(4, 3, '2024-02-01', '2024-07-01'),
(5, 4, '2024-03-01', '2024-08-01'),
(6, 5, '2024-04-01', '2024-09-01'),
(7, 6, '2024-05-01', '2024-10-01'),
(1, 7, '2024-06-01', '2024-11-01'),
(2, 8, '2024-07-01', '2024-12-01'),
(3, 9, '2024-08-01', '2024-01-01'),
(4, 10, '2024-09-01', '2024-02-01'),
(5, 11, '2024-10-01', '2024-03-01'),
(6, 12, '2024-11-01', '2024-04-01'),
(7, 13, '2024-12-01', '2024-05-01'),
(1, 14, '2024-01-01', '2024-06-01'),
(2, 15, '2024-02-01', '2024-07-01'),
(3, 16, '2024-03-01', '2024-08-01'),
(4, 17, '2024-04-01', '2024-09-01'),
(5, 18, '2024-05-01', '2024-10-01');

#Job data
INSERT INTO Job (Wage, User_ID, Employment_Status, start_date) VALUES
(20, 1, 'Part-Time', '2023-09-01'),
(50, 2, 'Full-Time', '2023-07-01'),
(52000, 13, 'Full-Time', '2024-01-01'),
(46000, 14, 'Contract', '2024-02-01'),
(57000, 15, 'Full-Time', '2024-03-01'),
(54000, 16, 'Part-Time', '2024-04-01'),
(63000, 17, 'Full-Time', '2024-05-01'),
(49000, 18, 'Intern', '2024-06-01'),
(58000, 19, 'Contract', '2024-07-01'),
(62000, 20, 'Full-Time', '2024-08-01'),
(55000, 21, 'Part-Time', '2024-09-01'),
(59000, 22, 'Full-Time', '2024-10-01'),
(61000, 23, 'Contract', '2024-11-01'),
(52000, 24, 'Part-Time', '2024-12-01'),
(64000, 25, 'Full-Time', '2025-01-01'),
(56000, 26, 'Intern', '2025-02-01'),
(67000, 27, 'Contract', '2025-03-01'),
(60000, 28, 'Full-Time', '2025-04-01'),
(58000, 29, 'Part-Time', '2025-05-01'),
(62000, 30, 'Full-Time', '2025-06-01'),
(53000, 31, 'Contract', '2025-07-01'),
(61000, 32, 'Full-Time', '2025-08-01'),
(56000, 33, 'Part-Time', '2025-09-01'),
(59000, 34, 'Intern', '2025-10-01'),
(63000, 35, 'Full-Time', '2025-11-01'),
(54000, 36, 'Contract', '2025-12-01'),
(65000, 37, 'Part-Time', '2026-01-01'),
(58000, 38, 'Full-Time', '2026-02-01'),
(61000, 39, 'Contract', '2026-03-01'),
(59000, 40, 'Full-Time', '2026-04-01'),
(56000, 1, 'Part-Time', '2026-05-01'),
(60000, 2, 'Intern', '2026-06-01'),
(62000, 3, 'Full-Time', '2026-07-01'),
(57000, 4, 'Contract', '2026-08-01'),
(64000, 5, 'Full-Time', '2026-09-01'),
(53000, 6, 'Part-Time', '2026-10-01'),
(65000, 7, 'Full-Time', '2026-11-01'),
(56000, 8, 'Contract', '2026-12-01'),
(61000, 9, 'Part-Time', '2027-01-01'),
(59000, 10, 'Full-Time', '2027-02-01'),
(62000, 11, 'Contract', '2027-03-01'),
(58000, 12, 'Intern', '2027-04-01'),
(64000, 13, 'Full-Time', '2027-05-01'),
(53000, 14, 'Part-Time', '2027-06-01'),
(60000, 15, 'Contract', '2027-07-01'),
(62000, 16, 'Full-Time', '2027-08-01'),
(57000, 17, 'Intern', '2027-09-01'),
(63000, 18, 'Full-Time', '2027-10-01'),
(55000, 19, 'Contract', '2027-11-01'),
(61000, 20, 'Part-Time', '2027-12-01');

#Performance data
-- Sample data for Performance (30 rows)
INSERT INTO Performance (Date, Avg_Speed, Median_Speed, Top_Speed, Low_Speed) VALUES
('2024-01-01', 60, 55, 80, 40),
('2024-01-02', 70, 65, 90, 50),
('2024-01-03', 75, 70, 95, 55),
('2024-01-04', 65, 60, 85, 45),
('2024-01-05', 80, 75, 100, 60),
('2024-01-06', 68, 63, 88, 48),
('2024-01-07', 72, 67, 92, 52),
('2024-01-08', 66, 61, 86, 46),
('2024-01-09', 74, 69, 94, 54),
('2024-01-10', 78, 73, 98, 58),
('2024-01-11', 62, 57, 82, 42),
('2024-01-12', 64, 59, 84, 44),
('2024-01-13', 70, 65, 90, 50),
('2024-01-14', 76, 71, 96, 56),
('2024-01-15', 82, 77, 102, 62),
('2024-01-16', 60, 55, 80, 40),
('2024-01-17', 72, 67, 92, 52),
('2024-01-18', 74, 69, 94, 54),
('2024-01-19', 68, 63, 88, 48),
('2024-01-20', 66, 61, 86, 46),
('2024-01-21', 78, 73, 98, 58),
('2024-01-22', 80, 75, 100, 60),
('2024-01-23', 64, 59, 84, 44),
('2024-01-24', 62, 57, 82, 42),
('2024-01-25', 70, 65, 90, 50),
('2024-01-26', 76, 71, 96, 56),
('2024-01-27', 82, 77, 102, 62),
('2024-01-28', 60, 55, 80, 40),
('2024-01-29', 72, 67, 92, 52),
('2024-01-30', 74, 69, 94, 54);
-- Sample data for Airport (10 rows)
INSERT INTO Airport (Name, City_ID, Zip) VALUES
('Logan International Airport', 1, 02115),
('O\'Hare International Airport', 2, 60616),
('John F. Kennedy International Airport', 3, 10001),
('Los Angeles International Airport', 4, 48204),
('San Francisco International Airport', 5, 94103),
('Seattle-Tacoma International Airport', 6, 98101),
('Denver International Airport', 7, 48202),
('Dallas/Fort Worth International Airport', 8, 98107),
('Miami International Airport', 9, 33101),
('Hartsfield-Jackson Atlanta International Airport', 10, 10006);

-- Sample data for Hospital (10 rows)
INSERT INTO Hospital (Name, City_ID, Zip) VALUES
('Boston Medical Center', 1, 02115),
('Rush University Medical Center', 2, 60616),
('New York General Hospital', 3, 10001),
('UCSF Medical Center', 5, 94103),
('Swedish Medical Center', 6, 98101),
('Denver Health Medical Center', 7, 48202),
('Baylor University Medical Center', 8, 98107),
('Jackson Memorial Hospital', 9, 33101),
('Orlando Health', 10, 94105),
('Emory University Hospital', 10, 10006);

-- Sample data for JobPosting (50 rows)
INSERT INTO JobPosting (Title, Bio, Compensation, Location_ID, User_ID) VALUES
('Software Engineer', 'Develop and maintain software applications.', 80000, 02115, 1),  -- Boston
('Data Scientist', 'Analyze data to drive business solutions.', 95000, 60616, 2),  -- Chicago
('Web Developer', 'Create and manage websites and web applications.', 75000, 10001, 3),  -- New York
('Product Manager', 'Lead product development and strategy.', 60000, 94103, 4),  -- San Francisco
('UX Designer', 'Design user-friendly interfaces and experiences.', 70000, 98101, 5),  -- Seattle
('Marketing Specialist', 'Develop marketing strategies and campaigns.', 85000, 33101, 6),  -- Miami
('Project Coordinator', 'Assist in project planning and execution.', 90000, 48201, 7),  -- Detroit
('Systems Analyst', 'Analyze and improve IT systems.', 65000, 02130, 1),  -- Boston
('Database Administrator', 'Manage and maintain database systems.', 72000, 60614, 2),  -- Chicago
('Network Engineer', 'Design and implement network solutions.', 68000, 10002, 3),  -- New York
('DevOps Engineer', 'Automate and streamline operations.', 62000, 94105, 4),  -- San Francisco
('Content Writer', 'Create engaging content for various platforms.', 58000, 98102, 5),  -- Seattle
('Sales Representative', 'Drive sales and build customer relationships.', 54000, 33102, 6),  -- Miami
('Quality Assurance Tester', 'Ensure software quality through testing.', 50000, 48202, 7),  -- Detroit
('Business Analyst', 'Analyze business needs and provide solutions.', 64000, 02131, 1),  -- Boston
('Graphic Designer', 'Create visual content for marketing materials.', 56000, 60615, 2),  -- Chicago
('SEO Specialist', 'Optimize website content for search engines.', 67000, 10003, 3),  -- New York
('Technical Writer', 'Document software and technical processes.', 60000, 94104, 4),  -- San Francisco
('Customer Support Specialist', 'Provide support to customers.', 58000, 98103, 5),  -- Seattle
('HR Manager', 'Manage human resources and employee relations.', 62000, 33103, 6),  -- Miami
('Financial Analyst', 'Analyze financial data and trends.', 53000, 48203, 7),  -- Detroit
('Operations Manager', 'Oversee daily operations and processes.', 61000, 02132, 1),  -- Boston
('IT Support Specialist', 'Provide technical support to users.', 57000, 60617, 2),  -- Chicago
('Network Administrator', 'Manage and maintain network infrastructure.', 64000, 10004, 3),  -- New York
('Web Designer', 'Design and create visually appealing websites.', 53000, 94106, 4),  -- San Francisco
('Mobile Developer', 'Develop applications for mobile devices.', 61000, 98104, 5),  -- Seattle
('Data Analyst', 'Analyze data to inform business decisions.', 56000, 33104, 6),  -- Miami
('Research Scientist', 'Conduct research and experiments.', 59000, 48204, 7),  -- Detroit
('Account Manager', 'Manage client accounts and relationships.', 65000, 02133, 1),  -- Boston
('Social Media Manager', 'Manage social media accounts and campaigns.', 58000, 60618, 2),  -- Chicago
('Event Coordinator', 'Plan and coordinate events.', 59000, 10005, 3),  -- New York
('Software Tester', 'Test software for bugs and issues.', 63000, 94107, 4),  -- San Francisco
('Business Development Manager', 'Identify and pursue new business opportunities.', 54000, 98105, 5),  -- Seattle
('Logistics Coordinator', 'Manage logistics and supply chain operations.', 61000, 33105, 6),  -- Miami
('Compliance Officer', 'Ensure compliance with regulations and policies.', 57000, 48205, 7),  -- Detroit
('Sales Manager', 'Lead the sales team and drive sales strategies.', 65000, 02134, 1),  -- Boston
('Product Designer', 'Design products that meet user needs.', 58000, 60619, 2),  -- Chicago
('Financial Consultant', 'Provide financial advice and planning.', 64000, 10006, 3),  -- New York
('IT Project Manager', 'Manage IT projects from start to finish.', 53000, 94108, 4),  -- San Francisco
('Cybersecurity Analyst', 'Protect systems and networks from cyber threats.', 61000, 98106, 39),  -- Seattle
('E-commerce Specialist', 'Manage online sales and marketing.', 56000, 33106, 39),  -- Miami
('Content Strategist', 'Develop content strategies for brands.', 59000, 48206, 39);  -- Detroit


## Persona 1: Timothy (Northeastern Student)**

## Find housing in the new city:
SELECT H.Address, H.Rent, H.Sq_Ft, L.Safety_Rating
FROM Housing H
JOIN Location L ON H.zipID = L.Zip
WHERE L.City_ID = (SELECT City_ID FROM City WHERE Name = 'New York');

## Find other students in the area:
SELECT U.name, U.email
FROM User U
WHERE U.Current_City_ID = (SELECT City_ID FROM City WHERE Name = 'New York')
  AND U.CategoryID = (SELECT CategoryID FROM Category WHERE CategoryName = 'Student');

## Understand the cost of living:
SELECT Name, Avg_Cost_Of_Living, Avg_Rent, Avg_Wage
FROM City
WHERE Name IN ('New York', 'Charlotte');

## Find information about the city:
SELECT Name, Population, Prop_Hybrid_Workers
FROM City
WHERE Name = 'New York';

-- ## Sublet existing apartment:
-- INSERT INTO Sublet (Housing_ID, Subleter_ID, Start_Date, End_Date)
-- VALUES (
--     (SELECT Housing_ID FROM Housing WHERE Address = '123 Main St, Boston'),
--     (SELECT UserID FROM User WHERE email = 'john.doe@example.com'),
--     '2024-06-01',
--     '2024-12-01'
-- );

## Find housing close to work:
SELECT H.Address, H.Rent, H.Sq_Ft, L.Safety_Rating
FROM Housing H
JOIN Location L ON H.zipID = L.Zip
WHERE L.City_ID = (SELECT City_ID FROM City WHERE Name = 'New York')
ORDER BY L.Safety_Rating DESC;

## **Persona 2: John (System Administrator)**

## Quickly add data to the database:
INSERT INTO City (Avg_Cost_Of_Living, Avg_Rent, Avg_Wage, Name, Population, Prop_Hybrid_Workers)
VALUES (2500, 1200, 3000, 'Vander', 800000, 0.3000);

## Efficiently delete unused data:
DELETE FROM Performance
WHERE Date < '2023-01-01';

## Manage user access levels:
UPDATE User
SET CategoryID = (SELECT CategoryID FROM Category WHERE CategoryName = 'Student')
WHERE email = 'john.doe@hotmail.com';

## Remove outdated logs:
DELETE FROM Performance
WHERE Date < '2023-01-01';

## Monitor database usage:
SELECT *
FROM Performance
ORDER BY Date DESC;

## Monitor database performance:
SELECT AVG(Avg_Speed) AS AvgPerformance, MAX(Top_Speed) AS PeakPerformance
FROM Performance;

## **Persona 3: Edward Elric (Employer)**

## Access data on cost of living:
SELECT Avg_Cost_Of_Living, Avg_Rent, Avg_Wage
FROM City
WHERE Name = 'New York';

## Find current students in New York:
SELECT COUNT(*) AS Total_Students
FROM User
WHERE Current_City_ID = (SELECT City_ID FROM City WHERE Name = 'New York');

## Locate main student areas:
SELECT L.Zip, L.Student_pop, L.Safety_Rating
FROM Location L
WHERE L.City_ID = (SELECT City_ID FROM City WHERE Name = 'New York');

## Post job details:
INSERT INTO JobPosting (Title, Bio, Compensation, Location_ID, User_ID)
VALUES (
    'Junior Developer',
    'Assist in the development of software applications.',
    5000,
    (SELECT Zip FROM Location WHERE City_ID = (SELECT City_ID FROM City WHERE Name = 'Boston') LIMIT 1),
    (SELECT UserID FROM User WHERE email = 'jane.smith@example.com')
);

## Update compensation packages:
UPDATE JobPosting
SET Compensation = Compensation + 500
WHERE Location_ID in (SELECT Zip FROM Location WHERE City_ID = (SELECT City_ID FROM City WHERE Name = 'New York'));

## Analyze remote work preferences:
SELECT Prop_Hybrid_Workers
FROM City
WHERE Name = 'New York';

## **Persona 4: Helen (Student Mother)**

## Access detailed city guides:
SELECT Name, Population, Prop_Hybrid_Workers, Avg_Cost_Of_Living
FROM City
WHERE Name = 'New York';

## Find safe housing for her child:
SELECT H.Address, H.Rent, H.Sq_Ft, L.Safety_Rating
FROM Housing H
JOIN Location L ON H.zipID = L.Zip
WHERE L.City_ID = (SELECT City_ID FROM City WHERE Name = 'New York')
  AND L.Safety_Rating >= 7;

## Streamline moving logistics:
SELECT A.Name AS Airport, H.Name AS Hospital
FROM Airport A
JOIN Hospital H ON A.City_ID = H.City_ID
WHERE A.City_ID = (SELECT City_ID FROM City WHERE Name = 'New York');

## Plan an effective budget:
SELECT Avg_Cost_Of_Living, Avg_Rent
FROM City
WHERE Name = 'New York';

## Connect with local communities:
SELECT U.name, U.email
FROM User U
WHERE U.Current_City_ID = (SELECT City_ID FROM City WHERE Name = 'New York')
  AND U.CategoryID = (SELECT CategoryID FROM Category WHERE CategoryName = 'Student');

## Set up an emergency contact network:
SELECT H.Name AS Hospital, A.Name AS Airport
FROM Hospital H
JOIN Airport A ON H.City_ID = A.City_ID
WHERE H.City_ID = (SELECT City_ID FROM City WHERE Name = 'New York');

Select *
From Performance
where date(Date) = '2024-12-07';

Select *
From User
where UserID = 39;

SELECT *
FROM Sublet
WHERE Subleter_ID = 1;

SELECT H.*
FROM Housing H
JOIN City C ON H.City_ID = C.City_ID
WHERE C.Name = 'Boston';

SELECT *
FROM JobPosting
WHERE User_ID = 39;