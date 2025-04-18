CREATE TABLE users (
  id int PRIMARY KEY,
  name varchar(128)
);

CREATE TABLE devices (
  id int PRIMARY KEY,
  device_name varchar(128),
  owned_by int,
  FOREIGN KEY (owned_by) REFERENCES devices(id)
);
