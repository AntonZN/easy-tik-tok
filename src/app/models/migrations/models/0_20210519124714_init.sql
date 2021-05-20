-- upgrade --
CREATE TABLE IF NOT EXISTS "category" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(64) NOT NULL,
    "views" INT NOT NULL  DEFAULT 0
);
CREATE INDEX IF NOT EXISTS "idx_category_views_dede54" ON "category" ("views");
CREATE TABLE IF NOT EXISTS "tag" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(64) NOT NULL UNIQUE,
    "views" INT NOT NULL  DEFAULT 0
);
CREATE INDEX IF NOT EXISTS "idx_tag_views_eb2f89" ON "tag" ("views");
CREATE TABLE IF NOT EXISTS "user" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "full_name" VARCHAR(100),
    "username" VARCHAR(100) NOT NULL UNIQUE,
    "email" VARCHAR(100) NOT NULL UNIQUE,
    "password_hash" VARCHAR(128),
    "is_active" INT NOT NULL  DEFAULT 1,
    "is_superuser" INT NOT NULL  DEFAULT 0
);
CREATE INDEX IF NOT EXISTS "idx_user_full_na_56ce62" ON "user" ("full_name");
CREATE INDEX IF NOT EXISTS "idx_user_usernam_9987ab" ON "user" ("username");
CREATE INDEX IF NOT EXISTS "idx_user_email_1b4f1c" ON "user" ("email");
CREATE TABLE IF NOT EXISTS "video" (
    "id" CHAR(36) NOT NULL  PRIMARY KEY,
    "loading_status" VARCHAR(20) NOT NULL  DEFAULT 'pending' /* PENDING: pending\nRUNNING: running\nFAIL: fail\nSUCCESS: success */,
    "storage" SMALLINT NOT NULL  DEFAULT 1 /* AWS_S3: 1\nLOCAL: 2 */,
    "title" VARCHAR(128) NOT NULL,
    "likes" INT NOT NULL  DEFAULT 0,
    "dislikes" INT NOT NULL  DEFAULT 0,
    "views" INT NOT NULL  DEFAULT 0,
    "size" VARCHAR(20),
    "path" VARCHAR(1024),
    "created" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    "category_id" INT REFERENCES "category" ("id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_video_likes_1de2b8" ON "video" ("likes");
CREATE INDEX IF NOT EXISTS "idx_video_views_0b4ad1" ON "video" ("views");
CREATE INDEX IF NOT EXISTS "idx_video_created_41fb0a" ON "video" ("created");
CREATE TABLE IF NOT EXISTS "userfollowing" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "created" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "following_user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_userfollowi_created_2e8100" ON "userfollowing" ("created");
CREATE TABLE IF NOT EXISTS "comment" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "text" TEXT NOT NULL,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    "reply_to_id" INT REFERENCES "comment" ("id") ON DELETE CASCADE,
    "video_id" CHAR(36) NOT NULL REFERENCES "video" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS "video_tag" (
    "video_id" CHAR(36) NOT NULL REFERENCES "video" ("id") ON DELETE CASCADE,
    "tag_id" INT NOT NULL REFERENCES "tag" ("id") ON DELETE CASCADE
);
