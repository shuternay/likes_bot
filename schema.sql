drop table if exists likes;
create table likes (
  id integer primary key autoincrement,
  chat_id integer,
  message_id integer,
  user_id integer,
  like_type integer
);

drop table if exists messages;
create table messages (
  message_id integer,
  chat_id integer,
  user_id integer
);
