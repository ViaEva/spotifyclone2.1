from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)

class SongSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    artist = fields.Str(required=True)
    album = fields.Str(required=True)
    genre = fields.Str(required=True)
    length = fields.Str(required=True)

class PlaylistSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    user_id = fields.Int(required=True)
    songs = fields.List(fields.Nested(SongSchema))