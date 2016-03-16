drop table if exists active;
drop table if exists ids;

create table active (
  id integer primary key autoincrement,
  img_type text not null,
  filename text not null, -- TODO: make unique
  insta_id text -- TODO: make unique
);

create table ids (
  id integer primary key autoincrement,
  img_type text not null,
  filename text not null,
  insta_id text not null -- TODO: make unique
);