#Creating the database
CREATE DATABASE if not exists coopConnect;

show databases;

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
    #Avg_Rent
    #Avg_Wage
    Name varchar(25),
    Population int,
    Prop_Hybrid_Workers decimal(5,4),
    check (Prop_Hybrid_Workers >= 0 and Prop_Hybrid_Workers <=1),
    PRIMARY KEY(City_ID)
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
        foreign key (zipID) references Location (Zipcode)
);

CREATE table if not exists Location
(
    Zipcode int not null,
    City_ID int not null,
    Student_pop int,
    Safety_Rating int,
    PRIMARY KEY(Zipcode)
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
    CONSTRAINT fk_05
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
)

Create table if not exists Hospital (
    HospitalID int auto_increment not null PRIMARY KEY,
    Name varchar(25) not null,
    City_ID int not null,
    Zip int not null,
    CONSTRAINT fk_07
                                    foreign key  (City_ID) references City (City_ID),
    CONSTRAINT fk_08
                                    foreign key (Zip) references Location (Zipcode)
);

# select statement representing the avg rent pulling the info from housing table
# SELECT avg(Rent) as Avg_Rent
# From Housing
# GROUP BY City_ID;

# select statement representing the avg wage pulling the info from the user and job tables
# SELECT avg(Job.Wage) as Avg_Wage
# From User join Job
# on User.UserID = Job.User_ID
# GROUP BY User.Current_City_ID;