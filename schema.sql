drop table if exists active;
drop table if exists ids;

create table active (
  id integer primary key autoincrement,
  img_type text not null,
  filename text not null,
  insta_id text
--   , active boolean not null TODO: make active state for super-like that start false and turn true after first pass
);

create table ids (
  id integer primary key autoincrement,
  img_type text not null,
  filename text not null,
  insta_id text not null
);