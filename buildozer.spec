[app]
title = Miracle AI Assistant
package.name = miracle
package.domain = com.miraclegideon
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3,kivy==2.3.0,requests,certifi
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,RECORD_AUDIO,MODIFY_AUDIO_SETTINGS,FLASHLIGHT,CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,WAKE_LOCK,VIBRATE,SET_ALARM,CALL_PHONE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.arch = arm64-v8a
presplash.color = #0D0D1A
android.presplash_color = #0D0D1A

[buildozer]
log_level = 2
warn_on_root = 1
