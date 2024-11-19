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
        foreign key (Housing_ID) references Housing (Housing_ID),
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
    Post_ID int auto_increment not null,
    Compensation int,
    Location_ID int not null,
    User_ID int not null,
    Primary Key (Post_ID),
    Constraint jp_loc
        foreign key (Location_ID) references Location (zip),
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
('Employer');

#City data
INSERT INTO City (Avg_Cost_Of_Living, Avg_Rent, Avg_Wage, Name, Population, Prop_Hybrid_Workers) VALUES
(3000, 1500, 3500, 'Boston', 700000, 0.2500),
(2000, 1000, 2500, 'Chicago', 2700000, 0.1500),
(4000, 2500, 4500, 'New York', 8000000, 0.4000);

#Location data
INSERT INTO Location (Zip, City_ID, Student_pop, Safety_Rating) VALUES
(02115, 1, 50000, 8),
(60616, 2, 30000, 7),
(10001, (SELECT City_ID FROM City WHERE Name = 'New York'), 200000, 9);

#User data
INSERT INTO User (CategoryID, name, email, Phone_Number, Current_City_ID) VALUES
(1, 'John Doe', 'john.doe@example.com', '123-456-7890', 1),
(2, 'Jane Smith', 'jane.smith@example.com', '987-654-3210', 2),
(1, 'Alice Walker', 'alice.walker@example.com', '555-123-4567', (SELECT City_ID FROM City WHERE Name = 'New York'));

#Housing data
INSERT INTO Housing (City_ID, zipID, Address, Rent, Sq_Ft) VALUES
(1, 02115, '123 Main St, Boston', 1500, 750),
(2, 60616, '456 Oak St, Chicago', 1200, 850),
(3, 10001, '789 Broadway, New York', 3000, 600);

#Sublet data
INSERT INTO Sublet (Housing_ID, Subleter_ID, Start_Date, End_Date) VALUES
(1, 1, '2024-01-01', '2024-06-01'),
(2, 2, '2024-02-01', '2024-07-01');

#Job data
INSERT INTO Job (Wage, User_ID, Employment_Status, start_date) VALUES
(20, 1, 'Part-Time', '2023-09-01'),
(50, 2, 'Full-Time', '2023-07-01');

#Performance data
INSERT INTO Performance (Avg_Speed, Median_Speed, Top_Speed, Low_Speed) VALUES
(60, 55, 80, 40),
(70, 65, 90, 50);


#Insert into Airport
INSERT INTO Airport (Name, City_ID, Zip) VALUES
('Logan International', 1, 02115),
('O\'Hare International', 2, 60616),
('JFK International', (SELECT City_ID FROM City WHERE Name = 'New York'), 10001);

#Insert into Hospital
INSERT INTO Hospital (Name, City_ID, Zip) VALUES
('Boston Medical Center', 1, 02115),
('Rush University Medical Center', 2, 60616),
('New York General Hospital', (SELECT City_ID FROM City WHERE Name = 'New York'), 10001);

INSERT INTO JobPosting (Post_ID, Compensation, Location_ID, User_ID) Values
(1, 80000, 02115, 2),
(2, 95000, 60616, 2),
(3, 75000, 02115, 2);



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

## Sublet existing apartment:
INSERT INTO Sublet (Housing_ID, Subleter_ID, Start_Date, End_Date)
VALUES (
    (SELECT Housing_ID FROM Housing WHERE Address = '123 Main St, Boston'),
    (SELECT UserID FROM User WHERE email = 'john.doe@example.com'),
    '2024-06-01',
    '2024-12-01'
);

## Find housing close to work:
SELECT H.Address, H.Rent, H.Sq_Ft, L.Safety_Rating
FROM Housing H
JOIN Location L ON H.zipID = L.Zip
WHERE L.City_ID = (SELECT City_ID FROM City WHERE Name = 'New York')
ORDER BY L.Safety_Rating DESC;

## **Persona 2: John (System Administrator)**

## Quickly add data to the database:
INSERT INTO City (Avg_Cost_Of_Living, Avg_Rent, Avg_Wage, Name, Population, Prop_Hybrid_Workers)
VALUES (2500, 1200, 3000, 'Seattle', 800000, 0.3000);

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
INSERT INTO JobPosting (Compensation, Location_ID, User_ID)
VALUES (
    5000,
    (SELECT Zip FROM Location WHERE City_ID = (SELECT City_ID FROM City WHERE Name = 'Boston') LIMIT 1),
    (SELECT UserID FROM User WHERE email = 'jane.smith@example.com')
);

## Update compensation packages:
UPDATE JobPosting
SET Compensation = Compensation + 500
WHERE Location_ID = (SELECT Zip FROM Location WHERE City_ID = (SELECT City_ID FROM City WHERE Name = 'New York'));

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
