function submitt() {
            var username = document.getElementById("username");
			var realname = document.getElementById("realname")
			var userid = document.getElementById("userid");
            var pass = document.getElementById("password");
			var repass = document.getElementById("repassword");
			var userEmail = document.getElementById("userEmail");
            if (username.value == "") {
                alert("请输入您的用户名");
                username.focus();
                return;
            }
			if(realname.value == "") {
				alert("请输入您的真实姓名");
				realname.focus();
				return;
			}
			if (userid.value == "") {
				alert("请输入您的学号");
				userid.focus();
				return;
			}
            if (pass.value == "") {
                alert("请输入密码");
                return;
            }
			if (repass.value == "") {
				alert("请再次输入密码");
				return;
			}
			if(repass.value != pass.value) {
				alert("您两次输入的密码不一致");
				return;
			}
			if(userEmail.value == "") {
				alert("请输入您的邮件地址");
				return;
			}
			/*
			这里实名认证
			for search local database;
			Not found? alert("认证失败，请重新属于信息");
			*/
		    var res = verifyCode.validate(document.getElementById("code_input").value);
		    if(res){
		        
		    }else{
		        alert("验证码错误");
		    }
            return true;
        }
		function confirm() {
			var username = document.getElementById("username");
			var realname = document.getElementById("realname")
			var userid = document.getElementById("userid");
			if (username.value == "") {
			    alert("请输入您的用户名");
			    username.focus();
			    return;
			}
			if(realname.value == "") {
				alert("请输入您的真实姓名");
				realname.focus();
				return;
			}
			if (userid.value == "") {
				alert("请输入您的学号");
				userid.focus();
				return;
			}
			/*
			实名认证检查
			分三种：
			1、学号姓名匹配：认证成功
			2、学号姓名已经注册：您已经注册过了
			3、学号姓名不匹配：认证失败，请核对您的信息
			*/
			/*
			if(“认证成功”){
				alert("认证成功");
			}
			*/
			return true;
		}