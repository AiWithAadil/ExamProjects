create database spotify;
use database spotify;
CREATE TABLE Playlists (
    Name VARCHAR(255) NOT NULL, 
    Tracks INT NOT NULL 
);

CREATE STAGE my_s3_stage
URL='s3://raw-bucket-ad/output/'
CREDENTIALS = (AWS_KEY_ID = '*************' AWS_SECRET_KEY = '**************');

show stages;

CREATE FILE FORMAT my_csv_format
TYPE = 'CSV'
FIELD_OPTIONALLY_ENCLOSED_BY = '"'
SKIP_HEADER = 1
FIELD_DELIMITER = ','
NULL_IF = ('NULL', 'null');

COPY INTO Playlists
FROM @my_s3_stage
FILE_FORMAT = (FORMAT_NAME = my_csv_format)
ON_ERROR = 'CONTINUE';  -- Adjust error handling as needed

select * from Playlists;