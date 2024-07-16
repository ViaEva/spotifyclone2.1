from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import User, Song, Playlist, db
from .schemas import UserSchema, SongSchema, PlaylistSchema
from . import bcrypt

user_schema = UserSchema()
users_schema = UserSchema(many=True)
song_schema = SongSchema()
songs_schema = SongSchema(many=True)
playlist_schema = PlaylistSchema()
playlists_schema = PlaylistSchema(many=True)

class UserRegister(Resource):
    def post(self):
        data = request.get_json()
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        user = User(username=data['username'], email=data['email'], password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return user_schema.dump(user), 201

class UserLogin(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        if user and bcrypt.check_password_hash(user.password, data['password']):
            access_token = create_access_token(identity=user.id)
            return jsonify(access_token=access_token)
        return {'message': 'Invalid credentials'}, 401

class SongList(Resource):
    @jwt_required()
    def get(self):
        songs = Song.query.all()
        return songs_schema.dump(songs), 200

    @jwt_required()
    def post(self):
        data = request.get_json()
        song = Song(**data)
        db.session.add(song)
        db.session.commit()
        return song_schema.dump(song), 201

class SongDetail(Resource):
    @jwt_required()
    def get(self, song_id):
        song = Song.query.get_or_404(song_id)
        return song_schema.dump(song), 200

    @jwt_required()
    def put(self, song_id):
        data = request.get_json()
        song = Song.query.get_or_404(song_id)
        for key, value in data.items():
            setattr(song, key, value)
        db.session.commit()
        return song_schema.dump(song), 200

    @jwt_required()
    def delete(self, song_id):
        song = Song.query.get_or_404(song_id)
        db.session.delete(song)
        db.session.commit()
        return {}, 204

class PlaylistList(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        playlists = Playlist.query.filter_by(user_id=user_id).all()
        return playlists_schema.dump(playlists), 200

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        data = request.get_json()
        playlist = Playlist(name=data['name'], user_id=user_id)
        db.session.add(playlist)
        db.session.commit()
        return playlist_schema.dump(playlist), 201

class PlaylistDetail(Resource):
    @jwt_required()
    def get(self, playlist_id):
        playlist = Playlist.query.get_or_404(playlist_id)
        return playlist_schema.dump(playlist), 200

    @jwt_required()
    def put(self, playlist_id):
        data = request.get_json()
        playlist = Playlist.query.get_or_404(playlist_id)
        for key, value in data.items():
            setattr(playlist, key, value)
        db.session.commit()
        return playlist_schema.dump(playlist), 200

    @jwt_required()
    def delete(self, playlist_id):
        playlist = Playlist.query.get_or_404(playlist_id)
        db.session.delete(playlist)
        db.session.commit()
        return {}, 204

class AddSongToPlaylist(Resource):
    @jwt_required()
    def post(self, playlist_id, song_id):
        playlist = Playlist.query.get_or_404(playlist_id)
        song = Song.query.get_or_404(song_id)
        playlist.songs.append(song)
        db.session.commit()
        return playlist_schema.dump(playlist), 200

class RemoveSongFromPlaylist(Resource):
    @jwt_required()
    def delete(self, playlist_id, song_id):
        playlist = Playlist.query.get_or_404(playlist_id)
        song = Song.query.get_or_404(song_id)
        playlist.songs.remove(song)
        db.session.commit()
        return {}, 204

def initialize_routes(api):
    api.add_resource(UserRegister, '/register')
    api.add_resource(UserLogin, '/login')
    api.add_resource(SongList, '/songs')
    api.add_resource(SongDetail, '/songs/<int:song_id>')
    api.add_resource(PlaylistList, '/playlists')
    api.add_resource(PlaylistDetail, '/playlists/<int:playlist_id>')
    api.add_resource(AddSongToPlaylist, '/playlists/<int:playlist_id>/songs/<int:song_id>')
    api.add_resource(RemoveSongFromPlaylist, '/playlists/<int:playlist_id>/songs/<int:song_id>')
