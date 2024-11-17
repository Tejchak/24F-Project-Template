#Creating the database
CREATE DATABASE if not exists coopConnect;

show databases;

Use coopConnect;

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

UPDATE City
SET Avg_Rent = (
    SELECT avg(Rent)
    FROM Housing
    WHERE Housing.City_ID = City.City_ID
    GROUP BY City_ID
);

Update City
SET Avg_Wage = (
    SELECT avg(Job.Wage) as Avg_Wage
    From User join Job
on User.UserID = Job.User_ID
    GROUP BY User.Current_City_ID
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

CREATE table if not exists Location
(
    Zip int not null,
    City_ID int not null,
    Student_pop int,
    Safety_Rating int,
    PRIMARY KEY(Zip)
);

CREATE table if not exists Sublet
(
    Sublet_ID int auto_increment not null,
    Housing_ID int not null,
    Subleter_ID int,
    Start_Date datetime,
    End_Date datetime,
    PRIMARY KEY(Sublet_ID),
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
    Name varchar(25) not null,
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
    Name varchar(25) not null,
    City_ID int not null,
    Zip int not null,
    CONSTRAINT fk_07
                                    foreign key  (City_ID) references City (City_ID),
    CONSTRAINT fk_08
                                    foreign key (Zip) references Location (Zip)
);
#sample data for each table

#Category data
INSERT INTO Category (CategoryName) VALUES
('Student'),
('Employer');

#City data
INSERT INTO City (Avg_Cost_Of_Living, Avg_Rent, Avg_Wage, Name, Population, Prop_Hybrid_Workers) VALUES
(3000, 1500, 3500, 'Boston', 700000, 0.2500),
(2000, 1000, 2500, 'Chicago', 2700000, 0.1500);

#Location data
INSERT INTO Location (Zip, City_ID, Student_pop, Safety_Rating) VALUES
(02115, 1, 50000, 8),
(60616, 2, 30000, 7);

#User data
INSERT INTO User (CategoryID, name, email, Phone_Number, Current_City_ID) VALUES
(1, 'John Doe', 'john.doe@example.com', '123-456-7890', 1),
(2, 'Jane Smith', 'jane.smith@example.com', '987-654-3210', 2);

#Housing data
INSERT INTO Housing (City_ID, zipID, Address, Rent, Sq_Ft) VALUES
(1, 02115, '123 Main St, Boston', 1500, 750),
(2, 60616, '456 Oak St, Chicago', 1200, 850);

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

-- Insert into Airport
INSERT INTO Airport (Name, City_ID, Zip) VALUES
('Logan International', 1, 02115),
('O\'Hare International', 2, 60616);

-- Insert into Hospital
INSERT INTO Hospital (Name, City_ID, Zip) VALUES
('Boston Medical Center', 1, 02115),
('Rush University Medical Center', 2, 60616);


