/* 
Created by : Srihari Kodam
Time Stamp : 2019-09-09
Version : 0.0.1
*/

/*
Problem Statement:

The ability for a company to retain its customers for a period of time is called
customer ​retention​.​Customer retention metrics are a set of measures that tells
how well a company is doing in retaining its customer base. There are various
measures of customer retention and every business/function chooses one that's most 
suitable for their business needs. The rider CRM team in Uber would want to find the retention 
of a customer cohort on a weekly-rolling basis, so that they can take necessary intervention if a 
rider has not taken a ride for 28 days.

Solution:

Steps Followed to provide Solution
    - Data Loading
    - Data Preparation
    - Data Aggregation
    - Metric Calculation
    - Storing in Results Table

Data Loading

/* Prepared Database named User_data*/
Create database User_data;
use User_data;

/* Loading sample data to Uber_main_data*/

Drop table if exists Uber_main_data;
create table if not exists Uber_main_data
(
    Ride_date Date,
    rider_id Varchar(40),
    trip_id Varchar(40),
    city_id Varchar(40),
    Ride_Status Varchar(40),
    index (rider_id,trip_id,city_id)  
);

/* sudo cp ~/Document/DataSciencePojects/Wipro_test/sample_trip_data.csv /usr/local/mysql/data 
sudo mysqld_safe --secure-file-priv="" */

LOAD DATA INFILE 'sample_trip_data.csv'
INTO TABLE Uber_main_data
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

/* Below date can be changed so that retention metric can be generate*/
set @date='2019-08-01'; 

/* Assigning most trips city for user as city for the user, who is using Uber from multiple cities*/
Drop table if exists Uber_city_updated_data;

create table if not exists Uber_city_updated_data
(city_id varchar(40),
 rider_id varchar(40),
 index(rider_id,city_id)
);
Insert into Uber_city_updated_data
select city_id,rider_id from 
(select rider_id,
        city_id,
row_number() over (partition by rider_id order by count(trip_id) desc) as rownumber
from Uber_main_data
Group by rider_id,city_id) as c
where rownumber=1
group by rider_id,city_id;

/* Assiging 'Active', 'Inactive' statuses for mau_28_status and pre_mau_28_status
By comparing indiviual ride_date with reporting date
     as recent 28 days and early 29 to 58 days.
*/
Drop table if exists Status_table;

create table if not exists Status_table
(
    Rider_id varchar(40),
    old_city_id varchar(40),
    upd_city_id varchar(40),
    Ride_date Date,
    trip_id varchar(40),
    mau_28_status varchar(40),
    pre_mau_28_status varchar(40),
    index (Rider_id,old_city_id,trip_id)
);

Insert into Status_table
select main.rider_id,main.city_id,upd.city_id,main.Ride_date,main.trip_id,
case 
when DateDiff(@date,Ride_date)<=28 and DateDiff(@date,Ride_date)>=0  then 'Active'
else 'Inactive' end mau_28_status,
case 
when DateDiff(@date,Ride_date)<=58 and DateDiff(@date,Ride_date)>=29 then 'Active'
else 'Inactive' end pre_mau_28_status
from Uber_main_data main
Left join Uber_city_updated_data upd
on main.rider_id=upd.rider_id;

/* Labeling each rider as Retained or Resurrected rider.
*/
Drop table if exists customer_status;

Create table if not exists customer_status
(rider_id varchar(40),
 rider_status varchar(40));

insert into customer_status
select 
    rider_id,
    case 
        when sum(if(mau_28_status='Active',1,0))>1 and sum(if(pre_mau_28_status='Active',1,0))>1 then 'Retained'
        when sum(if(mau_28_status='Active',1,0))>1 and sum(if(pre_mau_28_status='Inactive',1,0))>1 then 'Resurrect'
        end as rider_status
    from Status_table
Group by rider_id;

/* Preparing core table with all the information at each ride as its grain.
   Grain of the table is each ride
*/

Drop table if exists Uber_core_data;

Create table if not exists Uber_core_data
( Ride_date Date,
    rider_id Varchar(40),
    trip_id Varchar(40),
    m_city_id Varchar(40),
    city_upd varchar(40),
    mau_28_status varchar(40),
    pre_mau_28_status varchar(40),
    customer_status varchar(40),
    index (rider_id,trip_id,m_city_id)  
    );
Insert into Uber_core_data
select main.Ride_date,
        main.rider_id,
        main.trip_id,
        main.city_id as m_city_id,
        city.city_id as city_upd,
        Status.mau_28_status,
        Status.pre_mau_28_status,
        cs.rider_status
        from 
Uber_main_data main
Left outer join Uber_city_updated_data city
on main.rider_id=city.rider_id
left outer  join Status_table Status
on main.rider_id=Status.rider_id
and main.city_id=Status.old_city_id
and main.trip_id=Status.trip_id
left outer join customer_status cs
on main.rider_id=cs.rider_id;


/* Generating results and placing it in Result_first_query table
    This table grain is City
    This table contains information of
    - Number of Riders, took ride in early 28 days ride (inclusive)
    - Number of Riders, took ride in between 58 to 29 days (inclusive)
    - Number of Riders, took both the rides - Retention
    - Number of Riders, took only 28 days ride - Resurrect
*/
Drop table if exists Results_first_query;

Create table if not exists Results_first_query
( Date Date,
  City_id Varchar(40),
  mau_28 Int,
  pre_mau_28 Int,
  retention Int,
  Resurrect int);

Insert into Results_first_query
Select @date,
        city_upd,
        count(Distinct if(mau_28_status='Active',rider_id,Null)) as mau_28,
        count(Distinct if(pre_mau_28_status='Active',rider_id,Null)) as pre_mau_28,
        Count(Distinct if(customer_status ='Retained',rider_id,0)) as retention,
        Count(Distinct if(customer_status='Resurrect',rider_id,0)) as resurrect          
from Uber_core_data
Group by city_upd,@date
order by city_upd asc;


/* 
Provided calculation metrics is listed below
Retention: r​etained / mau_28
Reactivation:​ ​resurrect / previous_mau 

Metric to be tweaked as below to make more business sense:
Retention: r​etained / previous_mau_28
Reactivation:​ ​resurrect / mau_28

Retention is to be calculated based on riders who used Uber between 58 days to 29 days
Ex: Out of 100 riders of phase-1, still 80 riders are with Uber. 
Uber is able to retain 80% of rider from phase-1 to phase-2.

Reactivation is to be calculated as from total rider 28 days, how many have been resurrected.
i.e., earlier they were riders and dropped to use in the middle and started reusing the services of Uber.

Consider all riders were existing riders, no new riders. 
So reactivation is calculated w.r.to to total existing riders of past 28 days
*/

Drop table if exists Results_second_query;

Create table if not exists Results_second_query
(
    Date Date,
    City_id varchar(40),
    Retention Double,
    Reactivation Double
);

Insert into Results_second_query
select Date,
        City_id,
        retention/pre_mau_28 as Retention,
        resurrect/mau_28 as Reactivation
        From Results_first_query;

/* Below listed city has lowest retention and needs an attention,
However, how much is the retention differing more average retention is also to be looked at.
*/
select City_id from Results_second_query order by Retention asc limit 1;