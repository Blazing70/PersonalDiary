[app]
title = Personal Diary
package.name = personaldiary
package.domain = com.tangsabas.personaldiary
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,db
version = 1.0
requirements = python3,kivy,sqlite3
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[app]
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.ndk_api = 21
android.private_storage = True
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
