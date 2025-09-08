from django.urls import path

from . import views

urlpatterns = [path("index.html", views.index, name="index"),
			path("Login.html", views.Login, name="Login"),
			path("Signup.html", views.Signup, name="Signup"),
			path("SignupAction", views.SignupAction, name="SignupAction"),	    	
			path("UserLoginAction", views.UserLoginAction, name="UserLoginAction"),
			path("CaptureFaceAction", views.CaptureFaceAction, name="CaptureFaceAction"),
			path("ValidateFaceAction", views.ValidateFaceAction, name="ValidateFaceAction"),
			path("WebCam", views.WebCam, name="WebCam"),
			path("ValidateFace.html", views.ValidateFace, name="ValidateFace"),
			path("Upload.html", views.Upload, name="Upload"),
			path("UploadAction", views.UploadAction, name="UploadAction"),	
			path("Download", views.Download, name="Download"),
			path("DownloadFileAction", views.DownloadFileAction, name="DownloadFileAction"),
]